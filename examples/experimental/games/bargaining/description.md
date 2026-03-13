# Bargaining (Iterated Ultimatum Game)

## Overview
The Bargaining game is an iterated ultimatum game. Each round, one player (the Proposer) splits 10 tokens between themselves and the other player. The other player (the Responder) either accepts the split (both get their shares) or rejects it (both get nothing). Roles alternate each round. This tests fairness norms, negotiation, and strategic offer-making.

## Players
- Number of players: 2
- Roles: Both players alternate between "Proposer" and "Responder" each round.

## Objective
Maximize your own total tokens over 10 rounds. You need at least 25 tokens total to have a chance at winning; otherwise both players lose (draw).

## How to Play
1. Each round, the Proposer uses `offer N` where N is how many tokens the Proposer keeps (Responder gets 10-N).
2. The Responder then chooses `accept` or `reject`.
   - Accept: both get their proposed shares.
   - Reject: both get 0 for that round.
3. Roles switch each round (if Alice proposes in round 1, Bob proposes in round 2).
4. After 10 rounds, the higher-scoring player wins (if threshold is met).

## Scoring / Payoffs
Per round:
- If accepted: Proposer gets N tokens, Responder gets 10-N tokens
- If rejected: Both get 0

Win conditions:
- If both score < 25 total: Draw (0.0 each)
- Otherwise: Higher scorer wins (+1.0), lower loses (-1.0)
- Tied with both ≥ 25: Draw (0.0)

## Our Settings
- Max rounds: 10
- Win threshold: 25 tokens
- Tokens per round: 10
- Roles alternate each round
- Action order: sequential (Propose then Respond)
- Models: gpt-4o for all agents

## Social Skills Tested
- **Negotiation:** Making offers that are fair enough to be accepted while maximizing personal gain.
- **Fairness norms:** Deciding when to reject "unfair" offers even at personal cost.
- **Role-switching strategy:** Adapting behavior as both Proposer and Responder across different rounds.
- **Credible threats:** Whether a reputation for rejecting unfair offers influences future proposals.
