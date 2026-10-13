# Feature Intelligence

**Status:** Design and specification phase — no application runtime, APIs, or UI are implemented yet.

## Problem statement

Product teams receive noisy, duplicated, and solution-oriented feature requests. Raw text obscures underlying customer needs, fragments signal across duplicates, and makes prioritization inconsistent. Without structured evidence and clear guardrails, AI-assisted triage either over-automates consequential decisions or fails to scale human review.

## Product thesis

Feature Intelligence is an AI-assisted product decision intelligence system that transforms noisy, duplicated, and solution-oriented feature requests into structured product evidence.

## Primary workflow

```text
Raw feature request
→ AI understanding
→ underlying customer need extraction
→ semantic related-request discovery
→ duplicate / related / distinct classification
→ theme classification
→ signal aggregation
→ deterministic priority scoring
→ AI-generated decision brief
→ human product review
→ approved / overridden product decision
```

## Core principle

**AI interprets evidence. Deterministic systems enforce business rules. Humans make consequential product decisions.**

## Core functional requirements (planned)

When implementation begins, users should be able to:

1. Submit a feature request with title and description.
2. View and discover existing requests.
3. Express support or interest in an existing request.
4. Understand how requests are grouped, evaluated, or prioritized.

## AI-first approach

AI is used to interpret unstructured request text: extract underlying needs, classify themes, discover semantically related requests, classify relationships (duplicate / related / distinct), and draft decision briefs. Semantic retrieval (embeddings) and structured LLM outputs support consistent, reviewable artifacts.

## Human-in-the-loop philosophy

The system is designed so AI never deletes requests, merges records, sets final roadmap outcomes, overrides deterministic scores, or sends stakeholder communications without explicit human approval. Product owners review briefs and approve or override decisions.

## Proposed technical architecture

| Layer | Planned stack |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI, Pydantic |
| Challenge persistence | SQLite |
| Production evolution | PostgreSQL + pgvector |
| AI | Provider abstraction, embeddings, structured outputs, deterministic priority engine, graceful degradation |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/AI-DESIGN.md](docs/AI-DESIGN.md), [docs/SECURITY-AND-RELIABILITY.md](docs/SECURITY-AND-RELIABILITY.md), and [docs/EVALUATION.md](docs/EVALUATION.md) for detail.

## Evaluation philosophy

Quality will be measured with golden datasets and explicit metrics (precision, recall, accuracy, structured-output success, latency, manual-review rate) once AI components exist. No evaluation results are claimed at this stage.

## Security and reliability principles

Treat feature-request text as untrusted input; validate structured AI outputs; limit retries; degrade gracefully when providers fail; protect secrets; preserve audit trails and human approval for consequential actions. See [docs/SECURITY-AND-RELIABILITY.md](docs/SECURITY-AND-RELIABILITY.md).

## Scope

- Single-product decision intelligence for feature requests
- Bounded Feature Triage Agent (tool-assisted orchestration, not autonomous swarms)
- SQLite for the assessment challenge; documented path to PostgreSQL + pgvector

## Non-scope

Not in scope for this assessment:

- Authentication, multi-tenancy, billing
- Email or notification infrastructure
- Redis, Celery, Kafka, Kubernetes
- Distributed microservices
- Autonomous multi-agent swarms
- Production-grade RBAC

## Repository structure

```text
/
├── CLAUDE.md              # Project rules (including prompt logging)
├── AGENTS.md              # Rules for AI coding agents
├── README.md
├── prompts.txt
├── .gitignore
├── docs/
│   ├── ARCHITECTURE.md
│   ├── AI-DESIGN.md
│   ├── EVALUATION.md
│   ├── SECURITY-AND-RELIABILITY.md
│   └── adr/               # Architecture decision records
└── specs/                 # Numbered executable specifications (future)
```

## Current status

- **Done:** Architecture documentation, agent governance, specification process definition, ADR placeholder
- **Not started:** Frontend, backend, database migrations, Docker, dependencies, numbered specs, tests, or deployed environments

Implementation will follow approved specs in [specs/](specs/README.md) after this design phase.
