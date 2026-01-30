# Architecture Plan: AI-Powered 360 Feedback Voice Chat System

> **IMPORTANT:** Run validation spike FIRST (2-3 days) before committing to full build. See "Validation Spike" section below.

## Target Platform

**Web PWA (Progressive Web App)** - Browser-based, installable, works on all devices.
- Native iOS/Android apps are future scope
- Same WebSocket/audio architecture, but browser APIs
- Cross-platform from day one

## High-Level Architecture

```
Web PWA (Browser)
  • Web Audio API (mic capture)
  • MediaRecorder (audio streaming)
  • WebSocket API (bidirectional)
  • LocalStorage (session persistence)
  ↓ WebSocket (WSS)
  ↓ Audio: PCM chunks (20ms frames)
  ↓ Control: JSON messages
  ↓
Google Cloud Run (NOT Cloud Functions - WebSocket required)
  • WebSocketServer (client connections)
  • SessionOrchestrator (conversation state)
  • RetellProxy (bridge to Retell)
  • AnonymizationService (batch processing at end)
  • FirestoreConnector (persistence)
  • TextModeHandler (voice → text transition)
  ↓ ↓ ↓
  ↓ ↓ Firestore (sessions, transcripts, drafts, examples)
  ↓ ↓
  ↓ Retell AI WebSocket
  ↓   • STT (speech-to-text)
  ↓   • TTS Bridge → ElevenLabs Flash
  ↓   • LLM Bridge → Custom endpoint
  ↓
  Custom LLM WebSocket Endpoint (Cloud Run)
    → Gemini Flash API (custom prompts, full control)
```

---

## Critical Architectural Decisions

### 1. WEBSOCKET FLOW

**Decision: Cloud Run (NOT Cloud Functions)**
- Cloud Functions doesn't support WebSockets
- Cloud Run supports 60-minute WebSocket connections

**Architecture:**
```
Web PWA ←─ WSS ─→ Cloud Run ←─ WSS ─→ Retell AI
```

**Message Formats:**

Browser → Cloud Run:
```typescript
// Audio (binary)
{ type: 'audio_chunk', data: ArrayBuffer, timestamp, sequence }

// Control (JSON)
{ type: 'control', action: 'switch_to_text' | 'batch_approve_examples', sessionId, payload }

// Text input
{ type: 'text_input', sessionId, text }
```

Cloud Run → Browser:
```typescript
// Transcription
{ type: 'transcript', sessionId, text, isFinal, speaker }

// Audio response
{ type: 'audio_response', data: ArrayBuffer, timestamp, sequence }

// State updates
{ type: 'state_update', sessionId, state: { phase, transcript, tags, draftSummary } }

// Batch anonymized examples (at end of session)
{ type: 'anonymized_examples_ready', examples: Array<{id, original, anonymized}> }
```

**Proxy Pattern:**
Browser sends audio → Cloud Run validates/forwards to Retell → Retell processes (STT→LLM→TTS) → Cloud Run receives response → forwards to browser + saves to Firestore

**Browser Audio APIs:**
- `navigator.mediaDevices.getUserMedia()` for mic access
- `MediaRecorder` or `AudioContext` for capturing PCM chunks
- `AudioContext` for playback
- WebSocket API for bidirectional streaming

