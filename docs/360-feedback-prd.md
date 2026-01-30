# Product Requirements Document: AI-Powered 360 Feedback Voice Chat

**Version:** 1.0
**Date:** January 29, 2026
**Status:** Draft

---

## Executive Summary

This document outlines the requirements for an AI-powered 360 feedback system that replaces traditional survey forms with natural voice conversations. The goal is to make feedback collection feel comfortable, honest, and efficient—leveraging conversational AI to probe deeper while maintaining strict anonymization and user trust.

---

## Problem Statement

Traditional 360 feedback forms suffer from several limitations:
- Typing in boxes feels impersonal and leads to filtered, guarded responses
- Static questions miss opportunities to dig deeper on meaningful feedback
- Users feel disconnected from the process and uncertain about anonymity
- Form fatigue leads to shallow, unhelpful responses

**Opportunity:** People drop filters when they're just chatting. A conversational voice interface can extract more honest, nuanced feedback in less time.

---

## Product Vision

A voice-first feedback collection tool that feels like talking to a thoughtful colleague—quick, natural, and trustworthy. Users speak their feedback, see it captured in real-time, review an anonymized summary, and submit with confidence that their identity is protected.

---

## Technical Architecture

### Core Technology Stack

| Component | Tool | Purpose | Latency Target |
|-----------|------|---------|----------------|
| LLM Brain | Gemini Flash | Conversation logic, follow-ups, summarization, anonymization | <350ms to first token |
| Text-to-Speech | ElevenLabs Flash | Natural voice output | 75-135ms TTFAB |
| Voice Platform | Retell AI | End-to-end voice flow, STT, interruption handling | Sub-second round-trip |
| Backend | Google Cloud Functions | Single endpoint, websocket streaming | — |
| Database | Firestore | Draft storage, session management | — |
| Frontend | Native iOS/Android apps | Mic input, audio playback, UI | — |

### System Architecture

```
┌─────────────────┐
│  Mobile App     │
│  (iOS/Android)  │
│                 │
│  • Mic input    │
│  • Audio player │
│  • UI/Controls  │
└────────┬────────┘
         │ WebSocket
         ▼
┌─────────────────┐
│  Cloud Function │
│  (Single        │
│   Endpoint)     │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌──────────┐
│Retell │ │Firestore │
│  AI   │ │(Drafts)  │
└───┬───┘ └──────────┘
    │
    ▼
┌─────────────────┐
│  ElevenLabs     │
│  (Voice)        │
└─────────────────┘
    │
    ▼
┌─────────────────┐
│  Gemini Flash   │
│  (Brain)        │
└─────────────────┘
```

**Key Architecture Decisions:**
- No AI/LLM on device—all processing server-side
- No API keys on client
- Single websocket connection handles all communication
- Same backend serves both iOS and Android

---

## User Experience Requirements

### 1. Trust & Privacy (Critical)

**No Audio Storage**
- Transcribe live, delete audio instantly
- Zero voice retention—communicate this explicitly upfront
- Text-only processing after transcription

**Transparency Touchpoints:**
- Intro screen: "We transcribe live, delete the audio instantly, zero retention"
- AI voice repeats this verbally at conversation start
- Post-session confirmation: "Your input has been anonymized and deleted"

**Consent Flow:**
> "This chat is private. No recording. Your words go straight to anonymous insights. You can bail anytime."

### 2. Onboarding & Comfort

**Optional Warm-Up Round**
- 30-second practice chat before real feedback
- Nothing stored, nothing analyzed
- Example prompt: "Hey, I'm the feedback bot. What's your favorite lunch spot?"
- Purpose: Gets mic anxiety out of the way, proves the system is painless

**Skip Option**
- One-click bypass: "Skip to the real stuff"
- No judgment, no friction for tech-savvy users

### 3. Dual Exit System

Users must always feel in control. Two parallel escape routes:

| Exit Method | Trigger | System Response |
|-------------|---------|-----------------|
| **Verbal** | User says "text mode" | Bot acknowledges: "Switching to text—your last point was..." then continues in text |
| **Tap** | User taps mic-slash button | Audio dies silently, mic indicator turns off, screen shows "Now in text. Carry on." |

**Setup Communication:**
> "Whenever you're ready, say 'text mode' or hit the mic button up top and we'll drop the voice."

### 4. Live Transcription Display

- Real-time text streaming as user speaks (like Grok)
- Shows: "You're saying: 'Leadership is solid but...'"
- Builds trust: user sees they're being heard correctly
- Enables on-the-fly corrections before sending

### 5. Auto-Save & Draft Management

**Visual Indicator:**
- Small "Auto-saving" badge appears as conversation progresses
- On app close/switch: "Saved draft—come back anytime. Not submitted yet."

