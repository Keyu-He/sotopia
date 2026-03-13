# Game Designs for Sotopia

This document contains game designs for the Sotopia social game engine, organized by complexity tier.

Before implementing, read `ENGINE_REFERENCE.md` for engine capabilities and constraints.

---

## Design Principles

### What makes a good game for LLM evaluation?

1. **Social complexity over mechanical complexity**: Difficulty should come from multi-agent social dynamics (persuasion, deception, trust, alliance management) -- not from hidden random numbers or statistical estimation.

2. **No trivially solvable equilibria**: Games where "always cooperate" or "always defect" dominates are poor benchmarks. The optimal strategy must depend on what the other agents do.

3. **Not solvable by memorization**: Classic game theory problems with textbook solutions (one-shot PD, Pirate division) are weak unless parameterized. Iterated versions are better because optimal play requires opponent modeling.

4. **Language is strategically meaningful**: Since LLMs communicate via text, the best games are those where what you say changes outcomes -- persuasion, negotiation, deception, signaling.

5. **Instance variation**: Each game run should differ (randomized hidden info, different social dynamics) so no fixed strategy transfers across games.

### What kind of complexity to add (and avoid)

| Good (social complexity) | Bad (mechanical complexity) |
|---|---|
| Players must persuade and negotiate | Hidden random thresholds to guess |
| Players can lie and must detect lies | Randomized multipliers to estimate |
| Alliances form and break through conversation | Asymmetric hidden endowments |
| Past behavior creates reputation effects | More parameters to calculate |

### Anti-degeneracy checklist

A game passes if it satisfies at least 3 of these:
- [ ] Someone must lose (no all-win outcome)
- [ ] Interests are fundamentally misaligned for at least some players
- [ ] "Just be nice" is not a viable strategy
- [ ] Communication creates strategic tension (not just coordination)
- [ ] Information is revealed through play, changing the strategic landscape

---

## Tier 1: Simple Iterated Games

These have straightforward mechanics (single self-looping state, simultaneous binary choices) and follow the Prisoner's Dilemma pattern: no discussion phase, explicit round count and score thresholds communicated to agents.

**Design principles for Tier 1:**
- **No discussion phase**: Agents cannot explicitly coordinate, forcing implicit strategy adaptation.
- **Score threshold**: If all players score below the threshold, all lose (draw). This prevents pure cooperation from being a viable strategy and forces strategic exploitation.
- **More rounds** (10-12): Enough rounds for agents to observe opponent patterns and adapt (e.g., endgame betrayal, tit-for-tat emergence).
- **Agents know the rules**: The game description explicitly states total rounds, payoff matrix, and threshold -- enabling backward induction and strategic planning.

### Survivor (Social Voting)

**Concept**: No hidden roles. No hidden information. Each round: free discussion, then vote someone out. Eliminated players form a jury that decides the final winner among the last 2-3 survivors.

**Players**: 5-7

**Why it's strategically valid**: The jury mechanic means you can't just backstab everyone to reach the finale -- your victims decide if you win. Tests alliance management and reputation across rounds.

**Risk of degeneracy**: Moderate. Without hidden info, LLMs may produce generic diplomatic statements. Best used as a "social baseline" rather than a primary benchmark.

**FSM**:
```
Discussion (round-robin, public, speak)
  -> Vote (simultaneous, public, action: "vote NAME")
  -> [eliminated player joins jury]
  -> Discussion (repeat until 2-3 remain)
  -> Jury_plea (finalists only, round-robin, public, speak)
  -> Jury_vote (jurors only, simultaneous, public, action: "vote NAME")
```

**Win conditions**:
- Finalist with most jury votes: 1.0
- Other finalist: 0.0
- Eliminated players: -0.5

**Implementation notes**:
- Jury requires letting eliminated players act in Jury_vote. Override action mask to allow dead players in that state.
- Track `internal_state["jury"]` list of eliminated players.

**Config skeleton**:
```json
{
  "scenario": "Survivor",
  "description": "Each round: discuss, then vote someone out. No hidden roles. Eliminated players become jurors who pick the final winner. You need allies to survive but victims' goodwill to win. Players: {agent_names}.",
  "role_goals": {
    "Player": "Survive to the final round and win the jury vote."
  },
  "role_secrets": {},
  "initial_state": "Discussion",
  "state_transition": {
    "Discussion": "Vote",
    "Vote": "Discussion"
  },
  "state_properties": {
    "Discussion": {"actions": ["speak"], "action_order": "round-robin", "visibility": "public"},
    "Vote": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"}
  }
}
```

