"""2025 ordinary-salary assessment bridge; see references/salary-balance-calculator.md.

No payroll engine: use certified paid credits and reviewed annual deductions. Source rules:
LIR 154/154quater/129b and circular 152ter/1,154quater/2,154quinquies/2 of 12 March 2025.
"""
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR


def need(ok, message):
    if not ok:
        raise SystemExit("salary balance: " + message)


def money(value, name, signed=False):
    need(value is not None and not isinstance(value, bool), name + " is unknown; missing is not zero")
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        raise SystemExit("salary balance: " + name + " must be a finite monetary amount")
    need(amount.is_finite(), name + " must be finite")
    need(signed or amount >= 0, name + " must be non-negative")
    need(amount == amount.quantize(Decimal(".01")), name + " must be stated to cents")
    return amount


def annual_credits(gross, f):
    """Full eligible year only; floor aggregated gross once, round each credit up to cents."""
    g = money(gross, "annual salary gross").to_integral_value(rounding=ROUND_FLOOR)
    if g < f["cis_min_gross"] or g >= f["cis_nil_from"]:
        return {"cis": Decimal(0), "co2": Decimal(0)}
    if g < f["cis_full_from"]:
        cis = Decimal(str(f["cis_ramp_base"])) + (g - f["cis_min_gross"]) * Decimal(str(f["cis_ramp_rate"])) / 100
    elif g <= f["cis_phaseout_from"]:
        cis = Decimal(str(f["cis_full"]))
    else:
        cis = Decimal(str(f["cis_full"])) - (g - f["cis_phaseout_from"]) * Decimal(str(f["cis_phaseout_rate"])) / 100
    co2 = Decimal(str(f["co2_employee"]))
    if g > f["cis_phaseout_from"]:
        co2 -= (g - f["cis_phaseout_from"]) * Decimal(str(f["co2_employee_phaseout_rate"])) / 100
    return {"cis": cis.quantize(Decimal(".01"), rounding=ROUND_CEILING),
            "co2": max(co2, Decimal(0)).quantize(Decimal(".01"), rounding=ROUND_CEILING)}


def reconcile(person, f):
    """One person, one ordinary salary category; no cross-spouse credit ranking."""
    paid = {k: money(person.get(k), "paid " + k) for k in ("cis", "co2")}
    gate = person["card_count"] > 1 or person["without_card"]
    if not gate:
        need(person.get("payroll_final") is True,
             "one-card credits need a final/corrected payroll certificate; do not create another annual credit")
        retained = dict(paid)
        method = "payroll_final_no_assessment_recalculation"
    else:
        need(person.get("full_year_eligible") is True,
             "partial or unknown credit eligibility period needs the monthly/day reconciliation; no full-year assumption")
        retained = annual_credits(person["gross"], f)
        method = "full_year_ordinary_salary_reconciliation"
    components = {k: paid[k] - retained[k] for k in paid}
    raw = sum(components.values(), Decimal(0))
    threshold = Decimal(str(f["credit_recovery_minimum"]))
    waive = lambda x: Decimal(0) if 0 < x < threshold else x
    adjustment = waive(raw)
    # S57 expressly separates spouses, but does not explicitly define whether the two
    # credit components share the small-recovery unit. Do not guess where it changes tax.
    need(adjustment == sum((waive(x) for x in components.values()), Decimal(0)),
         "CIS/CO2 small-recovery grouping changes the result; manual review required (PIT-O-24)")
    return {"method": method, "gross": person["gross"], "paid": paid, "retained": retained,
            "component_adjustments": components, "raw_adjustment": raw,
            "waived_recovery": raw - adjustment, "adjustment": adjustment}


def full_year_coverage(periods, year):
    cursor = date(year, 1, 1)
    for start, end in sorted(periods):
        if start > cursor:
            return False
        cursor = max(cursor, end + timedelta(days=1))
    return cursor > date(year, 12, 31)