**Clear Separation:**
- Auto-save ≠ submission
- Only explicit "Submit" action finalizes feedback
- Progress never lost, but nothing sent without approval

---

## Core Feedback Flow

### Target Duration: 4-5 minutes

Longer than this becomes "homework." Keep it punchy.

### Three Core Questions

1. **"What do they absolutely crush?"** (Strengths)
2. **"What do they fumble?"** (Development areas)
3. **"Anything lately that caught you off guard—good or bad?"** (Surprises)

No scales. No ratings. Raw, honest language that mirrors how people actually talk.

### Conversational Probing

The AI doesn't just accept answers—it mines for insight:

| User Says | AI Follow-Up |
|-----------|--------------|
| "He rocks at sales" | "Awesome—what's one thing he does that actually closes deals?" |
| "She sucks at follow-up" | "Got a pattern, or was it just one meltdown?" |
| Generic praise | "That's cool. Can you give me one specific moment that showed that?" |

**Guardrail:** Always drive toward illuminating insight for the feedback receiver. If conversation gets chatty, loop back: "That's helpful. But on that development area—any more detail?"

### Example Collection & Anonymization

When probing for examples:

**Pre-Prompt Reassurance:**
> "Want to back that up with a real quick example? It'll stay totally anonymous—I'll scrub names, dates, everything. You'll hear the safe version before it leaves your mouth."

**Anonymization Process:**
1. User provides specific example
2. LLM strips identifiers (names, dates, projects, context clues)
3. Transformed example played back to user

**Example Transformation:**
- Input: "Missed the launch checklist twice in Q3"
- Output: "Missed key checklists on delivery items"

**Post-Anonymization Options:**
> "Spot on? Say 'yep' to keep it, 'more private' to dial it back, or 'drop it' to lose this bit entirely."

Three words, zero pressure, full control.

**Frequency:** Remind users about anonymization at least twice during example collection—casual, not preachy.

---

## Summary & Submission Flow

### Summary Generation

After questions complete, AI generates a summary that mirrors exactly what the recipient will see.

**Delivery Method:** Voice first, then text display

**Format:** Warm, human paragraph—not bullet points
> "Alright, here's the summary that'll actually go through. Listen up: 'Mark is quick on decisions, generous with credit, but his follow-through on small stuff needs work. Biggest win was how he rallied the team last quarter.'"

**With Examples (if provided):**
> "They flagged follow-through as weak—e.g., missed key checklists on delivery items."

### Edit Flow

**Prompt:**
> "Now—if that's not quite right, tell me what's off and I'll tweak it."

Users can:
- Approve verbally ("yep, that's good")
- Request edits by voice
- Edit text directly on screen

### Final Submission

**Pre-Submit Confirmation:**
> "This is what the final recipient will actually hear. No more edits once you hit send. Still good?"

**UI:** Single prominent "Submit" button
- No "save for later" (already auto-saved)
- No "maybe" options
- Binary: done or not done

---

## System Prompt Structure

The Gemini Flash system prompt defines all behavior:

```
ROLE:
You are a 360 feedback collection engine. Your job is to run a
three-question conversational loop, extract meaningful insights,
and produce anonymized summaries.

RULES:
- Never store voice recordings
- Never use or reveal names
- Always show summary before submission
- Always provide verbal and tap exit options to text mode
- Remind users about anonymization when requesting examples
- Keep total conversation under 5 minutes
- Tag all feedback: <strength>, <development_area>, <surprise>

QUESTION FLOW:
1. "What do they absolutely crush?"
   → Follow up: "What's one thing they do that really makes that shine?"
   → Tag: <strength>

2. "What do they fumble?"
   → Follow up: "Got a pattern, or an example you can share?"
   → If example given: anonymize, play back, get approval
   → Tag: <development_area>

3. "Anything that caught you off guard—good or bad?"
   → Follow up based on response
   → Tag: <surprise>

SUMMARY FORMAT:
- One warm paragraph, human tone
- Include anonymized examples where provided
- Structure: [Primary strength] + [Development area] + [Notable observation]

ANONYMIZATION RULES:
- Remove all names, dates, project names, team names
- Generalize specific events to patterns
- Preserve meaning while removing identifiers
- Always play back anonymized version for approval
```

---

## Success Metrics

| Metric | Target | Rationale |
|--------|--------|-----------|
| Completion rate | >85% | Higher than form-based feedback |
| Average session duration | 4-5 min | Sweet spot before fatigue |
| Text-mode fallback rate | <20% | Voice should feel natural for most |
| Summary approval rate (no edits) | >70% | AI understanding quality |
| User-reported trust score | >4/5 | Privacy confidence |

---

## Future Considerations

- **Multi-language support** via ElevenLabs voice cloning
- **Manager dashboard** for aggregated insights
- **Trend analysis** across feedback cycles
- **Integration** with existing HRIS systems
- **Scheduled reminders** for feedback collection periods

