# Sotopia Social Game Engine Reference

This document describes the capabilities and constraints of the Sotopia social game engine, so that an LLM (or a human) can design new games that are implementable without engine modifications.

## Architecture Overview

The engine lives in `sotopia/envs/social_game.py` and provides two base classes plus two abstract interfaces:

```
SocialGame (ABC)              <-- abstract base, extends ParallelSotopiaEnv
  └── SocialDeductionGame     <-- concrete base with FSM, roles, teams, visibility

ActionHandler (ABC)           <-- interface for game-specific action parsing
SocialGameEndEvaluator        <-- base class for win condition checking (in evaluators.py)
```

Each game implements:
1. A **subclass** of `SocialDeductionGame` (or `SocialGame` directly for unusual games)
2. An **ActionHandler** subclass for parsing agent actions
3. An **Evaluator** subclass for checking win/loss/draw
4. A **JSON config** defining states, roles, transitions, visibility

## What the Engine CAN Do

### 1. Finite State Machine (FSM)

Games define a set of named states and linear transitions between them.

```json
{
  "initial_state": "Night_werewolf",
  "state_transition": {
    "Night_werewolf": "Night_seer",
    "Night_seer": "Night_witch",
    "Night_witch": "Day_discussion",
    "Day_discussion": "Day_vote",
    "Day_vote": "Night_werewolf"
  }
}
```

- States cycle automatically when transition conditions are met.
- Self-loops are supported (`"Round": "Round"`) for repeated-round games.
- The engine resets round-robin counters and turn counts on transition.

### 2. Roles and Teams

Each agent is assigned a **role** (e.g. "Werewolf", "Seer", "Player") which maps to a **team** (e.g. "Villagers", "Werewolves").

```json
{
  "agents": [
    {"name": "Alice", "role": "Werewolf", "team": "Werewolves"},
    {"name": "Bob", "role": "Villager", "team": "Villagers"}
  ]
}
```

- Roles determine which agents can act in each state (via `acting_roles`).
- Teams determine visibility for `"team"` visibility mode.
- Role goals and secrets are defined per-role in the config.

### 3. Action Types

The engine supports exactly 5 action types (hardcoded as literals):

| Type | Typical Use |
|------|-------------|
| `"speak"` | Free-form text (discussion phases) |
| `"action"` | Structured commands parsed by ActionHandler (vote, kill, cooperate, etc.) |
| `"non-verbal communication"` | Gestures, signals |
| `"none"` | Skip/pass (auto-assigned to inactive agents) |
| `"leave"` | Leave the game |

Each state in the config specifies which action types are available:
```json
"Day_discussion": {
  "actions": ["speak"],
  ...
}
```

All game-specific semantics (what "action: vote Alice" means) are parsed from the `argument` string field inside the ActionHandler. The engine does not enforce any structure on the argument.

### 4. Action Ordering

Three modes control who acts when within a state:

| Mode | Behavior | Transition After |
|------|----------|-----------------|
| `"simultaneous"` | All eligible agents act at once | 1 turn |
| `"round-robin"` | Agents take turns cycling through eligible list | N turns (N = eligible agents) |
| `"random"` | One random eligible agent acts per turn | N turns |

Set per-state in config:
```json
"Day_vote": {
  "action_order": "simultaneous",
  ...
}
```

### 5. Visibility / Information Control

Each state has a visibility mode controlling who sees messages sent during that state:

| Mode | Who Sees |
|------|----------|
| `"public"` | All agents |
| `"team"` | Only agents on the same team as the sender |
| `"private"` | Only the sender |

**Exception**: Messages from `"Environment"` are always public unless explicitly targeted with the `receivers` parameter.

**Targeted messages**: The ActionHandler can send messages to specific agents using `env.recv_message("Environment", msg, receivers=["Alice"])`. This bypasses visibility rules and is essential for private information (e.g., Seer inspection results).

### 6. Alive/Dead Tracking

- `env.agent_alive` is a `Dict[str, bool]` tracking which agents are alive.
- Dead agents receive `["none"]` as their only available action.
- Dead agents are excluded from `eligible_indices` when computing action masks.
- Games set `agent_alive[name] = False` in `_check_eliminations()`.

