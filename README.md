# Small script fixes & data tools

Have one reproducible script error or repetitive data task? Send a small example
and the output you need. We agree on a narrow scope and a fixed price first.

This service is offered by John Tan, with OpenAI Codex performing development,
testing and written correspondence as an authorized AI assistant. The examples
below are newly built demonstrations, not past client projects.

| Service | Fixed starting scope | Price |
| --- | --- | ---: |
| Script repair | One reproducible bug in one small Python or JavaScript script; corrected source and a regression example | US$15 |
| CSV cleanup | One CSV up to 10,000 rows: agreed key-based duplicate removal and a before/after count report | US$30 |
| Small automation | One local file-conversion or validation workflow; source, run instructions and a repeatable example | US$50 |

The exact inputs, acceptance example and delivery time are agreed before work
starts. One correction round for the agreed scope is included. Larger work gets
a separate quote. Payment is by PayPal after the agreed deliverable is supplied
and checked, unless the venue requires a different order. No subscription is
required for these local examples.

**Request a quote:** [jointan691@gmail.com](mailto:jointan691@gmail.com)

**Order CSV cleanup on Upwork:**
[US$30: cleaned CSV, count report and reusable Python script](https://www.upwork.com/services/product/development-it-a-deduplicated-csv-file-and-a-reusable-python-cleanup-script-2097316387128636365?ref=project_share).
The listing covers one CSV up to 10,000 rows and 10 MB, three-day delivery after
complete requirements, and one revision. For Upwork orders, all communication,
funding and payment stay on Upwork under its terms.

Please include the error, expected result and a small sanitized sample. Remove
passwords, API keys and private customer records. Communication is asynchronous
in English or Chinese. We will say explicitly which checks ran and what remains
untested.

## Runnable examples

Python 3.10 or newer; standard library only. Both tools run locally without
uploading the input to any service. They are free under the MIT license.

### JSON Lines validator

```sh
python jsonl_check.py your-data.jsonl
```

Reads UTF-8 (with optional BOM), checks one JSON value per line, reports valid
record count and error line/column numbers. Blank lines and non-standard numeric
constants such as `NaN` are errors. It does not print record contents. Exit codes:
0 for valid data, 1 for validation errors, 2 for file/encoding failures.
This checks syntax, not a business schema. Duplicate object keys are accepted
according to Python's default JSON parser behavior. Memory use grows with the
largest line and number of reported errors.

### CSV duplicate cleanup

```sh
python csv_dedupe.py original.csv cleaned.csv --key customer_id
python csv_dedupe.py original.csv cleaned.csv --key first_name --key last_name --ignore-case
```

Supports comma-delimited UTF-8 input, quoted commas/newlines and composite keys.
Trims surrounding key whitespace only for comparison and preserves the original
field values of the first matching row. Rows with any blank key component are
preserved. Original input is unchanged; an existing output is refused. Malformed
row widths or missing/duplicate headers are rejected before a final output is
created. It reports input/output/duplicate/blank-key counts.

The unique-key set is held in memory. CSV quoting and line endings are normalized
in the output; this is not byte-for-byte formatting preservation. Formula-like
cell values are retained literally: review spreadsheet import settings before
opening untrusted input/output in spreadsheet software. A disk write failure can
leave a partial new output, so rerun with a fresh output path after resolving it.

## Verification

```sh
python -m unittest discover -s tests -v
```

The suite exercises the actual command-line programs and data functions,
including Unicode, malformed input, quoted multiline fields, composite keys,
blank IDs and overwrite protection. On 8 September 2026, all 11 tests passed
on Windows (Python 3.14.7) and Ubuntu under WSL (Python 3.14.4). Hosted CI,
other Python versions and macOS have not been tested.
