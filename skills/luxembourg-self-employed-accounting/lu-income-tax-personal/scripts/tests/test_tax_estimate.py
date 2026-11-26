#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Regression tests for tax_estimate.py – invented cases, each worked out by hand below.

Usage: python scripts/tests/test_tax_estimate.py   (exit code 1 when a case fails)

Change an expected figure only with a new hand calculation, never by copying the script's output.
Scale sums used (class 1, scale-and-calculation.md): tax up to €35,730 = €3,168.00; up to €54,090 = €8,859.60.
"""
import json
import re
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import tax_estimate as te  # noqa: E402

HOUSEHOLDS = HERE.parents[2] / "lu-annual-return" / "scripts" / "tests" / "households"
results = []


def check(name, got, want):
    ok = abs(Decimal(str(got)) - Decimal(str(want))) < Decimal("0.005")
    results.append((ok, f"{name}: {got}" + ("" if ok else f" – expected {want}")))


# 1. Couple, class 2, 2026: taxable €80,000 − €4,500 = €75,500; half €37,750 → €3,168.00 + 24% × €2,020
#    = €3,652.80; × 2 = €7,305.60 → €7,305; + 7% €511.35 → €7,816. Profit €30,000: CII €600 + CO2 €216.
#    €7,816 − €816 − €6,000 withheld − €1,000 advances = €0.
args = {"year": 2026, "taxable": 80000, "tax_class": 2, "both_professional": True, "profits": {"taxpayer": 30000},
        "withheld": 6000, "advances": 1000, "extra_professional_amount": 4500}
r = te.estimate(**args)
check("couple 2026: income tax", r["tax"], 7816)
check("couple 2026: credits", sum(r["credits"].values()), 816)
check("couple 2026: balance", r["balance"], 0)
check("couple 2026: marginal rate", r["marginal"], "25.68")  # 24% band × 1.07

# 1b. What-if on case 1.
#  special=3000: base €72,500, half €36,250 → €3,168.00 + 24% × €520 = €3,292.80; × 2 = €6,585.60 → €6,585;
#    × 1.07 = €7,045.95 → €7,045; saved €7,816 − €7,045 = €771.
#  business=2000: profit €28,000 is below the 2026 minimum base (€32,918.01), so only dependency 1.40% × €2,000
#    = €28 is saved; taxable falls by the full €2,000 → base €73,500, half €36,750 → €3,168.00 + 24% × €1,020
#    = €3,412.80; × 2 = €6,825.60 → €6,825; × 1.07 = €7,302.75 → €7,302; saved €514; credits unchanged.
_, rows = te.what_if({**args, "abatement": 0}, [("special", Decimal(3000))])
w = dict(rows)
check("what-if special 3000: tax saved", w["special=3000"]["tax_saved"], 771)
# Separate component: taxable 75,500, no professional allowance, gives the same initial
# adjusted income as case 1. The hand calculation above still gives 514 tax and 28 CCSS.
_, rows = te.what_if({**args, "taxable": 75500, "extra_professional_amount": 0}, [("business", Decimal(2000))])
w = dict(rows)
try:
    te.what_if({"year": 2025, "taxable": 60000, "tax_class": 2, "both_professional": True,
                "profits": {"taxpayer": 10000, "spouse": 70000}, "extra_professional_amount": 1000},
               [("business", Decimal(10000))])
    results.append((False, "business scenario cannot retain an allowance when qualifying profit disappears"))
except SystemExit as e:
    results.append(("re-establish the spouse allowance" in str(e), "business scenario rechecks allowance"))
check("what-if business 2000 below the minimum base: CCSS saved", w["business=2000"]["ccss_saved"], 28)
check("what-if business 2000: tax saved", w["business=2000"]["tax_saved"], 514)

# 2. Single, class 1, 2025 (the worked example in scale-and-calculation.md): taxable €57,000 →
#    €8,859.60 + 39% × €2,910 = €9,994.50 → €9,994; + 7% €699.58 → €10,693.
#    Profit €60,000: CII €600 − €20,000 × 1.5% = €300; CO2 €192 − €20,000 × 0.48% = €96.
#    €10,693 − €396 − €8,000 advances = €2,297.
args2 = {"year": 2025, "taxable": 57000, "tax_class": 1, "profits": {"taxpayer": 60000}, "advances": 8000}
r = te.estimate(**args2)
check("single 2025: income tax", r["tax"], 10693)
check("single 2025: CII in the phase-out", r["credits"]["CII taxpayer"], 300)
check("single 2025: CO2 credit in the phase-out", r["credits"]["CO2 credit taxpayer"], 96)
check("single 2025: balance", r["balance"], 2297)

# 2b. business=1000 on case 2: CCSS 2025 22.80% × €1,000 = €228 + dependency €14 = €242. Taxable falls by
#     €1,000 − €228 = €772 → €56,228 → base €56,200: €8,859.60 + 39% × €2,110 = €9,682.50 → €9,682;
#     × 1.07 = €10,359.74 → €10,359. Profit €59,000: CII €600 − €285 = €315; CO2 €192 − €91.20 = €100.80.
#     After credits €10,359 − €415.80 = €9,943.20 against €10,297 → tax saved €353.80; total €595.80.
_, rows = te.what_if({**args2, "abatement": 0}, [("business", Decimal(1000))])
w = dict(rows)
check("what-if business 1000 above the minimum base: CCSS saved", w["business=1000"]["ccss_saved"], 242)
check("what-if business 1000: tax saved incl. higher credits", w["business=1000"]["tax_saved"], "353.80")
check("what-if business 1000: total saved", w["business=1000"]["saved"], "595.80")

# 3. Single, 2026, taxable €20,000: €176.40 + €198.45 + €220.50 + 11% × €155 = €612.40 → €612; × 1.07
#    = €654.84 → €654. Profit €5,000: CII €300 + (€5,000 − €936) × 2.9% = €417.856 → rounded up €417.86;
#    CO2 €216. Raw balance €654 − €633.86 = €20.14; art.154(2) floors amount due to €20.
r = te.estimate(year=2026, taxable=20000, tax_class=1, profits={"taxpayer": 5000})
check("low profit: CII on the ramp, rounded up", r["credits"]["CII taxpayer"], "417.86")
check("low profit: positive final balance floors", r["balance"], "20")

# 4. Single, 2026, taxable €200,000, above €150,000: €8,859.60 + 39% × €63,360 = €24,710.40 + 40% × €58,710
#    = €23,484.00 + 41% × €23,840 = €9,774.40 → €66,828.40 → €66,828; surcharge 9% − €931.80 = €5,082.72;
#    total €71,910.72 → €71,910. (At €150,000 both formulas give €3,261.30 – the rule is continuous.)
r = te.estimate(year=2026, taxable=200000, tax_class=1)
check("high income: surcharge 9% less the deduction", r["surcharge"], "5082.72")
check("high income: income tax", r["tax"], 71910)

# 5. Loss or tiny profit: CII €300, no CO2 credit; profit €80,000 or more: neither.
for profit, cii, co2 in ((-2000, 300, 0), (500, 300, 0), (80000, 0, 0), (11266, 600, 216), (40000, 600, 216)):
    r = te.estimate(year=2026, taxable=50000, tax_class=1, profits={"taxpayer": profit})
    check(f"credits at profit {profit}", sum(r["credits"].values()), cii + co2)

# 5b. Both spouses with a profit: one CII and CO2 credit only, the larger (open point PIT-O-05):
#     €30,000 → €600 + €216 = €816; €5,000 → €417.86 + €216 = €633.86; count €816.
r = te.estimate(year=2026, taxable=50000, tax_class=2, both_professional=True, extra_professional_amount=0, profits={"taxpayer": 5000, "spouse": 30000})
check("two businesses: one credit counted", sum(r["credits"].values()), 816)

# 6. Salary-household balance needs credit reconciliation; no universal CIS subtraction.
src = HOUSEHOLDS / "couple_commercial_salaried.json"
if src.exists():
    text = re.sub(r'"@ID:(\d{4})-(\d{2})-(\d{2})"', lambda m: f'"{m[1]}{m[2]}{m[3]}' + "0" * 5 + '"', src.read_text())
    with tempfile.TemporaryDirectory() as t:
        path = Path(t) / "household.json"
        path.write_text(text)
        try:
            te.from_household(path, advances=1000)
            results.append((False, "salary household requires reconciliation"))
        except SystemExit as e:
            results.append(("reconcile credits" in str(e), "salary household requires reconciliation"))
else:
    results.append((False, "salary household fixture missing"))

# Annual professional allowance is reviewed, never inferred solely from both spouses working.
try:
    te.estimate(year=2025, taxable=30000, tax_class=2, both_professional=True)
    results.append((False, "unreviewed spouse allowance stops"))
except SystemExit:
    results.append((True, "unreviewed spouse allowance stops"))
r = te.estimate(year=2025, taxable=30000, tax_class=2, both_professional=True, extra_professional_amount=1200)
check("reviewed limited spouse allowance", r["adjusted"], 28800)

# LIR art. 124: tariff tax below EUR12 becomes zero before Fund, not after credits.
# Class1 R=13350: (13350-13230)*8%=9.60 ->9 ->0, Fund0.
# Class1 R=13400:170*8%=13.60 ->13; Fund0.91; final13.
# Class2 R=26600:2*((13300-13230)*8%)=11.20 ->11 ->0.
# Class2 R=26650:2*((13325-13230)*8%)=15.20 ->15; Fund1.05; final16.
for cls, income, wanted in ((1, 13350, 0), (1, 13400, 13), (2, 26600, 0), (2, 26650, 16)):
    r = te.estimate(year=2025, taxable=income, tax_class=cls)
    check(f"small-tax boundary class{cls} at {income}", r["tax"], wanted)
r = te.estimate(year=2025, taxable=13350, tax_class=1, profits={"taxpayer": 0})
check("zero tariff has zero Fund surcharge", r["surcharge"], 0)
check("small-tax rule does not erase refundable CII", r["balance"], -300)

# 7. What the script refuses.
for name, kwargs in (("class 1a", {"year": 2026, "taxable": 50000, "tax_class": 3}),
                     ("a year without figures", {"year": 2019, "taxable": 50000, "tax_class": 1})):
    try:
        te.estimate(**kwargs)
        results.append((False, f"stops: {name} – it did not stop"))
    except SystemExit:
        results.append((True, f"stops: {name}"))

failed = [m for ok, m in results if not ok]
for ok, m in results:
    print(("PASS  " if ok else "FAIL  ") + m)
print(f"\n{len(results) - len(failed)} passed, {len(failed)} failed, 0 skipped")
sys.exit(1 if failed else 0)
