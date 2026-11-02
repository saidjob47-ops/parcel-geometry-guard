import math
import pytest
from parcel_geometry_guard import audit_polygon, rings_match, simplify_collinear

RECT = [(0, 0), (4, 0), (4, 3), (0, 3)]


def test_area_orientation():
    report = audit_polygon(RECT)
    assert report["valid"] and report["area"] == 12
    assert report["orientation"] == "counterclockwise"


def test_ring_equivalence():
    assert rings_match(RECT, RECT[2:] + RECT[:2])
    assert rings_match(RECT, list(reversed(RECT)))
    assert not rings_match(RECT, [(0, 0), (2, 0), (4, 0), (4, 3), (0, 3)])


def test_strict_simplification():
    five = [(0, 0), (2, 0), (4, 0), (4, 3), (0, 3)]
    assert simplify_collinear(five) == [tuple(map(float, p)) for p in RECT]
    tiny_bend = [(0, 0), (2, 0.000001), (4, 0), (4, 3), (0, 3)]
    assert simplify_collinear(tiny_bend) == tiny_bend


def test_invalid_cases():
    assert "repeated_closure" in audit_polygon(RECT + [RECT[0]])["issues"]
    assert "self_intersection" in audit_polygon([(0,0),(3,3),(0,3),(3,0)])["issues"]
    assert "zero_area" in audit_polygon([(0,0),(1,1),(2,2)])["issues"]
    assert not audit_polygon([(0,0),(1,0),(math.inf,1)])["valid"]
    with pytest.raises(ValueError):
        simplify_collinear(RECT + [RECT[0]])
