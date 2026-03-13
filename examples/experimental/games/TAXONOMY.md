# Social Game Benchmark: Game Taxonomy

21 social games organized into 5 categories, annotated with social capabilities tested.

## Game Table

| # | Game | Category | Players | Info | Comm. | Iteration | Skills |
|---|------|----------|---------|------|-------|-----------|--------|
| 1 | Prisoner's Dilemma | Normal-Form | 2 | Complete | None | 5 rounds | SR, CO |
| 2 | Chicken | Normal-Form | 2 | Complete | None | 10 rounds | SR, CD |
| 3 | Battle of the Sexes | Normal-Form | 2 | Complete | None | 10 rounds | SR, CD |
| 4 | Stag Hunt | Normal-Form | 4 | Complete | None | 10 rounds | SR, CO, CD |
| 5 | Minority Game | Normal-Form | 5 | Complete | None | 12 rounds | SR, CD |
| 6 | Rock Paper Scissors | Normal-Form | 2 | Complete | None | 10 rounds | SR |
| 7 | Public Goods | Economic | 4 | Hidden State | None | 10 rounds | SR, CO |
| 8 | Centipede | Economic | 2 | Complete | None | 3 games | SR, CO |
| 9 | Bargaining | Economic | 2 | Complete | Structured | 10 rounds | SR, NG |
| 10 | Liar's Dice | Bluffing | 3 | Hidden State | Structured | Until elim. | SR, DC, PR |
| 11 | Skull | Bluffing | 4 | Hidden State | None | Until 2 wins | SR, DC, TM |
| 12 | Coup | Bluffing | 4 | Hidden State | Structured | Until elim. | SR, DC, TM |
| 13 | Sheriff of Nottingham | Bluffing | 4 | Hidden State | Free-form | 4 rounds | SR, NG, DC, PS |
| 14 | Chameleon | Deduction | 5 | Hidden Roles | Free-form | 1 round | DC, PS, TM |
| 15 | Insider | Deduction | 5 | Hidden Roles | Free-form | 1 round | CO, DC, TM |
| 16 | Spyfall | Deduction | 4 | Hidden Roles | Free-form | Multi-round | DC, PS, TM |
| 17 | Undercover | Deduction | 6 | Hidden Roles | Free-form | Multi-round | DC, PS, TM |
| 18 | Resistance | Deduction | 5 | Hidden Roles | Free-form | 5 missions | SR, DC, PS, TM |
| 19 | Werewolves | Deduction | 6 | Hidden Roles | Free-form | Multi-round | SR, DC, PS, TM |
| 20 | Survivor | Social Strategy | 6 | Complete | Free-form | Until 2-3 left | NG, PS, TM |
| 21 | Dead Last | Social Strategy | 6 | Complete | Free-form | Until 2-3 left | NG, PS, TM |

## Definitions

| Term | Definition | Comment |
|------|-----------|---------|
| **Categories** | | |
| Normal-Form | Simultaneous-choice games where players select actions independently from a fixed set, with outcomes determined by a payoff matrix. | Classic game theory settings (PD, Chicken, etc.). No language involved — isolates pure strategic reasoning. |
| Economic | Games involving resource allocation, sequential trust decisions, or explicit proposal-response negotiation. | Extends beyond matrix selection to multi-step reasoning about offers, contributions, and patience. |
| Bluffing | Games where players hold hidden private state (cards, dice, goods) and must strategically misrepresent or detect misrepresentation. | Tests whether agents can maintain lies and read opponents — a different skill from choosing between cooperate/defect. |
| Deduction | Team-based games with hidden role assignments, where one side must identify the other through discussion and behavioral signals. | Requires integrating linguistic cues, voting patterns, and action history to infer hidden identities. |
| Social Strategy | Open-information games with no hidden roles or private state, where outcomes are determined entirely by social dynamics (alliances, persuasion, voting). | The hardest to "solve" analytically — success depends on social influence, not information advantage. |
| **Properties** | | |
| Complete (Info) | All players observe the same game state; no private information. | Applies to Normal-Form and Social Strategy games. Strategic challenge comes from predicting others' choices, not from hidden state. |
| Hidden State (Info) | Players hold private information about their own game state (e.g., dice values, cards, packed goods). | Applies to Economic (Public Goods) and Bluffing games. Enables bluffing and probabilistic reasoning. |
| Hidden Roles (Info) | Players are secretly assigned to teams or roles unknown to others. | Applies to Deduction games. Creates asymmetric knowledge about who is on which side. |
| None (Comm.) | No free-text communication between players; actions only. | All Normal-Form games. Eliminates language as a variable. |
| Structured (Comm.) | Communication follows a fixed protocol (e.g., propose/accept, bid/challenge). | Bargaining, Liar's Dice, Coup. Language is constrained to game-specific speech acts. |
| Free-form (Comm.) | Players can say anything in natural language during discussion phases. | Deduction and Social Strategy games. Tests persuasion, deception, and argument quality. |
| **Skills** | | |
| Strategic Reasoning (SR) | Computing optimal actions given game rules, payoff structure, and opponent behavior. | Present in most games. In Normal-Form games, this is the *only* skill tested. |
| Cooperation (CO) | Choosing collectively beneficial actions despite individual incentive to defect. | Relevant when mutual cooperation yields higher payoffs but is individually risky (PD, Stag Hunt, Public Goods). |
| Coordination (CD) | Predicting others' choices to achieve compatible action profiles, without communication. | Relevant in games with multiple equilibria (BoS) or where being in the minority/majority matters (Chicken, Minority). |
| Negotiation (NG) | Making proposals, evaluating offers, and reaching mutually acceptable agreements. | Requires balancing greed against the risk of rejection or retaliation (Bargaining, Sheriff, Survivor). |
| Deception (DC) | Deliberately misrepresenting private information or role identity to gain advantage. | Core to Bluffing and Deduction games. Distinct from SR — you must maintain a false narrative, not just pick the right action. |
| Persuasion (PS) | Convincing other players to adopt a particular belief or action through natural language argument. | Requires free-form communication. Distinct from Deception — you can persuade truthfully (e.g., convincing others to vote out the real spy). |
| Theory of Mind (TM) | Modeling what other players know, believe, or intend — reasoning about their mental states, not just their likely actions. | Reserved for games with hidden information where you must reason about others' *knowledge states* (e.g., "does she know I'm the spy?"), not just predict behavior. |
| Probabilistic Reasoning (PR) | Computing likelihoods of hidden states from partial observations and game history. | Primarily Liar's Dice (inferring dice distributions from bids). A narrower skill than TM. |
