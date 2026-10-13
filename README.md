# Feature Intelligence

**Status:** SPEC-001 through SPEC-006 are implemented for this technical assessment.

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

## Core capabilities

1. Submit, discover, search, and support feature requests.
2. AI feature triage (theme, underlying need, impact, urgency).
3. Semantic relationship intelligence (DUPLICATE / RELATED / DISTINCT).
4. Deterministic priority scoring with human strategic alignment.
5. AI-assisted decision brief and human product decisions (with decision-time audit snapshot).

## AI-first approach

AI is used to interpret unstructured request text: extract underlying needs, classify themes, discover semantically related requests, classify relationships (duplicate / related / distinct), and draft decision briefs. Semantic retrieval (embeddings) and structured LLM outputs support consistent, reviewable artifacts.

## Human-in-the-loop philosophy

The system is designed so AI never deletes requests, merges records, sets final roadmap outcomes, overrides deterministic scores, or sends stakeholder communications without explicit human approval. Product owners review briefs and approve or override decisions.

## Technical architecture

| Layer | Stack |
| --- | --- |
| Frontend | React, TypeScript, Vite |
| Backend | Python, FastAPI, Pydantic, SQLAlchemy |
| Persistence | SQLite (assessment) |
| AI | OpenAI primary, Gemini 2.5 Flash fallback; OpenAI embeddings; structured outputs |
| Evaluation | Offline golden datasets + frozen fixtures (`make eval`); optional live eval |

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/AI-DESIGN.md](docs/AI-DESIGN.md), [docs/SECURITY-AND-RELIABILITY.md](docs/SECURITY-AND-RELIABILITY.md), and [docs/EVALUATION.md](docs/EVALUATION.md) for detail.

## Evaluation

- **`make eval`** — offline, deterministic regression on golden datasets and frozen predictions (no API credits).
- **`make eval-live`** — optional live provider benchmark when credentials are configured.

See [docs/EVALUATION.md](docs/EVALUATION.md). Offline fixture metrics validate the harness; they are **not** live model quality claims.

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

Runs backend lint/tests and frontend lint/typecheck/tests (no AI provider calls).

Additional offline commands:

```bash
make eval          # golden-set regression on frozen predictions
make demo-reset    # destructive local SQLite reset + baseline seed
```

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

### Semantic relationship intelligence (SPEC-004)

- `POST /api/feature-requests/{id}/relationships/analyze` — embedding, cosine-similarity Top K retrieval, LLM relationship classification
- `GET /api/feature-requests/{id}/relationships` — persisted relationship evidence

**Embeddings:** OpenAI (`OPENAI_EMBEDDING_MODEL`, default `text-embedding-3-small`), JSON-serialized vectors in SQLite, content-hash reuse.

**Retrieval:** In-process cosine similarity, `SEMANTIC_MIN_CANDIDATE_SCORE` (default `0.50`), `SEMANTIC_TOP_K` (default `5`). Similarity ranks candidates; the LLM adjudicates `DUPLICATE` / `RELATED` / `DISTINCT` (`relationship_classification_v1`).

**Providers:** Relationship classification reuses OpenAI primary + Gemini fallback (failover only).

**Safety:** No automatic merge, delete, or support transfer. `DUPLICATE` is advisory evidence only.

**Optional live embedding smoke (not part of `make verify`):**

```bash
cd backend && .venv/bin/python scripts/live_embedding_smoke.py
```

### Priority and human decision workflow (SPEC-005)

- `POST /api/feature-requests/{id}/priority` — calculate/recalculate deterministic priority (client sends **human** `strategic_alignment` only)
- `GET /api/feature-requests/{id}/priority` — current `PriorityAssessment` (404 `priority_not_found` when not yet assessed)
- `POST /api/feature-requests/{id}/decision-brief` — AI-assisted brief from trusted persisted evidence
- `GET /api/feature-requests/{id}/decision-brief` — current brief (404 `decision_brief_not_found`)
- `POST /api/feature-requests/{id}/decision` — human `APPROVED` / `OVERRIDDEN` / `DEFERRED` / `REJECTED`
- `GET /api/feature-requests/{id}/decision` — current decision (404 `decision_not_found`)

**Deterministic scoring (`priority_formula_v1`, max 100):** demand (support + DUPLICATE/RELATED signals, max 40), customer impact from validated triage (max 25), urgency from triage (max 15), strategic alignment from human input only (max 20). Priority levels: 0–39 LOW, 40–69 MEDIUM, 70–100 HIGH. No LLM calls during scoring.

**Decision brief:** `decision_brief_v1` structured output; OpenAI primary, Gemini fallback; failures do not alter priority scores.

**Human override:** `ProductDecision` preserves the system recommendation; overrides store separate reviewer priority and reason without rewriting `PriorityAssessment`.

### AI evaluation and submission (SPEC-006)

- Golden datasets: `backend/evals/datasets/` (`relationships_v1`, `themes_v1`, `underlying_needs_v1`)
- Offline runner: `make eval` (frozen predictions, confusion matrix, DUPLICATE precision/recall, theme accuracy, concept coverage)
- Live runner: `make eval-live` (opt-in; `EVAL_MAX_CASES` optional)
- Demo: `make demo-reset`, `make demo-setup-canonical` — see [docs/DEMO.md](docs/DEMO.md)
- Submission checklist: [docs/SUBMISSION.md](docs/SUBMISSION.md)

## Current status

**Implemented:** [SPEC-001](specs/SPEC-001-project-foundation.md) through [SPEC-006](specs/SPEC-006-ai-evaluation-and-submission-hardening.md).

## Why AI / what stays deterministic / human-controlled

| Layer | Role |
| --- | --- |
| AI | Interprets request text; themes, needs, relationships, decision brief prose |
| Deterministic | Priority formula (`priority_formula_v1`), support/relationship counting, schema validation |
| Human | Strategic alignment, product decision (approve/override/defer/reject), override preserved at decision time |

## Production evolution (documented, not implemented)

SQLite → PostgreSQL; in-process cosine similarity → pgvector ANN; background jobs where needed; real auth/multi-tenancy; larger labeled eval sets; provider cost telemetry.
