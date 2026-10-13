# Executable specifications

Implementation in this repository is driven by **numbered, executable specifications** — not ad-hoc prompts or undocumented scope creep.

## Process

1. **Design phase (current):** Architecture and cross-cutting docs live under [docs/](../docs/). No numbered specs are required yet.
2. **Spec authoring:** Each feature or vertical slice gets a spec file such as `001-feature-request-submission.md`.
3. **Approval:** A human approves the spec (objective, acceptance criteria, and out-of-scope sections) before implementation starts.
4. **Implementation:** Agents and developers implement exactly one approved spec at a time, per [AGENTS.md](../AGENTS.md).
5. **Verification:** Acceptance criteria and listed tests must pass before the spec is marked done.

## Numbering

Use zero-padded three-digit prefixes in filename order of dependency or priority, for example:

- `001-...` foundational data model and API skeleton
- `002-...` feature request submission
- `003-...` semantic discovery and classification

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

**Note:** No numbered specification files exist yet. Do not implement application code until the first spec is approved.
