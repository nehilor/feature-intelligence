# Agent operating rules

These rules apply to AI coding agents working in this repository.

## Before writing code

- Read [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/AI-DESIGN.md](docs/AI-DESIGN.md), [docs/SECURITY-AND-RELIABILITY.md](docs/SECURITY-AND-RELIABILITY.md), and the relevant numbered spec under [specs/](specs/).
- Implement **only** what an approved, numbered specification defines.
- Do not silently change requirements, acceptance criteria, or scope. Surface conflicts to a human.

## Change discipline

- Keep diffs narrowly scoped to the spec in progress.
- Avoid unnecessary dependencies, frameworks, and abstraction layers.
- Do not add speculative features or “nice to have” infrastructure (see README non-scope).

## AI and data handling

- Treat user-submitted feature request title and description as **untrusted input** (injection, exfiltration, and abuse scenarios).
- Validate all structured AI outputs against schemas before persisting or displaying them.
- Never implement autonomous delete, merge, roadmap finalization, score override, or outbound communications.
- Preserve human approval gates for all consequential product actions.

## Quality and completion

- When implementation begins: add or update tests that match the spec’s acceptance criteria.
- Run project validation (lint, typecheck, tests) before reporting work complete.
- Report assumptions, blockers, and failures explicitly; do not imply success for unverified steps.
- Follow [CLAUDE.md](CLAUDE.md) prompt logging for each new instruction.

## Architecture alignment

- Prefer the bounded Feature Triage Agent and deterministic priority engine described in [docs/AI-DESIGN.md](docs/AI-DESIGN.md).
- Do not introduce multi-agent swarms, message buses, or distributed orchestration unless a future ADR and spec explicitly require them.
