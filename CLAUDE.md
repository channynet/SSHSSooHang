# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

**세렝게티의 눈물** — a 2D savanna ecosystem simulation in Python (`pygame-ce` for rendering).
Animals live on a tile grid (water / land / plant), eat, drink, hunt, breed, and die. The
simulation ends when **any species goes extinct** (먹이사슬 붕괴 / food-chain collapse). README,
the design doc (`*.docx`), and in-sim messages are in Korean.

## Setup & Run

```
python -m venv .venv
.venv/Scripts/activate          # Windows (README); use .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
python main.py
```

- **No display? It still runs.** `ui.py` falls back to a headless console mode if `pygame`
  can't be imported — it prints a per-second species-count summary and exits on collapse.
- There is no test suite or linter config. The standard way to verify a change is a headless
  smoke run, e.g.:
  ```
  python3 -c "import setup; e=setup.build_env(seed=1)
  while not e.collapsed and e.elapsed<300: e.update(16)
  print(e.elapsed, e.collapse_reason, e.species_counts())"
  ```
  `build_env(seed=...)` makes runs deterministic.

## Architecture

**Hybrid Entity/Behavior pattern.** Animals hold state + low-level actions; *decisions* about
when to act are separate `Behavior` objects evaluated each frame.

- `main.py` — loop: `env.update(MS_PER_FRAME)` → `ui.draw(env)` until `ui.draw` returns False.
- `env.py` — `Env` owns the tile grid, animal list, dead bodies, and weather. `update(dt_ms)`
  is the per-frame tick (order matters): weather/plants → each animal's `tick()` + **first
  passing behavior runs** → clean up the dead → decay corpses → check extinction. Exposes
  spatial helpers (`tile_at`, `animals_near`, `nearest_tile`, `nearest_dung_tile`,
  `nearest_dead_body`, `clamp`). `update` stashes the current `dt` on `env._dt` so behaviors
  can read it.
- `base.py` — abstract `Entity` (`behaviors()`) and `Behavior` (`determine(entity, env)` →
  `act(entity, env)`).
- `animal.py` — `Animal(Entity)` base: shared attributes (speed, body_water, fullness,
  stamina, detection_range, gender, ...) and low-level methods (`step_toward`/`step_away`,
  `drink`, `eat_plant`, `eat_prey`, `produce_dung`, `breed_with`, `on_capture_attempt`).
  `tick()` applies per-second decay and triggers death at 0 water/fullness. Subclasses set
  class-level defaults (species, color, base_speed, prey, predators, ...) and implement
  `build_behaviors()`.
- `behaviors.py` — generic behaviors reused across species: `ProduceDung`, `Flee`, `SeekWater`,
  `SeekPlantFood`, `Hunt`, `Breed`, `Wander`. Species-specific skills live in the species file.
- `geo.py` — `Point` / `Vector` value types with arithmetic.
- `tile.py`, `weather.py`, `dead_body.py` — environment pieces.
- `setup.py` — `build_env(seed)`: generates the grid (water ponds + plant patches) and the
  initial population (`POPULATION` dict). Genders alternate M/F so breeding pairs exist.
- `ui.py` — pygame renderer + headless fallback. `config.py` — all tunable constants.

### Behavior ordering is load-bearing

`build_behaviors()` returns behaviors in **priority order**; `env.update` runs only the *first*
one whose `determine()` is True. The established convention is:

```
ProduceDung → Flee → SeekWater (survival) → feeding (Hunt/SeekPlantFood/RollDung/Steal/...) → Breed → Wander
```

Putting a feeding or skill behavior *above* `SeekWater` is a bug: a well-fed-area animal will
never drink and dies of thirst at exactly `max_body_water / WATER_DECAY` seconds. If many
animals die simultaneously at a round time, suspect behavior-ordering, not the decay math.

### The 8 species (per the design doc's role split)

`elephant.py` `eagle.py` (김민찬D), `cheetah.py` `rabbit.py` (노민준),
`dung_beetle.py` `hyena.py` (박시은), `lion.py` `zebra.py` (윤준우). Each subclasses `Animal`
and adds its unique skill as a `Behavior` or an overridden hook:

- Skills as speed multipliers: override `hunt_speed_mult(target, env)` (cheetah sprint,
  hyena dash, eagle dive) — drain `stamina` there if the skill is stamina-gated.
- Evasion: override `on_capture_attempt(predator, env)` to return False to dodge (rabbit jump,
  zebra camouflage). `Hunt`/`Trample` call it before killing.
- Cross-species interactions live in the predator/actor's behavior (e.g. `StealFood`,
  `Scavenge` in `hyena.py`, `Trample` in `elephant.py`), keyed off `species` name strings in
  `prey`/`predators` tuples to avoid circular imports.

## Balance / tuning

All knobs are in `config.py` (decay rates, thresholds, breeding, skill costs) and `POPULATION`
in `setup.py`. The ecosystem is intentionally fragile; with the design-doc predator set, rabbit
(prey to 4 predators + trampled) is the usual first extinction. Adjusting populations/breeding
is expected "수치 세부조정" work, not a structural change.
