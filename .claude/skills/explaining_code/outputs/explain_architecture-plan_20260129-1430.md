# Explain: architecture-plan.md

**Generated:** 2026-01-29 14:30
**Target:** `/Users/brandonparker/Projects/360-feedback/docs/architecture-plan.md`

---

## Context

This architecture plan lives in `docs/architecture-plan.md` and serves as the technical blueprint for building the 360 feedback voice chat system. It defines the full stack (Web PWA → Cloud Run → Retell AI → Gemini), critical architectural decisions, data models, and implementation phases. This is the foundational doc that translates the PRD into buildable infrastructure.

## Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                      Web PWA (Browser)                       │
│  ┌────────────┐  ┌──────────────┐  ┌──────────────────┐    │
│  │ Web Audio  │  │  WebSocket   │  │  LocalStorage    │    │
│  │    API     │  │    Client    │  │  (sessions)      │    │
│  └─────┬──────┘  └──────┬───────┘  └──────────────────┘    │
└────────┼─────────────────┼──────────────────────────────────┘
         │                 │
         │ PCM Audio       │ WSS (JSON control messages)
         │ 20ms chunks     │
         └────────┬────────┘
                  ▼
┌──────────────────────────────────────────────────────────────┐
│              Cloud Run (WebSocket Server)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Session      │  │  Retell      │  │  Anonymization   │  │
│  │ Orchestrator │  │  Proxy       │  │  Service         │  │
│  └──────┬───────┘  └──────┬───────┘  └─────────┬────────┘  │
└─────────┼──────────────────┼────────────────────┼───────────┘
          │                  │                    │
          │                  ▼                    │
          │         ┌─────────────────┐           │
          │         │   Retell AI     │           │
          │         │  STT → TTS      │           │
          │         └────────┬────────┘           │
          │                  │                    │
          │                  ▼                    │
          │    ┌──────────────────────────┐      │
          │    │   Custom LLM Endpoint    │      │
          │    │    (Cloud Run #2)        │      │
          │    └──────────┬───────────────┘      │
          │               │                       │
          │               ▼                       │
          │      ┌─────────────────┐              │
          │      │  Gemini Flash   │              │
          │      └─────────────────┘              │
          │                                       │
          └───────────────┬───────────────────────┘
                          ▼
                 ┌─────────────────┐
                 │   Firestore     │
                 │ (sessions, etc) │
                 └─────────────────┘
```

## Walkthrough

**Critical architectural decisions** (in order of doc appearance):

### 1. Platform Choice
Web PWA over native apps—cross-platform from day one, browser APIs sufficient for audio/WebSocket

### 2. Cloud Run vs Functions
Cloud Run required because WebSockets need persistent connections (Functions doesn't support this)

### 3. Retell Integration Pattern
"Bring Your Own LLM" via custom WebSocket endpoint → full control over Gemini prompts, 3x faster than Retell-hosted

### 4. Session State Strategy
Firestore with auto-save on every interaction + localStorage for offline resilience. Resume capability rebuilds context from transcripts

### 5. Latency Budget
830ms target breakdown across 10 components. Most critical: Gemini TTFT (200ms) + ElevenLabs TTFAB (100ms). Uses streaming + pre-warming to optimize

### 6. Anonymization Architecture
**Key innovation:** Batch processing at end instead of inline interruptions. Queues examples during conversation, processes all in parallel (1-2s), presents side-by-side review on summary screen. Saves ~10s per example

### 7. Text Mode Fallback
Same session, same context—just swaps I/O format. Preserves transcripts, kills Retell gracefully, switches to direct Gemini calls

### 8. Error Handling
Graceful degradation: Retell drop → text mode, ElevenLabs timeout → default TTS, Gemini slow → cached pattern. WebSocket auto-reconnect with exponential backoff

**Implementation approach:**
- **Validation spike FIRST** (2-3 days): benchmark Retell vs Vapi, test anonymization quality on 20 examples, prototype batch UI, calculate costs
- **Decision gate:** Only proceed to full build if spike validates <1s latency, satisfactory anonymization, clear UI, <$0.50/session
- **5-week build** (if approved): Foundation → Conversation → Anonymization → Error handling → Testing

## Side Effects

**External API calls:**
- Retell AI WebSocket (persistent connection, audio streaming)
- Gemini Flash API (every user turn, token costs)
- ElevenLabs Flash API (every agent response, audio generation)
- Firestore writes (every interaction, batched)

**State mutations:**
- Firestore sessions + subcollections (transcripts, tags, anonymizedExamples, drafts)
- localStorage sessionId persistence (browser)

**Cost implications:**
- Per-session costs: Gemini tokens + ElevenLabs audio seconds + Retell minutes + Firestore R/W
- Target: <$0.50/session (validated in spike)

## Gotchas

**Gotcha [CRITICAL]:** Validation spike is **mandatory** before full build. Architecture plan (lines 545-586) emphasizes this 4 times. Going straight to implementation without latency benchmarks, anonymization quality tests, and cost validation = high risk of wasted effort if core assumptions fail.

**Gotcha [HIGH]:** Retell vs Vapi decision deferred to spike (line 136, 550-554). Retell has better docs but Vapi is faster (~600ms vs ~800ms). Choice impacts entire voice pipeline—can't be changed easily post-implementation.

**Gotcha [HIGH]:** Gemini TTFT variability (200-350ms, line 233-236). If Gemini hits the high end frequently, total latency exceeds 1s target. Mitigation requires "low thinking mode" + aggressive streaming—not guaranteed to work.

**Gotcha [MEDIUM]:** Browser Web Audio API compatibility (line 473-474). Safari has quirks with `MediaRecorder` and `AudioContext`. The plan mentions "polyfills" but doesn't detail Safari-specific fallbacks—needs investigation during Phase 1.

**Gotcha [MEDIUM]:** Batch anonymization assumes 1-2s for parallel processing (line 298). If Gemini doesn't support batch API and parallel requests hit rate limits, this becomes sequential (5-10s for 5 examples). Would break UX promise.

**Gotcha [LOW]:** Custom LLM endpoint adds operational complexity (line 104-128). Two Cloud Run services to maintain instead of one. Retell-hosted LLM would be simpler but loses prompt control—acceptable trade-off per plan, but worth monitoring in production.

## Dependencies

**External services** (all mission-critical):
- **Retell AI** (voice pipeline orchestration, STT, TTS bridge)
- **ElevenLabs Flash** (text-to-speech, 75-135ms target)
- **Gemini Flash** (LLM, <350ms TTFT target)
- **Firestore** (session persistence, transcripts, drafts)
- **Cloud Run** (WebSocket hosting, serverless compute)

**Browser APIs** (platform requirements):
- Web Audio API (mic capture, playback)
- WebSocket API (bidirectional streaming)
- localStorage (offline session persistence)
- PWA APIs (manifest, service worker)

**Related docs:**
- `docs/360-feedback-prd.md` (product requirements)
- `docs/architect-prompt.md` (technical questions)
- `SKILL.md` (project overview, stack constraints)

---

**Source:** `/Users/brandonparker/Projects/360-feedback/docs/architecture-plan.md`
**Explained by:** Claude Sonnet 4.5 via `/explain` skill
