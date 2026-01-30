# Architect Prompt for 360 Feedback Voice Chat

Use this prompt when starting the architecture conversation in plan mode.

---

## Prompt

I'm building an AI-powered 360 feedback tool that replaces forms with voice conversations. I've attached the PRD with full context on UX, flow, and requirements.

**The core technical challenge:** Wire up a real-time voice conversation system with sub-second latency.

**Stack I'm planning:**
- Mobile apps (iOS/Android) → websocket connection
- Google Cloud Functions → single backend endpoint
- Retell AI → handles STT, conversation flow, interruptions
- ElevenLabs Flash → TTS (75-135ms target)
- Gemini Flash → LLM brain (<350ms to first token)
- Firestore → draft storage, session state

**What I need you to architect:**

1. **Websocket flow**: How does the mobile client connect to Cloud Functions, and how does Cloud Functions orchestrate Retell? What's the message format for audio chunks going in and out?

2. **Retell integration**: Retell handles the voice pipeline (STT → LLM → TTS). What's the right way to configure it with my custom Gemini system prompt? Do I use their hosted LLM option or bring my own?

3. **Session state**: User can leave mid-conversation and come back. How do I persist conversation state (transcript, tags, draft summary) in Firestore and restore it seamlessly?

4. **Latency budget**: End-to-end round-trip target is sub-second. Break down the latency budget across each component (STT, LLM, TTS, network hops). Where are the risks?

5. **Anonymization pipeline**: When the user gives a specific example, I need to run it through Gemini to strip identifiers before playing it back. How does this fit into the real-time flow without adding noticeable delay?

6. **Text mode fallback**: User can switch to text mid-conversation. How do I handle the transition cleanly—kill the audio stream, switch to a text-based exchange, but keep the same session and context?

7. **Error handling**: What happens if Retell drops, ElevenLabs times out, or Gemini is slow? How do I build resilience without the user feeling it?

Start with a high-level architecture diagram, then dive into each component. Flag any decisions I need to make (e.g., Retell vs Vapi, hosted vs bring-your-own LLM).