---

## Open Questions

1. Should warm-up questions be customizable per organization?
2. What's the minimum viable anonymization threshold for examples?
3. How do we handle feedback that's impossible to anonymize (unique situations)?
4. Do we need human review as a backend safety net for anonymization?

---

## Appendix: User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         START                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Consent & Privacy Disclosure                                    │
│  "This chat is private. No recording. You can bail anytime."    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Warm-Up (Optional)                                              │
│  "What's your favorite lunch spot?"                             │
│                                                                  │
│  [Skip] ─────────────────────────────────────────────┐          │
└─────────────────────────────────────────────────────────────────┘
                              │                         │
                              ▼                         │
┌─────────────────────────────────────────────────────────────────┐
│  Q1: "What do they absolutely crush?"                           │
│  → Follow-up probe                                               │
│  → Tag: <strength>                                               │
│                                                    ┌────────────┐│
│  [Say "text mode" or tap mic] ────────────────────►│ Text Mode  ││
└─────────────────────────────────────────────────────────────────┘│
                              │                         │          │
                              ▼                         │          │
┌─────────────────────────────────────────────────────────────────┐
│  Q2: "What do they fumble?"                                     │
│  → Follow-up probe                                               │
│  → Request example (optional)                                    │
│  → Anonymize & playback                                          │
│  → User approves/edits/drops                                     │
│  → Tag: <development_area>                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Q3: "Anything catch you off guard?"                            │
│  → Follow-up based on response                                   │
│  → Tag: <surprise>                                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Summary Playback                                                │
│  "Here's what the recipient will hear: [summary]"               │
│                                                                  │
│  → User approves / requests edits                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Final Confirmation                                              │
│  "No more edits once you hit send. Still good?"                 │
│                                                                  │
│                    [ SUBMIT ]                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Confirmation                                                    │
│  "Your input has been anonymized and submitted. Thanks."        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Build Checklist

### Phase 1: Foundation
- [ ] Finalize stack decision: Retell vs Vapi (run latency tests)
- [ ] Set up Cloud Functions endpoint with websocket
- [ ] Connect Retell/Vapi → ElevenLabs → Gemini Flash pipeline
- [ ] Measure end-to-end round-trip latency (target: sub-second)
- [ ] Build basic mobile shell (mic input, audio playback, websocket connection)

### Phase 2: Core Flow
- [ ] Write system prompt for Gemini Flash (questions, follow-ups, tagging)
- [ ] Implement three-question conversation loop
- [ ] Build live transcription display
- [ ] Add dual exit system (verbal trigger + tap button)
- [ ] Implement auto-save to Firestore
- [ ] Build summary generation and playback

### Phase 3: Anonymization
- [ ] Define anonymization rules (names, dates, projects, teams)
- [ ] Build redaction pipeline with example transformations
- [ ] Implement "play back anonymized version" flow
- [ ] Add approve/edit/drop options for examples

### Phase 4: Polish
- [ ] Design warm-up flow (optional, skippable)
- [ ] Build submission confirmation screen
- [ ] Write all privacy/consent microcopy
- [ ] Create recipient-facing summary display
- [ ] End-to-end testing of full 4-5 minute flow

### Phase 5: Ship
- [ ] Record demo video showing complete flow
- [ ] Write privacy promises and consent script
- [ ] Build simple landing page / explainer
- [ ] Beta test with a handful of real users

---

## Supporting Assets to Build

| Asset | Purpose | When |
|-------|---------|------|
| **Demo video** (2-3 min) | Show warm-up → questions → anonymization → summary → submit | Before launch |
| **Privacy one-pager** | Explain no-audio retention, anonymization process, user controls | Before launch |
| **Conversation design doc** | Document all prompts, follow-ups, opt-outs for future iteration | During build |
| **Landing page** | Explain why voice-first beats forms, link to demo | Launch |

---

## Launch Ideas

**Content plays:**
- Post demo clip on LinkedIn/X highlighting the instant text-switch and "hear your summary before it sends" features
- Write a short post on the trust problem with traditional 360s and how voice + anonymization changes it
- Share the technical architecture on dev communities (how to wire Retell + ElevenLabs + Gemini)

**Distribution experiments:**
- Cold outreach to HR/People Ops folks who complain about low feedback completion rates
- Submit to Product Hunt with the "conversational feedback" angle
- Pitch to future-of-work or AI-in-HR podcasts
- Post in relevant Slack/Discord communities (HR tech, AI builders)

**Validation before scaling:**
- Run 5-10 real feedback sessions, measure completion rate and time
- Ask: "Did you feel comfortable? Did the anonymization work?"
- Iterate on question phrasing and follow-up probes based on transcripts

---
