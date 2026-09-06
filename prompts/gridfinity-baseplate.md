# Prompt — Gridfinity baseplate

Feed this to `/model`.

---

Design a parametric **Gridfinity baseplate** as
`models/gridfinity-baseplate/model.py`, built with `build.py`. Use
`lib/gridfinity.py`; read `docs/design-rules.md` (Gridfinity section).

## Intent

The basic Gridfinity baseplate — `nx × ny` cells of the 42 mm mating profile, no
weighted skeleton. Bins drop into it.

## Parameters (`P` dataclass)

| name | default | meaning |
|---|---|---|
| `nx` / `ny` | `3` / `2` | cells (42 mm) |
| `magnets` | `False` | Ø6.5 × 2.4 pockets, 13 mm off each cell centre |
| `screws` | `False` | Ø3 × 6 pilot holes at the same points (bolt-down) |

## Geometry

- Just `return gridfinity.base_plate(nx, ny, magnets=magnets, screws=screws)`.
- Top face at z = `BASE_H` (4.75 mm). Origin centred.
- Add `CHECKS = {"min_wall": False}` — the basic baseplate is thin at the cell
  mouths by design and the heuristic would only cry wolf.

## Print

- Flat, no supports. PLA, layer 0.20.

## Deliverables

1. `models/gridfinity-baseplate/model.py`
2. `models/gridfinity-baseplate/README.md` — params, the "glue it down / bolt it
   down" note, licence.
3. Build it; `pytest` green.