def replacement_allowance_bounds(h, hh, f, records):
    """Prove the full129b cap without relying on95a eligibility or benefit gross.

    All costs/contributions are subtracted, even those attributable to excluded
    replacement income. S may contain unitemised CNS advances, so its label alone
    does not prove the ordinary component. Keep the evidenced split explicit.
    """
    review = h['salary_balance'].get('extra_professional_review') or {}
    people = review.get('people') or {}
    need(review.get('evidence') and set(people) == {'taxpayer', 'spouse'},
         'replacement benefit: separate reviewed ordinary activity/gross split required for both spouses')
    limits = {}
    cap = Decimal(str(f['extra_professional_abatement']))
    for side in ('taxpayer', 'spouse'):
        facts = people[side]
        need(facts.get('ordinary_activity_current_year') is True
             and facts.get('ordinary_activity_affiliation_confirmed') is True
             and facts.get('ordinary_gross_excludes_replacements') is True
             and facts.get('activity_evidence') and facts.get('gross_split_evidence'),
             side + ': ordinary article95 activity, affiliation and gross excluding all replacements must be evidenced')
        ordinary = money(facts.get('ordinary_article95_gross'), side + ' ordinary article95 gross')
        # Only ordinary S can support this bound; exclude direct benefits and known IMAL.
        maximum = sum((money(p['amount'], 'ordinary salary component')
                       for s in records if s['owner'] == side and not hh.salary_details.replacement(s)
                       for p in s['pay'] if p['kind'] == 'S'), Decimal(0))
        need(0 < ordinary <= maximum, side + ': reviewed ordinary gross exceeds eligible salary records or is zero')
        costs = hh.salary_costs(h, side)
        costs += sum((money(s['travel'], 'commuting') + hh.salary_details.exemptions(s)
                      for s in records if s['owner'] == side), Decimal(0))
        costs += hh.contributions(h, side) + Decimal(str(f['special_expenses_flat_minimum']))
        limits[side] = ordinary - costs
        need(limits[side] >= cap,
             'replacement benefit: conservative ordinary-income bound is below the full extra-professional cap; article95a interaction needs review')
    return limits


