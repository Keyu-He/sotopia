# Prisoner's Dilemma

## Overview
The Prisoner's Dilemma is the most famous game in game theory. Two players independently decide whether to cooperate or defect. Mutual cooperation gives the best joint outcome, but each player is individually tempted to defect (which yields a higher personal payoff regardless of the other's choice). In this iterated version, players play 5 rounds, allowing strategies like tit-for-tat to emerge.

## Players
- Number of players: 2
- Roles: Both players are symmetric "Player" roles with no information advantage.

## Objective
Maximize your own cumulative score over 5 rounds. If both players score fewer than 10 points total, it is a draw (both lose). Otherwise, the higher scorer wins.

## How to Play
1. Each round, both players simultaneously choose `cooperate` or `defect`.
2. No speaking is allowed — only actions.
3. Points are awarded based on the combination of choices (see payoffs below).
4. After 5 rounds, the higher-scoring player wins (if threshold is met).

## Scoring / Payoffs
Per round payoffs (Player 1, Player 2):
- Both cooperate: 3 each
- Player 1 defects, Player 2 cooperates: 5, 0
- Player 1 cooperates, Player 2 defects: 0, 5
- Both defect: 1 each

Win conditions:
- If both players score < 10 total: Draw (0.0 each)
- Otherwise: Higher scorer wins (+1.0), lower scorer loses (-1.0)
- Tied with both ≥ 10: Draw (0.0)

## Our Settings
- Max rounds: 5
- Win threshold: 10 points
- Action order: simultaneous
- No speaking allowed
- Models: gpt-4o for all agents

## Social Skills Tested
- **Cooperation vs. self-interest:** The core tension between maximizing joint payoff and personal gain.
- **Trust and reciprocity:** Whether players develop mutual cooperation after observing each other's choices.
- **Punishment and forgiveness:** How agents respond to defection — do they retaliate or maintain cooperation?
- **Tit-for-Tat reasoning:** Detecting and responding to the opponent's strategy across repeated rounds.
