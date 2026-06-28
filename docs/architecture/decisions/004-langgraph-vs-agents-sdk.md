# ADR-004: LangGraph versus OpenAI Agents SDK versus Direct Adapter

## Status

Accepted

## Context

MVP requires single-step failure classification with structured output. Free-tier models via Groq/Gemini.

## Decision

Use **direct LLM provider adapters** with prompt + Pydantic validation. **Do not use LangGraph or OpenAI Agents SDK in MVP.**

## Options considered

| Option | Advantages | Disadvantages |
|--------|------------|---------------|
| Direct adapter | Simple, testable, provider-agnostic | Manual failover logic |
| LangGraph | Multi-step agent flows | Overkill; extra dependency |
| OpenAI Agents SDK | Tool use | Tied to OpenAI; not free-first |

## Consequences

- Classification pipeline is explicit Python code.
- Easier unit testing with mocked adapters.
- Add orchestration library only when multi-step agents justified.

## Revisit conditions

- Product requires autonomous multi-source investigation (PR diff + logs + metrics).
- Tool-calling agents become core feature.
