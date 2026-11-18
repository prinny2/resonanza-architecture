import math

import pytest

from horner import Reading, horner_time, static_temperature


def make(bht, dt, t_circ=4.0, depth=2124.0):
    return Reading(bht_c=bht, t_circ_h=t_circ, dt_h=dt, depth_m=depth)


def test_recovers_known_static_temperature():
    # Synthetic series built from T = 100 - 20 * x
    readings = [make(100 - 20 * horner_time(4.0, dt), dt) for dt in (2.0, 6.0, 12.0)]
    assert static_temperature(readings) == pytest.approx(100.0)


def test_single_reading_is_not_enough():
    assert static_temperature([make(80.0, 6.0)]) is None


def test_readings_at_different_depths_are_not_a_series():
    readings = [make(80.0, 6.0, depth=792.0), make(95.0, 12.0, depth=2124.0)]
    assert static_temperature(readings) is None


def test_repeated_shut_in_time_has_no_slope():
    # The AGP trap: the same BHT repeated across logging groups
    readings = [make(76.7, 8.5), make(76.7, 8.5)]
    assert static_temperature(readings) is None


def test_never_below_highest_reading():
    # Noisy data where the fit would land below a measured value
    readings = [make(90.0, 2.0), make(85.0, 12.0)]
    assert static_temperature(readings) >= 90.0


def test_horner_time_rejects_non_positive_times():
    with pytest.raises(ValueError):
        horner_time(0.0, 5.0)
    with pytest.raises(ValueError):
        horner_time(4.0, 0.0)


def test_horner_time_goes_to_zero_with_long_shut_in():
    assert horner_time(4.0, 1e9) == pytest.approx(0.0, abs=1e-6)
    assert math.isfinite(horner_time(4.0, 0.5))
