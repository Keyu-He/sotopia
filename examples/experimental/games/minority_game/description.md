# Minority Game (El Farol Bar Problem)

## Overview
The Minority Game, inspired by the El Farol Bar problem, is a multi-player anti-coordination game. Players must independently decide to "go" or "stay," and whichever choice fewer than half the players make is the winning side. No communication is allowed — success requires predicting what the majority will do and doing the opposite.

## Players
- Number of players: 5
- Roles: All players are symmetric "Player" roles with no special information.

## Objective
Maximize your own cumulative score over 12 rounds. You need at least 15 total points to have a chance at winning; otherwise everyone loses (draw).

## How to Play
1. Each round, all 5 players simultaneously choose `go` or `stay`.
2. No speaking is allowed — only actions.
3. The minority group (fewer than half = fewer than 2.5 players, i.e., 0 or 1 out of 5 choosing the same option) wins 3 points each.
4. The majority group scores 0 for that round.
5. After 12 rounds, whoever has the most total points wins (if threshold is met).

## Scoring / Payoffs
Per round:
- Players in the minority group: +3 points each
- Players in the majority group: 0 points

Win conditions:
- If ALL players score < 15 total: Draw (everyone loses)
- Otherwise: Highest scorer wins (+1.0), others lose (-1.0)
- All tied: Draw (0.0)

## Our Settings
- Max rounds: 12
- Win threshold: 15 points
- Number of players: 5
- Minority threshold: fewer than 2.5 (i.e., 0 or 1 out of 5)
- Points per winning round: 3
- Action order: simultaneous
- No speaking allowed
- Models: gpt-4o for all agents

## Social Skills Tested
- **Anti-coordination:** Unlike most games where you want to match the group, here you must predict and avoid the majority choice.
- **Crowd psychology modeling:** Estimating what most agents will do in order to deliberately do the opposite.
- **Decentralized equilibrium:** Whether a stable distribution emerges (roughly half go / half stay) without communication.
- **Adaptive strategy:** Adjusting behavior when your previous choice became the majority.
