# Architecture Decision Records (ADR)

This directory holds short, dated records of significant technical decisions.

## When to add an ADR

Add an ADR when a decision is hard to reverse or affects multiple specs, for example:

- Switching from SQLite to PostgreSQL + pgvector
- Choosing an embedding model or LLM provider default
- Changing human-approval or AI processing state semantics
- Introducing a new cross-cutting library or deployment shape

## Format (suggested)

Use a numbered filename: `NNNN-short-title.md`

```markdown
# Title

- Status: proposed | accepted | deprecated | superseded
- Date: YYYY-MM-DD

## Context

## Decision

## Consequences
```

Placeholders and future ADRs live alongside [.gitkeep](.gitkeep) so the directory remains tracked before the first record is written.
