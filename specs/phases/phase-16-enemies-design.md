# Phase 16 — Enemies Design

> Fill the **Human** sections. Set **Status** to `Ready` when the agent may implement it.
> The agent fills the **Agent** sections and never edits the requirement sections.

**Status:** Ready  <!-- Draft | Ready -->
**Depends on:** Phase 15 (and the enemies of Phase 5, the bosses of Phases 7–10, the readability rules of Phase 14)

---

## 🧑 Goal
Every enemy and every boss gets a new **Cyber-Organic** look: bodies that read as living tissue fused with machinery (carapaces, ribs, veins, sinews, glowing organs, plated over by metal). Most keep their wings and reactors. Only the look changes: behaviour, hitboxes, shooting and balance stay the same.

## 🧑 Requirements

> ID format `P16-Rxx`. Every requirement is **MUST** (no SHOULD / MAY).

### P16-R01 — Cyber-Organic style guide  · MUST
Write down the shared visual language before reworking the models, as a section of the implementation report (and a reusable kit in code, see R02). It covers:
- **Organic body**: rounded, asymmetric-but-balanced shapes (pods, segmented abdomens, carapace shells, ribcages, skull-like heads, tendrils, mandibles) instead of boxes and plain wedges.
- **Cyber parts**: metal plates, rivets, armour bands, ports, pipes and cables grafted onto the body, clearly man-made against the organic shapes.
- **Wings**: membranes or insect-like wings stretched on metal struts, or metal wings with organic roots. Kinds that had wings keep them.
- **Reactors**: kept, read as glowing organs (bulbs, sacs, vents) fused into the body, still at the back.
- **Lights**: neon veins, eyes and glowing glands replace plain neon strips.
- **Palette**: still dark metallic with neon lights (GD-61), within the enemy colour family and reserved colours of P14-R02 / P14-R04. Organic parts in dark flesh tones (deep crimson, purple, dark teal) that stay dark enough to keep the enemy vs. background contrast of P14.

**Acceptance criteria**
- [ ] The style guide is in the report and every reworked model follows it.

### P16-R02 — Engine-agnostic shape kit  · MUST
The organic shapes come from reusable builders (e.g. segmented body, carapace, rib, tendril, membrane wing, organ bulb, vein light, armour plate graft). Generic builders live outside `src/game/` (01-engineering §2.3); the concrete enemy/boss models stay in `src/game/`.

**Acceptance criteria**
- [ ] Builders have unit tests (vertex counts, bounds, determinism for the same seed).
- [ ] No code outside `src/game/` names a concrete enemy or boss.

### P16-R03 — Basic enemies reworked  · MUST
The 11 basic kinds (Gnat, Hornet, Scout, Strafer, Weaver, Spinner, Lancer, Rocketeer, Bulwark, Splitter, Carrier) get Cyber-Organic models. Each kind keeps a silhouette that tells it apart from the others and matches its role (e.g. Gnat a small insect drone, Hornet a stinger diver, Bulwark a heavy armoured beetle, Carrier a brood sac that releases Gnats, Splitter a body visibly made of the parts it splits into).

**Acceptance criteria**
- [ ] Each kind is recognisable at gameplay size, in a side-by-side view on the `enemies/` debug page.
- [ ] Wings and reactors kept on every kind that had them.

### P16-R04 — Veteran and elite enemies reworked  · MUST
The veteran and elite kinds (Wasp, Mortar, Mantis, Phantom, Minelayer, Hydra, Orbiter, Scissor, Juggernaut, Hive) get Cyber-Organic models. Their moving parts (P05-R13) become organic limbs: Mantis scythes, Hydra necks, Scissor blades, Orbiter drones, Juggernaut armour still move as before. Elites look more armoured and more complex than veterans, veterans more than basic kinds.

**Acceptance criteria**
- [ ] Moving parts still animate and stay where the gameplay expects them (lasers, shots and hitboxes come from the same points).
- [ ] The tier (basic / veteran / elite) is readable from the look.

### P16-R05 — Mini bosses reworked  · MUST
Every mini boss of Worlds 1–4 gets a Cyber-Organic model. Each destroyable part (P07-R01) is an organ, limb or armoured growth with a clear outline, so the player sees what to shoot.

