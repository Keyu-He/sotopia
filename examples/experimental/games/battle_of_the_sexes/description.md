# Battle of the Sexes

## Overview
Battle of the Sexes is a classic coordination game where two players prefer different outcomes but both prefer coordinating over not coordinating at all. One player prefers "opera" and the other prefers "football," but meeting at the same event is better than going to different events alone.

## Players
- Number of players: 2
- Roles: Both players are "Player" roles, but they have opposite preferences (Alice prefers opera, Bob prefers football).

## Objective
Maximize your own score over 10 rounds. You need at least 28 total points to have a chance at winning; otherwise both players lose (draw).

## How to Play
1. Each round, both players simultaneously choose `opera` or `football`.
2. No speaking is allowed — only actions.
3. Points are awarded based on the combination of choices (see payoffs below).
4. After 10 rounds, whoever has more total points wins (provided at least one player reached 28).

## Scoring / Payoffs
Per round payoffs (Alice, Bob):
- Both opera: Alice gets 3, Bob gets 2
- Both football: Alice gets 2, Bob gets 3
- One opera, one football: 0 each (miscoordination)

Win conditions:
- If both score < 28 total: Draw (both lose)
- Otherwise: Higher scorer wins (+1.0), lower scorer loses (-1.0)
- Tied with both ≥ 28: Draw (0.0)

## Our Settings
- Max rounds: 10
- Win threshold: 28 points
- Action order: simultaneous
- No speaking allowed
- Models: gpt-4o for all agents

## Social Skills Tested
- **Coordination:** Aligning on the same event despite differing preferences.
- **Compromise:** Learning to alternate between preferred outcomes across rounds.
- **Implicit communication:** Signaling intent through repeated choices without explicit speech.
