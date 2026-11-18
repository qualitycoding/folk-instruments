# Human gates

At a gate the implementer halts, writes the gate record from the template in `HANDOFF.md`, commits and pushes it, and reports its path and questions in chat. Only an allowed response counts. Silence is never a response. Sign-off at one gate never covers another gate, and sign-off for one round never covers the next.

| Gate | Opened by | Kind | Round limit |
|---|---|---|---|
| G-P1 | S-210 | pilot listening, harmonica (demos only) | 2 |
| G-P2 | S-250 | pilot listening, mandolin (demos only) | 2 |
| G-L1 to G-L5 | S-LISTEN | listening validation, one per instrument | 3 each |
| G-002 | any step that would release or publish | external or irreversible action | no limit |
| G-003 | S-KNOW | lesson and knowledge stores | no limit |
| G-004 | S-REVIEW, S-ADVERSARIAL or S-REVIEW-DELTA, only when a Critical or High finding is not fixed | acceptance of a review finding | no limit |

Gates not required: `G-001` (profiles `math` and `computational` are inactive); `G-INT` (the integration route is `pull-request`: the owner merges the pull request, which is the owner's own action).

---

## G-P1 and G-P2: pilot listening

Purpose: an early check by the owner's ear, before the second and third instruments of a family are built on the same core (A-003). Demos only; no blind pairs; no pass score.

- **Trigger.** G-P1: `S-210` after its tests pass. G-P2: `S-250` after its tests pass.
- **Blocks.** G-P1 blocks `S-220` and `S-230`. G-P2 blocks `S-260`.
- **Continues meanwhile.** G-P1: `S-212`, `S-101`, `S-240`, `S-250`, `S-REF`. G-P2: `S-200` to `S-230` (subject to G-P1), `S-REF`.
- **Evidence bundle.** The rendered demo files named in the step's gate actions, on the evidence branch `evidence/G-P1` or `evidence/G-P2` (built by pushing a commit with the marker `[gate-evidence G-P1 harmonica seed=1]` or `[gate-evidence G-P2 mandolin seed=1]`; no pairs are built for a pilot gate); the list of frozen tests that pass for the instrument; the real-time factor printed by `folk-perf` for the instrument.
- **Questions.**
  1. Does this sound like the instrument? If not, what is wrong, in your own words (for example: too clean, too bright, synthetic attack, wrong pitch, lifeless sustain)?
  2. Which demo is the weakest?
  3. May the remaining instruments of this family be built on this sound engine as it is?
- **Allowed responses.** `proceed`; `iterate: <notes>`; `proceed-with-rescope: <text>`; `stop`.
- **Branches.** `proceed`: continue. `iterate: <notes>`: apply the iterate procedure of `HANDOFF.md` to this instrument (analysis chosen from the listener's words, one general change per difference, all frozen tests re-run), render the same demos again, open round 2; after round 2 only `proceed`, `proceed-with-rescope`, `stop` or `override-round-limit: <reason>` are accepted. `proceed-with-rescope: <text>`: copy the text into `DEVIATIONS.md`, apply it if it is a reduction of scope (for example dropping a variant), and continue; if the text asks for something that changes a public interface or a frozen test, write `BLOCKED.md` instead. `stop`: rule DR-15: halt and write `BLOCKED.md` (the instruments not yet built would leave frozen tests unpassable, so the plan must be amended first).

## G-L1 to G-L5: listening validation

G-L1 harmonica, G-L2 mandolin, G-L3 accordion, G-L4 melodion, G-L5 bouzouki.

- **Trigger.** `S-LISTEN`; a closed gate is reopened for a confirmation round (D-053) when shared sound code changes after its evidence commit.
- **Blocks.** `S-INTEGRATE` (all five must be answered).
- **Continues meanwhile.** The other listening gates.
- **Evidence bundle.** The evidence branch `evidence/<gate id>` built by the `gate-evidence` workflow (demos as WAV, `MANIFEST.json`, `SHA256SUMS`, `ATTRIBUTION.md`, `METRICS.md`, and blind pairs when every reference is redistributable); for an instrument whose pairs use a private reference, the pairs delivered privately by the delivery rule and their hashes (`PAIRS-SHA256SUMS`) in the gate record; the statement of how many references are redistributable and how many private; the frozen pass condition; any reference test that failed in `S-330`.
- **Reference set and pass condition (frozen).**

| Gate | References at planning time | Blind pairs | Pass condition |
|---|---|---|---|
| G-L3 accordion | TinySOL 6.0, 12 mf notes (MIDI 48, 52, 55, 59, 62, 65, 69, 72, 76, 79, 83, 86), CC BY 4.0, redistributable | 12, cut from the start of each note | at most 8 of 12 picked correctly, and no demo reported as wrong |
| G-L2 mandolin | Philharmonia mandolin notes, private reference (D-051), if `S-REF` indexed 12 or more | 12, cut from the start, delivered privately | the same |
| G-L1 harmonica, G-L4 melodion, G-L5 bouzouki | none with 12 notes at planning time; whatever `S-REF` indexed | 12 if `S-REF` indexed 12 or more notes of the instrument, otherwise none | with pairs: the same; without pairs: no demo reported as wrong |

  The pass condition is necessary, not sufficient: the listener's remarks on the demos count alongside the score. Two of the 14 pairs are controls (D-053); a round with a missed control, or with one letter given for 10 or more of the 14 pairs where the key has fewer than 10 of that letter, is void and repeated with a new seed (D-053 gives the seeds, record names and the owner's choices after two void attempts), and does not count towards the round limit. A gate without pairs rests on the listener's remarks alone; its record says so.
- **Questions.**
  1. (Only if pairs were delivered.) For each of the 14 pairs, which side is the real instrument? Answer with 14 letters in order, for example `ABBABAABABBAAB`. Play each pair once, A then B, on your own headphones.
  2. Do the demos sound like the instrument? End your answer with a line `wrong: <demo names>` or `wrong: none`; that line alone decides 'no demo reported as wrong'.
  3. Per instrument: harmonica: do the bends (`-08-bend`, `-10-chromatic-on-diatonic`) sound like a player bending? Mandolin and bouzouki: does the tremolo (`-07-tremolo`) sound like picking, and do the variants differ as you expect? Accordion: do the registers and the musette (`-2xx-variant`) sound right, and does the cassotto setting sound warmer rather than just duller? Melodion: do chords under a limited breath (`-11-chords-limited-breath`) sag believably, and does the limited-breath variant (`-204-variant`) still sound right on single notes?
  4. (G-L1 only, once for all five plugins.) Install the plugins from the CI artifact named in the record, load one in your usual host, and play it: do the pitch wheel and a breath controller (CC 2 or CC 11) act, does a factory preset load, and does a saved session reopen with the same sound? (R-019, R-018.) A defect reported here is handled as `iterate: <the report>` for the plugin concerned: it is fixed, the frozen suite re-run, and the question asked again in the next round of G-L1.
- **Allowed responses.** `proceed`; `iterate: <notes>`; `proceed-with-rescope: <text>`; `stop`; `override-round-limit: <reason>` (only to allow a round beyond the third); and, only after two void attempts in one round (D-053), `repeat` or `proceed-without-pairs: <text>`; in a confirmation round (D-053), `confirm-again` or `stop` when a third confirmation round would start, otherwise `confirm` (closes the gate again, valid only if the pass condition holds where pairs exist) or `iterate: <notes>` (opens the next normal round, counted towards the limit).
- **Branches.** `proceed`: only valid if the pass condition is met and no reference test of the instrument was recorded as failed in `S-330` (in that case ask once whether `iterate`, `proceed-with-rescope` naming the shortfall, or `stop` is meant; rule DR-16); if pairs were judged and more than 8 were correct, tell the owner the score and ask once whether `iterate`, `proceed-with-rescope` or `stop` is meant. `iterate: <notes>`: rule DR-12; new evidence with a new seed; next round. After round 3: only `proceed` (if the condition is met), `proceed-with-rescope`, `stop` or `override-round-limit`. `proceed-with-rescope: <text>`: the text names the accepted shortfall; copy it into `DEVIATIONS.md` and the retrospective; continue. `repeat`: another attempt with the next seed. `proceed-without-pairs: <text>`: the gate is judged on the remarks alone; the text is copied into `DEVIATIONS.md` as a rescope. `stop`: rule DR-15: the instrument stays built and tested; the answer is recorded in `DEVIATIONS.md` and `README.md`; the other instruments continue.

## G-002: external or irreversible action

This plan releases nothing (A-018, D-007), so no step opens this gate. It exists so that the rule has a place: if any step, deviation or request would create a tagged release, an installer, a package, an upload outside the repository, a change of repository visibility or settings, or a merge into `main`, the implementer halts first.

- **Trigger.** Before any such action.
- **Evidence bundle.** What would be published, where, under which licence; the CI run that built it; the licences of everything inside it; the count of redistributable and private references and confirmation that nothing derived from a private reference is included (`tools/evidence_guard.py` output).
- **Questions.** 1. May this be published as described? 2. Under which version number?
- **Allowed responses.** `publish: <version>`; `do-not-publish`.
- **Branches.** `publish`: perform exactly the described action, record it. `do-not-publish`: record it and continue without the action.

## G-004: acceptance of a Critical or High review finding

- **Trigger.** `S-REVIEW`, `S-ADVERSARIAL` or `S-REVIEW-DELTA` ends with a Critical or High finding that has no fix commit verified by the reviewer (R-025). The implementer never accepts such a finding.
- **Blocks.** Every later step.
- **Evidence bundle.** The finding as the reviewer wrote it, the attempted fixes, the failure path, and the options.
- **Question.** May this finding ship unfixed, and with what statement in `README.md`?
- **Allowed responses.** `accept: <statement>`; `fix: <direction>`; `stop`.
- **Branches.** `accept`: record the risk as accepted by the owner, copy the statement into `README.md` and `DEVIATIONS.md`, continue. `fix`: apply the direction and repeat the review of that finding. `stop`: halt with `BLOCKED.md`.

## G-003: lesson and knowledge stores

- **Trigger.** `S-KNOW`, the last step.
- **Blocks.** Only the pushes to the stores.
- **Evidence bundle.** `GATE-G-003.md` as described in `S-KNOW`.
- **Question.** May the lessons be pushed to `https://github.com/qualitycoding/Lessons` and the knowledge items to `https://github.com/qualitycoding/knowledge`?
- **Allowed responses.** `push-to-proposed`; `push-to: <lesson-target> [knowledge-target]`; `do-not-push`.
- **Branches.** As in `S-KNOW`. If no response arrives, the bundle fallback of `S-KNOW` is written and reported; writing a bundle is not a push.
