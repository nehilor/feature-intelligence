# AI design

This document defines how AI is used in Feature Intelligence and where it **must not** act alone.

## Responsibility split

| Area | AI | Deterministic systems | Humans |
| --- | --- | --- | --- |
| Parse and interpret request text | Primary | Schema validation | Review edge cases |
| Underlying need extraction | Propose structured need | Validate schema, store version | Correct in review if wrong |
| Theme classification | Propose label(s) + confidence | Enforce allowed taxonomy | Override theme if needed |
| Semantic related-request discovery | Retrieve candidates via embeddings | Top-k limits, filters | Confirm relationships |
| Duplicate / related / distinct | Propose relationship edges | Graph rules, no auto-merge | Approve merge/grouping |
| Signal aggregation | N/A | Count support/interest | N/A |
| Priority score | N/A | Engine from rules + signals | Override **decision**, not engine silently |
| Decision brief | Draft narrative summary | Template slots, validation | Approve / override decision |
| Delete / merge / roadmap / comms | **Forbidden** | Block without approval | Explicit action only |

## Feature Triage Agent boundary

The **Feature Triage Agent** is a **bounded orchestration workflow** that sequences AI and tool calls for a single request (or batch job spec), for example:

- `search_related_requests` — embedding similarity + metadata filters
- `get_request_signals` — support/interest counts and recency
- `calculate_priority` — invokes deterministic engine only
- `get_theme_context` — taxonomy definitions and historical theme stats

**The agent may:**

- Read request and catalog data via tools.
- Call the LLM with versioned prompts and structured output schemas.
- Write **proposed** AI artifacts (needs, themes, relationships, brief drafts) pending validation.

**The agent must not:**

- Delete requests.
- Merge requests without recorded human approval.
- Set final roadmap outcomes.
- Change priority scores outside the engine.
- Send emails or notifications.

This is intentionally **not** an autonomous multi-agent swarm: one orchestrator, explicit tool list, deterministic checkpoints, and human gates on consequential outcomes.

## Semantic retrieval

- Embed title + description (and optionally normalized need text after extraction).
- Retrieve top-k neighbors above a similarity threshold; pass candidates to relationship classification.
- Store embedding model id and content hash for reproducibility and re-embedding policies.

## Structured outputs

- All LLM steps return JSON matching Pydantic (or equivalent) models.
- Invalid or incomplete outputs trigger retry (bounded), then `AI_PARTIAL` or `MANUAL_REVIEW_REQUIRED`.
- No free-text-only persistence for fields that drive scoring or grouping without a structured companion.

## Relationship classification

- Labels: **duplicate**, **related**, **distinct** (and optionally confidence + rationale for reviewers).
- Outputs are **edges** or **cluster hints**, not automatic merges.
- Deterministic rules may collapse obvious cases only when a future spec defines safe auto-linking (e.g. same id); never silent deletion.

## Prompt versioning

- Prompts live in code or versioned files with an identifier stored on each AI run record.
- Changing a prompt creates a new version; evaluation compares versions against golden sets ([EVALUATION.md](EVALUATION.md)).

## Provider abstraction

Assessment provider strategy (see SPEC-003–006):

| Role | Provider |
| --- | --- |
| Primary LLM | OpenAI |
| Fallback LLM | Gemini 2.5 Flash (eligible failures only; not routine dual calls) |
| Embeddings | OpenAI |

- Provider SDK details stay inside adapters; domain code uses internal interfaces and validated models.
- OpenAI model, Gemini model, and embedding model are **environment-configurable**.
- Credentials are environment-driven; never committed.
- Normal automated tests use mocks/fakes and MUST NOT require live provider access by default.
- Do not add separate provider infrastructure (proxy services, multi-vendor routing layers) beyond this abstraction.

Interface covers: chat/completions with schema, embeddings, timeouts, and optional streaming (if needed later).

## Retry and fallback

- Transient errors: limited retries with backoff and jitter.
- After exhaustion: persist what validated, set processing state, expose degraded UI copy.
- Do not infinite-loop or block the API worker indefinitely.

## Graceful degradation

If the AI provider is unavailable:

- Ingestion and read paths for existing data continue.
- New triage may stop at last successful step with `AI_PARTIAL` or `MANUAL_REVIEW_REQUIRED`.
- Priority engine may still run on non-AI fields (signals only) if spec allows, with clear labeling that AI fields are missing.

## Why bounded orchestration over heavy agent frameworks

For this assessment, the workflow is **linear with branches**, a **small fixed tool set**, and **strict human/deterministic gates**. A full autonomous multi-agent framework (dynamic agent spawning, inter-agent negotiation, open-ended tool discovery) adds:

- Harder testing and reproducibility
- Weaker guarantees on forbidden actions
- More moving parts without benefit at SQLite scale

A simple orchestrator (explicit steps + tool functions + state machine) matches the core principle, keeps evaluation tractable, and can later be wrapped or replaced if ADRs justify richer orchestration — without committing to that complexity upfront.
