# Survivor

## Overview
Survivor is a social strategy game inspired by the TV show. Players form alliances, vote out opponents one by one, and compete to reach the final round. The twist: eliminated players become jurors who choose the final winner. To win, you need allies to survive the votes — but you also need to avoid making enemies who will refuse to give you the jury victory.

## Players
- Number of players: variable (configurable)
- Roles: All players are symmetric "Player" roles with no hidden information.

## Objective
Survive to the final round and win the jury vote. You must balance making allies (to avoid being voted out) against managing your reputation with those you vote out (who will judge you at the end).

## How to Play
**Elimination phase (repeat until 2-3 survivors remain):**
1. **Discussion:** All living players speak freely — form alliances, make arguments, lobby for targets.
2. **Vote:** All players simultaneously vote to eliminate one person. Most votes = eliminated. Eliminated players join the jury.

**Final phase:**
3. **Jury Plea:** Final survivors each make a plea to the jury explaining why they deserve to win.
4. **Jury Vote:** Each jury member votes for which finalist should win. Highest jury votes wins.

## Scoring / Payoffs
- Winner of jury vote: +1.0
- Runner-up finalists: 0.0 (or -1.0 depending on configuration)
- Eliminated players: -1.0

## Our Settings
- Action order: round-robin for discussion/plea, simultaneous for votes
- Models: gpt-4o for all agents
- Final phase triggered when 2-3 players remain

## Social Skills Tested
- **Alliance formation:** Building coalitions to protect yourself while targeting others.
- **Long-term reputation management:** Balancing strategic betrayals against maintaining goodwill with future jurors.
- **Persuasion:** Making compelling arguments in jury pleas about why you played the best game.
- **Social awareness:** Reading who is aligned with whom and who is a threat vs. a potential ally.
