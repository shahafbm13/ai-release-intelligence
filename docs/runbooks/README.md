# Runbooks

Operational guides for the AI Release Intelligence Platform demo deployment.

| Runbook | When to use |
|---------|-------------|
| [Failed webhook processing](./failed-webhook-processing.md) | Webhooks return 4xx/5xx or runs never appear |
| [Worker backlog](./worker-backlog.md) | Runs stuck in `pending`, classifications missing |
| [AI provider outage](./ai-provider-outage.md) | Groq/Gemini errors; high rules fallback rate |
| [Database outage](./database-outage.md) | `/ready` fails, migration or connection errors |
| [Incorrect release-risk result](./incorrect-release-risk.md) | Risk score seems wrong; need to explain or tune |

Local commands reference: [README.md](../../README.md) and [docs/deploy/README.md](../deploy/README.md).
