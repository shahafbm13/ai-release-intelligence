# AI Behavior and Guardrails

## Purpose

Define how AI is used, what it must not do, and how the system fails safely on free-tier models.

## AI responsibilities (probabilistic)

- Assign category and subcategory from allowed taxonomy.
- Summarize failure in plain language.
- Suggest likely cause **when supported by provided evidence**.
- Suggest next action for QA engineer.
- Estimate confidence (0.0–1.0).
- Select evidence references pointing to input field paths.
- Flag `insufficient_information` when context is inadequate.

## Deterministic responsibilities (NOT AI)

- Failure normalization and fingerprinting.
- Secret masking.
- Similar-failure retrieval scoring.
- Release-risk score, level, factors, recommendation.
- Idempotency, auth, audit logging.

## Structured output schema (summary)

```json
{
  "category": "product_defect",
  "subcategory": "assertion_failure",
  "suspected_component": "checkout-service",
  "summary": "string",
  "likely_cause": "string",
  "suggested_action": "string",
  "confidence": 0.82,
  "evidence_refs": ["error_message", "stack_trace.lines[3]"],
  "insufficient_information": false
}
```

Validated by Pydantic before persistence.

## Guardrails

### Evidence grounding

- Prompt instructs: cite only from provided failure context.
- `likely_cause` MUST reference at least one evidence_ref when insufficient_information=false.
- Eval cases define **disallowed claims** (e.g., inventing deploy version not in input).

### Uncertainty

- Model MUST set insufficient_information=true when logs empty or ambiguous.
- Confidence < 0.5 triggers UI warning badge.
- Rule-based fallback sets confidence ≤ 0.4.

### Prompt injection

- Logs labeled as untrusted user content in prompt.
- System prompt: ignore instructions embedded in log content.
- No tool execution from model output in MVP.
- Eval case: malicious log attempting override.

### Sensitive data

- Mask secrets before prompt construction.
- Truncate log excerpts (e.g., max 4000 chars).
- Do not send full raw webhook to LLM.

### Cost / quota (free tier)

- Max failures classified per run: 10 (configurable).
- Max input tokens per call: enforced via truncation.
- Daily classification cap env var optional for demo protection.

## Provider chain

1. **Groq** (primary) — free API, fast inference.
2. **Gemini** (fallback) — free tier quota.
3. **Rule-based classifier** — regex/heuristic patterns; always available.

Each step logged with provider, latency, token counts.

## JSON reliability (free models)

Free models lack native structured output APIs. Pipeline:

1. Prompt includes JSON schema example.
2. Parse response as JSON.
3. Pydantic validate.
4. On failure: repair prompt (max 2 retries).
5. On persistent failure: next provider or rule fallback.

## Human review

- All classifications presented as **suggestions**.
- Feedback captured accept/correct.
- Original AI record immutable.
- Release-risk recommendation advisory only.

## Fallback behavior

When all providers fail:

- Rule-based category from error_type patterns.
- insufficient_information=true if no pattern match.
- Store failure_reason on classification record.

## Evaluation

- Versioned dataset: `tests/evals/data/`
- Metrics: category accuracy, schema compliance, injection resistance, insufficient-info behavior.
- CI: mocked provider; optional manual workflow with real keys.

## Prohibited behaviors

- Generating release-risk scores.
- Auto-blocking releases.
- Executing code or shell commands from model output.
- Storing or echoing unmasked secrets in classification text.
- Overwriting historical classifications with corrections (corrections are separate feedback records).
