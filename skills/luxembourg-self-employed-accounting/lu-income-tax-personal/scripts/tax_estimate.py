#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Estimate a resident household's Luxembourg income tax for one year, and what extra deductions would save.

Usage:
    python tax_estimate.py --year 2026 --taxable 80000 --class 2 --both-professional --extra-professional-amount 4500 --profit 30000 --withheld 6000 --advances 1000
    python tax_estimate.py --household household.json [--year 2026] [--advances 4800]
    ... --what-if special=9000 --what-if business=2000 --what-if household-help=5400   (repeatable)

The year: taxable income (Form 100 box 2038) − abatements (the extra-professional abatement when both
spouses have professional income; --abatement for others) → rounded down to €50 → the scale (class 2:
twice the class-1 tax on half) → rounded down to the euro → + Employment Fund surcharge (7%; 9% less the
ACD's deduction above the threshold) → − the self-employed credits (CII and CO2 credit; only one when
both spouses have a profit – open point PIT-O-05) → + paid-minus-retained salary credit
reconciliation → − pre-credit tax withheld − advances paid = balance (minus = refund).
The positive final balance floors to whole euros (art.154(2)); refund cents are preserved. Rules:
references/scale-and-calculation.md and tax-credits.md.

--household reads the Form 100 household file of lu-annual-return (form100-tools.md): taxable income as
its indicative check computes it, class, profits, tax withheld and "advances_paid". --year can differ
from the file's year to plan the next one on the same figures; the taxable income keeps the file's
own ceilings.

What-if (references/deduction-review.md), each option alone and then all together:
  special=X         a special expense (private pension contract, insurance, donation): taxable − X
  abatement=X       an abatement as allowed: adjusted income − X
  household-help=X  the household-help abatement, capped at the year's maximum
  business=X        genuine business costs of the taxpayer (spouse if only the spouse has a profit):
                    the profit falls by X, so CCSS falls (deductible part only down to the minimum base;
                    dependency on all of it), taxable income falls by X less the deductible CCSS saved,
                    and the credits follow the new profit. The CCSS saving comes with the regularisation.