def prepare(h, hh, f, year):
    """Validate explicit case facts, then derive calculator inputs from the same household.

    Unknown evidence never becomes zero or full-year eligibility. This narrower contract is
    for the balance calculator; existing PDF/XML preparation remains a separate capability.
    """
    review = h.get("salary_balance")
    need(isinstance(review, dict), "provide salary_balance facts to reconcile credits; see salary-balance-calculator.md")
    need(year == 2025 and int(h["tax_year"]) == year, "automatic salary balances support tax year 2025 only")
    need(h.get("resident_full_year") is True and h.get("tax_liability_months", 12) == 12,
         "full-year resident tax liability must be established")
    need(review.get("income_and_deductions_complete") is True,
         "confirm all income and eligible deductions are represented in the supported household fields")
    need(isinstance(review.get("evidence"), str) and review["evidence"].strip(),
         "record the evidence/review supporting the household and annual tax class")
    tax_class = review.get("tax_class")
    need((type(tax_class) is int and tax_class in (1, 2)) or tax_class == "1a", "explicit reviewed tax class 1, 2 or class 1a required")
    spouse = h.get("spouse")
    alone = review.get("class2_alone")
    need((tax_class == 2 and (spouse or alone)) or (tax_class in (1, "1a") and not spouse),
         "use a single class-1 household, a joint class-2 household or a reviewed class-2 year assessed alone; individual spouse taxation needs separate preparation")
    need(not h.get("individual_taxation"), "individual spouse taxation requires separate preparation")
    need(not alone or (tax_class == 2 and not spouse), "class2_alone is for one person assessed alone in class 2")
    latest = hh.events.sequence(h, "taxpayer")[-1]
    if alone:
        # Art. 119 no. 3 b) and c) LIR: the three tax years after the year of the court's permission or of the death.
        need(isinstance(alone, dict) and alone.get("ground") in ("separation", "widowed")
             and isinstance(alone.get("evidence"), str) and alone["evidence"].strip() and type(alone.get("event_year")) is int,
             "class2_alone: ground (separation or widowed), event_year and evidence required")
        need(1 <= year - alone["event_year"] <= 3, "class2_alone: class 2 covers only the three tax years after the year of the decision or death")
        if alone["ground"] == "separation":
            need(alone.get("no_use_in_five_years_before") is True, "class2_alone: establish that the transition was not used in the five years before")
            need(latest[0] in ("SV", "DI"), "class2_alone: a separation needs the status SV or DI")
        else:
            need(latest[0] == "VE", "class2_alone: a widowed person needs the status VE")
    if spouse and hh.events.status_used(h):
        need(hh.events.joint_married(h), "joint household status must be consistent")
        died = hh.events.death_date(h)
        need(died is None or died == date(year, 12, 31),
             "a spouse died during the year: whether the flat amounts are cut to months is not settled (PIT-O-40); prepare the balance by hand")
    elif spouse:
        status = h["taxpayer"].get("status")
        need(status == spouse.get("status") and status in ("MA", "PA"), "joint household status must be consistent")
        need(status == "MA" or h.get("joint_taxation_option") is True, "PACS joint assessment must be established")
    need(not any(c.get("request_rebate") for c in h.get("children", [])),
         "CIM/child rebate requires its separate credit calculation")
    need(tax_class in (2, "1a") or not h.get("children"),
         "children in a non-class-2 household require class 1a/CIM review")
    ground = review.get("class_1a_ground")
    need((tax_class == "1a") == (bool(h.get("single_parent_credit")) or bool(ground)),
         "class 1a requires the supported reviewed single-parent request, or a reviewed ground (widowed, age)")
    if ground:
        # Art. 119 no. 2 a) and c) LIR: widowed persons, and persons aged 64 on 1 January. No single-parent credit without a child.
        need(not h.get("single_parent_credit") and not h.get("children"),
             "class_1a_ground is for class 1a without a child; with a child use the single-parent route")
        need(ground in ("widowed", "age") and isinstance(review.get("class_1a_evidence"), str) and review["class_1a_evidence"].strip(),
             "class_1a_ground: widowed or age, with class_1a_evidence")
        if ground == "widowed":
            since = h["taxpayer"].get("status_since")
            need(latest[0] == "VE" and since and year - int(str(since)[:4]) >= 4,
                 "class 1a as a widowed person starts in the fourth year after the death (class 2 before): status VE with status_since required")
        else:
            need(hh.age_on_1_jan(str(h["taxpayer"]["national_id"]), year) >= 64, "class 1a by age needs 64 completed years on 1 January")
    people = review.get("people")
    need(isinstance(people, dict), "per-person credit facts required")
    salary_owners = {s["owner"] for s in h["salaries"]}
    business_owners = {v["owner"] for v in h.get("businesses", [])}
    owners = salary_owners | business_owners
    need(not salary_owners & business_owners, "one person's mixed salary/business credits need the monthly category-ranking calculation")
    need(not owners - ({"taxpayer", "spouse"} if spouse else {"taxpayer"}), "income owner is not in this household")
    need(set(people) == owners, "credit facts must cover exactly the income recipients")
    for side, facts in people.items():
        need(isinstance(facts, dict) and facts.get("compulsory_affiliation") is True,
             side + ": establish personal compulsory affiliation for the income")
        if side in business_owners:
            need(facts.get("full_year_eligible") is True, side + ": business credit period must be a full year")
            need(any(c.get("owner") == side for c in h.get("ccss_self_employed", [])),
                 side + ": explicit deductible business contributions required, including evidenced zero")
    for c in h.get("ccss_self_employed", []):
        need(c.get("owner") in business_owners, "self-employed contributions need the corresponding business income")
        money(c.get("deductible"), "business deductible contributions")
    for group in ("insurance", "home_savings", "pension_plans"):
        for item in h.get(group, []):
            money(item.get("amount"), group + " amount")
            if group in ("home_savings", "pension_plans") or "holder" in item:
                need(item.get("holder") in ({"taxpayer", "spouse"} if spouse else {"taxpayer"}),
                     group + ": deduction holder is not in this household")

    people_credit, periods, cards = {}, {}, {}
    seen, fingerprints = set(), set()
    records = h["salaries"]
    record_ids = [s.get("certificate_id") for s in records]
    withholding = Decimal(0)
    for s in records:
        side = s["owner"]
        need('includes_cns_advances' not in s or type(s['includes_cns_advances']) is bool,
             'includes_cns_advances must be boolean when supplied')
        need(s.get("tax_regime") == "ordinary" and (s.get("occupation", "SALA") == "SALA" or (hh.salary_details.replacement(s) and s.get("occupation") == "DEMP")),
             "explicit ordinary employee regime required; domestic-flat/manager/special pay remains manual")
        need(s.get("all_pay_luxembourg_taxable") is True,
             "establish that all salary components are Luxembourg-taxable; foreign/exempt progression needs separate treatment")
        cid = s.get("certificate_id")
        need(isinstance(cid, str) and cid.strip() and cid not in seen, "missing or duplicate logical certificate_id")
        need(not s.get("replaces") or s["replaces"] not in record_ids,
             "a corrected certificate and its replaced version cannot both be included")
        seen.add(cid)
        need("tax_card_id" in s and (s["tax_card_id"] is None or isinstance(s["tax_card_id"], str) and s["tax_card_id"].strip()),
             cid + ": state the tax-card identity, or null for evidenced absence; do not count certificates as cards")
        try:
            start, end = date.fromisoformat(s["start"]), date.fromisoformat(s["end"])
        except (KeyError, TypeError, ValueError):
            raise SystemExit("salary balance: " + cid + ": valid employment dates required")
        need(start <= end and start.year == year and end.year == year, cid + ": covered dates must be inside the tax year")
        periods.setdefault(side, []).append((start, end))
        cards.setdefault(side, set()).add(s["tax_card_id"])
        need(s.get("pay") and (hh.salary_details.replacement(s) or all(v.get("kind") in ("S", "IMAL") for v in s["pay"])),
             cid + ": only ordinary salary and employer-advanced sickness are supported")
        gross = sum((money(v.get("amount"), cid + " pay component") for v in s["pay"]), Decimal(0))
        social = money(s.get("contributions"), cid + " deductible contributions")
        travel = money(s.get("travel"), cid + " reviewed commuting")
        paid = {k: money(s.get(k), cid + " paid " + k) for k in ("cis", "co2")}
        withheld = money(s.get("withheld"), cid + " withholding", signed=True)
        basis = s.get("withholding_basis")
        need(basis in ("before_cis_co2", "after_cis_co2", "before_cis_co2_cim", "after_cis_co2_cim"), cid + ": establish whether withholding is before or after CIS/CO2")
        precredit = hh.salary_withheld(s)
        need(precredit >= 0, cid + ": inconsistent negative withholding before credits")
        need((not s.get("cim") or bool(h.get("single_parent_credit"))) and not s.get("cihs"), cid + ": other paid tax credits require separate reconciliation")
        fingerprint = (side, s.get("employer"), s.get("employment_id"), start, end, gross, social, travel,
                       precredit, paid["cis"], paid["co2"], s["tax_card_id"])
        need(fingerprint not in fingerprints, "equivalent salary records may duplicate a certificate; resolve logical employment identity")
        fingerprints.add(fingerprint)
        withholding += precredit
        row = people_credit.setdefault(side, {"gross": Decimal(0), "cis": Decimal(0), "co2": Decimal(0)})
        row["gross"] += gross
        for key in paid:
            row[key] += paid[key]
    for side, row in people_credit.items():
        facts = people[side]
        full = facts.get("full_year_eligible") is True
        need(not full or full_year_coverage(periods[side], year),
             side + ": salary dates do not cover a full eligible year; reconcile the missing period")
        row.update(card_count=len(cards[side] - {None}), without_card=None in cards[side],
                   full_year_eligible=full, payroll_final=facts.get("payroll_final") is True)
    reconciliations = {side: reconcile(v, f) for side, v in people_credit.items()}
    profits = {}
    for business in h.get("businesses", []):
        profit = hh.profit(business)
        need(profit.is_finite(), "business profit must be finite")
        owner = business["owner"]
        profits[owner] = profits.get(owner, Decimal(0)) + profit
    # Art.129b(3): supported ordinary active income, less earning costs, related
    # compulsory contributions and the person's article113 minimum. No pension/cessation route.
    both = bool(spouse) and owners == {"taxpayer", "spouse"}
    allowance, limits = Decimal(0), {}
    allowance_method = 'ordinary_income_limiter'
    if both:
        for side in ("taxpayer", "spouse"):
            net = profits.get(side, Decimal(0))
            if side in salary_owners:
                net += people_credit[side]["gross"] - hh.salary_costs(h, side) - sum((hh.salary_details.exemptions(s) for s in records if s["owner"] == side), Decimal(0))
                net -= sum((money(s["travel"], "commuting") for s in records if s["owner"] == side), Decimal(0))
            net -= hh.contributions(h, side) + Decimal(str(f["special_expenses_flat_minimum"]))
            limits[side] = max(net, Decimal(0))
        allowance = min(Decimal(str(f["extra_professional_abatement"])), *limits.values())
        uncertain_replacement = any(
            (hh.salary_details.replacement(s) and s.get('replacement_kind') != 'unemployment')
            or s.get('includes_cns_advances') is True or any(p['kind'] == 'IMAL' for p in s['pay'])
            for s in records)
        if uncertain_replacement:
            need(salary_owners == {'taxpayer', 'spouse'} and not business_owners,
                 'replacement benefit: invariant route requires independently evidenced ordinary salary for both spouses')
            limits = replacement_allowance_bounds(h, hh, f, records)
            allowance = Decimal(str(f['extra_professional_abatement']))
            allowance_method = 'full_cap_proved_without_replacement_income'
    if h.get("extra_professional_amount") is not None:
        supplied = money(h["extra_professional_amount"], "reviewed spouse allowance")
        need(supplied == allowance, "supplied spouse allowance differs from this supported-case computation; review the additional facts")
    advances = money(h.get("advances_paid"), "advances paid (explicit zero if none)")
    return {"tax_class": tax_class, "both_professional": both, "profits": profits,
            "extra_professional_amount": allowance, "withheld": withholding, "advances": advances,
            "salary_reconciliation": reconciliations,
            "single_parent_context": hh.single_parent.context(h) if h.get("single_parent_credit") else None,
            "salary_context": {"scope": "2025_resident_ordinary_salary", "allowance_limits": limits,
                               "allowance_method": allowance_method,
                               "evidence": review["evidence"], "withholding_basis": "before_cis_co2"}}
