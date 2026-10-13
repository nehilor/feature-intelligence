# Feature Intelligence offline evaluation

This package holds **golden datasets**, **frozen prediction fixtures**, and **deterministic metric runners** for SPEC-006.

## Principles

- `make eval` is **offline** — no OpenAI, Gemini, embeddings, or network access.
- Frozen fixture scores validate the **evaluation harness and regression gates**, not live model quality.
- Live provider evaluation is opt-in via `make eval-live` (requires credentials).

## Layout

```text
evals/
  datasets/          # Curated golden labels (versioned JSON)
  fixtures/          # Frozen predictions + regression baselines
  metrics/           # Pure Python metric implementations
  runners/           # Offline and live orchestration
  results/           # Local run output (gitignored except .gitkeep)
```

## Dataset versions

- `relationships_v1`
- `themes_v1`
- `underlying_needs_v1`

## Zero-division policy

Classification metrics use explicit `zero_division=0.0` — no NaN values are emitted when a class has zero predicted or true positives.