### Chicken (Hawk-Dove)

**Concept**: Two players simultaneously choose "swerve" or "straight". Both straight = crash (0,0). One straight, one swerve = straight wins big. Both swerve = modest tie. Repeated.

**Players**: 2

**Payoff matrix**:
| | Swerve | Straight |
|--|--------|----------|
| **Swerve** | 3, 3 | 1, 5 |
| **Straight** | 5, 1 | 0, 0 |

**Risk of degeneracy**: High in one-shot (both swerve). In iterated play, opponent modeling (will they swerve this round?) adds depth. Consider adding a discussion round to increase social dynamics.

**Implementation**: Nearly identical to existing Prisoner's Dilemma. Different payoff matrix, different action names.

### Stag Hunt

**Concept**: All players simultaneously choose "stag" or "hare". All-stag = 5 points each. Any hare = stag hunters get 0, hare hunters get 2. Repeated.

**Players**: 3-5

**Risk of degeneracy**: High (all-stag is both Pareto-optimal and Nash equilibrium). Multi-player version is slightly better (more players = more risk). Adding a discussion round where players can make promises helps test whether LLMs honor commitments.

### Centipede Game

**Concept**: Two players alternate. "Take" the pot (game ends, you get the larger share) or "pass" (pot grows, opponent gets next turn). Pot grows exponentially.

**Players**: 2

**Risk of degeneracy**: High (LLMs likely always pass, reaching the end). Interesting as a test of backward induction reasoning but may not differentiate between models.

### Minority Game (El Farol Bar)

**Concept**: Each round, simultaneously choose "go" or "stay". If fewer than half go, goers score. If half or more go, stayers score. You want to be in the minority.

**Players**: 5-7 (odd number)

**Anti-coordination**: Cannot degenerate because doing the same thing is structurally punished. However, no communication phase makes it more mechanical than social. Consider adding a discussion round.

**FSM**: Single self-looping state (simultaneous, private choices, public results).

### Battle of the Sexes

**Concept**: Two players coordinate on one of two options, but each prefers a different one. Coordinating on either is better than miscoordinating.

**Players**: 2

**Risk of degeneracy**: Moderate. LLMs may agree to alternate. Adding a discussion phase tests negotiation and commitment.

### Public Goods Game

**Concept**: Each round, secretly contribute 0-10 tokens to a shared pool. Pool is multiplied and split equally. Free-riding is tempting but destructive.

**Players**: 4-6

**Risk of degeneracy**: High (LLMs either all contribute max or all free-ride). Can be improved by revealing individual contributions (enabling social punishment) and adding a discussion phase.

---

## Tier 2: Complex Games (Priority Implementation)

These games have richer mechanics, hidden information, and multiple types of social interaction. They test distinct dimensions of strategic social reasoning and resist degeneracy by design.

### 1. Dead Last

**Concept**: Each round, players discuss openly, then simultaneously point at someone to eliminate. Strict majority on a target = elimination. No majority = no one dies. Last 2-3 survivors negotiate a prize split.

**Players**: 5-6

**Social behaviors tested**:
- Alliance formation and persuasion ("let's all vote out Bob")
- Self-preservation through rhetoric (talking your way out of being targeted)
- Betrayal timing (when to turn on allies)
- Reading social signals ("everyone keeps mentioning my name")
- Endgame negotiation under pressure

**Why it won't degenerate**: Someone MUST be eliminated each round. There is no all-win outcome. Even the endgame split is zero-sum.

**FSM**:
```
Discussion (round-robin, public, speak)
  -> Point (simultaneous, public, action: "point NAME")
  -> [if majority: eliminate target; if no majority: no elimination]
  -> Discussion (repeat until 2-3 remain)
  -> Final_negotiation (round-robin, public, speak)
  -> Final_offer (simultaneous, private, action: "offer SPLIT")
```

**Win conditions**:
- Eliminated players: -1.0
- Survivors who agree on split: proportional to share (normalized to [0, 1])
- Survivors who fail to agree: 0.0

**Implementation notes**:
- Majority calculation: target needs > half of alive players pointing at them.
- Final split: players propose splits. If unanimous agreement, split accordingly. Otherwise all get 0.
- When 2-3 remain, override `current_state` to jump to Final_negotiation.
- No hidden information -- all social complexity comes from the discussion.

