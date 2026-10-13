# Feature Intelligence demo guide (~5 minutes)

This flow is designed for a short Loom walkthrough. It uses **local SQLite only**.

## Prerequisites

```bash
cp .env.example .env
make verify
make demo-reset
make backend-dev   # terminal 1
make frontend-dev    # terminal 2
```

Live AI steps require provider keys in `.env`. Deterministic priority scoring and offline evaluation do not.

## 1. Reset baseline inbox

```bash
make demo-reset
```

Loads five baseline requests (CSV export, dashboard download, dark mode, Slack, enterprise SSO). **Does not** include the finance Excel request.

## 2. Discovery

Open the UI, search/sort requests, show support counts.

## 3. Submit canonical request (live demo moment)

Submit a **new** request:

- **Title:** Monthly finance analytics in Excel
- **Description:** Our finance team needs monthly analytics in Excel so they can reconcile results outside the platform.

## 4. AI Feature Triage (optional live)

Run analysis from the detail page (or `POST /api/feature-requests/{id}/analysis`).

Expect reporting/data theme and finance reconciliation need when providers succeed.

## 5. Semantic relationships (optional live)

Run relationship analysis. Show DUPLICATE/RELATED/DISTINCT evidence — advisory only, no merge.

## 6. Canonical 78-point priority (deterministic)

If you need a reproducible score without depending on live AI output:

```bash
make demo-setup-canonical
```

This applies **local deterministic demo fixtures** (`provider=local_demo_fixture`) for analysis and relationships, plus four supporters. It does **not** claim OpenAI/Gemini provenance.

In the UI:

1. Set **Human strategic alignment** → High
2. **Calculate priority**

Expected system recommendation:

```text
Demand 30 + Impact 25 + Urgency 3 + Strategic 20 = 78 (HIGH)
```

## 7. Decision brief (optional live)

Generate the AI-assisted decision brief after priority exists.

## 8. Human decision

Demonstrate override, e.g. **OVERRIDDEN → MEDIUM** with a substantive reason.

Confirm the **system recommendation at decision time** remains **HIGH / 78** while the current priority panel may show updated evidence after recalculation.

## 9. Evaluation harness (offline)

```bash
make eval
```

Shows frozen-fixture regression metrics — not live model quality.

Optional:

```bash
make eval-live
```

## Talking points

- AI interprets evidence; priority is deterministic; humans decide.
- Duplicate suggestions never auto-merge.
- Offline eval protects prompt/schema regressions; live eval is opt-in.
