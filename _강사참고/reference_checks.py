"""Offline M3/M4 reference checks; does not call APIs or modify source data."""
import argparse
import csv
import hashlib
import json
from decimal import Decimal, InvalidOperation
from pathlib import Path

SERIES = {
    "NY.GDP.MKTP.CD": ("nominal_gdp_usd", "current US$"),
    "FP.CPI.TOTL.ZG": ("inflation_percent", "annual %"),
    "PA.NUS.FCRF": ("exchange_rate", "KRW per US$, annual average"),
}


def inspect_csv(path):
    path = Path(path)
    errors, values = [], {}
    with path.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"year", "series_id", "value", "country_code"}
        if not required.issubset(reader.fieldnames or []):
            return {"status": "FAIL", "errors": ["missing_columns"]}
        rows = list(reader)
    for line, row in enumerate(rows, 2):
        key = (row["year"], row["series_id"])
        if key in values:
            errors.append(f"duplicate_key:line{line}:{key}")
            continue
        try:
            year = int(row["year"])
        except ValueError:
            errors.append(f"invalid_year:line{line}")
            continue
        if row["country_code"] != "KOR":
            errors.append(f"unexpected_country:line{line}")
        if row["series_id"] not in SERIES:
            errors.append(f"unexpected_series:line{line}")
            continue
        raw = row["value"].strip()
        try:
            value = Decimal(raw)
            if not value.is_finite():
                raise InvalidOperation
        except InvalidOperation:
            errors.append(f"{'missing_value' if not raw else 'invalid_number'}:line{line}")
            value = None
        values[key] = (year, value)
    expected = {(str(y), s) for y in range(2015, 2025) for s in SERIES}
    for key in sorted(expected - values.keys()):
        errors.append(f"missing_key:{key}")
    for key in sorted(values.keys() - expected):
        errors.append(f"unexpected_key:{key}")
    result = {
        "status": "FAIL" if errors else "PASS",
        "source_path": str(path.resolve()),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "row_count": len(rows),
        "errors": errors,
        "numeric_encoding": "Decimal values serialized as strings to preserve precision",
        "method": "Frozen local CSV, not a fresh API collection",
        "wide_rows": [],
    }
    if errors:
        return result
    previous = None
    base = {s: values[("2015", s)][1] for s in SERIES}
    for year in range(2015, 2025):
        current = {s: values[(str(year), s)][1] for s in SERIES}
        row = {"year": year}
        for s, (name, unit) in SERIES.items():
            row[name] = str(current[s])
        fx = current["PA.NUS.FCRF"]
        row["exchange_rate_yoy_percent"] = (
            None if previous is None or previous["PA.NUS.FCRF"] == 0
            else str((fx / previous["PA.NUS.FCRF"] - 1) * 100)
        )
        row["inflation_change_pp"] = (
            None if previous is None
            else str(current["FP.CPI.TOTL.ZG"] - previous["FP.CPI.TOTL.ZG"])
        )
        row["exchange_rate_index_2015_100"] = (
            None if base["PA.NUS.FCRF"] == 0 else str(fx / base["PA.NUS.FCRF"] * 100)
        )
        result["wide_rows"].append(row)
        previous = current
    result["series"] = [
        {"id": s, "field": name, "unit": unit,
         "source_url": f"https://api.worldbank.org/v2/country/KOR/indicator/{s}?date=2015:2024&format=json",
         "url_status": "derived_from_series_id_not_retrieved_by_this_script"}
        for s, (name, unit) in SERIES.items()
    ]
    result["limits"] = [
        "GDP is nominal current US$, not real GDP growth.",
        "Inflation is annual %, not a price index; its annual difference is percentage points.",
        "Exchange rate is an annual average, not a tradable current quote.",
        "The first observed year has no previous-year comparison in this input.",
    ]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=Path, default=Path(__file__).resolve().parents[1] / "data/source_macro_2015_2024.csv")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = inspect_csv(args.csv)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    raise SystemExit(0 if report["status"] == "PASS" else 1)
