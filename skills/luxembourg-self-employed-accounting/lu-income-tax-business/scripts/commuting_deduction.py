#!/usr/bin/env python3
"""Luxembourg flat commuting deduction (frais de déplacement) for one tax year.

Rule (Forms 112/152, 2025-2026): units x EUR 99, the first 4 units are not counted,
the deduction is capped at EUR 2,574 (26 counted units). Units are the official
distance units between the home commune and the work commune, not road km.

Usage:
    python commuting_deduction.py --units 18

Prints JSON with the working. It does not decide whether the trip is commuting
(home -> fixed place of business) or a business trip; that is a legal question.
Part-year activity and mid-year moves are not handled: check the year's rules.

The figures per tax year come from lu-tax-core/data/tool-figures.json (keys commuting_*), which
the year files own; add a year there only after checking that year's forms.
"""
import argparse
import json
from pathlib import Path

FIGURES_SOURCE = Path(__file__).resolve().parents[2] / "lu-tax-core" / "data" / "tool-figures.json"


def params(year: int) -> dict:
    years = json.loads(FIGURES_SOURCE.read_text(encoding="utf-8"))["years"]
    if str(year) not in years:
        raise SystemExit(f"No parameters for tax year {year}; known years: {sorted(years)}")
    f = {k: v["value"] for k, v in years[str(year)].items()}
    return {"eur_per_unit": f["commuting_eur_per_unit"], "free_units": f["commuting_free_units"],
            "max_counted_units": f["commuting_max_counted_units"], "cap_eur": f["commuting_cap"]}


def commuting_deduction(units: float, year: int = 2025) -> dict:
    if units < 0:
        raise SystemExit("units must be >= 0")
    p = params(year)
    counted = max(0, min(units - p["free_units"], p["max_counted_units"]))
    full_year = round(counted * p["eur_per_unit"], 2)
    amount = min(full_year, p["cap_eur"])
    return {
        "tax_year": year,
        "units": units,
        "counted_units": counted,
        "eur_per_unit": p["eur_per_unit"],
        "deduction_eur": amount,
        "working": f"max(0, min({units} - {p['free_units']}, {p['max_counted_units']})) x {p['eur_per_unit']} = {amount}",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--units", type=float, required=True, help="official distance units home -> work")
    ap.add_argument("--year", type=int, default=2025)
    a = ap.parse_args()
    print(json.dumps(commuting_deduction(a.units, a.year), indent=2))