Supported 2025 class1a and bounded CIM: forms/2025/form100-deductions.md in lu-annual-return.
Not covered (the script says so): other child reductions, non-residents and the 15% minimum,
extraordinary income, the overtime credit and pension/mixed-category credit reconciliation.
2025 ordinary salary households use explicit salary_balance facts (salary-balance-calculator.md);
partial credit periods, special regimes and ambiguous small-recovery grouping stop for review. Figures: lu-tax-core/data/tool-figures.json. An estimate – the ACD's bulletin decides.
"""
import argparse
import json
import math
import sys
from decimal import Decimal, ROUND_FLOOR
from pathlib import Path
import salary_balance as salary

SKILLS = Path(__file__).resolve().parents[2]
FIGURES_SOURCE = SKILLS / "lu-tax-core" / "data" / "tool-figures.json"
HOUSEHOLD_MODULE = SKILLS / "lu-annual-return" / "scripts"


def D(x):
    return Decimal(str(x))


def floor(x, step=1):
    return (D(x) / D(step)).to_integral_value(ROUND_FLOOR) * D(step)


def figures(year):
    years = json.loads(FIGURES_SOURCE.read_text(encoding="utf-8"))["years"]
    if str(year) not in years:
        sys.exit(f"no figures for tax year {year}; known: {sorted(years)}")
    return {k: v["value"] for k, v in years[str(year)].items()}


def class1_tax(x, scale):
    tax, low = D(0), D(0)
    for top, rate in scale:
        top = D(top) if top is not None else None
        if x > low:
            tax += ((x if top is None else min(x, top)) - low) * D(rate) / 100
        if top is None:
            break
        low = top
    return tax


def band_rate(x, scale):
    for top, rate in scale:
        if top is None or x <= D(top):
            return D(rate)


def class1a_tax(base, scale, f):
    kink = D(f["class1a_kink"])
    transform = lambda x: max(D(0), x - (D(f["class1a_shortfall"]) - x) * D(f["class1a_reduction_percent"]) / 100)
    if base <= kink:
        x = transform(base)
        return class1_tax(x, scale), band_rate(x, scale) * (1 + D(f["class1a_reduction_percent"])/100)
    tax, low = class1_tax(transform(kink), scale), kink
    for top, rate in scale:
        if rate < f["class1a_continuation_rate"]:
            continue
        high = D(top) if top is not None else base
        tax += max(min(base, high)-low, D(0)) * D(rate)/100
        if base <= high:
            return tax, D(rate)
        low = high
    raise AssertionError("class1a continuation missing")


def income_tax(adjusted, tax_class, f):
    """Scale tax and surcharge on the adjusted taxable income."""
    base = max(floor(adjusted, f["rounding_step"]), D(0))
    scale = f["scale_class1"]
    if tax_class == 2:
        scale_tax, rate = 2 * class1_tax(base / 2, scale), band_rate(base / 2, scale)
    elif tax_class == "1a":
        scale_tax, rate = class1a_tax(base, scale, f)
    else:
        scale_tax, rate = class1_tax(base, scale), band_rate(base, scale)
    scale_tax = floor(scale_tax)
    if scale_tax < D(f["minimum_tariff_tax"]):  # LIR art. 124(2), before Fund and credits
        scale_tax = D(0)
    threshold = f[f"employment_fund_threshold_class{tax_class}"]
    if base > D(threshold):
        surcharge = scale_tax * D(f["employment_fund_high_rate"]) / 100 - D(f[f"employment_fund_high_deduction_class{tax_class}"])
        fund = D(f["employment_fund_high_rate"])
    else:
        surcharge = scale_tax * D(f["employment_fund_rate"]) / 100
        fund = D(f["employment_fund_rate"])
    total = floor(scale_tax + surcharge)
    return {"base": base, "scale_tax": scale_tax, "surcharge": surcharge.quantize(D("0.01")), "tax": total,
            "band": rate, "marginal": (rate * (1 + fund / 100)).quantize(D("0.01"))}


def up_to_cent(x):
    return D(math.ceil(D(x) * 100)) / 100


def self_employed_credits(profit, f):
    """CII and CO2 credit for one person's business profit (art. 152ter LIR)."""
    p = D(profit)
    if p < D(f["cii_min_profit"]):
        return D(f["cii_low"]), D(0)
    if p >= D(f["cii_nil_from"]):
        return D(0), D(0)
    if p < D(f["cii_full_from"]):
        cii = D(f["cii_low"]) + (p - D(f["cii_min_profit"])) * D(f["cii_ramp_rate"]) / 100
    elif p <= D(f["cii_phaseout_from"]):
        cii = D(f["cii_full"])
    else:
        cii = D(f["cii_full"]) - (p - D(f["cii_phaseout_from"])) * D(f["cii_phaseout_rate"]) / 100
    co2 = D(f["co2_self_employed"])
    if p > D(f["cii_phaseout_from"]):
        co2 -= (p - D(f["cii_phaseout_from"])) * D(f["co2_phaseout_rate"]) / 100
    return up_to_cent(cii), up_to_cent(max(co2, D(0)))


def ccss(profit, f):
    """Yearly CCSS of a self-employed person on a profit (no maximum base, no Mutualité)."""
    p = D(profit)
    deductible = max(p, D(f["ccss_min_base_annual"])) * D(f["ccss_rate_deductible"]) / 100
    dependency = max(p, D(0)) * D(f["ccss_dependency_rate"]) / 100
    return deductible, dependency


