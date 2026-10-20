# crewkit-memory

Shared, persistent memory for the [CrewKit](https://github.com/patrickboxfordpartners/crewkit) agent studio,
built on [Cognee](https://docs.cognee.ai). Every agent in the Band room (planner, builders, reviewer,
security) writes decisions, findings and lessons to one Cognee dataset, `studio`, and recalls them before acting.
Memory survives restarts and is shared between agents, so a lesson learned by one agent changes what another does tomorrow.

Related: [crewkit](https://github.com/patrickboxfordpartners/crewkit) · [lexis](https://github.com/patrickboxfordpartners/lexis)

## Setup

```bash
uv sync                      # Python 3.11
cp .env.example .env         # set LLM_PROVIDER, LLM_MODEL, LLM_API_KEY
set -a; . ./.env; set +a
```

`memory.py` exits with a clear message if no LLM is configured. If `LLM_API_KEY` is unset it falls back to
`OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` matching `LLM_PROVIDER`.

| Env var | Purpose |
|---|---|
| `LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`, `LLM_ENDPOINT` | Cognee's LLM for graph extraction and answers |
| `EMBEDDING_*` | optional embedding config |
| `GRAPH_DATABASE_PROVIDER=neo4j` + `GRAPH_DATABASE_URL/USERNAME/PASSWORD` | optional Neo4j graph backend (default: local store) |

## Commands

```bash
uv run python memory.py remember planner decision "Lexis exports history as CSV via /api/history?format=csv"
uv run python memory.py remember --no-cognify security-reviewer finding "[security] picomatch ReDoS via vite"   # fast, batched
uv run python memory.py cognify                                  # rebuild the graph once after a batch
uv run python memory.py recall "What security findings has Snyk reported for lexis?"
uv run python memory.py improve                                  # Cognee memory enrichment
uv run python memory.py forget studio                            # wipe the dataset
uv run python roundtrip.py                                       # end-to-end smoke test on "studio"
```

`remember` rebuilds the graph by default (always correct). Pass `--no-cognify` when writing several
memories in a row, then run `cognify` once. The CrewKit Snyk gate does exactly this.

## Showing recall across a restart (demo)

1. Security agent runs the Snyk gate on Lexis; the finding is stored with `remember`.
2. Quit every agent session / restart the machine's terminals.
3. In a **new** session, a *different* agent (the reviewer) runs
   `memory.py recall "Has Snyk flagged this dependency before?"` and gets the earlier finding back,
   then refuses to approve the PR that reintroduces it. Memory changed what the agent did.
