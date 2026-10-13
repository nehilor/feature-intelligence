# Feature Intelligence — submission checklist

## Repository

- [ ] Repository is **public** (or accessible to reviewers)
- [ ] No secrets committed (`.env` gitignored; scan before push)
- [ ] README reflects SPEC-001 through SPEC-006 implemented

## Environment setup

```bash
cp .env.example .env
cd backend && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cd ../frontend && npm install
```

AI keys are optional for `make verify`, `make eval`, and `make demo-reset`.

## Verification commands

| Command | Purpose |
| --- | --- |
| `make verify` | Lint + offline tests (no AI calls) |
| `make eval` | Offline golden-set regression (frozen predictions) |
| `make eval-live` | Optional live provider benchmark (credentials required) |
| `make demo-reset` | Destructive local SQLite reset + baseline seed |

## Demo checklist (~5 min)

See [DEMO.md](DEMO.md).

1. `make demo-reset`
2. Show discovery + submit **Monthly finance analytics in Excel**
3. Run triage / relationships (live if keys available)
4. `make demo-setup-canonical` (if needed for deterministic 78 demo)
5. Calculate priority, decision brief, human override
6. `make eval` (offline metrics)

## Loom

- **URL:** _(add your Loom link before submission — do not invent)_

## Recipients

Email the repository link and Loom to:

- andres.saldarriaga@metacto.com
- jamie@metacto.com

(Do not send from automated tooling in this repo.)

## Loom outline (~5 minutes)

1. Business problem — noisy, duplicated feature requests
2. Who benefits — PM / product ops triage
3. Why AI — unstructured text → structured evidence
4. Why deterministic scoring — explainable, non-LLM priority
5. Why human decision — approve / override / defer / reject
6. Architecture — React, FastAPI, SQLite, OpenAI primary, Gemini fallback
7. Semantic duplicate safety — no auto-merge
8. Evaluation — offline frozen harness vs optional live eval
9. Tradeoffs — SQLite, small gold sets, in-process vectors
10. Production evolution — Postgres, pgvector, auth, jobs

## Business success metrics (future, not measured here)

- Median time from submission to initial triage
- % of new requests correctly linked to existing needs
- Time from submission to product review decision

## AI quality metrics (evaluation harness)

- Relationship macro F1, DUPLICATE precision/recall
- Theme accuracy
- Underlying-need concept coverage
- Structured-output success rate