**Acceptance criteria**
- [ ] Each part keeps its position, size and hitbox.
- [ ] A destroyed part leaves a visible wound/stump (torn plating, dimmed organ), not a hole in the model.

### P16-R06 — Final bosses reworked  · MUST
Every final boss of Worlds 1–4 gets a Cyber-Organic model, larger and more detailed than mini bosses: a living biomechanical mothership/creature, with the world's theme still recognisable (e.g. a coastal boss feels marine, a metropolis boss feels like a city-sized organism). Same rules for parts and wounds as R05.

**Acceptance criteria**
- [ ] Each final boss keeps its parts, their order, hitboxes and patterns.
- [ ] The boss reads as one creature, not parts stuck on a box.

### P16-R07 — Living motion  · MUST
Bodies feel alive with light, cheap animation: slow breathing (scale pulse), pulsing vein/organ glow, wing flutter or membrane ripple, tendril sway. Animation is visual only and does not move hitboxes.

**Acceptance criteria**
- [ ] Animation runs from the sim time, so pause freezes it.
- [ ] Hitboxes and shot origins are identical with and without animation (test).

### P16-R08 — Gameplay and readability unchanged  · MUST
The rework is visual only. Hitboxes (GD-21: visual equivalent hitbox), speeds, paths, HP, patterns, scores and spawns don't change. The Phase 14 readability rules still pass: enemies stand out from the ground, enemy bullets stay the most visible thing, reserved colours unused by bodies.

**Acceptance criteria**
- [ ] The readability check of the test API (P14-R08) passes in every world.
- [ ] Each model's footprint matches its hitbox within the tolerance below.
- [ ] Existing gameplay unit tests and e2e pass without changing their expected values.

### P16-R09 — Performance kept  · MUST
The new models must not bring back the long frames fixed in Phase 13. Triangle budgets per tier below; models are built once and shared (prebuilt models, P13).

**Acceptance criteria**
- [ ] Each model is within its triangle budget (unit test).
- [ ] The perf monitor shows no more long sim frames than before on the busiest wave and on each final boss.

### P16-R10 — Debug pages show the new look  · MUST
The `enemies/` and `bosses/` debug pages show the new models, with a toggle to pause/run the living motion and to show the hitbox over the model.

**Acceptance criteria**
- [ ] Every enemy kind and every boss can be viewed and its parts destroyed one by one on the debug pages.

## 🧑 Tunable values
| Name | Value | Notes |
|------|-------|-------|
| tri_budget_basic | 400 | triangles per basic enemy |
| tri_budget_veteran | 700 | |
| tri_budget_elite | 1200 | |
| tri_budget_mini_boss | 4000 | |
| tri_budget_final_boss | 10000 | |
| breathing_amplitude | 3 % | body scale pulse |
| breathing_period | 2.5 s | randomised ±20 % per enemy |
| glow_pulse_period | 1.2 s | veins and organs |
| wing_flutter_freq | 6 Hz | small kinds; slower for big ones |
| hitbox_footprint_tolerance | 15 % | model footprint vs hitbox |

## 🧑 Out of scope for this phase
- New enemy kinds, new bosses, new attacks or boss parts.
- Any balance change (HP, speed, patterns, scores, spawns).
- Player ship, player shots, enemy bullets, levels, backgrounds, HUD, music.
- Death/explosion effects beyond the wound on destroyed parts.

## 🧑 Engineering additions for this phase
- Unit tests per model: triangle budget, footprint vs hitbox, deterministic build.
- An e2e test that opens `enemies/` and `bosses/` and checks every model renders without console errors.

## 🧑 Manual validation checklist
- [ ] Runs on GitHub Pages / `make dev` without console errors
- [ ] On `enemies/`: every kind looks Cyber-Organic, kinds are told apart at a glance, tiers are readable
- [ ] On `bosses/`: every boss reads as one creature; destroying parts leaves wounds
- [ ] In a level of each world: enemies stand out, bullets stay readable, no slowdown
- [ ] Living motion is subtle, freezes on pause

