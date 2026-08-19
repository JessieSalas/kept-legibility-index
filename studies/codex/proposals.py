"""Capital-O skeleton proposals for OCR legibility experiments."""

import math


_OUTER_BOX = (54.0, 738.0, -12.0, 712.0)
_TAU = 2.0 * math.pi
_SAMPLES = 192


def _signed_power(value, exponent):
    """Return sign(value) * abs(value) ** exponent."""
    return math.copysign(abs(value) ** exponent, value)


def _normalise(points, box):
    """Map a point cloud independently onto an exact rectangular extent."""
    x_min, x_max, y_min, y_max = box
    source_x_min = min(x for x, _ in points)
    source_x_max = max(x for x, _ in points)
    source_y_min = min(y for _, y in points)
    source_y_max = max(y for _, y in points)
    x_scale = (x_max - x_min) / (source_x_max - source_x_min)
    y_scale = (y_max - y_min) / (source_y_max - source_y_min)
    return [
        (
            x_min + (x - source_x_min) * x_scale,
            y_min + (y - source_y_min) * y_scale,
        )
        for x, y in points
    ]


def _loop(box, exponent=0.60, warp=None, clockwise=False):
    """Sample and normalise a warped superellipse."""
    points = []
    for index in range(_SAMPLES):
        angle = _TAU * index / _SAMPLES
        x = _signed_power(math.cos(angle), exponent)
        y = _signed_power(math.sin(angle), exponent)
        if warp is not None:
            x, y = warp(x, y, angle)
        points.append((x, y))
    points = _normalise(points, box)
    if clockwise:
        points.reverse()
    return points


def diagonal_balance():
    """Opposed diagonal bulges break both zero axes while avoiding D's continuous left stem."""

    def outer_warp(x, y, angle):
        return x + 0.105 * y * (1.0 - x * x), y + 0.025 * math.sin(2.0 * angle)

    def inner_warp(x, y, angle):
        return x - 0.070 * y * (1.0 - x * x), y - 0.018 * math.sin(2.0 * angle)

    outer = _loop(_OUTER_BOX, exponent=0.61, warp=outer_warp)
    inner = _loop((139.0, 653.0, 65.0, 635.0), exponent=0.64,
                  warp=inner_warp, clockwise=True)
    return [outer, inner]


def offset_counter():
    """A left-high counter makes unequal side weights unlike 0, while the fully bowed left edge rejects D."""

    def outer_warp(x, y, angle):
        return x + 0.020 * y * (1.0 - x * x), y

    def inner_warp(x, y, angle):
        return x + 0.045 * (1.0 - x * x) + 0.035 * y, y + 0.035 * (1.0 - y * y)

    outer = _loop(_OUTER_BOX, exponent=0.67, warp=outer_warp)
    inner = _loop((128.0, 661.0, 75.0, 646.0), exponent=0.70,
                  warp=inner_warp, clockwise=True)
    return [outer, inner]


def diagonal_corners():
    """Square upper-left and lower-right corners oppose each other, defeating 0 symmetry without forming a D stem."""

    def corner_warp(x, y, angle):
        diagonal = -x * y
        strength = 1.0 + 0.105 * diagonal
        return x * strength, y * strength

    def counter_warp(x, y, angle):
        diagonal = -x * y
        strength = 1.0 + 0.055 * diagonal
        return x * strength, y * strength

    outer = _loop(_OUTER_BOX, exponent=0.50, warp=corner_warp)
    inner = _loop((139.0, 653.0, 65.0, 635.0), exponent=0.66,
                  warp=counter_warp, clockwise=True)
    return [outer, inner]


def high_shoulder():
    """One elevated right shoulder breaks horizontal and vertical symmetry while keeping both sides curved unlike D."""

    def outer_warp(x, y, angle):
        shoulder = 0.085 * max(x, 0.0) * (1.0 - y * y)
        return x, y + shoulder - 0.025 * min(x, 0.0) * (1.0 - y * y)

    def inner_warp(x, y, angle):
        shoulder = 0.045 * max(x, 0.0) * (1.0 - y * y)
        return x, y + shoulder

    outer = _loop(_OUTER_BOX, exponent=0.59, warp=outer_warp)
    inner = _loop((139.0, 653.0, 65.0, 635.0), exponent=0.64,
                  warp=inner_warp, clockwise=True)
    return [outer, inner]


def pinched_quadrant():
    """A local upper-right pinch supplies a nonzero landmark without the straight left boundary that cues D."""

    def outer_warp(x, y, angle):
        pinch = max(x, 0.0) * max(y, 0.0)
        scale = 1.0 - 0.115 * pinch
        return x * scale - 0.020 * pinch, y * scale

    def inner_warp(x, y, angle):
        pinch = max(x, 0.0) * max(y, 0.0)
        scale = 1.0 - 0.055 * pinch
        return x * scale, y * scale

    outer = _loop(_OUTER_BOX, exponent=0.56, warp=outer_warp)
    inner = _loop((139.0, 653.0, 65.0, 635.0), exponent=0.65,
                  warp=inner_warp, clockwise=True)
    return [outer, inner]


VARIANTS = {
    "diagonal_balance": diagonal_balance,
    "offset_counter": offset_counter,
    "diagonal_corners": diagonal_corners,
    "high_shoulder": high_shoulder,
    "pinched_quadrant": pinched_quadrant,
}