**Why proxy instead of direct?**
- No API keys on client
- Batch anonymization processing (doesn't interrupt conversation)
- Session state management
- Better error handling

### 2. RETELL INTEGRATION

**Decision: Bring-Your-Own (BYO) Gemini via Custom LLM WebSocket**

**Architecture:**
```
Web PWA ←→ Cloud Run ←→ Retell ←→ Cloud Run LLM Endpoint ←→ Gemini Flash
```

Retell handles voice pipeline orchestration, but delegates LLM calls to custom endpoint.

**Setup:**
1. Create second Cloud Run service: `/llm-websocket/:call_id`
2. Receives Retell's `RetellRequest` objects (transcript history, interaction type)
3. Transform to Gemini API format with custom system prompt
4. Stream Gemini response back to Retell as `RetellResponse`

**System Prompt Injection:**
- Lives entirely in Cloud Run LLM endpoint
- Retell never sees it—100% control
- Includes conversation state (current phase, completed questions, tags)

**Why BYO vs Retell-hosted LLM?**
- Full prompt control
- Gemini 3 Flash is 3x faster
- Cost savings
- Access to "low thinking mode" latency optimization

**Retell Configuration:**
- Voice: ElevenLabs Flash (configured in dashboard)
- LLM: Set `custom_llm_websocket_url` to Cloud Run endpoint
- Interruption handling: Enabled (Retell handles barge-in)
- STT: Retell's default (Deepgram)

**Alternative Considered:** Vapi (sub-600ms vs Retell's ~800ms), but Retell has better docs and stability. Consider Vapi if latency testing shows Retell >1s.

### 3. SESSION STATE MANAGEMENT

**Firestore Data Model:**

```typescript
// Collection: sessions
{
  sessionId: string,
  userId: string,
  feedbackRecipient: string,
  createdAt: Timestamp,
  lastActiveAt: Timestamp,
  status: 'active' | 'completed' | 'abandoned',
  currentPhase: 'warmup' | 'consent' | 'q1' | 'q2' | 'q3' | 'summary' | 'complete',
  completedQuestions: string[],
  retellCallId: string,
  isVoiceMode: boolean,
  textModeSwitchedAt?: Timestamp,
  switchTrigger?: 'tap' | 'verbal',
  deviceInfo: { platform, version }
}

// Subcollection: sessions/{sessionId}/transcripts
{
  speaker: 'user' | 'agent',
  text: string,
  timestamp: Timestamp,
  isFinal: boolean,
  sequence: number,
  mode: 'voice' | 'text'
}

// Subcollection: sessions/{sessionId}/tags
{
  type: 'strength' | 'development_area' | 'surprise',
  content: string,
  extractedAt: Timestamp,
  exampleIds: string[]
}

// Subcollection: sessions/{sessionId}/anonymizedExamples
{
  original: string,
  anonymized: string,
  status: 'processing' | 'pending_approval' | 'approved' | 'dropped',
  processedAt: Timestamp,
  approvalMethod?: 'verbal' | 'tap'
}

// Subcollection: sessions/{sessionId}/drafts
{
  version: number,
  summary: string,
  generatedAt: Timestamp,
  status: 'pending_review' | 'approved' | 'submitted',
  editHistory: Array<{timestamp, changes}>
}
```

**Auto-Save Strategy:**
- Save on every interaction (transcript, state update)
- Batch writes using Firestore batch operations
- Visual indicator: "Auto-saving..." badge appears briefly

**Session Resume:**
1. Client sends `start_session` with stored `sessionId`
2. Cloud Run calls `restoreSession(sessionId)` → loads session + transcripts + tags
3. Rebuild Gemini context from transcript history
4. Initialize Retell with "resume" context
5. Agent: *"Welcome back. We were just talking about [last topic]. Ready to continue?"*

### 4. LATENCY BUDGET

**Target: <1000ms end-to-end (user stops speaking → agent starts speaking)**

**Breakdown:**

| Component | Latency | Notes |
|-----------|---------|-------|
| VAD (Voice Activity Detection) | 200ms | Retell built-in |
| Network: Mobile → Cloud Run | 30ms | WSS, minimal payload |
| Cloud Run processing | 10ms | Proxy logic |
| Network: Cloud Run → Retell | 20ms | GCP region co-location |
| Retell STT | 100ms | Deepgram streaming |
| Network: Retell → Cloud Run LLM | 20ms | Internal GCP |
| **Gemini Flash TTFT** | **200ms** | Gemini 3 Flash optimized |
| Gemini streaming (first sentence) | 50ms | Stream aggressively |
| Network: Cloud Run → Retell TTS | 20ms | Internal to Retell |
| **ElevenLabs Flash TTFAB** | **100ms** | 75-135ms documented |
| Network: Retell → Cloud Run | 20ms | Return audio |
| Network: Cloud Run → Mobile | 30ms | WSS binary frames |
| Mobile audio buffer → speaker | 30ms | Platform pipeline |
| **TOTAL** | **830ms** | **✓ Achievable** |

**Latency Risks:**
1. **Gemini variability** (200-350ms TTFT)
   - Use "low" thinking mode parameter
   - Keep prompts under 500 tokens
   - Pre-warm connections
2. **Mobile network jitter**
   - WebSocket auto-reconnect
   - 100ms playback buffer on client
3. **ElevenLabs regional latency**
   - Use US region for US users
   - Pre-warm connections
4. **Retell overhead**
   - Benchmark Vapi if Retell >1s consistently

**Optimizations:**
- Stream Gemini response immediately (send first sentence to TTS ASAP)
- ElevenLabs streaming with `optimize_streaming_latency: 4`
- Keep-alive connections to all services
- Monitor per-component latency in Cloud Monitoring

### 5. ANONYMIZATION PIPELINE

**Strategy: Batch Approval at End of Session**

Instead of interrupting mid-conversation, collect all examples during the conversation, then present them for review on the summary screen. Faster UX, cleaner flow.

**Architecture:**

```
User gives example during Q2/Q3
  ↓
Save original to Firestore (status: 'queued')
  ↓
Agent: "Got it, thanks."
  ↓
Continue conversation (no interruption)
  ↓
[Background] Queue all examples for batch processing
  ↓
When Q3 completes → trigger batch anonymization
  ↓
Gemini processes all examples in parallel (1-2 seconds total)
  ↓
Update Firestore (status: 'pending_approval')
  ↓
Generate summary with anonymized examples
  ↓
Show summary screen with all examples side-by-side
  ↓
User reviews: approve/edit/drop each example
  ↓
Final submission
```

**Implementation Flow:**

1. **During Conversation:**
   - User provides example: *"She missed the Q3 launch checklist twice"*
   - Cloud Run saves to Firestore: `{ original: "...", status: 'queued', questionContext: 'q2' }`
   - Agent acknowledges: *"Got it."*
   - Continue conversation (no blocking, no interruption)

2. **End of Q3 → Batch Processing:**
   - Trigger: User completes final question
   - Cloud Run fetches all queued examples
   - Process all in parallel using Gemini (batch API call if available, or parallel requests)
   - Total time: 1-2 seconds for all examples combined

3. **Summary Screen:**
   - Display summary with anonymized examples embedded
   - Show side-by-side comparison UI for each example:
     ```
     Original: "She missed the Q3 launch checklist twice"
     Anonymized: "Missed key checklists on delivery items"

     [Keep] [Make More Private] [Drop]
     ```
   - User reviews all examples at once
   - Can edit any example inline

4. **Final Submission:**
   - User clicks "Submit Feedback"
   - Only approved examples included in final summary
   - Dropped examples removed entirely

**Gemini Anonymization Prompt:**
```
TASK: Anonymize these feedback examples by removing identifiers.

RULES:
- Remove names, dates, project names, team names
- Generalize specific events to patterns
- Preserve meaning and impact
- Keep concise (1-2 sentences max)

Process each example:

EXAMPLE 1:
Original: "[example 1]"
Anonymized:

EXAMPLE 2:
Original: "[example 2]"
Anonymized:

[etc.]
```

**Benefits Over Inline Approval:**
- No mid-conversation interruptions (faster, smoother UX)
- User sees all examples in context with full summary
- Can compare anonymization quality across all examples
- Faster total session time (~20 seconds vs ~10 seconds per example)
- Simpler state management (no conversation pause/resume logic)

**Latency Impact:**
- Background processing during conversation: transparent to user
- Batch anonymization after Q3: 1-2 seconds
- User reviews on summary screen: ~30 seconds
- Total session time: **4-5 minutes maintained**

### 6. TEXT MODE FALLBACK

**Triggers:**
1. **Verbal:** User says "text mode"
2. **Tap:** User taps mic-slash button

**Flow:**
1. Browser stops audio capture immediately (`mediaRecorder.stop()`)
2. Send control message: `{ type: 'control', action: 'switch_to_text', sessionId }`
3. Cloud Run updates Firestore: `isVoiceMode: false`
4. Cloud Run kills Retell WebSocket gracefully
5. Preserve conversation context (transcripts, tags, phase)
6. Send acknowledgment: *"Switching to text—your last point was: '[last transcript]'. Go ahead and type."*
7. UI switches to text input view (chat interface)

**Seamless Continuity:**
- Same `sessionId` maintained
- Same Firestore session document
- Same conversation history fed to Gemini
- Only difference: I/O format (audio vs text)

**Text Mode Processing:**
- User sends `{ type: 'text_input', text: '...' }`
- Cloud Run calls Gemini directly (same LLM, no Retell)
- Response sent as `{ type: 'text_response', text: '...' }`
- Save to transcripts with `mode: 'text'`

**Re-enabling Voice:**
- Allow user to switch back
- Re-establish Retell connection with same session context
- Continue from where they left off

### 7. ERROR HANDLING & RESILIENCE

**Failure Scenarios & Mitigations:**

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| **Retell drops mid-conversation** | WebSocket `onclose` event | Auto-reconnect (3 retries, exponential backoff). If fails → force text mode switch. |
| **ElevenLabs timeout** | 2-second timeout on TTS request | Fallback to Retell's default TTS. Ultimate fallback: text-only response. |
| **Gemini slow (>1.5s)** | AbortController timeout | Use cached response pattern based on current phase (e.g., "Tell me more about that."). |
| **Network interruption (browser)** | WebSocket connection loss | Auto-reconnect with exponential backoff (max 5 attempts). Session saved in Firestore + localStorage, resume on reconnect. |
| **Firestore write failure** | Exception on write | Retry 3x with exponential backoff. Queue in memory buffer, flush periodically. |

**Graceful Degradation Principles:**
- Never crash—always provide fallback
- Preserve session state at all costs
- Clear user messaging (e.g., "Voice connection lost. Let's continue in text.")
- Automatic recovery when possible

**Error Messages:**
```typescript
const ERROR_MESSAGES = {
  retell_failure: "Voice connection lost. Let's continue in text.",
  tts_timeout: "Audio temporarily unavailable. I'll send text instead.",
  gemini_slow: "Thinking... (this is taking longer than usual)",
  network_offline: "Your session is saved. Reconnect when you're back online.",
  firestore_error: "Saving... (retrying in background)"
};
```

**Health Monitoring:**
- Track uptime for Retell, Gemini, ElevenLabs
- Monitor average latencies per component
- Alert if metrics degrade (e.g., Retell uptime <95%)

---

## Critical Files to Create

### Backend (Cloud Run Services)

1. **`/backend/cloud-run/websocket-server.js`**
   - Core WebSocket server handling mobile client connections
   - Bidirectional proxy to Retell
   - Session orchestration (start, resume, end)
   - Control message handling (text mode switch, example approval)
   - Auto-save to Firestore on every interaction

2. **`/backend/cloud-run/llm-endpoint.js`**
   - Custom LLM WebSocket endpoint for Retell
   - Receives `RetellRequest` objects (transcript, interaction type)
   - Transforms to Gemini API format
   - Injects custom system prompt (conversation state, phase, rules)
   - Streams Gemini response back as `RetellResponse`

3. **`/backend/cloud-run/anonymization-service.js`**
   - Async anonymization pipeline
   - Queue management (process examples in background)
   - Gemini API calls with anonymization prompt
   - Playback approval flow (interrupt, play, wait for approval)
   - Fast-path regex optimizations for common patterns

4. **`/backend/cloud-run/firestore-schema.js`**
   - Data model definitions (TypeScript interfaces)
   - Session CRUD operations (create, restore, update)
   - Transcript persistence
   - Draft summary generation and storage
   - Batch write operations for performance

5. **`/backend/cloud-run/error-handlers.js`**
   - Centralized error handling
   - Retry logic with exponential backoff
   - Fallback strategies (Retell → text mode, ElevenLabs → default TTS)
   - Health monitoring and alerting
   - Memory queue for failed Firestore writes

### Frontend (Web PWA)

6. **`/frontend/src/services/WebSocketClient.ts`**
   - Resilient WebSocket client with auto-reconnect
   - Audio streaming (PCM chunks, 20ms frames)
   - Control message sending (text mode switch, batch approval)
   - Transcript display updates
   - Session persistence (save sessionId in localStorage for resume)

7. **`/frontend/src/services/AudioManager.ts`**
   - Microphone capture using Web Audio API (PCM 16kHz mono)
   - Audio playback pipeline using AudioContext
   - Visual indicators (waveform, volume levels)
   - Browser compatibility handling (Chrome, Safari, Firefox)
   - Permission handling (mic access)

8. **`/frontend/src/components/VoiceFeedbackScreen.tsx`**
   - Voice mode UI (mic button, live transcription, audio visualizer)
   - Text mode UI (chat-style input, message history)
   - Mode switching (tap mic button, handle voice trigger)
   - Auto-save indicator

9. **`/frontend/src/components/SummaryReviewScreen.tsx`**
   - Summary display with full feedback text
   - Batch example review UI (side-by-side original/anonymized)
   - Approve/edit/drop controls for each example
   - Final submission confirmation
   - Edit inline capability for any example

10. **`/frontend/public/manifest.json`**
    - PWA manifest (installable app metadata)
    - Icons, theme colors, display mode
    - Offline capabilities configuration

---

## Implementation Plan

> **NOTE:** Only proceed with full implementation AFTER validation spike (see below).

### Phase 1: Foundation (Week 1)
1. Set up Cloud Run service with WebSocket support
2. Implement basic WebSocket server (browser ↔ Cloud Run)
3. Integrate Retell AI (voice pipeline)
4. Set up custom LLM endpoint (Cloud Run ↔ Gemini)
5. Build basic PWA shell (Web Audio API, mic access, playback)
6. Test end-to-end audio flow with dummy prompts
7. **Validation:** Measure latency (target: <1s)

### Phase 2: Core Conversation Flow (Week 2)
1. Write Gemini system prompt (3-question loop, probing, tagging)
2. Implement session state management in Firestore
3. Build live transcription display in browser
4. Add auto-save on every interaction (Firestore + localStorage)
5. Implement dual exit system (verbal + tap → text mode)
6. **Validation:** Complete end-to-end 4-5 minute session

### Phase 3: Batch Anonymization (Week 3)
1. Build batch anonymization service (queue examples during conversation)
2. Implement Gemini batch anonymization prompt
3. Create SummaryReviewScreen with side-by-side example review
4. Add approve/edit/drop controls for each example
5. **Validation:** Test with 20 real examples, tune prompt, validate UX

### Phase 4: Error Handling & Polish (Week 4)
1. Implement all error handlers (Retell drop, Gemini timeout, network loss)
2. Add auto-reconnect logic (WebSocket, Retell)
3. Build graceful degradation fallbacks
4. Add health monitoring and alerting
5. Optimize latency (streaming, pre-warming)
6. PWA optimizations (service worker, offline support, install prompt)
7. **Validation:** Chaos testing (simulate failures)

### Phase 5: Testing & Launch (Week 5)
1. Cross-browser testing (Chrome, Safari, Firefox, Edge)
2. Mobile browser testing (iOS Safari, Android Chrome)
3. Latency benchmarking under load
4. Cost analysis (per-session costs)
5. Privacy audit (verify zero audio storage)
6. Beta test with 10 real users
7. **Validation:** >85% completion rate, <1s latency, positive feedback

---

## Validation Spike (REQUIRED FIRST STEP)

> **CRITICAL:** Run this 2-3 day spike BEFORE committing to full build. Validates all critical assumptions.

### Spike Goals

1. **Latency Benchmark (Retell vs Vapi)**
   - Deploy minimal Cloud Run + Retell + Gemini + ElevenLabs
   - Measure end-to-end with 10 real audio samples
   - Test Vapi with same setup
   - Compare average latency, P95, P99
   - **Decision point:** Choose Retell or Vapi based on data (target: <1s P95)

2. **Anonymization Quality Test**
   - Test Gemini on 20 diverse example cases
   - Manually evaluate quality (scale: 1-5)
   - Tune prompt iteratively until 90%+ achieve 4+ rating
   - Test edge cases (unique situations, specific details)
   - **Decision point:** If quality <80% satisfactory, consider human review layer

3. **Batch Approval UI Prototype**
   - Build quick prototype of summary screen with batch example review
   - Side-by-side original/anonymized comparison
   - Test with 3-5 users: "Is this UX clear? Do you trust the anonymization?"
   - **Decision point:** If users confused or distrustful, refine UX or add explanations

4. **Cost Projection**
   - Run 10 complete simulated sessions (4-5 minutes each)
   - Calculate actual costs per session:
     - Gemini: tokens × pricing
     - ElevenLabs: audio seconds × pricing
     - Retell: minutes × pricing
     - Firestore: reads/writes × pricing
   - **Decision point:** If >$0.50/session, optimize token usage or reconsider stack

### Spike Deliverables

- Latency comparison report (Retell vs Vapi)
- Anonymization quality evaluation (20 examples, ratings, tuned prompt)
- Batch approval UI prototype (working HTML/JS mockup)
- Cost model spreadsheet (per-session breakdown)
- Go/no-go recommendation with confidence level

---

## Risk Matrix

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| **Latency >1s** | High | Medium | **Validation spike:** Benchmark Retell vs Vapi, optimize Gemini, stream aggressively, pre-warm |
| **Retell reliability** | High | Low | Auto-reconnect (3 retries), fallback to text, monitor uptime |
| **Anonymization quality** | Medium | Medium | **Validation spike:** Test 20 examples, tune prompt, allow user edits in batch review UI |
| **Batch UI confusing** | Medium | Medium | **Validation spike:** Prototype testing with 3-5 users, refine based on feedback |
| **Browser compatibility** | Medium | Medium | Test Web Audio API across browsers, polyfills for Safari, fallback to MediaRecorder |
| **Voice drops (poor network)** | Medium | High | WebSocket auto-reconnect, session persistence (Firestore + localStorage), offline-first |
| **Cost overruns** | Medium | Low | **Validation spike:** Calculate per-session costs, set quotas, optimize tokens |
| **Privacy breach** | Critical | Very Low | Zero audio storage (verify in code), anonymization audit, encryption in transit/rest |

---

## Key Trade-offs

| Decision | Why This Choice | Alternative Considered |
|----------|----------------|------------------------|
| **Web PWA vs Native Apps** | Cross-platform day one, faster iteration, same WebSocket/audio architecture | Native iOS/Android (better performance but 2x dev effort) |
| **Cloud Run vs Functions** | WebSocket required | Cloud Functions (no WebSocket support) |
| **BYO Gemini vs Retell-hosted** | Speed (3x faster), cost, full control | Retell-hosted (simpler but less control) |
| **Batch anonymization vs Inline** | Faster UX (no interruptions), simpler state management, user sees all examples in context | Inline approval (interrupts conversation, adds ~10s per example) |
| **Same session for text mode** | Seamless context preservation | Separate endpoint (lose context) |
| **Retell vs Vapi** | TBD in validation spike | Both contenders, need latency data |

---

## Success Criteria

- ✓ End-to-end latency <1s (95th percentile)
- ✓ Session completion rate >85%
- ✓ Text mode fallback <20% usage
- ✓ Summary approval (no edits) >70%
- ✓ Batch example approval clear and trustworthy (user testing)
- ✓ Zero audio storage (verified in code audit)
- ✓ Cost <$0.50 per session
- ✓ PWA works on major browsers (Chrome, Safari, Firefox, Edge)
- ✓ PWA installable on mobile browsers (iOS Safari, Android Chrome)

---

## Next Steps

1. **Approve This Architecture Plan**
   - Review the plan
   - Ask any clarifying questions
   - Confirm approach before proceeding

2. **Run Validation Spike (2-3 days) - REQUIRED**
   - Benchmark Retell vs Vapi latency
   - Test anonymization quality on 20 examples
   - Prototype batch approval UI and test with 3-5 users
   - Calculate per-session costs
   - **Decision point:** Go/no-go based on spike results

3. **Full Implementation (5 weeks) - ONLY if spike validates**
   - Phase 1: Foundation (Cloud Run, Retell, Gemini, PWA shell)
   - Phase 2: Core conversation flow
   - Phase 3: Batch anonymization
   - Phase 4: Error handling & polish
   - Phase 5: Testing & launch

4. **Beta Testing & Iteration**
   - Beta test with 10 users
   - Collect feedback on UX, trust, completion rate
   - Iterate based on learnings
   - Prepare for broader launch

---

## Summary

This architecture plan delivers a **Web PWA-based voice feedback system** with:
- Sub-second latency voice conversations
- Batch anonymization review (no mid-conversation interruptions)
- Seamless text mode fallback
- Cross-platform from day one (browser-based)
- Validation spike to de-risk before full build

**Critical decision:** Run validation spike FIRST to confirm Retell vs Vapi choice, anonymization quality, and batch UI trustworthiness.
