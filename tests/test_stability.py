from open_dam_integry.stability.stability import (
    InfiniteSlopeParams,
    factor_of_safety_infinite_slope,
)


def test_infinite_slope_fs_basic():
    params = InfiniteSlopeParams(
        cohesion_kpa=8.0,
        phi_deg=30.0,
        beta_deg=18.0,
        height_m=15.0,
        unit_weight_kN_m3=18.5,
        ru=0.15,
    )
    fs = factor_of_safety_infinite_slope(params)
    assert fs > 1.0
    assert 1.0 < fs < 3.0
