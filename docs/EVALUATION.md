# Evaluation (planned)

This document defines **how** Feature Intelligence AI components will be evaluated once implemented. **No results, benchmarks, or production metrics exist yet.**

## Objectives

- Measure quality of classification and extraction against labeled examples.
- Track operational health (latency, structured-output reliability, manual-review burden).
- Compare prompt/model changes using consistent datasets and versioning ([AI-DESIGN.md](AI-DESIGN.md)).

## Golden datasets (planned)

Each dataset is a curated, version-controlled collection of inputs and expected labels (or acceptable label sets). Format and storage location will be defined in the first AI-related numbered spec.

### Duplicate / related / distinct classification

- **Inputs:** Pairs or small clusters of feature requests (title + description).
- **Labels:** duplicate | related | distinct (per pair or cluster policy).
- **Use:** Regression tests for relationship step; precision/recall per class.

### Theme classification

- **Inputs:** Single requests or normalized need text.
- **Labels:** One or more themes from a fixed taxonomy (exact set TBD in spec).
- **Use:** Accuracy and confusion analysis; manual review of low-confidence cases.

### Underlying-need extraction

- **Inputs:** Solution-oriented request text.
- **Labels:** Reference need statements (or rubric-scored human judgments).
- **Use:** Semantic similarity or human rubric scoring; track regression when prompts change.

## Planned metrics

| Metric | Applies to | Notes |
| --- | --- | --- |
| Precision | Relationship, theme | Per-class and macro where useful |
| Recall | Relationship, theme | Especially for duplicate detection |
| Accuracy | Theme (single-label cases) | Not sufficient alone for imbalanced classes |
| Structured-output success rate | All LLM steps | % runs passing schema validation without retry exhaustion |
| Latency | End-to-end triage, per step | p50/p95 targets TBD in NFR specs |
| Manual-review rate | Pipeline | % requests entering `MANUAL_REVIEW_REQUIRED` or human override |

Additional tracking (not claimed now):

- Inter-rater agreement when building gold labels
- Cost per triage (tokens) for provider comparison

## Evaluation workflow (planned)

1. **Offline:** Run pipeline or individual steps against frozen dataset versions; store predictions with prompt/model ids.
2. **Compare:** Diff metrics against baseline commit or previous prompt version.
3. **Gate:** Spec acceptance may require minimum metrics on gold sets before merge (thresholds TBD per spec).
4. **Online (later):** Sample production/manual review for drift; out of scope until a deployed environment exists.

## Non-goals (evaluation phase)

- Public leaderboard or invented benchmark scores in README/marketing copy
- Fully automated merge approval based on model confidence alone
- Multi-tenant A/B infrastructure

## Reporting

When implementation begins, evaluation runs should produce reproducible artifacts (command, dataset version, git sha, metric summary) checked into CI logs or a reports directory per spec — not fabricated numbers in documentation.
