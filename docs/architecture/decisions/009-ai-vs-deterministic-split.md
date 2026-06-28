# ADR-009: AI versus Deterministic Responsibility

## Status

Accepted

## Context

Product must avoid "AI wrapper" perception and unsafe release decisions.

## Decision

Split responsibilities strictly:

**AI:** category, summary, likely cause (evidence-bound), suggested action, confidence, evidence refs.

**Deterministic:** normalization, masking, similar-failure matching, release-risk score, idempotency, auth, audit.

## Consequences

- Release-risk module has zero LLM imports.
- Classification service never writes risk scores.
- Eval suite tests each side independently.
- Rule fallback ensures pipeline completes without AI.

## Revisit conditions

- Product explicitly requests natural-language risk narrative (still not score generation).
- Hybrid models with human-approved weight learning from feedback.
