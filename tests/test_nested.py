import pytest
from src.medium import Region, Box
from src.geometry import calculate_nearest_boundary

def test_nested_region_crash():
    """
    Tests that the code can handle a Region inside a Region.
    Old code fails with AttributeError: 'Region' object has no attribute 'nearest_surface_method'.
    """
    # 1. Create a basic primitive region (A Box)
    # Bounds: x=0 to 10
    inner_box = Box(0, 10, 0, 10, 0, 10)

    # 2. Create a Nested Region (A Wrapper)
    # This represents a complex assembly containing the box
    wrapper_region = Region(
        surfaces=[inner_box],
        operation="union",
        name="Wrapper"
    )

    # 3. Setup Particle State
    # Particle is at x=-5, moving Right (+x)
    state = {"x": -5, "y": 5, "z": 5}
    u, v, w = 1, 0, 0

    # 4. Run Calculation on the WRAPPER, not the box
    # This forces the solver to drill down into wrapper -> inner_box -> planes
    point, medium, distance = calculate_nearest_boundary(state, [wrapper_region], u, v, w)

    # 5. Assertions
    # Should hit the box face at x=0
    assert distance == pytest.approx(5.0)
    assert point == pytest.approx((0, 5, 5))

    # The returned medium should be the Wrapper (the region we passed in)
    assert medium.name == "Wrapper"

if __name__ == "__main__":
    pytest.main([__file__])