def estimate(year, taxable, tax_class, both_professional=False, profits=None, withheld=0, advances=0, abatement=0, household_help_used=0, extra_professional_amount=None, salary_reconciliation=None, salary_context=None, single_parent_context=None, deduction_context=None):
    if tax_class not in (1, 2, "1a"):
        sys.exit("unsupported tax class; use 1, 2 or 1a")
    if tax_class == "1a" and year != 2025:
        sys.exit("class 1a automation is verified for 2025 only")
    if single_parent_context and tax_class != "1a":
        sys.exit("CIM requires the supported child-based class 1a context")
    f = figures(year)
    profits = {k: D(v) for k, v in (profits or {}).items() if v is not None}
    if both_professional and extra_professional_amount is None:
        sys.exit("extra-professional allowance: provide the reviewed amount after each spouse's income limit and tax-liability period")
    extra_prof = D(extra_professional_amount or 0)
    if not extra_prof.is_finite() or extra_prof < 0 or extra_prof > D(f["extra_professional_abatement"]):
        sys.exit("extra-professional allowance: reviewed amount outside the supported range")
    if extra_prof and (tax_class != 2 or not both_professional):
        sys.exit("extra-professional allowance: this calculator supports only the reviewed joint professional-income case")
    adjusted = D(taxable) - extra_prof - D(abatement)
    t = income_tax(adjusted, tax_class, f)
    credits, notes = {}, []
    per_person = {who: self_employed_credits(p, f) for who, p in profits.items()}
    if len(per_person) == 2:  # open point PIT-O-05: a second CII only for a helping spouse – count one
        keep = max(per_person, key=lambda w: sum(per_person[w]))
        notes.append("both spouses have a profit: one CII and CO2 credit counted (open point PIT-O-05)")
        per_person = {keep: per_person[keep]}
    for who, (cii, co2) in per_person.items():
        credits[f"CII {who}"], credits[f"CO2 credit {who}"] = cii, co2
    reconciliation = salary_reconciliation or {}
    if set(reconciliation) & set(profits):
        sys.exit("same-person salary/business credits require monthly ranking; cannot add both categories")
    salary_adjustment = sum((D(v["adjustment"]) for v in reconciliation.values()), D(0))
    single_parent = {}
    if single_parent_context:
        sys.path.insert(0, str(HOUSEHOLD_MODULE))
        import form100_single_parent as parent_credit
        single_parent = parent_credit.reconcile(adjusted, single_parent_context, f)
    after = t["tax"] - sum(credits.values(), D(0)) + salary_adjustment + single_parent.get("adjustment", D(0))
    raw_balance = after - D(withheld) - D(advances)
    # LIR154(2): positive final balance floors to euros;154(7) does not erase refund cents.
    balance = floor(raw_balance) if raw_balance > 0 else raw_balance
    return {"year": year, "class": tax_class, "taxable": D(taxable), "extra_professional_abatement": extra_prof,
            "other_abatements": D(abatement), "adjusted": adjusted, **t, "credits": credits, "tax_after_credits": after, "amount_before_payments": after,
            "withheld": D(withheld), "advances": D(advances), "balance_before_rounding": raw_balance,
            "balance_rounding": balance - raw_balance, "balance": balance,
            "salary_reconciliation": reconciliation, "salary_credit_adjustment": salary_adjustment,
            "salary_context": salary_context, "single_parent_reconciliation": single_parent, "notes": notes}


def what_if(args, options):
    """Tax and CCSS saved by extra deductions – each alone, then together."""
    f = figures(args["year"])
    for kind, value in options:
        salary.money(value, kind + " extra deduction")
    if (args.get("deduction_context") or {}).get("donations") and any(k == "business" and D(v) != 0 for k, v in options):
        sys.exit("donation what-if: changed business income changes the donation cap; regenerate and compare complete household cases")
    if D(args.get("household_help_used", 0)) and any(k == "household-help" for k, _ in options):
        sys.exit("household-help what-if: childcare already uses the shared ceiling; recalculate the monthly schedule first")
    if D(args.get("extra_professional_amount") or 0) > 0 and any(k == "business" and D(v) != 0 for k, v in options):
        sys.exit("business what-if: re-establish the spouse allowance for the changed profit; compare separately reviewed estimates")
    if (args.get('deduction_context') or {}).get('medical') and any(k in ('special', 'business') and amt for k, amt in options):
        sys.exit('medical what-if: recompute the normal burden for changed taxable income; compare reviewed households')
    base = estimate(**args)
    profits = {k: D(v) for k, v in (args.get("profits") or {}).items() if v is not None}
    owner = "taxpayer" if "taxpayer" in profits else next(iter(profits), None)
    rows = []

    def run(opts):
        a = dict(args)
        a["profits"] = dict(profits)
        special = sum((amt for k, amt in opts if k == "special"), D(0))
        abate = sum((amt for k, amt in opts if k == "abatement"), D(0))
        help_ = min(sum((amt for k, amt in opts if k == "household-help"), D(0)), D(f["household_help_cap"]))
        business = sum((amt for k, amt in opts if k == "business"), D(0))
        ccss_saved = D(0)
        a["taxable"] = D(args["taxable"]) - special
        if business:
            if owner is None:
                sys.exit("business=… needs a self-employed profit (--profit or --spouse-profit)")
            old, new = profits[owner], profits[owner] - business
            ded_old, dep_old = ccss(old, f)
            ded_new, dep_new = ccss(new, f)
            ccss_saved = (ded_old - ded_new) + (dep_old - dep_new)
            a["taxable"] -= business - (ded_old - ded_new)  # the deductible contributions fall too
            a["profits"][owner] = new
        a["abatement"] = D(args.get("abatement", 0)) + abate + help_
        r = estimate(**a)
        tax_saved = base["tax_after_credits"] - r["tax_after_credits"]
        paid = special + abate + help_ + business
        return {"tax_saved": tax_saved, "ccss_saved": ccss_saved.quantize(D("0.01")), "paid": paid,
                "saved": (tax_saved + ccss_saved).quantize(D("0.01")),
                "pct": ((tax_saved + ccss_saved) / paid * 100).quantize(D("0.1")) if paid else D(0),
                "cost_after": (paid - tax_saved - ccss_saved).quantize(D("0.01"))}

    for kind, amt in options:
        rows.append((f"{kind}={amt}", run([(kind, amt)])))
    if len(options) > 1:
        rows.append(("all together", run(options)))
    return base, rows


