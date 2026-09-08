"""Validate UTF-8 JSON Lines without printing record contents."""
import argparse
import json
from pathlib import Path


def reject_constant(value):
    raise ValueError(f"non-standard JSON constant {value}")


def validate(path):
    records = 0
    errors = []
    with Path(path).open(encoding="utf-8-sig") as source:
        for number, line in enumerate(source, 1):
            if not line.strip():
                errors.append({"line": number, "error": "blank line"})
                continue
            try:
                json.loads(line, parse_constant=reject_constant)
            except json.JSONDecodeError as error:
                errors.append({"line": number, "column": error.colno,
                               "error": error.msg})
            except ValueError as error:
                errors.append({"line": number, "error": str(error)})
            else:
                records += 1
    return {"valid_records": records, "errors": errors}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    try:
        result = validate(args.input)
    except (OSError, UnicodeError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 1 if result["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