### 7. Internal State

`env.internal_state` is a freeform `Dict[str, Any]` for game-specific data:

- Votes: `{"votes": {"Alice": "Bob", "Charlie": "Bob"}}`
- Scores: `{"scores": {"Alice": 3, "Bob": 5}}`
- Current moves: `{"current_moves": {"Alice": "Rock", "Bob": "Paper"}}`
- Resources: `{"witch_have_save": True, "witch_have_poison": True}`

This is the primary mechanism for tracking game-specific state. Any data structure works.

### 8. Action Instructions

The ActionHandler's `get_action_instruction()` method returns state-specific text that is injected into the agent's observation. This tells the agent what commands are available:

```python
def get_action_instruction(self, env, agent_name):
    if env.current_state == "Day_vote":
        return "You MUST use 'vote NAME' to vote."
    return ""
```

### 9. Evaluator Return Format

Evaluators return a list of tuples:

```python
[
    ("environment", (("terminated", True), "Villagers win!")),
    ("agent_1", (("complete_rating", 1.0), "Won")),
    ("agent_2", (("complete_rating", -1.0), "Lost")),
]
```

- `complete_rating` is the final reward: typically `1.0` (win), `-1.0` (loss), `0.0` (draw).
- Agent keys are `"agent_1"`, `"agent_2"`, etc. (1-indexed, matching `env.agents` order).

### 10. Prompt Template

All games use the same prompt template with these placeholders:

```
{agent}                 -- Agent's name (filled by engine)
{description}           -- Game description (from config, filled at setup)
{goal}                  -- Role-specific goal (filled at setup)
{secret}                -- Private info (filled at setup)
{action_list}           -- Available actions (filled per-turn by engine)
{action_instructions}   -- State-specific instructions (from ActionHandler)
{history}               -- Message history (from agent_message_buffer)
{format_instructions}   -- JSON format requirements (filled by engine)
```

Games fill `{description}`, `{goal}`, and `{secret}` at agent creation time. The rest are filled dynamically each turn.

## What the Engine CANNOT Do (Limitations)

### 1. No Role/Team Swapping

`agent_to_role` and `role_to_team` are set once during `reset()` and there is no API to change them mid-game. This means:

- No "convert" mechanics (e.g., a player becoming a werewolf after being bitten)
- No role-trading or identity-swapping games
- No "promotion" mechanics (e.g., a pawn becoming a queen)

**Workaround**: You can simulate role-like changes using `internal_state` (e.g., tracking a "converted" flag) and having the ActionHandler check that flag instead of the formal role. However, visibility rules (`"team"` mode) will still use the original role/team assignments.

### 2. Linear FSM Only (No Branching)

`state_transition` maps each state to exactly one successor:

```json
"state_transition": {
    "StateA": "StateB"   // OK: one successor
}
```

There is no way to say "if condition X, go to StateB; else go to StateC" in the config.

**Workaround**: The ActionHandler or the game subclass can directly set `env.current_state = "SomeState"` in code, bypassing the config FSM. This is a code-level workaround; the config alone cannot express branching. However, this requires careful handling of turn counters and round-robin state.

### 3. No Numeric Displays or Structured UI

Agents only see text observations. There is no mechanism to render tables, boards, grids, or structured data. All information must be communicated as natural language text or simple formatted strings within the observation.

### 4. No Inter-Agent Private Messaging (Native)

There is no built-in "whisper" or direct-message system between agents. Visibility is per-state, not per-message.

**Workaround**: The ActionHandler can parse a "whisper NAME message" action and use `env.recv_message("Environment", msg, receivers=[target])` to deliver it privately. But this requires custom code per game.

### 5. No Persistent Memory Between Episodes

Each episode starts fresh. There is no built-in mechanism for agents to remember previous games or build long-term reputation.

### 6. No Real-Time or Timed Actions

All actions are turn-based. There is no timeout mechanism forcing agents to act within a time limit, and no ability for one agent to interrupt another mid-turn.

### 7. No Dynamic Player Count

The number of agents is fixed at game start. Players cannot join or leave mid-game (though they can be marked as dead/inactive).

