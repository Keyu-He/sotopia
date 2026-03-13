# Stag Hunt

## Overview
Stag Hunt is a cooperation and trust game. Players must decide whether to hunt a stag together (high reward, requires full cooperation) or hunt a hare alone (safe but lower reward). If even one player breaks rank and hunts a hare, the stag hunters get nothing. This game tests trust and collective coordination.

## Players
- Number of players: 4
- Roles: All players are symmetric "Player" roles.

## Objective
Maximize your own score over 10 rounds. You need at least 45 total points to have a chance at winning; otherwise everyone loses (draw).

## How to Play
1. Each round, all 4 players simultaneously choose `stag` or `hare`.
2. No speaking is allowed — only actions.
3. If ALL 4 players choose stag: each gets 5 points.
4. If anyone chooses hare: stag hunters get 0, hare hunters each get 2.
5. After 10 rounds, whoever has the most total points wins (provided threshold is met).

## Scoring / Payoffs
Per round:
- All choose stag: 5 points each
- Any hare chosen: hare hunters get 2, stag hunters get 0

Win conditions:
- If ALL players score < 45 total: Draw (everyone loses)
- Otherwise: Highest scorer wins (+1.0), others lose (-1.0)
- All tied: Draw (0.0)

## Our Settings
- Max rounds: 10
- Win threshold: 45 points
- Number of players: 4
- Action order: simultaneous
- No speaking allowed
- Models: gpt-4o for all agents

## Social Skills Tested
- **Trust:** Relying on all other players to cooperate, knowing one defection ruins it.
- **Coordination under uncertainty:** Aligning on the risky-but-rewarding equilibrium vs. the safe equilibrium.
- **Collective action:** Maintaining group cooperation over repeated rounds without communication.
