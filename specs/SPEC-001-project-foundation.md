# SPEC-001 — Project Foundation

Status: Draft  
Type: Foundation  
Priority: Required  
Dependencies: None

## 1. Objective

Create the minimal, production-aware application foundation required to implement the Feature Intelligence assessment.

This specification establishes:

- frontend application structure
- backend API structure
- local persistence foundation
- configuration conventions
- development commands
- health checks
- baseline automated testing
- validation harness
- local developer experience

This specification MUST NOT implement product features or AI functionality.

The purpose is to create a small, predictable, testable foundation that subsequent specifications can build on without changing the project architecture.

---

## 2. Business Context

Feature Intelligence is an AI-assisted product decision intelligence system.

The complete product will eventually allow users to:

- submit feature requests
- discover existing requests
- express support for requests
- receive AI-assisted request analysis
- identify semantically related requests
- aggregate product signals
- calculate deterministic priority recommendations
- generate AI-assisted decision briefs
- preserve final product decisions for human reviewers

None of those business capabilities belong in SPEC-001.

SPEC-001 exists solely to establish the technical runtime and engineering quality baseline.

---

## 3. Architectural Constraints

Implementation MUST remain consistent with:

- `README.md`
- `AGENTS.md`
- `docs/ARCHITECTURE.md`
- `docs/AI-DESIGN.md`
- `docs/EVALUATION.md`
- `docs/SECURITY-AND-RELIABILITY.md`

If implementation requires a meaningful architectural deviation, stop and document the decision before proceeding.

Do not silently reinterpret architecture.

---

## 4. Required Technology

### Frontend

Use:

- React
- TypeScript
- Vite

The frontend should remain intentionally small.

Do not introduce:

- Next.js
- Redux
- complex state-management frameworks
- large component libraries
- authentication frameworks

unless a later approved specification explicitly requires them.

### Backend

Use:

- Python
- FastAPI
- Pydantic

The backend should use clear separation between HTTP concerns, domain logic, persistence, and future AI services.

Avoid unnecessary framework abstractions.

### Persistence

Use:

- SQLite

The persistence layer MUST be structured so that moving to PostgreSQL later would not require rewriting business logic.

Production evolution toward PostgreSQL + pgvector is documented architecture, not part of this specification.

---

## 5. Repository Structure

Create a pragmatic structure approximately equivalent to:

```text
/
├── frontend/
│   ├── src/
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── domain/
│   │   ├── services/
│   │   └── persistence/
│   ├── tests/
│   └── ...
│
├── scripts/
│   └── ...
│
├── docs/
├── specs/
├── CLAUDE.md
├── AGENTS.md
├── README.md
├── prompts.txt
└── .gitignore
```

Optional root-level files introduced by this spec when implemented:

```text
Makefile
.env.example
```

Do not create domain tables or product routes beyond the foundation health check.

---

## 6. Backend Foundation

### Technology

- Python
- FastAPI
- Pydantic
- SQLite

### Application initialization

On startup, the backend MUST:

1. Load configuration from environment (with sensible local defaults).
2. Initialize logging.
3. Initialize SQLite connectivity (file path from configuration).
4. Register API routes under a consistent prefix convention: `/api/...`.
5. Expose the application entrypoint suitable for local development and tests.

Startup MUST succeed when AI-related environment variables are absent or empty.

### API routing convention

- Product and foundation HTTP routes live under `/api`.
- Health check: `GET /api/health`.
- Future specs add routes under the same prefix without changing the convention.

### Configuration management

Configuration MUST be environment-driven and typed (Pydantic settings or equivalent).

Required categories for this spec:

- application environment (e.g. `development`, `test`)
- SQLite database URL or file path
- optional CORS allowed origins for local frontend development

Document placeholders for later specs (not required for startup):

- OpenAI / Gemini credentials and models
- AI feature flags

Real secrets MUST NOT be committed.

### SQLite initialization

