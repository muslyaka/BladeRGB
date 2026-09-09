def palette_cycle_position(elapsed, color_count, hold_time, transition_time):
    """Return (current_index, next_index, blend) for a palette cycle.

    The current color is held for hold_time seconds, then crossfaded to the
    next color over transition_time seconds. blend is smoothstepped 0..1.
    """
    count = max(1, int(color_count))
    if count == 1:
        return 0, 0, 0.0

    hold = max(0.0, float(hold_time))
    transition = max(0.001, float(transition_time))
    elapsed = max(0.0, float(elapsed))
    segment = hold + transition

    step = int(elapsed // segment)
    local = elapsed - step * segment
    current = step % count
    following = (current + 1) % count

    if local <= hold:
        blend = 0.0
    else:
        blend = min(1.0, (local - hold) / transition)
        blend = blend * blend * (3.0 - 2.0 * blend)

    return current, following, blend


def palette_clock_active(params):
    try:
        return float(params.get("palette_delay", 0.0)) > 0.0
    except Exception:
        return False


def automatic_palette_phase(value, params):
    """Disable an effect's own continuous palette drift when hold timing is on."""
    return 0.0 if palette_clock_active(params) else float(value)
