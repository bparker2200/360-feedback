# SKILL.md — 360 Feedback Voice Chat

## What Is This

AI-powered 360 feedback tool. Replaces forms with voice conversations. Users speak feedback, see live transcription, review anonymized summary, submit.

## Core Problem

Forms → guarded responses, shallow feedback, form fatigue.
Voice → natural conversation, deeper probing, higher completion.

## Stack (Planned)

| Layer | Choice | Notes |
|-------|--------|-------|
| Mobile | iOS/Android native | Mic input, audio playback, websocket |
| Backend | Google Cloud Functions | Single endpoint |
| Voice pipeline | Retell AI | STT, conversation flow, interruptions |
| TTS | ElevenLabs Flash | 75-135ms target |
| LLM | Gemini Flash | <350ms to first token |
| Storage | Firestore | Drafts, session state |

## Key Constraints

- **Sub-second latency** — end-to-end round-trip
- **No audio storage** — transcribe live, delete instantly
- **No API keys on client** — all processing server-side
- **4-5 min sessions** — longer = homework
- **Dual exit** — verbal ("text mode") + tap anytime

## Technical Unknowns (Architect First)

1. Websocket flow: mobile → Cloud Functions → Retell
2. Retell config: hosted LLM vs bring-your-own Gemini
3. Session persistence: mid-conversation exit/resume
4. Latency budget breakdown per component
5. Real-time anonymization without blocking
6. Text mode transition mid-conversation
7. Error handling / resilience

## Reference Docs

- `docs/360-feedback-prd.md` — Full PRD with UX, flow, requirements
- `docs/architect-prompt.md` — Technical architecture questions

## Build Phases

1. **Foundation** — Stack decision, websocket, latency validation
2. **Core Flow** — 3-question loop, live transcription, auto-save
3. **Anonymization** — Redaction pipeline, playback approval
4. **Polish** — Warm-up, consent copy, summary display
5. **Ship** — Demo video, beta test

## Success Metrics

| Metric | Target |
|--------|--------|
| Completion rate | >85% |
| Session duration | 4-5 min |
| Text fallback rate | <20% |
| Summary approval (no edits) | >70% |
