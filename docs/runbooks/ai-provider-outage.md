# Runbook: AI provider outage

## Symptoms

- Classifications show `provider: rules` for all failures.
- Logs contain `classification_adapter_skipped` (not configured) or `classification_adapter_failed`.
- Higher latency acceptable; output still produced via rule fallback.

## Quick checks

1. **API keys:** `GROQ_API_KEY` and `GEMINI_API_KEY` empty → rules-only mode (expected in CI and local dev without keys).
2. **Quota:** Free-tier rate limits cause adapter failures; check provider dashboards.
3. **Eval pass rate:** Run `python tests/evals/runner.py` — rules baseline should stay ≥ 70%.

## Resolution steps

1. **Demo without keys:** Rules fallback is designed for $0 operation. Confirm categories are reasonable for your scenario.
2. **Restore LLM path:** Set valid keys in env; restart API and worker.
3. **Verify chain:** Groq primary → Gemini fallback → rules. Logs show which step succeeded.
4. **Prompt changes:** Re-run eval suite before promoting prompt updates.

## When rules-only is acceptable

- Portfolio demo on free hosting without secrets.
- Provider outage during triage — human feedback still captured.

## Escalation

- Review [AI architecture](../architecture/08-ai-architecture.md) fallback chain.
- Optional manual workflow with live keys (not in PR CI).
