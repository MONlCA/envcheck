#!/usr/bin/env python3
"""EnvCheck: verify required environment variables without exposing values."""

import argparse
import json
import os
import re
from pathlib import Path

VAR_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def parse_spec(path):
    """Parse a .env.example-style file into variable requirements.

    Add `# optional` to a line to mark a variable optional.
    Values in the example file are ignored and never used as runtime secrets.
    """
    variables = []
    seen = set()

    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue

        body, _, comment = line.partition("#")
        assignment = body.strip()
        name = assignment.split("=", 1)[0].strip()

        if not VAR_PATTERN.match(name):
            raise ValueError(f"invalid variable name on line {line_number}: {name or line!r}")
        if name in seen:
            raise ValueError(f"duplicate variable on line {line_number}: {name}")

        seen.add(name)
        variables.append({"name": name, "required": "optional" not in comment.lower()})

    if not variables:
        raise ValueError("spec file does not contain any environment variables")
    return variables


def check_environment(variables, environ=None):
    environ = os.environ if environ is None else environ
    results = []

    for item in variables:
        value = environ.get(item["name"])
        is_set = value is not None and value != ""
        if is_set:
            state = "SET"
        elif item["required"]:
            state = "MISSING"
        else:
            state = "OPTIONAL_MISSING"

        results.append({
            "name": item["name"],
            "required": item["required"],
            "state": state,
        })
    return results


def summarize(results):
    return {
        "set": sum(item["state"] == "SET" for item in results),
        "missing": sum(item["state"] == "MISSING" for item in results),
        "optional_missing": sum(item["state"] == "OPTIONAL_MISSING" for item in results),
    }


def print_report(results):
    print("\nENVCHECK")
    print("─" * 54)
    for item in results:
        if item["state"] == "SET":
            icon, label = "✓", "SET"
        elif item["state"] == "MISSING":
            icon, label = "✗", "MISSING"
        else:
            icon, label = "○", "OPTIONAL / MISSING"
        print(f"{icon} {item['name']:<30} {label}")

    counts = summarize(results)
    print("─" * 54)
    print(
        f"{counts['set']} set • {counts['missing']} missing • "
        f"{counts['optional_missing']} optional missing"
    )
    print("\n✓ Environment is ready.\n" if counts["missing"] == 0 else "\n✗ Environment is not ready.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Check required environment variables without printing secret values."
    )
    parser.add_argument("spec", type=Path, nargs="?", default=Path(".env.example"))
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    try:
        variables = parse_spec(args.spec)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    results = check_environment(variables)
    counts = summarize(results)

    if args.json:
        print(json.dumps({"ready": counts["missing"] == 0, "summary": counts, "variables": results}, indent=2))
    else:
        print_report(results)

    raise SystemExit(1 if counts["missing"] else 0)


if __name__ == "__main__":
    main()
