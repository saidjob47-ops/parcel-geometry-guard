"""Command-line audit and comparison for JSON arrays of vertices."""
import argparse
import json
from pathlib import Path
from .geometry import audit_polygon, rings_match, simplify_collinear


def _load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("points"), list):
        raise ValueError("expected a JSON object with 'points' array")
    return data["points"]


def main(argv=None):
    parser = argparse.ArgumentParser(description="2D polygon checks")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("audit", "compare", "simplify"):
        command = sub.add_parser(name)
        command.add_argument("path")
        if name == "compare":
            command.add_argument("other")
    args = parser.parse_args(argv)
    try:
        points = _load(args.path)
        if args.command == "audit":
            result = audit_polygon(points)
            status = 0 if result["valid"] else 2
        elif args.command == "compare":
            result = {"match": rings_match(points, _load(args.other))}
            status = 0 if result["match"] else 1
        else:
            result = {"points": simplify_collinear(points)}
            status = 0
    except (ValueError, TypeError, OSError) as exc:
        result, status = {"error": str(exc)}, 1
    print(json.dumps(result, indent=2))
    return status


if __name__ == "__main__":
    raise SystemExit(main())
