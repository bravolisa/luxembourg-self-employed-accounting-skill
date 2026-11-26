#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Deductible car costs by business-km share (Luxembourg Forms 112/152 car block).

Deductible = car costs x business km / total km + direct business-trip costs.
Car costs = fuel, repairs, tyres, leasing, garage rent, taxes and insurance.
Direct costs (parking, tolls on business trips) are added in full.
Depreciation is NOT included here: it goes through Form 113 for business-asset cars.
Fines are never deductible and must not be included.

Usage:
    python car_km_share.py --costs 4500 --total-km 20000 --business-km 6000 --direct 150
"""
import argparse
import json


def car_km_share(costs: float, total_km: float, business_km: float, direct: float = 0.0) -> dict:
    if total_km <= 0:
        raise SystemExit("total km must be > 0 (odometer at 31 Dec minus odometer at 1 Jan)")
    if not 0 <= business_km <= total_km:
        raise SystemExit("business km must be between 0 and total km")
    if costs < 0 or direct < 0:
        raise SystemExit("costs must be >= 0")
    share = business_km / total_km
    car_part = round(costs * share, 2)
    return {
        "car_costs_eur": costs,
        "total_km": total_km,
        "business_km": business_km,
        "business_share_pct": round(share * 100, 2),
        "deductible_car_costs_eur": car_part,
        "direct_trip_costs_eur": direct,
        "total_deductible_eur": round(car_part + direct, 2),
        "working": f"{costs} x {business_km}/{total_km} = {car_part}; + {direct} direct = {round(car_part + direct, 2)}",
        "reminder": "Needs a km record (logbook or equivalent); excludes depreciation and fines.",
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--costs", type=float, required=True, help="total car costs of the year (car block)")
    ap.add_argument("--total-km", type=float, required=True)
    ap.add_argument("--business-km", type=float, required=True)
    ap.add_argument("--direct", type=float, default=0.0, help="parking/tolls on business trips")
    a = ap.parse_args()
    print(json.dumps(car_km_share(a.costs, a.total_km, a.business_km, a.direct), indent=2))
