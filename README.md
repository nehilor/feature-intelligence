# Feature Intelligence

**Status:** SPEC-001 foundation, SPEC-002 feature request core, and SPEC-003 AI Feature Triage are implemented. SPEC-004+ remain planned.

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
├── backend/               # FastAPI application (SPEC-001)
├── frontend/              # React + Vite shell (SPEC-001)
├── Makefile               # verify, dev, test, lint
└── specs/                 # Executable specifications SPEC-001–006
```

## Local development (SPEC-001)

### Prerequisites

- Python 3.9+
- Node.js 20+ and npm

### Environment

```bash
cp .env.example .env
```

Edit `.env` if needed. AI credentials are **not** required for core product flows or `make verify` (tests use mock providers). Live triage requires provider keys in `.env` only on the server.

### Backend setup

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
cd ..
```

### Frontend setup

```bash
cd frontend
npm install
cd ..
```

### Run

```bash
make backend-dev    # API at http://localhost:8000
make frontend-dev   # UI at http://localhost:5173
```

Health check: `GET http://localhost:8000/api/health` → `{"status":"ok"}`

### Verification

```bash
make verify
```

Runs backend lint/tests and frontend lint/typecheck/tests.

### Demo seed (SPEC-002)

Load deterministic sample requests (resets existing feature-request data in the configured SQLite database):

```bash
make seed
```

### Feature request API (SPEC-002)

- `POST /api/feature-requests` — submit title + description (status defaults to `SUBMITTED`)
- `GET /api/feature-requests` — list with `q`, `sort` (`recent` | `supported`), `limit`, `offset`, optional `supporter_key`
- `GET /api/feature-requests/{id}` — detail (optional `supporter_key` for `supported_by_current_user`)
- `POST /api/feature-requests/{id}/support` — anonymous support via opaque `supporter_key`

The UI supports discovery, search, sort, pagination, submit, detail view, and Support / Supported states using a browser-local supporter key.

### AI Feature Triage (SPEC-003)

- `POST /api/feature-requests/{id}/analysis` — run triage (returns existing valid analysis when present)
- `GET /api/feature-requests/{id}/analysis` — current analysis state

**Providers:** OpenAI primary, Google Gemini 2.5 Flash fallback (failover only — not model voting).

**Structured output:** Provider-native JSON/schema where available, then mandatory Pydantic validation (`feature_triage_v1` prompt). Processing states: `AI_COMPLETE`, `AI_PARTIAL` (low confidence), `MANUAL_REVIEW_REQUIRED`.

**Configuration (backend `.env`):**

| Variable | Purpose |
| --- | --- |
| `AI_ENABLED` | `false` disables provider calls; core app still works |
| `AI_PRIMARY_PROVIDER` | Default `openai` |
| `AI_FALLBACK_PROVIDER` | Default `gemini` |
| `OPENAI_API_KEY` / `OPENAI_MODEL` | Primary provider (model must be set for OpenAI use) |
| `GEMINI_API_KEY` / `GEMINI_MODEL` | Fallback (default model `gemini-2.5-flash`) |
| `AI_REQUEST_TIMEOUT_SECONDS` | Per-request timeout (default `30`) |

**Failure behavior:** Missing keys or provider errors do not block startup or feature-request CRUD. When both providers fail or AI is disabled, analysis returns `MANUAL_REVIEW_REQUIRED` without mutating the original request text.

**Optional live validation (not part of `make verify`):**

```bash
cd backend && .venv/bin/python scripts/live_triage_smoke.py
```

Requires `OPENAI_API_KEY` and `OPENAI_MODEL` in the environment. Skips safely when unset.

Not implemented yet: embeddings, semantic duplicate detection, priority scoring, decision briefs, or evaluation harness (SPEC-004–006).

## Current status

**Implemented:**

- [SPEC-001](specs/SPEC-001-project-foundation.md) — application foundation, `/api/health`, `make verify`
- [SPEC-002](specs/SPEC-002-feature-request-core.md) — feature requests, deterministic search, anonymous support, demo seed
- [SPEC-003](specs/SPEC-003-ai-feature-triage.md) — AI Feature Triage, provider abstraction, structured analysis persistence

**Planned (not implemented):** [SPEC-004](specs/SPEC-004-semantic-relationship-intelligence.md) through [SPEC-006](specs/SPEC-006-ai-evaluation-and-submission-hardening.md) — semantic relationships, priority/decisions, evaluation harness.

Implementation continues **spec-by-spec** in order.