**Config skeleton**:
```json
{
  "scenario": "Dead Last",
  "description": "Each round: discuss, then simultaneously point at someone to eliminate. Majority on a target = eliminated. No majority = no elimination. Last 2-3 players negotiate a prize split. Fail to agree = everyone gets nothing. Players: {agent_names}.",
  "role_goals": {
    "Player": "Survive to the final round and negotiate the largest share of the prize."
  },
  "role_secrets": {},
  "initial_state": "Discussion",
  "state_transition": {
    "Discussion": "Point",
    "Point": "Discussion"
  },
  "state_properties": {
    "Discussion": {"actions": ["speak"], "action_order": "round-robin", "visibility": "public"},
    "Point": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"}
  }
}
```

---

### 2. Insider

**Concept**: The group cooperatively tries to guess a secret word by asking yes/no questions (answered truthfully by the environment). One player -- the Insider -- secretly knows the word and must subtly help the group guess it. After the word is guessed, the group votes on who the Insider is. If identified, the group wins. If the Insider stays hidden, the Insider wins. If the word isn't guessed, everyone loses (including the Insider).

**Players**: 5-6 (1 Insider, rest Citizens)

**Social behaviors tested**:
- Subtle communication and indirection (guiding without being obvious)
- Suspicion detection from conversational patterns
- Balancing cooperative goals with individual goals
- Theory of mind ("would a normal person ask this question?")

**Why it won't degenerate**: The Insider MUST help (or the word isn't guessed and they lose) but MUST hide (or they're identified and lose). This tightrope creates genuine tension with no easy solution. The optimal level of helpfulness depends on the specific word, the group's progress, and how suspicious people are.

**Instance variation**: The secret word changes each game. Social dynamics of "which questions seemed too insightful" are entirely emergent.

**FSM**:
```
Questioning (round-robin, public, speak)
  -> [environment answers yes/no; repeat for N rounds or until ready to guess]
  -> Guess (simultaneous, public, action: "guess WORD" or "pass")
  -> [if correct: proceed to Discussion; if wrong: game over, everyone loses]
  -> Discussion (round-robin, public, speak)
  -> Vote (simultaneous, public, action: "vote NAME")
```

**Win conditions**:
- Word not guessed: everyone loses (-1.0 for all)
- Word guessed + Insider identified: Citizens win (1.0), Insider loses (-1.0)
- Word guessed + Insider NOT identified: Insider wins (1.0), Citizens lose (-1.0)

**Implementation notes**:
- **Yes/no answering**: The environment must answer questions about the secret word. Best approach: store a fact sheet in config (`"secret_word_facts"`) and use LLM-based yes/no answering, or pre-define Q&A pairs for simpler implementation.
- **Insider's secret**: `role_secrets` for Insider contains the word.
- **Question limit**: Track `internal_state["questions_asked"]`, cap at ~15.
- **Branching on guess**: If no correct guess, game ends (all lose). Override `current_state` in code.
- **Multiple Questioning→Guess cycles**: May need to loop Questioning→Guess→Questioning if no one guesses correctly on first attempt.

**Config skeleton**:
```json
{
  "scenario": "Insider",
  "description": "The group asks yes/no questions to guess a secret word. One player (the Insider) secretly knows the word and must subtly guide the group without being too obvious. After the word is guessed, the group votes on who the Insider is. If the word isn't guessed, everyone loses. Players: {agent_names}.",
  "role_goals": {
    "Citizen": "Help guess the word, then identify the Insider.",
    "Insider": "Subtly help the group guess the word, then avoid being identified."
  },
  "role_secrets": {
    "Insider": "The secret word is: {word}"
  },
  "secret_word": "kangaroo",
  "secret_word_facts": "It is an animal. It is a mammal. It lives in Australia. It hops on two legs. It has a pouch. It is not a pet. It is larger than a dog. It is brown or grey. It eats grass. Baby ones are called joeys.",
  "max_questions": 15,
  "initial_state": "Questioning",
  "state_transition": {
    "Questioning": "Guess",
    "Guess": "Discussion",
    "Discussion": "Vote"
  },
  "state_properties": {
    "Questioning": {"actions": ["speak"], "action_order": "round-robin", "visibility": "public"},
    "Guess": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"},
    "Discussion": {"actions": ["speak"], "action_order": "round-robin", "visibility": "public"},
    "Vote": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"}
  }
}
```

---

### 3. Liar's Dice

**Concept**: Each player has hidden dice (rolled fresh each round). Players take turns making bids about the total count of a face value across ALL players' dice. Each bid must be higher than the previous. Instead of bidding higher, you can call "liar". If the actual count is less than the bid, the bidder loses a die. If it meets or exceeds the bid, the caller loses. Last player standing wins.

**Players**: 3-5 (each starts with 5 dice)

**Social behaviors tested**:
- Bluffing through bid escalation
- Reading bidding patterns across rounds ("Alice always bids conservatively, but now she jumped high -- bluff?")
- Pressure management (escalating bids create increasing tension)
- Risk assessment informed by social signals

**Why it won't degenerate**: Dice are random each round, so no fixed strategy works. Bluffing is necessary (you won't always have good dice) but over-bluffing gets punished. The social reading of opponents' bidding history creates emergent dynamics.

