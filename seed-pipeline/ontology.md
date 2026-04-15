# DeFi Ontology for MiroFish GraphRAG

Entity + edge type spec for the Mantis Money DeFi simulation. Posted to MiroFish via `POST /api/graph/ontology/generate` (or embedded in the ontology generator prompt). Zep requires ≥10 entity types; `Person` and `Organization` are mandatory catch-alls.

## Entity Types

| # | Type | Description | Examples from Buttondown seeds |
|---|---|---|---|
| 1 | **Token** | Crypto assets — L1, stablecoins, governance, meme, RWA | BTC, ETH, SOL, USDC, USDT, DAI, ZEC, TAO, XRP, LINK, HYPE, TRX, DOGE |
| 2 | **Protocol** | DeFi protocols (DEXes, lenders, yield aggregators, perps) | Uniswap v3, Uniswap v4, Curve, Fluid, Hyperliquid, Chainlink, Aave |
| 3 | **Pool** | Liquidity pools / specific pairs with fee tiers | WETH/USDC 0.05%, DAI/USDC/USDT 3pool, USDC/USDT 0.001% |
| 4 | **Chain** | L1 / L2 networks | Ethereum, Solana, Arbitrum, Base, Optimism |
| 5 | **Wallet** | On-chain addresses (individual, whale, contract, treasury) | Unknown whale wallets, protocol treasuries |
| 6 | **GovernanceProposal** | DAO votes, on-chain proposals, regulatory bills | CLARITY Act, EU MiCA Phase II |
| 7 | **MarketEvent** | Discrete events: exploits, depegs, ETF approvals, shocks | Grayscale ZEC ETF filing, SEC investigation closure |
| 8 | **SentimentIndicator** | Market sentiment / trending signals | Fear & Greed Index, CoinGecko trending, whale accumulation scores |
| 9 | **YieldOpportunity** | APY offerings, staking, LP rewards, lending rates | Curve 3pool fee income, HYPE buyback flywheel |
| 10 | **RegulatoryBody** | Agencies / jurisdictions shaping DeFi | SEC, CFTC, MAS, EU (MiCA) |
| * | **Person** *(mandatory)* | Individuals: analysts, founders, politicians, whales | Arthur Hayes |
| * | **Organization** *(mandatory)* | Firms, DAOs, funds, issuers | Grayscale, BlackRock, Bitwise, Mantis Money, Western Union |

## Edge Types (Relations)

| # | Relation | Subject → Object | Semantics |
|---|---|---|---|
| 1 | **HOLDS** | Wallet / Organization → Token | Balance position |
| 2 | **PROVIDES_LIQUIDITY** | Wallet / Organization → Pool | LP position |
| 3 | **DEPLOYED_ON** | Pool / Protocol → Chain | Where it lives |
| 4 | **TRADES_PAIR** | Pool → Token | Pool constituents |
| 5 | **ISSUED_BY** | Token → Protocol / Organization | Native vs issued relationship |
| 6 | **GOVERNS** | Person / Organization → Protocol | Voting / decision power |
| 7 | **BRIDGES_TO** | Chain → Chain | Cross-chain routes |
| 8 | **EXPLOITS** | MarketEvent → Protocol / Pool | Security incidents |
| 9 | **INFLUENCES** | SentimentIndicator / MarketEvent → Token / Protocol | Price/flow impact |
| 10 | **REGULATES** | RegulatoryBody → Token / Protocol / Chain | Jurisdictional oversight |
| 11 | **CORRELATES_WITH** | Token → Token | Observed price co-movement |
| 12 | **OFFERS_YIELD** | Protocol / Pool → YieldOpportunity | APY surface |
| 13 | **TRANSFERS_TO** | Wallet → Wallet | On-chain flow observation |

## Design Notes

- **Pool ≠ Protocol**: We separate them so we can track a single Uniswap pool's health independently of Uniswap-the-protocol. Critical for LP rotation and IL signals.
- **MarketEvent is time-bound**: each instance is a node; its `INFLUENCES` edges drive the risk domain predictions.
- **SentimentIndicator** is intentionally a first-class entity (not a property) because Buttondown issues consistently reference Fear & Greed and trending lists — the graph should query them directly.
- **Wallet nodes** will stay sparse initially (Buttondown references "unknown whales"); they fill in once Alchemy/Goldsky sources join the pipeline.
- **No "Persona" entity**: simulation personas (whale/degen/LP/protocol team) are agents, not graph nodes — they *query* this graph.

## Mapping to Prediction Domains

| Domain | Key entities | Key edges |
|---|---|---|
| Token prices | Token, SentimentIndicator, MarketEvent | INFLUENCES, CORRELATES_WITH |
| Yield + APY | Pool, Protocol, YieldOpportunity | OFFERS_YIELD, DEPLOYED_ON |
| Liquidity + TVL | Pool, Chain, Protocol, Wallet | PROVIDES_LIQUIDITY, DEPLOYED_ON, TRANSFERS_TO |
| Risk signals | MarketEvent, RegulatoryBody, GovernanceProposal | EXPLOITS, REGULATES, INFLUENCES |
