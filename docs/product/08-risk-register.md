# Risk Register

| ID | Risk | Probability | Impact | Mitigation | Detection | Owner | Residual |
|----|------|-------------|--------|------------|-----------|-------|----------|
| R-001 | Incorrect AI classification | High | High | Structured schema, evidence refs, confidence, human feedback, eval suite, rule fallback | Correction rate, eval failures | AI/Backend | Medium |
| R-002 | Hallucinated root causes | Medium | High | Evidence must reference input fields; insufficient_information flag; disallow uncited claims in prompt | Eval disallowed-claims cases; manual review | AI | Medium |
| R-003 | Overreliance on AI | Medium | High | Advisory release-risk; human feedback required for trust narrative; UI shows evidence | User research; feedback rate | Product | Medium |
| R-004 | Insufficient supporting evidence in UI | Medium | Medium | Link evidence_refs to normalized fields; show raw failure alongside summary | UX review; story acceptance | Frontend | Low |
| R-005 | Sensitive logs/secrets exposed | Medium | High | Masking pipeline; truncate logs; never log raw secrets; README warning | Secret-pattern tests; security review | Backend | Low |
| R-006 | Malicious webhook payloads | Low | Medium | Signature verification; schema validation; size limits; no eval of payload as code | Invalid payload tests | Backend | Low |
| R-007 | Prompt injection via logs | Medium | High | Untrusted input treatment; system prompt guards; eval injection cases | Eval suite | AI | Medium |
| R-008 | Incorrect release-risk calculation | Low | High | Deterministic documented formula; unit tests; no LLM in score | Unit tests; golden cases | Backend | Low |
| R-009 | Free-tier rate limits / outage | High | Medium | Failover chain Groq→Gemini→rules; pre-seeded classifications; demo script | Fallback rate metric | Platform | Medium |
| R-010 | Vendor dependency (Groq/Gemini) | Medium | Medium | Pluggable adapter; rule fallback; optional future OpenAI adapter | Provider error logs | Architecture | Medium |
| R-011 | Poor evaluation data | Medium | Medium | 10 diverse synthetic cases; versioned dataset; eval report generator | Eval pass rate trends | AI | Medium |
| R-012 | Low user trust | Medium | High | Transparency, feedback loop, honest limitations in README | Acceptance rate | Product | Medium |
| R-013 | Scope creep | High | High | MoSCoW; Phase A/B gates; milestone exit criteria | Backlog review | Product | Medium |
| R-014 | Demo cold start / spin-down | High | Medium | Wake-up in demo script; pre-seeded data; optional recorded video | Demo rehearsal | Delivery | Medium |
| R-015 | Free DB/Redis limits exceeded | Low | Medium | Seed data size caps; retention policy doc | Storage monitoring | Platform | Low |

## Review cadence

- Review at each milestone exit.
- Update probabilities after M3 (first real classifications) and M5 (deployed demo).
