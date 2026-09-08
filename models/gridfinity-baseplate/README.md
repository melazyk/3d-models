# Gridfinity baseplate

`nx × ny` cells of the standard 42 mm Gridfinity mating profile — the **basic**
baseplate (profile only, no weighted skeleton). Top face at z = 4.75 mm.
Default **3 × 2** → 126 × 84 × 4.75 mm.

## Parameters

`nx` / `ny` cells · `magnets` (Ø6.5 × 2.4 pockets) · `screws` (Ø3 × 6 pilot holes),
both 13 mm off each cell centre for bolting the plate down.

```
python build.py models/gridfinity-baseplate
```

## Print

- Flat on the plate, no supports. Layer 0.20, PLA.
- The basic baseplate is thin at the cell mouths and not very rigid — glue it to a
  backing board, or add `screws=True` and bolt it down. `CHECKS = {"min_wall": False}`
  in the model silences the (expected) thin-wall warning.

## Licence

Gridfinity spec by Zack Freedman, CC BY 4.0. Parametric implementation is our own
(`lib/gridfinity.py`).