### 8. Action Parsing is String-Based

The ActionHandler receives the raw `argument` string from the agent and must parse it. There is no structured input validation. If an agent sends a malformed command (e.g., "vote" with no target), the handler must decide what to do (ignore, use default, etc.).

### 9. No Spatial/Positional State

There is no built-in concept of positions, locations, or spatial relationships. Any positional logic must be tracked in `internal_state` and communicated to agents via text.

## Design Patterns from Existing Games

### Pattern A: Deduction Game (Werewolves, Undercover, Spyfall)

```
Roles:   Asymmetric (different roles with different powers)
Teams:   Two opposing teams
States:  Cyclic (Night phases -> Day discussion -> Day vote -> Night)
Actions: "speak" for discussion, "action" for commands (vote, kill, etc.)
Win:     Team elimination or parity condition
```

Components needed:
- ActionHandler: Parse vote/kill/inspect commands, tally votes
- Evaluator: Check team_eliminated and parity conditions
- `_check_eliminations()`: Apply vote results, resolve kills

### Pattern B: Symmetric Strategy Game (RPS, Prisoner's Dilemma)

```
Roles:   Symmetric (all agents have role "Player")
Teams:   None (individual competition)
States:  Single self-looping state ("Round" -> "Round")
Actions: "action" only (no discussion)
Win:     Score-based after fixed number of rounds
```

Components needed:
- ActionHandler: Parse move choices (rock/paper/scissors, cooperate/defect)
- Evaluator: Track scores, determine winner after max rounds
- Override `astep()`: Resolve round before calling `super().astep()`

### Pattern C: Override astep() for Pre-Processing

RPS and Prisoner's Dilemma both override `astep()` to process moves and resolve the round *before* calling `super().astep()`. This is because the base class's `build_state()` -> `state_transition()` pipeline doesn't naturally handle "collect all simultaneous moves, resolve, then transition."

```python
async def astep(self, actions):
    # 1. Process moves via action handler
    # 2. If all players have moved, resolve the round
    # 3. Call super().astep(actions) for standard pipeline
    return await super().astep(actions)
```

## Config Schema Reference

```json
{
  "scenario": "Game Name",
  "description": "Full description with {agent_names} placeholder",
  "role_goals": {
    "RoleName": "What this role is trying to achieve"
  },
  "role_secrets": {
    "RoleName": "Private information for this role"
  },
  "initial_state": "FirstStateName",
  "state_transition": {
    "State1": "State2",
    "State2": "State1"
  },
  "state_properties": {
    "StateName": {
      "actions": ["speak", "action"],
      "action_order": "round-robin|random|simultaneous",
      "visibility": "public|team|private",
      "acting_roles": ["RoleName"],
      "internal_state": {}
    }
  },
  "end_conditions": [
    {
      "type": "team_eliminated|parity",
      "team": "TeamName",
      "winner": "WinningTeamName",
      "message": "Message to display",
      "other": "OtherTeamName"
    }
  ],
  "agents": [
    {
      "name": "Alice",
      "role": "RoleName",
      "team": "TeamName",
      "agent_model": "gpt-4o"
    }
  ]
}
```

Optional config fields (game-specific, read by ActionHandler/Evaluator):
- `"payoff_matrix"`: For matrix games (Prisoner's Dilemma)
- Any custom keys the game code reads from `env._config`

## File Structure for a New Game

```
examples/experimental/games/your_game/
  ├── config.json       # Game config (states, roles, transitions)
  ├── roster.json       # Agent roster (names, roles, models)
  └── main.py           # ActionHandler, Evaluator, Env subclass, setup helpers
```

`main.py` must provide:
- `YourGameActionHandler(ActionHandler)` with `handle_action()` and `get_action_instruction()`
- `YourGameEvaluator(SocialGameEndEvaluator)` with `_check_win_conditions()` (and override `__call__` for score-based games)
- `YourGameEnv(SocialDeductionGame)` with optional overrides for `reset()`, `_check_eliminations()`, `astep()`
- `prepare_scenario()` function returning `(env, agents)` tuple
- Helper functions: `ensure_agent_profile()`, `create_environment()`, `create_agents()`
