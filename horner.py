"""Horner correction for bottom-hole temperature (BHT).

Standalone illustration of the first correction path used in ResonAnza.
Written for this public repo; the production code is private.

Drilling mud cools the hole, so a temperature logged soon after circulation
stops reads low. With several readings at the same depth taken at different
shut-in times, plot BHT against the Horner time

    x = log10((t_circ + dt) / dt)

and fit a line. As dt grows, x goes to 0, so the intercept is the static
formation temperature.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Reading:
    bht_c: float  # measured bottom-hole temperature, °C
    t_circ_h: float  # circulation time before the log, hours
    dt_h: float  # time since circulation stopped, hours
    depth_m: float  # measured depth of the reading


def horner_time(t_circ_h: float, dt_h: float) -> float:
    if t_circ_h <= 0 or dt_h <= 0:
        raise ValueError("circulation and shut-in times must be positive")
    return math.log10((t_circ_h + dt_h) / dt_h)


def static_temperature(readings: list[Reading], depth_tol_m: float = 1.0) -> float | None:
    """Static formation temperature from a Horner fit, or None.

    Returns None instead of a guess when the data can't support a fit:
    fewer than two readings, readings from different depths, or all
    readings at the same shut-in time. The result is never below the
    highest reading, because mud only cools the hole.
    """
    if len(readings) < 2:
        return None
    depths = [r.depth_m for r in readings]
    if max(depths) - min(depths) > depth_tol_m:
        return None  # different depths are not one Horner series

    xs = [horner_time(r.t_circ_h, r.dt_h) for r in readings]
    ys = [r.bht_c for r in readings]
    n = len(xs)
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    if sxx == 0:
        return None  # same shut-in time repeated: no slope to fit
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = mean_y - slope * mean_x

    return max(intercept, max(ys))
