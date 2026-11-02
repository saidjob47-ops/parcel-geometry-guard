# Parcel Geometry Guard

Zero-dependency Python tools for auditing 2D polygon vertices used in GIS,
CAD, and surveying workflows. This is a **new, early-stage** open-source
project. It is not a cadastral authority or a substitute for a surveyor.

## Features

- Detects invalid coordinates, duplicate closing points, zero area and
  self-intersections; reports area and orientation.
- Compares polygons regardless of start vertex and winding, without losing
  meaningful differences in vertex count.
- Simplifies only exact collinear vertices by default, retaining small bends.
- Keeps coordinates untouched; never guesses CRS or rounds coordinates.

## Install and use

```bash
python -m pip install -e ".[test]"
python -m pytest -q
parcel-geometry-guard audit examples/rectangle.json
```

```python
from parcel_geometry_guard import audit_polygon, rings_match, simplify_collinear
points = [(0,0), (4,0), (4,3), (0,3)]
assert audit_polygon(points)["area"] == 12
assert rings_match(points, list(reversed(points)))
assert simplify_collinear([(0,0),(2,0),(4,0),(4,3),(0,3)]) == points
```

CLI: `audit FILE`, `compare FILE FILE`, `simplify FILE`.
Input format: `{"points": [[0,0],[4,0],[4,3],[0,3]]}`.
All coordinates are **planar (X, Y) in the same known CRS and units**.
Never compare degrees to meters. The tool does not handle DWG/DXF files,
deeds, official boundaries, or private platform integrations.

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).
**Do not submit proprietary engineering documents or personal data.**

MIT licensed. Maintained by saidjob47-ops.
