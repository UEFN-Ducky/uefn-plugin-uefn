---
description: "Physics Beta FAQ — existing projects, Sequencer, movement, weapons, vehicles, object budget, Creative"
metadata:
  order: 40
  label: "FAQ and limits"
  default_enabled: false
  load_condition: "Physics performance, vehicles, Sequencer, weapons, movement modes, or Creative support questions"
---

# Physics FAQ and limits

## Existing projects

Yes — enable Physics on an existing project. **Copy the project first.** You can
disable Physics later and publish without the experimental feature if needed.
Publishing with Physics Beta is allowed, but expect frequent tool changes.

## Sequencer

**No.** Sequenced objects run on the game thread, not the physics thread — they
do not interact correctly with simulated props. Use **Prop Mover** for motion that
must collide with physics objects.

## Player movement

Works: walk, run, sprint, sprint jump, jump, fall, swim, crouch, crouch walk,
crouch jump, glide, skydive.

**Not available** with physics: mantling, sliding, ziplines, grind rails, DBNO.

## Weapons

Most weapons work with Physics Beta. Expect coverage to grow; test critical
weapons in PIE.

## Vehicles

**Unsupported.** Vehicles create instability. Do not use on physics islands.

## Object budget

Monitor simulated object count. Exceeding ~**50 simple** shapes (boxes/spheres)
can hurt performance. Complex collision costs more. Environment complexity also
matters — profile on target platforms.

## Fortnite Creative

Physics is **UEFN only** at this time — not available in Creative.

## Brand templates

Physics is **not supported** for brand templates. Use Blank or a non-brand island.

## Agent defaults when unsure

- Prefer simple collision + fewer bodies over complex mesh collision.
- Prefer Prop Mover over Sequencer for moving platforms that hit physics props.
- Prefer Volume + Verse PropEnterEvent for goal/trigger detection over polling.
