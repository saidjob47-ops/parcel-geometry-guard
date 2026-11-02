"""Pure-Python checks of simple 2D rings (not geographic CRS transforms)."""

import math


def _points(points):
    result = []
    for i, value in enumerate(points):
        if not isinstance(value, (list, tuple)) or len(value) != 2:
            raise ValueError(f"vertex {i} must contain two numbers")
        if any(isinstance(v, bool) or not isinstance(v, (float, int)) for v in value):
            raise ValueError(f"vertex {i} has invalid coordinate type")
        pair = (float(value[0]), float(value[1]))
        if not all(map(math.isfinite, pair)):
            raise ValueError(f"vertex {i} is non-finite")
        result.append(pair)
    return result


def _cross(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, c):
    return (_cross(a, b, c) == 0 and
            min(a[0], b[0]) <= c[0] <= max(a[0], b[0]) and
            min(a[1], b[1]) <= c[1] <= max(a[1], b[1]))


def _intersect(a, b, c, d):
    p, q, r, s = _cross(a, b, c), _cross(a, b, d), _cross(c, d, a), _cross(c, d, b)
    if ((p > 0 > q or p < 0 < q) and (r > 0 > s or r < 0 < s)):
        return True
    return ((p == 0 and _on_segment(a, b, c)) or
            (q == 0 and _on_segment(a, b, d)) or
            (r == 0 and _on_segment(c, d, a)) or
            (s == 0 and _on_segment(c, d, b)))


def audit_polygon(points):
    """Return a JSON-friendly audit without changing any vertices."""
    try:
        v = _points(points)
    except (TypeError, ValueError) as exc:
        return {"valid": False, "issues": ["invalid_coordinate: " + str(exc)],
                "area": None, "orientation": None}
    n = len(v)
    issues = []
    if n < 3:
        issues.append("insufficient_vertices")
    if n > 1 and v[0] == v[-1]:
        issues.append("repeated_closure")
    if any(v[i] == v[i-1] for i in range(1, n)):
        issues.append("consecutive_duplicate")
    area = (math.fsum(v[i][0]*v[(i+1)%n][1]-v[(i+1)%n][0]*v[i][1]
                     for i in range(n))/2) if n >= 3 else None
    if area == 0:
        issues.append("zero_area")
    for i in range(n):
        for j in range(i+1, n):
            if j == i+1 or (i == 0 and j == n-1):
                continue
            if _intersect(v[i], v[(i+1)%n], v[j], v[(j+1)%n]):
                issues.append("self_intersection")
                break
        if "self_intersection" in issues:
            break
    orient = ("counterclockwise" if area > 0 else "clockwise" if area < 0
              else "degenerate") if area is not None else None
    return {"valid": not issues, "issues": issues, "vertex_count": n,
            "area": abs(area) if area is not None else None,
            "orientation": orient}


def simplify_collinear(points, tolerance=0.0):
    """Drop points on a neighbor segment; exact collinearity by default."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    if not audit_polygon(points)["valid"]:
        raise ValueError("cannot simplify invalid polygon")
    v = _points(points)
    while len(v) > 3:
        found = False
        for i in range(len(v)):
            a, p, b = v[i-1], v[i], v[(i+1)%len(v)]
            dx, dy = b[0]-a[0], b[1]-a[1]
            size = dx*dx+dy*dy
            if size == 0:
                continue
            fraction = ((p[0]-a[0])*dx+(p[1]-a[1])*dy)/size
            if 0 <= fraction <= 1 and abs(_cross(a,b,p)) <= tolerance*math.sqrt(size):
                del v[i]
                found = True
                break
        if not found:
            break
    return v


def rings_match(first, second, tolerance=0.0):
    """Compare two valid rings independent of start vertex and direction."""
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("invalid tolerance")
    if not audit_polygon(first)["valid"] or not audit_polygon(second)["valid"]:
        return False
    a, b = _points(first), _points(second)
    if len(a) != len(b):
        return False
    n = len(a)
    for direction in (1, -1):
        for offset in range(n):
            rotated = [b[(offset+direction*i) % n] for i in range(n)]
            if all(math.hypot(x[0]-y[0], x[1]-y[1]) <= tolerance
                   for x, y in zip(a, rotated)):
                return True
    return False