- Use a single SQLite database file for local development unless overridden.
- Apply only foundation-level schema needed for this spec (no product domain tables).
- Migrations MAY be a simple init script or lightweight migration helper; avoid speculative tables.

### Standard error behavior

API errors SHOULD return predictable JSON bodies, for example:

```json
{
  "detail": "Human-readable message"
}
```

Use conventional HTTP status codes (`400`, `404`, `422`, `500`) consistently.

Validation errors from Pydantic/FastAPI MUST NOT crash the process.

### Test isolation

- Tests MUST NOT depend on a developer’s manual database file.
- Use isolated temporary SQLite databases (or in-memory SQLite) per test session or test case as appropriate.
- Tests MUST NOT require network access or AI credentials.

---

## 7. Health Endpoint

### Contract

```http
GET /api/health
```

Successful response:

- Status code: `200`
- JSON body:

```json
{
  "status": "ok"
}
```

Requirements:

- MUST NOT call LLM or embedding providers.
- MUST NOT require AI credentials.
- MAY verify process liveness and basic app readiness only.

---

## 8. Frontend Foundation

### Technology

- React
- TypeScript
- Vite

### Requirements

The frontend foundation MUST:

- start successfully in local development
- render a minimal **Feature Intelligence** shell (title/branding and layout placeholder)
- represent backend health/connectivity (connected vs unavailable vs loading)
- organize code so later product screens can be added without restructuring

The frontend foundation MUST NOT implement:

- feature request submission
- request discovery or search
- support / voting
- AI triage or analysis UI
- prioritization or scoring UI
- human product decision workflow

### API client boundary

- Centralize HTTP access in a small API client module (base URL from environment/config).
- Do NOT scatter hardcoded backend URLs across components.
- Avoid React Query, Redux, or similar unless a later spec requires them.

### Connectivity and errors

When the backend is unavailable or health check fails:

- the UI MUST remain usable (no uncaught render crash)
- show a recoverable, user-visible state (e.g. disconnected banner or message)
- allow retry or automatic re-check where practical

---

## 9. Environment Configuration

Implementation MUST add `.env.example` with placeholders only.

Document at minimum:

| Variable (conceptual) | Purpose |
| --- | --- |
| Application environment | `development` / `test` |
| Backend listen configuration | host/port as needed |
| Frontend API base URL | Vite env for backend origin |
| SQLite database URL/path | backend persistence |
| Optional future AI keys/models | commented or empty placeholders |

Rules:

- `.env` MUST remain gitignored.
- Application MUST run without AI credentials.
- README setup instructions MUST list only commands verified during SPEC-001 implementation.

---

## 10. Persistence Foundation

- SQLite is the assessment persistence engine.
- SPEC-001 creates only foundation persistence wiring, not product entities.
- Tests use isolated temporary databases; never share state with manual dev DB unless explicitly documented.

---

## 11. Development Commands

Provide simple, documented developer commands. Preferred root interface:

```bash
make dev-backend
make dev-frontend
make test-backend
make test-frontend
make typecheck
make lint
make verify
```

Equivalent `npm` / `uv` / `pytest` scripts are acceptable if documented in README and wired into `make verify`.

Requirements:

- backend and frontend can be started independently
- backend tests run in isolation
- frontend typecheck and lint are invocable separately
- `make verify` is the canonical full-repo validation entrypoint

---

## 12. Verification Harness

### Canonical command

```bash
make verify
```

When SPEC-001 is complete, `make verify` MUST run all currently applicable checks:

- backend tests
- backend lint/static validation (e.g. ruff)
- frontend tests (if any beyond typecheck in v1; at minimum typecheck satisfies “frontend validation”)
- frontend TypeScript typecheck
- frontend lint

Future specs (e.g. SPEC-006) MAY extend `make verify` with offline evaluation steps.

Behavior:

- exit code `0` only if every required step passes
- non-zero exit if any required step fails
- MUST NOT invoke live OpenAI or Gemini APIs

---

## 13. Testing Requirements

### Backend (minimum)

- application imports and starts for tests
- `GET /api/health` returns `200`
- response body equals `{"status":"ok"}`
- persistence uses isolated test database configuration

