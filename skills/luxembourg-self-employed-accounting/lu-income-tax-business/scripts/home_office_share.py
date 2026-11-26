#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Office share of housing costs (area method, as in ACD circular L.I.R. n° 105/2).

Share = office m2 / living area m2. The living area EXCLUDES accessory rooms
(cellar, garage, laundry room, attic). The office counts in the living area.
Office-only costs (desk, office lamp) are added in full.

This computes the number only. Whether the room qualifies (separate room with a
door, used >= 90% for work, no other office) is a separate test.

Usage:
    python home_office_share.py --office-m2 10 --living-m2 80 --costs 21600
    python home_office_share.py --office-m2 10 --living-m2 80 --costs 21600 --office-only 300 --borne-share 0.5
"""
import argparse
import json


def home_office_share(office_m2: float, living_m2: float, costs: float,
                      office_only: float = 0.0, borne_share: float = 1.0) -> dict:
    if living_m2 <= 0 or office_m2 <= 0:
        raise SystemExit("areas must be > 0")
    if office_m2 > living_m2:
        raise SystemExit("office cannot be larger than the living area")
    if not 0 < borne_share <= 1:
        raise SystemExit("borne-share must be in (0, 1]: the part of the household costs the person really pays")
    share = office_m2 / living_m2
    housing_part = round(costs * borne_share * share, 2)
    total = round(housing_part + office_only, 2)
    warn = []
    if share > 0.5:
        warn.append("Office above half of the living area: ACD may see it as disproportionate.")
    if borne_share < 1:
        warn.append("Only the share actually paid counts; keep proof of payments to the partner.")
    return {
        "office_m2": office_m2,
        "living_m2": living_m2,
        "office_share_pct": round(share * 100, 2),
        "housing_costs_eur": costs,
        "share_of_costs_borne": borne_share,
        "deductible_housing_part_eur": housing_part,
        "office_only_costs_eur": office_only,
        "total_deductible_eur": total,
        "working": f"{costs} x {borne_share} x {office_m2}/{living_m2} = {housing_part}; + {office_only} office-only = {total}",
        "warnings": warn,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--office-m2", type=float, required=True)
    ap.add_argument("--living-m2", type=float, required=True, help="excluding cellar, garage, laundry, attic")
    ap.add_argument("--costs", type=float, required=True, help="yearly housing costs to split (rent, charges, energy...)")
    ap.add_argument("--office-only", type=float, default=0.0)
    ap.add_argument("--borne-share", type=float, default=1.0, help="part of household costs the person pays (0-1)")
    a = ap.parse_args()
    print(json.dumps(home_office_share(a.office_m2, a.living_m2, a.costs, a.office_only, a.borne_share), indent=2))
