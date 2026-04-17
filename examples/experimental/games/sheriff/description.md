# Sheriff of Nottingham

## Overview
Sheriff of Nottingham is a bluffing and negotiation game set in a medieval market. Players act as merchants who must get goods past a rotating Sheriff. Merchants secretly pack either honest goods (safe but less profitable) or contraband (risky but highly profitable). The Sheriff decides whether to inspect each merchant's bag. Merchants can bribe the Sheriff or try to convince them they're honest. After 4 rounds (each player serves as Sheriff once), the richest player wins.

## Players
- Number of players: 4 (Alice, Bob, Charlie, Diana)
- Roles: All players share the "Player" role. The Sheriff role rotates — each player is Sheriff exactly once across 4 rounds.

## Objective
Maximize your total gold after 4 rounds. The player with the most gold wins; the player with the least gold loses.

## How to Play
Each round, one player is designated Sheriff. The other 3 are Merchants.

**Phase 1 — Pack (private, simultaneous):**
- Each Merchant secretly chooses to pack `honest` (3 legal goods worth 3 gold) or `smuggle` (contraband worth 8 gold if not caught).

**Phase 2 — Negotiate (public, round-robin speaking):**
- Merchants can offer bribes, make promises, or argue they packed honestly.
- The Sheriff can demand bribes, threaten inspections, or accept deals.
- No binding agreements — any deals made are on the honor system.

**Phase 3 — Inspect (simultaneous):**
- The Sheriff decides for each Merchant: `inspect NAME` or `pass NAME`.
  - **Inspected + honest:** Sheriff pays a 2-gold penalty to the Merchant.
  - **Inspected + smuggling:** Merchant pays a 4-gold penalty to Sheriff and earns 0 from goods.
  - **Passed:** Merchant keeps their goods (honest=3 gold, smuggle=8 gold).

After 4 rounds, total gold determines the winner.

## Scoring / Payoffs
- Highest gold total: +1.0 reward
- Lowest gold total: -1.0 reward
- Middle players: 0.0

## Social Skills Tested
- **Bluffing:** Smugglers must convince the Sheriff they packed honestly.
- **Negotiation:** Bribing and deal-making during the Negotiate phase.
- **Trust calibration:** The Sheriff must estimate which merchants are lying based on behavior and history.
- **Risk assessment:** Merchants must decide when smuggling is worth the inspection risk given who is Sheriff.