### Frontend (minimum)

- TypeScript compiles (`typecheck`)
- application renders the foundation shell in tests or smoke test
- backend-unavailable state renders without crashing the UI

### Required test scenarios

1. Backend health succeeds.
2. Backend starts without AI credentials.
3. Frontend starts (dev/build smoke as documented).
4. Frontend handles backend unavailable.
5. `make verify` (or equivalent) exits non-zero when a required validation step is intentionally failing (demonstrated in CI or documented local procedure).

---

## 14. Security Baseline

- `.env` ignored; `.env.example` contains placeholders only
- no committed secrets or API keys
- deliberate localhost-oriented CORS for frontend ↔ backend during development
- no authentication or authorization in SPEC-001
- do not log secrets, tokens, or full sensitive configuration values

---

## 15. Reliability Baseline

- Frontend and backend restart independently without shared fragile global state.
- Missing AI credentials MUST NOT prevent backend or frontend startup.
- Preserve: **AI enhancement should degrade gracefully rather than make the core product unavailable.**

Health and shell connectivity MUST reflect this principle.

---

## 16. Observability Baseline

Use lightweight, consistent logging (stdlib logging or equivalent):

- log application startup (environment mode, bind address — not secrets)
- log meaningful backend failures (HTTP 5xx, DB init failures)

Do NOT require Prometheus, OpenTelemetry collectors, or distributed tracing platforms in SPEC-001.

---

## 17. Developer Experience

- README MUST include local setup steps after implementation.
- Document only commands that were actually run successfully during SPEC-001 completion.
- Prefer one obvious path: install deps → configure `.env` from example → `make verify` → run dev servers.

---

## 18. Explicit Out of Scope

SPEC-001 MUST NOT implement:

- feature request domain models or routes (beyond health)
- support / voting
- embeddings or vector storage
- LLM calls or provider clients (except optional config placeholders)
- AI agents or triage orchestration
- semantic retrieval or duplicate detection
- priority scoring or decision briefs
- human product decision workflow
- authentication, authorization, multi-tenancy
- Redis, Celery, Kafka, Kubernetes
- background workers or job queues
- production deployment infrastructure (Docker/K8s/terraform as required deliverables)

---

## 19. Acceptance Criteria

### Repository

- [ ] Clear `frontend/` and `backend/` structure exists
- [ ] No unnecessary infrastructure introduced

### Backend

- [ ] FastAPI application starts locally and in tests
- [ ] `GET /api/health` returns `200` with `{"status":"ok"}`
- [ ] SQLite initializes for dev and isolated test modes
- [ ] Backend tests pass

### Frontend

- [ ] React + Vite app starts locally
- [ ] TypeScript compiles
- [ ] Foundation shell renders
- [ ] Backend-unavailable state is handled without crash

### Configuration

- [ ] `.env.example` exists with placeholders only
- [ ] No real secrets committed
- [ ] No AI credential required to start app or pass `make verify`

### Verification

- [ ] `make verify` exists and passes when implementation is complete
- [ ] `make verify` fails non-zero when a required check fails

### Documentation

- [ ] README local setup instructions reflect verified commands

### Governance

- [ ] `CLAUDE.md` remains intact
- [ ] `AGENTS.md` remains intact
- [ ] `prompts.txt` records SPEC-001 implementation interactions

---

## 20. Definition of Done

SPEC-001 is complete only when:

- all acceptance criteria in §19 pass
- relevant automated tests exist and pass
- typecheck and lint/static validation pass
- `make verify` passes
- no secrets are committed
- README documents verified setup commands
- no unrelated product functionality was added
- `prompts.txt` includes this implementation session
- changes are ready for a focused commit, e.g. `chore: bootstrap application foundation`

---

## 21. Closing Principle

Prefer **restraint**, **testability**, **reproducibility**, and **clear boundaries** over unnecessary architectural complexity. SPEC-001 exists so later specs can add product value without renegotiating the runtime foundation.