**FSM**:
```
Bidding (round-robin, public, action: "bid QUANTITY FACE" or "liar")
  -> [if "liar" called: resolve, loser loses a die, new dice rolled]
  -> [if bid raised: continue round-robin]
  -> Bidding (self-loop)
```

**Win conditions**:
- Last player with dice: 1.0
- All eliminated: -1.0

**Implementation notes**:
- **Dice storage**: `internal_state["dice"] = {"Alice": [1, 3, 3, 5, 6], ...}`. Re-rolled after each "liar" resolution.
- **Private dice reveal**: Use `env.recv_message("Environment", msg, receivers=[name])` for each player at round start.
- **Bid tracking**: `internal_state["current_bid"] = {"quantity": 4, "face": 3, "bidder": "Alice"}`.
- **Bid validation**: The ActionHandler must verify new bids are strictly higher (higher quantity, or same quantity with higher face).
- **Round-robin with dynamic start**: After a "liar" resolution, the loser of that challenge starts the next bidding round. Track in `internal_state["start_player_idx"]`.
- **"Liar" call handling**: When someone calls "liar", the ActionHandler counts the actual total of the bid face across all dice, resolves who loses, removes a die from the loser, and re-rolls all dice. This all happens within the Bidding state (self-loop) via code logic.
- **Elimination**: When a player reaches 0 dice, `agent_alive[name] = False`.

**Config skeleton**:
```json
{
  "scenario": "Liar's Dice",
  "description": "Each player has hidden dice. Take turns bidding on the total count of a face value across ALL players' dice. Each bid must be higher than the previous. Call 'liar' instead of bidding to challenge. If caller is right, bidder loses a die. If wrong, caller loses. Last player standing wins. Players: {agent_names}.",
  "role_goals": {
    "Player": "Be the last player with dice remaining. Bluff strategically and call liars wisely."
  },
  "role_secrets": {
    "Player": "Your dice are revealed privately each round."
  },
  "starting_dice": 5,
  "initial_state": "Bidding",
  "state_transition": {
    "Bidding": "Bidding"
  },
  "state_properties": {
    "Bidding": {
      "actions": ["action"],
      "action_order": "round-robin",
      "visibility": "public"
    }
  }
}
```

---

### 4. The Resistance

**Concept**: 5 players: 3 Resistance, 2 Spies. Resistance wants 3 of 5 missions to succeed. Spies want 3 to fail. Each round, a rotating leader proposes a mission team. Everyone votes. If approved, team members secretly play "succeed" or "fail". Resistance must play succeed; Spies may play either. The number of fail cards is announced (not who played them). No one is ever eliminated.

**Players**: 5 (3 Resistance, 2 Spies)

**Social behaviors tested**:
- Social deduction from behavioral patterns (voting history, proposal patterns)
- Persuasive argumentation ("I should be on this mission because...")
- Sustained deception under scrutiny (Spies must defend themselves round after round)
- Coalition building and trust management
- Information accumulation (no elimination means evidence compounds)

**Why it won't degenerate**: Spies MUST sabotage to win. Pure cooperation means Resistance auto-wins. But sabotaging creates evidence (fail cards). The tension between needing to sabotage and needing to stay hidden is irreconcilable.

**Key difference from Werewolves**: No elimination. Mistakes are recoverable. Information accumulates instead of being destroyed. All players stay active throughout, creating richer social dynamics.

**FSM**:
```
Discussion (round-robin, public, speak)
  -> Mission_proposal (leader only, public, action: "propose NAME1 NAME2")
  -> Mission_vote (simultaneous, public, action: "approve" or "reject")
  -> [if rejected: rotate leader, back to Discussion; 5 rejections = Spies win]
  -> Mission_execute (team only, private, action: "succeed" or "fail")
  -> [environment announces: "X fail cards played"]
  -> Discussion (next leader)
```

