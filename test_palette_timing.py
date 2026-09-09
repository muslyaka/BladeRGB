from engine.palette_timing import (
    automatic_palette_phase,
    palette_cycle_position,
)


def close(a, b, eps=1e-6):
    assert abs(a - b) <= eps, (a, b)


# 2s hold + 1s transition.
i, n, blend = palette_cycle_position(0.0, 3, 2.0, 1.0)
assert (i, n) == (0, 1)
close(blend, 0.0)

i, n, blend = palette_cycle_position(1.999, 3, 2.0, 1.0)
assert (i, n) == (0, 1)
close(blend, 0.0)

i, n, blend = palette_cycle_position(2.5, 3, 2.0, 1.0)
assert (i, n) == (0, 1)
close(blend, 0.5)

i, n, blend = palette_cycle_position(3.0, 3, 2.0, 1.0)
assert (i, n) == (1, 2)
close(blend, 0.0)

i, n, blend = palette_cycle_position(6.0, 3, 2.0, 1.0)
assert (i, n) == (2, 0)
close(blend, 0.0)

# An enabled palette hold disables a second, effect-local color clock.
assert automatic_palette_phase(12.5, {"palette_delay": 2.0}) == 0.0
assert automatic_palette_phase(12.5, {"palette_delay": 0.0}) == 12.5

print("palette timing tests: OK")
