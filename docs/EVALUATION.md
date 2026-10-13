# Evaluation

Feature Intelligence separates **deterministic software tests** (`make verify`) from **probabilistic AI evaluation** (`make eval` / `make eval-live`).

## Golden datasets (version controlled)

| Dataset | Version | Location |
| --- | --- | --- |
| Relationship classification | `relationships_v1` | `backend/evals/datasets/relationships.json` |
| Theme classification | `themes_v1` | `backend/evals/datasets/themes.json` |
| Underlying need concepts | `underlying_needs_v1` | `backend/evals/datasets/underlying_needs.json` |

Schemas are validated with Pydantic before metrics run. Invalid gold data fails loudly.

## Offline evaluation (`make eval`)

- **Mode:** offline frozen predictions
- **Fixtures:** `backend/evals/fixtures/*_predictions.json`
- **Purpose:** regression harness for metric code, schema gates, and prompt-change workflow — **not** a claim of live model quality
- **Network / credits:** none

Regression baselines live in `backend/evals/fixtures/baselines.json`.

### Relationship metrics

- Accuracy, per-class precision/recall/F1, macro F1
- Explicit DUPLICATE precision and DUPLICATE recall
- Text confusion matrix (DUPLICATE / RELATED / DISTINCT)

**Zero-division policy:** precision/recall/F1 use `0.0` when denominators are zero (no NaN).

### Theme metrics

- Accuracy (primary)
- Failure list for misclassified case IDs

### Underlying need

- **Concept recall** = matched expected concepts / total expected concepts (per case)
- Case pass if recall ≥ 0.5 (documented threshold)
- Not exact string match; not a perfect semantic metric — see limitations in SPEC-006

### Structured output reliability

- Success rate = valid structured outputs / attempted outputs across frozen prediction records and schema stress cases

## Live evaluation (`make eval-live`)

- Opt-in only; never runs under `make verify` or `make eval`
- Uses configured primary provider by default (`AI_EVAL_PROVIDER=openai|gemini` optional)
- Reports prompt versions (`feature_triage_v1`, `relationship_classification_v1`), provider, model, dataset versions
- Limit cases with `EVAL_MAX_CASES`
- Results may be written under `backend/evals/results/` (gitignored)

Any numeric live result must be labeled as an **assessment-scale benchmark**, not production evidence.

## Prompt regression workflow

```text
change prompt → increment prompt version → run same golden dataset → compare metrics → accept or reject
```

Do not change prompt semantics without version bumps.

## Non-goals

- Enterprise ML platforms, auto prompt optimization, fabricated README accuracy claims
- Using live model scores as CI gates for this assessment