**Win conditions**:
- 3 missions succeed: Resistance wins (1.0), Spies lose (-1.0)
- 3 missions fail: Spies win (1.0), Resistance loses (-1.0)
- 5 consecutive rejected proposals: Spies win (1.0), Resistance loses (-1.0)

**Implementation notes**:
- **Leader rotation**: `internal_state["leader_idx"]`, increment after each proposal cycle.
- **Mission team**: `internal_state["mission_team"] = ["Alice", "Bob"]`.
- **Mission sizes**: For 5 players: [2, 3, 2, 3, 3]. Store in config.
- **Branching on vote**: If rejected, override `current_state` back to Discussion and rotate leader. Track `internal_state["consecutive_rejections"]`.
- **Mission results tracking**: `internal_state["successes"]` and `internal_state["failures"]` counters.
- **Spy knowledge**: Spies know each other. Fill in `role_secrets` at agent creation with partner names.
- **Mission_execute restriction**: Only mission team members can act. Override `_update_action_mask()` to set masks for non-team members to False.

**Config skeleton**:
```json
{
  "scenario": "The Resistance",
  "description": "Social deduction. 3 Resistance vs 2 Spies. A rotating leader proposes mission teams. Everyone votes to approve/reject. If approved, team members secretly succeed or fail the mission. Number of fails is announced (not who). Resistance wins with 3 successes. Spies win with 3 failures or 5 rejected proposals. No one is eliminated. Players: {agent_names}.",
  "role_goals": {
    "Resistance": "Complete 3 missions successfully. Identify and exclude spies from teams.",
    "Spy": "Sabotage 3 missions. Get on teams without being detected."
  },
  "role_secrets": {
    "Spy": "You are a Spy."
  },
  "mission_sizes": [2, 3, 2, 3, 3],
  "initial_state": "Discussion",
  "state_transition": {
    "Discussion": "Mission_proposal",
    "Mission_proposal": "Mission_vote",
    "Mission_vote": "Mission_execute",
    "Mission_execute": "Discussion"
  },
  "state_properties": {
    "Discussion": {"actions": ["speak"], "action_order": "round-robin", "visibility": "public"},
    "Mission_proposal": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"},
    "Mission_vote": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"},
    "Mission_execute": {"actions": ["action"], "action_order": "simultaneous", "visibility": "private"}
  },
  "end_conditions": []
}
```

---

### 5. Coup

**Concept**: A bluffing game. Each player has 2 hidden influence cards (Duke, Assassin, Captain, Ambassador, Contessa). On your turn, declare an action (some claim a specific role). All other players simultaneously choose to challenge, block, or pass. If challenged and caught bluffing, you lose a life. If the challenger is wrong, they lose a life. Last player standing wins.

**Players**: 4-6 (each starts with 2 lives and 2 coins)

**Social behaviors tested**:
- Bluffing frequency management (too much = caught; too little = predictable)
- Challenge decision-making (risk a life to call a bluff?)
- Information tracking (revealed cards narrow possibilities)
- Social pressure and targeting (who to assassinate, who to steal from)
- Reading opponents ("Alice has claimed Duke three times -- real or bluff?")

**Why it won't degenerate**: Every turn creates genuine tension. Declaring any powerful action risks being challenged. Challenging risks losing a life. There is no safe strategy -- even "Income" (unchallengeble) is slow and lets others build power. The information space shifts every turn as cards are revealed.

**Actions available**:
| Action | Claims | Effect | Can be blocked by |
|--------|--------|--------|-------------------|
| Income | None | +1 coin | Nothing |
| Foreign Aid | None | +2 coins | Duke |
| Tax | Duke | +3 coins | Nothing |
| Steal | Captain | Take 2 from target | Captain, Ambassador |
| Assassinate | Assassin | Pay 3, target loses life | Contessa |
| Exchange | Ambassador | Swap cards with deck | Nothing |
| Coup | None | Pay 7, target loses life (mandatory at 10+) | Nothing |

**FSM (simplified -- no challenge-of-blocks in v1)**:
```
Declare (round-robin, public, action: "income"/"tax"/"steal NAME"/etc.)
  -> Response (simultaneous, all others, public, action: "challenge"/"block"/"pass")
  -> [ActionHandler resolves: challenge > block > pass priority]
  -> Declare (next alive player)
```