def from_household(path, year=None, advances=None):
    sys.path.insert(0, str(HOUSEHOLD_MODULE))
    import form100_household as hh  # lu-annual-return: the household file and its indicative check
    h = hh.load(path)
    if year and int(year) != int(h["tax_year"]) and any(h.get(k) for k in ("consumer_loans", "donations", "single_parent_credit", "salary_costs", "occupational_pension", "voluntary_contributions", "medical_expenses", "partnership")):
        sys.exit("new deduction fields: re-establish eligibility and ceilings before estimating another year")
    deduction_context = {"donations": bool(h.get("donations")), "medical": bool(h.get("medical_expenses"))}
    if h.get("salaries"):
        chosen_year = int(year or h["tax_year"])
        if advances is not None:
            h["advances_paid"] = advances
        calculated = salary.prepare(h, hh, figures(chosen_year), chosen_year)
        check = hh.indicative_check(h)
        return {"deduction_context": deduction_context, "year": chosen_year, "taxable": check["taxable income"],
                "abatement": check["childcare abatement"] + check["medical abatement"],
                "household_help_used": check["childcare abatement"], **calculated}
    sp = h.get("spouse")
    status = h["taxpayer"].get("status", "MA" if sp else "CE")
    tax_class = 2 if sp and (status == "MA" or (status == "PA" and h.get("joint_taxation_option"))) else 1
    if h.get("single_parent_credit"):
        tax_class = "1a"
    if h.get("children") and tax_class not in (2, "1a"):
        sys.exit("household has children: class 1a/CIM calculation needs manual review; class 1 must not be assumed")
    if any(c.get("request_rebate") for c in h.get("children", [])):
        sys.exit("child tax rebate requested: final credits need manual review; no balance estimated")
    if any(h.get(k) for k in ("children", "own_home", "childcare")) and year and int(year) != int(h["tax_year"]):
        sys.exit("family fields: re-establish eligibility and ceilings before estimating another year")
    professional = {s["owner"] for s in h.get("salaries", [])} | {b["owner"] for b in h.get("businesses", [])}
    profits = {}
    for b in h.get("businesses", []):
        profits[b["owner"]] = profits.get(b["owner"], D(0)) + hh.profit(b)
    return {"deduction_context": deduction_context, "single_parent_context": hh.single_parent.context(h) if h.get("single_parent_credit") else None,
            "year": int(year or h["tax_year"]), "taxable": hh.indicative_check(h)["taxable income"], "tax_class": tax_class,
            "both_professional": professional >= {"taxpayer", "spouse"}, "profits": profits,
            "extra_professional_amount": h.get("extra_professional_amount"),
            "withheld": sum((D(s.get("withheld", 0)) for s in h.get("salaries", [])), D(0)),
            "advances": D(advances if advances is not None else h.get("advances_paid", 0)),
            "abatement": hh.indicative_check(h)["childcare abatement"] + hh.indicative_check(h)["medical abatement"],
            "household_help_used": hh.indicative_check(h)["childcare abatement"]}


