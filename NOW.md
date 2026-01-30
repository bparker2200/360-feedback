# NOW

## Current Task
Validation spike (2-3 days) — de-risk architecture before full build

## Blocker
None

## Next 3
1. **Latency benchmark:** Deploy minimal stack, compare Retell vs Vapi (target: <1s P95)
2. **Anonymization test:** Gemini quality on 20 examples, tune prompt (target: 90%+ quality)
3. **Batch UI prototype:** Build summary screen mockup, test with 3-5 users for trust/clarity
4. **Cost projection:** Run 10 simulated sessions, validate <$0.50/session

## Decisions Log
| Date | Decision | Context |
|------|----------|---------|
| 2026-01-29 | Web PWA (not native apps) | Cross-platform day one, faster iteration |
| 2026-01-29 | Batch anonymization (not inline) | Faster UX, no mid-conversation interruptions |
| 2026-01-29 | BYO Gemini via custom LLM endpoint | Full prompt control, 3x faster, cost savings |
| 2026-01-29 | Validation spike required first | De-risk latency, anonymization, costs before build |