**Win conditions**:
- Last player with lives: 1.0
- All eliminated: -1.0

**Resolution logic** (in ActionHandler):
1. If anyone challenged:
   - Declarer has the claimed card: challenger loses 1 life. Declarer shuffles card back and draws new.
   - Declarer doesn't have it: declarer loses 1 life. Action cancelled.
2. Else if anyone blocked: action cancelled (simplified: block succeeds without counter-challenge).
3. Else: action effect applied.

**Implementation notes**:
- **Card management**: `internal_state["hands"] = {"Alice": ["Duke", "Assassin"], ...}`, `internal_state["coins"] = {"Alice": 2, ...}`, `internal_state["revealed"] = ["Captain", ...]`.
- **Card pool**: 3 copies of each of 5 roles = 15 cards. Deal 2 per player, rest form court deck.
- **Exclude declarer from Response**: Override `_update_action_mask()` to set declarer's mask to False during Response. Track `internal_state["current_declarer"]`.
- **Mandatory coup**: If a player has 10+ coins, they must coup. ActionHandler enforces this.
- **Card shuffle on successful defense**: When defending against a challenge (has the card), shuffle that card back into deck and draw a new one. Simulated via `internal_state`.
- **Elimination**: `agent_alive[name] = False` when both lives lost.
- **v1 simplification**: No challenge-of-blocks. Blocks simply succeed. This preserves 90% of strategic depth.

**Config skeleton**:
```json
{
  "scenario": "Coup",
  "description": "Bluffing game. Each player has 2 hidden influence cards and 2 coins. On your turn, declare an action (some claim a role). Others can challenge your claim or block. Caught bluffing = lose a life. Wrong challenge = lose a life. Last player standing wins. Actions: Income (+1 coin, safe), Foreign Aid (+2, blockable by Duke), Tax (claim Duke, +3), Steal (claim Captain, take 2 from target), Assassinate (claim Assassin, pay 3, target loses life), Exchange (claim Ambassador, swap cards), Coup (pay 7, target loses life, mandatory at 10+). Players: {agent_names}.",
  "role_goals": {
    "Player": "Be the last player with influence remaining."
  },
  "role_secrets": {
    "Player": "Your influence cards will be revealed privately."
  },
  "card_types": ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"],
  "cards_per_type": 3,
  "starting_coins": 2,
  "initial_state": "Declare",
  "state_transition": {
    "Declare": "Response",
    "Response": "Declare"
  },
  "state_properties": {
    "Declare": {"actions": ["action"], "action_order": "round-robin", "visibility": "public"},
    "Response": {"actions": ["action"], "action_order": "simultaneous", "visibility": "public"}
  }
}
```

---

## Tier 3: Long-Form and Complex Board+Social Games (Future)

These games require substantially more infrastructure (persistent state across many rounds, complex board/territory mechanics, or very long gameplay sessions). They represent the highest complexity tier and are candidates for future implementation.

- **Diplomacy-lite**: Territory control + non-binding alliances + simultaneous order resolution. Excellent social dynamics (negotiation, betrayal, coalition management) but requires spatial state tracking and multi-order resolution. Long games (10+ strategic rounds with negotiation phases).
- **Secret Hitler**: Similar to Resistance but with a policy card deck adding ambiguity about whether bad outcomes are due to spies or bad luck. Multiple win paths (legislative, executive actions). Most complex social deduction game.
- **Jubensha (Script Murder)**: Chinese-origin social deduction format with extensive narrative, character backstories, clue investigation phases, and multi-hour gameplay. Tests sustained in-character reasoning, information synthesis across many clues, and long-horizon strategic planning.
- **Sheriff of Nottingham**: Smuggling + bribery + inspection with rotating Sheriff role. Rich social dynamics (negotiation, bribing, bluffing about goods) but requires goods/inventory system.
- **20 Questions with a Mole**: Similar to Insider but with inverted incentive -- the Mole secretly hinders the group's guessing. Tests a different deception dynamic (subtle obstruction vs. subtle help).

### Other candidates (lower priority)
- **Sealed-Bid Auction**: Private valuations + sealed bids. Strategic but more mathematical than social.
- **Pirate Loot Division**: Classic backward induction problem. Risk of memorization unless heavily parameterized.
- **Trust Game / Dictator Game**: Iterated versions test opponent modeling but may degenerate to cooperative equilibria.