def eur(x):
    return f"€{D(x):,.2f}"


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--household", help="Form 100 household file (lu-annual-return form100-tools.md)")
    ap.add_argument("--year", type=int)
    ap.add_argument("--taxable", type=float, help="taxable income, Form 100 box 2038")
    ap.add_argument("--class", dest="tax_class", type=lambda x: x if x == "1a" else int(x), choices=(1, 2, "1a"))
    ap.add_argument("--both-professional", action="store_true", help="class 2: qualifying professional income, with a separately reviewed allowance")
    ap.add_argument("--extra-professional-amount", type=str, help="reviewed allowance after art.129b income and liability-period limits")
    ap.add_argument("--profit", type=float, help="taxpayer's business profit (for the CII and CO2 credit)")
    ap.add_argument("--spouse-profit", type=float)
    ap.add_argument("--withheld", type=float, default=0)
    ap.add_argument("--advances", type=float)
    ap.add_argument("--abatement", type=float, default=0, help="other abatements already allowed")
    ap.add_argument("--what-if", action="append", default=[], metavar="KIND=AMOUNT",
                    help="special, abatement, household-help or business")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    if a.household:
        args = from_household(a.household, a.year, a.advances)
    else:
        if a.taxable is None or a.tax_class is None or a.year is None:
            ap.error("give --household, or --year, --taxable and --class")
        args = {"year": a.year, "taxable": D(a.taxable), "tax_class": a.tax_class, "both_professional": a.both_professional,
                "profits": {k: v for k, v in (("taxpayer", a.profit), ("spouse", a.spouse_profit)) if v is not None},
                "withheld": D(a.withheld), "advances": D(a.advances or 0),
                "extra_professional_amount": a.extra_professional_amount}
    args["abatement"] = D(args.get("abatement", 0)) + D(a.abatement)
    options = []
    for item in a.what_if:
        kind, _, amount = item.partition("=")
        if kind not in ("special", "abatement", "household-help", "business") or not amount:
            ap.error(f"--what-if {item!r}: use special=, abatement=, household-help= or business=")
        options.append((kind, D(amount)))
    base, rows = what_if(args, options)

    if a.json:
        print(json.dumps({"estimate": base, "what_if": dict(rows)}, default=str, indent=2))
        return
    print(f"Tax year {base['year']}, class {base['class']}")
    print(f"  taxable income                {eur(base['taxable']):>14}")
    if base["extra_professional_abatement"]:
        print(f"  − extra-professional abatement {eur(base['extra_professional_abatement']):>13}")
    if base["other_abatements"]:
        print(f"  − other abatements            {eur(base['other_abatements']):>14}")
    print(f"  base (rounded down to €50)    {eur(base['base']):>14}")
    print(f"  scale tax                     {eur(base['scale_tax']):>14}")
    print(f"  + Employment Fund surcharge   {eur(base['surcharge']):>14}")
    print(f"  = income tax                  {eur(base['tax']):>14}")
    for k, v in base["credits"].items():
        print(f"  − {k:27} {eur(v):>14}")
    for who, row in base["salary_reconciliation"].items():
        paid = sum(row["paid"].values(), D(0))
        retained = sum(row["retained"].values(), D(0))
        print(f"  {who} salary credits: paid {eur(paid)}, retained {eur(retained)}")
        print(f"    credit adjustment {eur(row['adjustment'])}; waived recovery {eur(row['waived_recovery'])}")
    if base["single_parent_reconciliation"]:
        row = base["single_parent_reconciliation"]
        print(f"  CIM: paid {eur(row['paid'])}, retained {eur(row['retained'])}; adjustment {eur(row['adjustment'])}")
    print(f"  = before withholding/advances {eur(base['amount_before_payments']):>14}")
    print(f"  − tax withheld                {eur(base['withheld']):>14}")
    print(f"  − advances paid               {eur(base['advances']):>14}")
    if base["balance_rounding"]:
        print(f"  final-balance rounding        {eur(base['balance_rounding']):>14}")
    print(f"  = {'balance to pay' if base['balance'] >= 0 else 'refund':27} {eur(abs(base['balance'])):>14}")
    print(f"  marginal rate: {base['band']}% band × surcharge = {base['marginal']}% on the next euro deducted")
    for note in base["notes"]:
        print(f"  note: {note}")
    if rows:
        print("What if (saving = tax + CCSS; cost after = what is paid less the saving):")
        for name, r in rows:
            print(f"  {name:24} tax {eur(r['tax_saved']):>11}  CCSS {eur(r['ccss_saved']):>10}  saved {eur(r['saved']):>11}"
                  f" ({r['pct']}%)  cost after {eur(r['cost_after']):>11}")
    print("An estimate: the ACD's bulletin decides; scope and any manual-review boundaries are documented.")


if __name__ == "__main__":
    main()
