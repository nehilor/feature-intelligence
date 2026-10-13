# Executable specifications

Implementation in this repository is driven by **numbered, executable specifications** — not ad-hoc prompts or undocumented scope creep.

## Process

1. **Design phase:** Architecture and cross-cutting docs live under [docs/](../docs/). Numbered executable specs define implementation slices.
2. **Approval:** Each spec’s objective, acceptance criteria, and out-of-scope sections are approved before implementation of that spec.
3. **Implementation:** Agents and developers implement exactly one spec at a time, per [AGENTS.md](../AGENTS.md).
4. **Verification:** Acceptance criteria and listed tests must pass before the spec is marked done.

## Approved implementation sequence

Implement in strict order — do not skip ahead:

| Order | Spec | Title |
| --- | --- | --- |
| 1 | [SPEC-001-project-foundation.md](SPEC-001-project-foundation.md) | Project Foundation |
| 2 | [SPEC-002-feature-request-core.md](SPEC-002-feature-request-core.md) | Feature Request Core |
| 3 | [SPEC-003-ai-feature-triage.md](SPEC-003-ai-feature-triage.md) | AI Feature Triage |
| 4 | [SPEC-004-semantic-relationship-intelligence.md](SPEC-004-semantic-relationship-intelligence.md) | Semantic Relationship Intelligence |
| 5 | [SPEC-005-priority-and-human-decision-workflow.md](SPEC-005-priority-and-human-decision-workflow.md) | Priority & Human Decision Workflow |
| 6 | [SPEC-006-ai-evaluation-and-submission-hardening.md](SPEC-006-ai-evaluation-and-submission-hardening.md) | AI Evaluation & Submission Hardening |

**Order:** SPEC-001 → SPEC-002 → SPEC-003 → SPEC-004 → SPEC-005 → SPEC-006.

Renumbering is avoided once a spec is approved; supersede with a new spec and reference the old one if requirements change materially.

## Specification template

Copy the following sections into each new spec. Fill every section; use “N/A” only when genuinely not applicable and explain why in one line.

### Objective

What this spec delivers and why it matters for the product workflow.

### Business Context

How this slice fits the end-to-end flow (request → evidence → score → brief → human decision).

### Dependencies

Prior specs, docs, or external services that must exist first.

### Functional Requirements

Testable user- and system-visible behavior.

### Non-Functional Requirements

Performance, reliability, operability, and UX constraints for this slice.

### Data Model

Entities, fields, relationships, and invariants introduced or changed.

### API Contract

Endpoints, request/response shapes, error codes, and idempotency where relevant.

### AI Behavior

Prompts, tools, structured output schemas, retrieval strategy, and degradation for this slice — aligned with [docs/AI-DESIGN.md](../docs/AI-DESIGN.md).

### UI Behavior

Screens, states, empty/error/loading behavior, and what is read-only vs actionable.

### Failure Modes

Expected failures (provider outage, validation errors, partial AI) and system responses.

### Security Considerations

Untrusted input, injection, secrets, and approval gates for this slice.

### Acceptance Criteria

Checklist a reviewer can verify without interpretation.

### Tests

Unit, integration, and evaluation tests to add or extend.

### Out of Scope

Explicit exclusions to prevent scope drift.

### Definition of Done

Concrete completion signals (merged code, passing CI, docs updated, ADR if needed).

---

Implementation has not started yet; begin with **SPEC-001** when ready.
