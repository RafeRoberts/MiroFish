# MiroFish + Mantis Money Integration

MiroFish (swarm-intelligence prediction engine) is being integrated as the prediction core for Mantis Money's DeFi agent suite. Predictions flow into trading, yield, risk, and portfolio agents across multiple chains.

## Infrastructure

- **Jetson Thor** — LLM inference via Ollama. Endpoint: `http://192.168.0.87:11434/v1` (OpenAI-compatible). 128GB unified memory. Env: `OLLAMA_HOST=0.0.0.0:11434`, `OLLAMA_KEEP_ALIVE=-1`, `OLLAMA_FLASH_ATTENTION=1`, `OLLAMA_NUM_PARALLEL=4`.
- **MacBook** — orchestration: MiroFish, OASIS, GraphRAG build, Zep memory.
- **Zep Cloud** — agent long-term memory (API key TBD).

## Model Routing

| Stage | Model | Rationale |
|---|---|---|
| Seed extraction + GraphRAG | `gemma4:31b` | Precision, runs infrequently |
| Agent persona actions (per round) | `nemotron-3-nano` | High throughput, thousands of calls |
| Mid-sim event injection | `nemotron-3-super` | More reasoning, still fast |
| ReportAgent synthesis | `qwen3:30b` | Deep reasoning, runs once at end |

Fallback: `gemma4:latest`.

## Seed Data Pipeline

Sources → Seed Material Formatter → structured JSON docs → GraphRAG:
- **Chatty agent** — daily DeFi market briefs
- **Alchemy** — on-chain (balances, transfers, pools, DEX)
- **Goldsky** — subgraph events, historical patterns
- **CT + sentiment** — Twitter/X, Discord, news

Formatter must normalize into MiroFish seed docs with tagged entities (tokens, protocols, wallets, sentiment).

## DeFi Personas

Whales, Degens, LPs, Protocol teams — simulate on MiroFish's Twitter-like + Reddit-like dual-platform env. 5–10 rounds per sim with mid-sim shocks (price, yield, exploit, governance).

## Prediction Domains → Mantis Agents

| Domain | Consumer | Action |
|---|---|---|
| Token prices | Trading agent | Entry/exit |
| Yield + APY | Yield optimizer | Rebalance |
| Liquidity + TVL | Portfolio agent | Allocation |
| Risk signals | Risk manager | Exposure limits |

Chains: Ethereum, Solana, Arbitrum, Base, others. Execution results feed back as next-cycle seed material.

## Open Tasks

1. Explore MiroFish repo — locate LLM API endpoint config
2. Configure Ollama endpoint + per-stage model routing
3. Document MiroFish seed material format
4. Locate Zep integration point for API key
5. Build seed material formatter (Chatty + Alchemy + Goldsky → seed docs)
6. Design whale/degen/LP/protocol-team persona templates

## Timeline

- **Wk 1–2**: Ollama + MiroFish on Mac + Zep account
- **Wk 3–4**: Seed pipeline end-to-end
- **Wk 5–6**: Persona design, tune rounds + routing
- **Wk 7+**: Wire predictions to Mantis execution agents

## Repo

Upstream: https://github.com/666ghj/MiroFish
Remote: https://github.com/RafeRoberts/MiroFish/

Critical Rules
NEVER make code changes without data to justify them.

Do NOT edit execution scripts based on assumptions or theories.
ALWAYS collect logs and DB records FIRST, analyze them, THEN propose changes.
If there are no logs or records to reference, ask the user to run the monitor first.
Do NOT run the monitor yourself — ask the user to run it. You leave zombie processes.
Do NOT start multiple investigation paths at once. One change, one test, one result.
Stop guessing. If you don't know, say so. Don't waste tokens going in circles.
