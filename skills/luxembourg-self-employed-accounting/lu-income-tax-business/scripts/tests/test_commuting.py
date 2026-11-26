#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Regression test for commuting_deduction.py (hand-calculated cases; figures from tool-figures.json).

Usage: python scripts/tests/test_commuting.py   (exit code 1 when a case fails)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from commuting_deduction import commuting_deduction  # noqa: E402

# units, year, expected deduction – 2025 and 2026: (units - 4) x €99, at most 26 counted units = €2,574
CASES = [(18, 2025, 1386), (4, 2025, 0), (2, 2025, 0), (30, 2025, 2574), (45, 2025, 2574), (10.5, 2026, 643.5)]

failed = 0
for units, year, want in CASES:
    got = commuting_deduction(units, year)["deduction_eur"]
    ok = abs(got - want) < 0.005
    failed += not ok
    print(f"{'PASS' if ok else 'FAIL'}  {units} units in {year}: {got}" + ("" if ok else f" – expected {want}"))
try:
    commuting_deduction(10, 2019)
    print("FAIL  an unknown year must stop")
    failed += 1
except SystemExit:
    print("PASS  an unknown year stops")
print(f"\n{len(CASES) + 1 - failed} passed, {failed} failed, 0 skipped")
sys.exit(1 if failed else 0)