## 🧑 Notes, references, sketches
- Mood: biomechanical / insectoid; living hulls with metal grafted on; glowing organs as engines.
- Keep GD-61 (dark metallic, neon lights): the organic part is in the shapes and the dark flesh tones, the neon stays.

---

## 🧑 Review feedback
> After the agent reports, write corrections here, then say **"Fix phase 16"**.
> The agent ticks each item when fixed.

- [ ] 

---

## 🤖 Implementation report
> Filled by the agent. Do not edit (comment in Review feedback instead).

### Questions / blockers
None.

### Style guide (P16-R01)
Shared by every enemy and boss model. Builders: `src/render/geometry/organic.ts` (shapes),
`EnemyParts` in `src/game/view/enemies/enemy-mesh.ts` (materials and motion).

- **Two materials for the body.** `flesh` is the living body: a waxy, barely metallic material
  (`ENEMY_LOOK.flesh`: metallic 0.25, roughness 0.5) in dark flesh shades: `crimson`, `purple`,
  `teal`, `sinew`, `bone`, `membrane`. `hull` is the cyber part: the dark metal of before
  (`ENEMY_LOOK.hull` shades), only for what is grafted on: armour plates, rivets, bands, barrels,
  ports, pipes, reactor nozzles. Every shade stays under 0.2 so enemies keep their contrast with
  the darkened ground (P14-R04); both materials get the enemy rim.
- **Organic body.** Swollen, rounded shapes instead of boxes and plain wedges:
  `segmentedBody` (abdomens and thoraxes of swollen segments, `ROUND_SECTION`), `carapace`
  (ridged shells with darker seams between plates), `organ` (bulbs, sacs, heads), `ribs`
  (arches over a back), `tendril` / `curve` (tentacles, mandibles, sinews, necks), `grown`
  (uneven outlines). Balanced left and right, uneven in the details.
- **Cyber parts.** `plate` (bevelled armour with rivets) and the existing hull solids, on top of
  the flesh, reading as man-made: straight edges, metal shades. A model is mostly flesh, with
  metal on its nose, guns, joints and reactors.
- **Wings.** Kinds that had wings keep them: `membraneWing` (a `membrane` skin stretched between
  `bone` struts, from the root out to each tip), or a metal wing with a flesh root. Drawn with
  `parts.flap(pivot, side, span, draw)` they flutter (P16-R07); big, heavy wings may stay still.
- **Reactors.** Kept, at the back, as before (`parts.reactor`), set in a glowing organ: a flesh
  sac or bulb around the nozzle, a vein running from it into the body.
- **Lights.** `parts.vein` (pulsing, P16-R07) for veins, eyes and glands drawn with `vein` /
  `organ`; `parts.neon` for steady lights; `parts.charge` for what brightens as an attack
  charges. Lights stay the kind's neon colour, folded into the enemy family (P14-R02).
- **Tiers.** Basic kinds: one body, a few grafts. Veterans: more armour plates, more limbs.
  Elites: heavily armoured, plated shells, more organs and veins. Bosses: one creature, its
  destroyable parts organs, limbs or armoured growths with a clear outline; a destroyed part
  leaves a wound (torn flesh, dimmed organ, ribs and shards).
- **Gameplay unchanged (P16-R08).** Same footprint (within 15 % of the spec size, the existing
  size tests), same muzzles (the existing muzzle tests), flat (height under half the length).
- **Budgets (P16-R09).** Triangles per model: basic 400, veteran 700, elite 1200, mini boss
  4000, final boss 10000 (`ENEMY_LOOK.budget`).

### Plan
| Task | Requirement IDs |
|------|-----------------|
| | |

### Requirement traceability
| ID | Status (Done / Partial / Not done) | Code | Tests | Notes |
|----|-----------------------------------|------|-------|-------|
| P16-R01 | | | | |

### Gate results
```
make check output summary: lint ✔ / typecheck ✔ / tests N passed / coverage xx% / build ✔
```

### How to test manually
<!-- Steps, keys, debug toggles, URL. -->

### Deviations from spec
<!-- Anything done differently and why. Also logged in DECISIONS.md. -->

### Known limitations
-

### Suggestions for future phases
-
