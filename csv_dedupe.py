"""Remove repeated nonempty CSV keys while preserving original field values."""
import argparse
import csv
import json
from pathlib import Path
import tempfile


def deduplicate(source_path, output_path, keys, *, ignore_case=False):
    source_path, output_path = Path(source_path), Path(output_path)
    if source_path.resolve() == output_path.resolve():
        raise ValueError("input and output must be different files")
    if output_path.exists():
        raise FileExistsError("output already exists; choose a new output path")
    if not keys or len(set(keys)) != len(keys):
        raise ValueError("choose at least one distinct key column")

    temporary = None
    counts = {"input_rows": 0, "output_rows": 0, "duplicates_removed": 0,
              "rows_with_blank_keys_preserved": 0}
    try:
        with source_path.open(encoding="utf-8-sig", newline="") as source:
            reader = csv.reader(source, strict=True)
            header = next(reader, None)
            if not header or len(set(header)) != len(header):
                raise ValueError("CSV needs a nonempty header with unique column names")
            missing = set(keys) - set(header)
            if missing:
                raise ValueError("missing key columns: " + ", ".join(sorted(missing)))
            indexes = [header.index(key) for key in keys]
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", newline="", delete=False,
                prefix=".csv-dedupe-", suffix=".tmp", dir=output_path.parent,
            ) as output:
                temporary = Path(output.name)
                writer = csv.writer(output)
                writer.writerow(header)
                seen = set()
                for row in reader:
                    counts["input_rows"] += 1
                    if len(row) != len(header):
                        raise ValueError(f"record ending at line {reader.line_num} has the wrong number of fields")
                    key = tuple(row[index].strip() for index in indexes)
                    if ignore_case:
                        key = tuple(value.casefold() for value in key)
                    if not all(key):
                        counts["rows_with_blank_keys_preserved"] += 1
                    elif key in seen:
                        counts["duplicates_removed"] += 1
                        continue
                    else:
                        seen.add(key)
                    writer.writerow(row)
                    counts["output_rows"] += 1
            # Exclusive creation protects an output created while we were working.
            with output_path.open("x", encoding="utf-8", newline="") as destination:
                with temporary.open(encoding="utf-8", newline="") as result:
                    for block in iter(lambda: result.read(65536), ""):
                        destination.write(block)
        return counts
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--key", action="append", required=True,
                        help="exact header name; repeat for a composite key")
    parser.add_argument("--ignore-case", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = deduplicate(args.input, args.output, args.key,
                             ignore_case=args.ignore_case)
    except (OSError, UnicodeError, ValueError, csv.Error) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=True))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
