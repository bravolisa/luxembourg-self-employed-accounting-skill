"""The household file behind every Form 100 output: checks, PDF boxes, receipts, indicative tax base.

One household file (format: references/forms/2025/form100-tools.md) feeds
- build_form100_xml.py      – the MyGuichet pre-fill XML,
- fill_form100_pdf.py       – the filled PDF (via to_pdf_values),
- make_receipts_annex.py    – the « Détail des recettes » annex (via receipts_breakdown),
so the three cannot drift apart. Figures (ceilings, flat amounts) come from figures().
2025 children, childcare and own-home interest: form100_family.py and form100-family.md.
Not covered yet (load() stops): rental, pensions, capital income, incoming donation carryforwards, other extraordinary charges.
"""
import form100_events as events
import form100_family as family
import form100_deductions as deductions
import form100_single_parent as single_parent
import form100_employment_deductions as employment
import form100_medical as medical
import form100_salary_details as salary_details
import json
import re
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

NOT_COVERED = ("rental", "pensions", "capital_income", "extraordinary_charges")
SIDES = ("taxpayer", "spouse")

# Captions for the PDF where the household gives only a code
RISK_LABELS = {"SC": "Suivant certificat", "PU": "Prime unique (assurance temporaire au décès)", "AV": "Assurance vie",
               "AD": "Assurance décès", "VV": "Véhicule (montants déductibles)", "AA": "Accidents",
               "AC": "Dommages corporels", "AI": "Invalidité", "AM": "Maladie", "AS": "Santé",
               "RC": "Responsabilité civile", "AJ": "Indemnité journalière", "AU": "Autre"}
SAVINGS_BANKS = {"BB": "BHW Bausparkasse", "WB": "Wüstenrot Bausparkasse", "BH": "Bausparkasse Schwäbisch Hall",
                 "BS": "Bausparkasse der Sparkassen", "AB": "Aachener Bausparkasse", "AL": "Alte Leipziger Bauspar",
                 "BM": "Bausparkasse Mainz", "BQ": "BSQ Bauspar", "DB": "Debeka Bausparkasse",
                 "DE": "Deutsche Bausparkasse Badenia", "SI": "Signal Iduna Bauspar", "SB": "Start Bausparkasse"}
STATUS_RADIO = {"CE": "/celibataire", "MA": "/marie", "DI": "/divorce", "VE": "/veuf"}


def stop(msg):
    sys.exit(msg)


def need(cond, msg):
    if not cond:
        stop(msg)


def D(x):
    return Decimal(str(x))


def figures(year):
    """Ceilings and flat amounts for a tax year (see FIGURES_SOURCE)."""
    table = _load_figures()
    need(str(year) in table, f"no figures for tax year {year} in {FIGURES_SOURCE.name}")
    return {k: v["value"] for k, v in table[str(year)].items()}


FIGURES_SOURCE = Path(__file__).resolve().parents[2] / "lu-tax-core" / "data" / "tool-figures.json"


def _load_figures():
    need(FIGURES_SOURCE.exists(), f"figures file missing: {FIGURES_SOURCE}")
    return json.loads(FIGURES_SOURCE.read_text(encoding="utf-8"))["years"]


def load(path):
    h = json.loads(Path(path).read_text(encoding="utf-8"))
    validate(h)
    return h


def validate(h):
    for k in NOT_COVERED:
        need(not h.get(k), f"'{k}' is not covered by the Form 100 tools yet: leave it out and enter it in MyGuichet")
    need(int(h.get("tax_year", 0)) >= 2025, "tax_year missing")
    for side in SIDES:
        p = h.get(side)
        if side == "spouse" and not p:
            continue
        need(p and re.fullmatch(r"(19|20)\d{11}", str(p.get("national_id", ""))),
             f"{side}: national_id must be the 13-digit matricule")
        need(p.get("last_name"), f"{side}: last_name missing")
    need(re.fullmatch(r"\d{11}", str(h.get("file_number", ""))), "file_number must have 11 digits")
    if h.get("filed_by") == "agent":
        ag = h.get("agent") or {}
        need(ag.get("last_name") and (ag.get("phone") or ag.get("email")), "agent: last_name and a phone or an e-mail")
    for b in h.get("businesses", []):
        need(b.get("kind") in ("commercial", "liberal"), f"business kind must be commercial or liberal, not {b.get('kind')!r}")
        need(b.get("owner") in SIDES, "business owner must be taxpayer or spouse")
        if b.get("receipts_breakdown"):
            total = receipts_breakdown(h, b)["total"]
            need(total == D(b["receipts"]), f"receipts_breakdown adds up to {total}, receipts are {b['receipts']}")
    for s in h.get("salaries", []):
        need(s.get("owner") in SIDES and (s.get("workplaces") or salary_details.replacement(s)), "each salary needs an owner and its workplace commune(s)")

    events.validate(h)  # first: the other checks rely on who is taxed jointly
    _check_special_payments(h)
    salary_details.validate(h)
    employment.validate(h)
    deductions.validate(h)
    _check_single_premium(h)
    _check_salary_inputs(h)
    family.validate(h)
    single_parent.validate(h)
    medical.validate(h)

def _check_special_payments(h):
    def review(record):
        if 'special_payment_review' not in record:
            return  # Legacy inputs still need document review; absence is not proof of absence.
        value = record['special_payment_review']
        need(isinstance(value, dict) and value.get('status') == 'clear'
             and isinstance(value.get('evidence'), str) and bool(value['evidence'].strip()),
             'special-payment review: present, unclear or undocumented findings require manual preparation; do not assume zero')
    review(h)
    special = ('employer_interest_support', 'termination_payment')
    need(not any(h.get(k) for k in special),
         "special employment payments: reconcile employer interest support or termination compensation manually; automatic household output is not supported")
    home = h.get('own_home') or {}
    groups = [home.get('loans', []) if isinstance(home, dict) else [], h.get('consumer_loans', [])]
    loans = [l for group in groups if isinstance(group, list) for l in group if isinstance(l, dict)]
    need(not any(l.get('employer_interest_support') for l in loans),
         "employer interest support: distinguish exempt cash reimbursement from taxable benefit and employer-loan savings before computing deductible interest; automatic output is not supported")
    for s in h.get("salaries", []):
        review(s)
        need(not any(s.get(k) for k in special)
             and not any(str(p.get(key, '')).strip().upper() in ('PPPH', 'IDPT', 'IDEP', 'IDCC', 'REX1', 'REX2')
                         for p in s.get('pay', []) + s.get('exemptions', []) for key in ('kind', 'source_code')),
             "special employment payments: PPPH/IDPT/IDEP/IDCC/REX1/REX2 require reviewed benefit, termination or extraordinary-income treatment; automatic output is not supported")


def _check_salary_inputs(h):
    """Reject unhandled regimes and unreconciled commuting; do not infer from issuer names."""
    f = figures(int(h["tax_year"]))
    for s in h.get("salaries", []):
        need(s.get("tax_regime", "ordinary") == "ordinary"
             and s.get("occupation", "SALA") not in ("SRF5", "SRFA")
             and not any(p.get("kind") in ("SALF", "SAFA") for p in s.get("pay", [])),
             "flat-tax salary: establish the household-wide regularisation choice and use "
             "lu-income-tax-personal references/domestic-employment-income.md; automatic output is not supported")
        travel = D(s.get("travel", 0))
        need(travel.is_finite() and travel >= 0, "salary commuting must be a known non-negative amount")
    if h.get("salaries"):
        need(h.get("tax_liability_months", 12) == 12,
             "part-year tax liability: review salary flat costs and allowances manually")
    for side in SIDES:
        mine = [s for s in h.get("salaries", []) if s["owner"] == side]
        gross = sum((D(p["amount"]) for s in mine for p in s["pay"]), D(0))
        travel = sum((D(s.get("travel", 0)) for s in mine), D(0))
        need(travel <= min(max(gross, D(0)), D(f["commuting_cap"])),
             "salary commuting exceeds the person's receipts or annual ceiling; reconcile workplaces and periods")


def salary_flat_costs(h, side):
    """Art.107(5): one salary flat per person, limited to receipts after commuting."""
    mine = [s for s in h.get("salaries", []) if s["owner"] == side]
    gross = sum((D(p["amount"]) for s in mine for p in s["pay"]), D(0))
    travel = sum((D(s.get("travel", 0)) for s in mine), D(0))
    return min(D(figures(int(h["tax_year"]))["salary_flat_costs"]), max(gross - travel, D(0)))


def salary_costs(h, side):
    actual = employment.actual_cost(h, side)
    return salary_flat_costs(h, side) if actual is None else actual


def salary_withheld(s):
    """Keep PDF, XML and estimates on separately certified pre-credit withholding.

    Legacy inputs omit the basis and already mean before-credit withholding. New balance
    inputs must declare it; do not silently export a net-of-credit tax as the gross withholding.
    """
    basis = s.get("withholding_basis", "before_cis_co2")
    need(basis in ("before_cis_co2", "after_cis_co2", "before_cis_co2_cim", "after_cis_co2_cim"), "salary withholding: establish before or after CIS/CO2")
    if basis in ("after_cis_co2", "after_cis_co2_cim"):
        need(s.get("withheld") is not None and s.get("cis") is not None and s.get("co2") is not None,
             "net salary withholding requires known withholding and CIS/CO2; missing is not zero")
    need(s.get("withheld", 0) is not None, "salary withholding is unknown")
    amount = D(s.get("withheld", 0))
    if basis in ("after_cis_co2", "after_cis_co2_cim"):
        amount += D(s["cis"]) + D(s["co2"])
        if basis == "after_cis_co2_cim":
            amount += family.money(s.get("cim"), "paid CIM")
    need(amount.is_finite() and amount >= 0, "salary withholding before CIS/CO2 must be finite and non-negative")
    return amount


def profit(b):
    return D(b["profit"]) if b.get("method") == "BILA" else D(b["receipts"]) - D(b["expenses"])


def members(h):
    return 1 + bool(h.get("spouse")) + family.child_count(h)


def age_on_1_jan(national_id, year):
    born = date(int(national_id[:4]), int(national_id[4:6]), int(national_id[6:8]))
    return year - born.year - (0 if (born.month, born.day) == (1, 1) else 1)


def _check_single_premium(h):
    deductions.validate_premiums(h)



def allowed(h):
    """The capped special expenses the filer types on the PDF (1471, 1527/1528, 1551/1552, 1554)."""
    validate(h)
    year, f = int(h["tax_year"]), figures(int(h["tax_year"]))
    out = {}
    ins_total = sum((D(i["amount"]) for i in h.get("insurance", [])), D(0))
    out["premium_increases"] = deductions.premium_increases(h, f) if any(i.get("risk") == "PU" for i in h.get("insurance", [])) else {}
    out["insurance_ceiling"] = D(f["insurance_per_member"]) * members(h) + sum((v["increase"] for v in out["premium_increases"].values()), D(0))
    out["insurance"] = min(ins_total + deductions.interest(h), out["insurance_ceiling"])
    for side in SIDES:
        plans = [p for p in h.get("pension_plans", []) if p["holder"] == side]
        out[f"pension_{side}"] = min(sum((D(p["amount"]) for p in plans), D(0)), D(f["pension_plan_per_person"]))
    hsv = h.get("home_savings", [])
    if hsv:
        ages = [age_on_1_jan(h[i["holder"]]["national_id"], year) for i in hsv]
        per = f["home_savings_per_member_18_40"] if 18 <= min(ages) <= 40 else f["home_savings_per_member"]
        left = D(per) * members(h)
        for side in SIDES:  # the household ceiling, taxpayer's column first
            paid = sum((D(i["amount"]) for i in hsv if i["holder"] == side), D(0))
            out[f"home_savings_{side}"] = min(paid, left)
            left -= out[f"home_savings_{side}"]
    salaried = {s["owner"] for s in h.get("salaries", [])}
    minimum = D(f["special_expenses_flat_minimum"])
    out["flat_minimum"] = minimum
    if len(salaried) == 2:
        # Art.113(2): the second flat is limited by the lower spouse's salary after related costs/contributions.
        remaining = []
        for side in SIDES:
            mine = [s for s in h.get("salaries", []) if s["owner"] == side]
            gross = sum((D(p["amount"]) for s in mine for p in s["pay"]), D(0))
            costs = salary_costs(h, side) + sum((D(s.get("travel", 0)) + D(s["contributions"]) + salary_details.exemptions(s) for s in mine), D(0))
            costs += employment.related_salary_contributions(h, side, f)
            need(gross >= costs, "negative salary remainder: special-expense minimum requires manual review")
            remaining.append(gross - costs)
        out["flat_minimum"] += min(minimum, *remaining)
    covered = out["insurance"] + sum((out.get(f"pension_{s}", D(0)) for s in SIDES), D(0)) + \
        sum((out.get(f"home_savings_{s}", D(0)) for s in SIDES), D(0))
    covered += sum((employment.voluntary(h, side) for side in SIDES), D(0))
    out['occupational_pension'] = sum((employment.occupational(h, side, f) for side in SIDES), D(0))
    out["covered"] = max(covered, out["flat_minimum"])
    return out


def contributions(h, side):
    sal = sum((D(s["contributions"]) for s in h.get("salaries", []) if s["owner"] == side), D(0))
    ccss = sum((D(c["deductible"]) for c in h.get("ccss_self_employed", []) if c["owner"] == side), D(0))
    return sal + ccss


def indicative_check(h):
    """Taxable income as MyGuichet and box 2038 should show it."""
    validate(h)
    f = figures(int(h["tax_year"]))
    sal = h.get("salaries", [])
    salaried = {s["owner"] for s in sal}
    gross = sum((D(p["amount"]) for s in sal for p in s["pay"]), D(0))
    travel = sum((D(s.get("travel", 0)) for s in sal), D(0))
    salary_net = gross - sum((salary_costs(h, side) for side in salaried), D(0)) - travel - sum((salary_details.exemptions(s) for s in sal), D(0))
    business = sum((profit(b) for b in h.get("businesses", [])), D(0))
    special = allowed(h)["covered"] + allowed(h)["occupational_pension"] + sum((contributions(h, s) for s in SIDES), D(0))
    net_income = business + salary_net - family.home_allowed(h, f)["allowed"]
    gift = deductions.donations(h, net_income, f) if h.get("donations") else {"allowed": D(0)}
    need(not h.get("donations") or gift["allowed"] <= net_income - special,
         "donations: insufficient income after earlier special expenses; ordering/carry treatment requires review")
    special += gift["allowed"]
    taxable = business + salary_net - special - family.home_allowed(h, f)["allowed"]
    medical_result = medical.calculation(h, taxable, f)
    return {"medical abatement": medical_result['allowed'], "medical calculation": medical_result, "total net income": net_income, "donations": gift["allowed"], "business profit": business, "net salaries": salary_net, "special expenses": special,
            "own-home interest": family.home_allowed(h, f)["allowed"],
            "childcare abatement": family.childcare_allowed(h, f),
            "taxable income": business + salary_net - special - family.home_allowed(h, f)["allowed"]}


def receipts_breakdown(h, b):
    """The « Détail des recettes » lines of one business (receipts-and-expenses method)."""
    need(b.get("method", "REDE") == "REDE", "a receipts breakdown is for the receipts-and-expenses method only")
    rb = b.get("receipts_breakdown") or {}
    mut_ccss = sum((D(v) for c in h.get("ccss_self_employed", []) if c["owner"] == b["owner"]
                    for v in (c.get("mutualite") or {}).values()), D(0))
    mutualite = D(rb.get("mutualite", mut_ccss))
    need(mutualite == mut_ccss or not h.get("ccss_self_employed"),
         f"Mutualité in the breakdown ({mutualite}) differs from the CCSS certificate ({mut_ccss})")
    lines = [("customers", "Prestations et ventes encaissées (T.V.A. comprise)", D(rb.get("customers", b["receipts"])))]
    refunds = rb.get("vat_refunds", [])
    if refunds:
        for r in refunds:
            lines.append(("vat_refund", f"Remboursement du crédit de T.V.A. de l'année {r['vat_year']}, reçu de l'AED en {h['tax_year']}",
                          D(r["amount"])))
    else:
        lines.append(("vat_refund", "Remboursements de T.V.A. reçus de l'AED", D(0)))
    lines.append(("mutualite", "Remboursements Mutualité (suivant certificat CCSS)", mutualite))
    for o in rb.get("other", []):
        lines.append(("other", o["label"], D(o["amount"])))
    return {"lines": lines, "total": sum((x[2] for x in lines), D(0))}


# ---------------------------------------------------------------- Form 100 PDF (tax year 2025)

def to_pdf_values(h):
    """PDF field -> value for fill_form100_pdf.py, with the capped amounts already applied."""
    validate(h)
    need(int(h["tax_year"]) == 2025, "the PDF box map is for the 2025 form; add the new year's map first")
    v = {}
    tp, sp = h["taxpayer"], h.get("spouse")
    addr = h["address"]
    if h.get("tax_office"):
        v["T.Bureaux_d_imposition"] = h["tax_office"]
    if h.get("tax_office_address"):
        v["X.bureau_adress"] = h["tax_office_address"]
    v["F.0109"] = v["F.1"] = h["file_number"]
    for p, n in ((tp, 0), (sp, 1)):
        if not p:
            continue
        v[f"A.010{1 + n}"] = p["last_name"]
        if p.get("first_name"):
            v[f"A.010{3 + n}"] = p["first_name"]
        v[f"F.010{5 + n}"] = p["national_id"]
        if p.get("birth_place"):
            v[f"A.010{7 + n}"] = p["birth_place"]
        if p.get("profession"):
            v[f"A.011{0 + n}"] = p["profession"]
        if p.get("phone"):
            v[f"A.011{2 + n}"] = p["phone"]
        if p.get("email"):
            v[f"A.011{4 + n}"] = p["email"]
        v[f"A.011{6 + 2 * n}"] = str(addr.get("number", ""))
        v[f"A.011{7 + 2 * n}"] = addr.get("street", "")
        v[f"A.012{0 + 2 * n}"] = "L-" + str(addr["postcode"])
        v[f"A.012{1 + 2 * n}"] = addr["locality"]
        v[f"A.012{4 + n}"] = "LU"
    status = tp.get("status", "MA" if sp else "CE")
    if status in STATUS_RADIO:
        v["R.0301"] = STATUS_RADIO[status]
    if tp.get("status_since") and status != "CE":
        v["D.0305"] = _dmy(tp["status_since"])
    if sp and status == "MA" and h.get("joint_taxation_option"):
        v["C.0316"], v["R.0317"] = "/Yes", "/3"  # art. 3 L.I.R., ticked as an explicit request

    for key, value in events.pdf_values(h, _dmy).items():  # status after an event, separation, other addresses
        if value is None:
            v.pop(key, None)
        else:
            v[key] = value

    if h.get('partnership'):
        facts = h['partnership']
        v.update({'R.0301': '/celibataire', 'C.0312': '/Yes', 'D.0313': _dmy(facts['declaration_date']),
                  'R.0314': '/presente' if facts['certificate_already_presented'] else '/enannexe'})
    for b in h.get("businesses", []):
        col = 0 if b["owner"] == "taxpayer" else 1
        if b["kind"] == "commercial":
            _add(v, f"N.050{1 + col}", profit(b))
        elif b.get("method") == "BILA":
            _add(v, f"N.060{1 + col}", D(b["profit"]))
        else:
            _add(v, f"N.060{5 + col}", D(b["receipts"]))
            _add(v, f"N.06{9 + col:02d}", D(b["expenses"]))

    f = figures(int(h["tax_year"]))
    for side, col in (("taxpayer", 0), ("spouse", 1)):
        mine = [s for s in h.get("salaries", []) if s["owner"] == side]
        if not mine:
            continue
        boxes = [f"N.070{1 + col}", f"N.070{5 + col}"]  # first and second employment contract
        for i, s in enumerate(s for s in mine if not salary_details.replacement(s)):
            gross = sum((D(p["amount"]) for p in s["pay"]), D(0))
            if i < 2:
                _add(v, boxes[i], gross)
            else:
                v["A.0713"] = "Autres contrats de louage de service"
                _add(v, f"N.071{4 + col}", gross)
        v[f"N.074{3 + col}"] = salary_costs(h, side)
        travel = sum((D(s.get("travel", 0)) for s in mine), D(0))
        if travel:
            v[f"N.074{7 + col}"] = travel
        workplace_record = next((s for s in mine if not salary_details.replacement(s) and s.get('workplaces')), None)
        if workplace_record:
            v[f"A.075{1 + col}"] = workplace_record.get("workplace_label") or workplace_record["workplaces"][0].title()
        withheld = sum((salary_withheld(s) for s in mine), D(0))
        if withheld:
            v[f"N.190{1 + col}"] = withheld

    rows = [(1436 + 4 * i) for i in range(8)]
    ins = h.get("insurance", [])
    need(len(ins) <= len(rows), "more than 8 insurance lines: group them per insurer")
    for i, item in zip(rows, ins):
        v[f"A.{i}"] = item["insurer"]
        v[f"A.{i + 1}"] = item.get("label") or RISK_LABELS.get(item["risk"], item["risk"])
        v[f"N.{i + 2 + (0 if item['paid_by'] == 'taxpayer' else 1)}"] = D(item["amount"])
    a = allowed(h)
    if ins or h.get("consumer_loans"):
        v["N.1470"], v["N.1471"] = a["insurance_ceiling"], a["insurance"]

    plain = [p for p in h.get("pension_plans", []) if not p.get("pepp")]
    pepp = [p for p in h.get("pension_plans", []) if p.get("pepp")]
    for group, starts in ((plain, (1503, 1508)), (pepp, (1515, 1520))):
        need(len(group) <= 2, "more than two pension contracts of one kind: not covered")
        for s0, p in zip(starts, group):
            v[f"A.{s0}"] = p["insurer"]
            v[f"D.{s0 + 1}"], v[f"D.{s0 + 2}"] = _dmy(p["start"]), _dmy(p["end"])
            v[f"N.{s0 + 3 + (0 if p['holder'] == 'taxpayer' else 1)}"] = D(p["amount"])
    if h.get("pension_plans"):
        v["N.1527"], v["N.1528"] = a["pension_taxpayer"], a["pension_spouse"]

    hrows = (1529, 1534, 1539, 1544)
    hsv = h.get("home_savings", [])
    need(len(hsv) <= 4, "more than 4 home-savings contracts: not covered")
    for s0, c in zip(hrows, hsv):
        v[f"A.{s0}"] = c.get("bank_name") or SAVINGS_BANKS.get(c["bank"], c["bank"])
        v[f"F.{s0 + 1}"] = c.get("subscriber_id") or h[c["holder"]]["national_id"]
        v[f"D.{s0 + 2}"] = _dmy(c["contract_date"])
        _add(v, f"N.{s0 + 3 + (0 if c['holder'] == 'taxpayer' else 1)}", D(c["amount"]))
    if hsv:
        for side, box in (("taxpayer", "N.1551"), ("spouse", "N.1552")):
            if a.get(f"home_savings_{side}"):
                v[box] = a[f"home_savings_{side}"]
    v["N.1554"] = a["flat_minimum"]

    for side, box in (("taxpayer", "N.1601"), ("spouse", "N.1602")):
        if contributions(h, side):
            v[box] = contributions(h, side)
    v["R.1915"] = "/DAC6O" if h.get("dac6") else "/DAC6N"
    v["A.p16SignLieu"] = h.get("signature_place") or addr["locality"]
    v.update(family.pdf_values(h, f))
    v.update(deductions.pdf_values(h))
    v.update(employment.pdf_values(h, f))
    v.update(medical.pdf_values(h))
    v.update(salary_details.pdf_values(h))
    if h.get('single_parent_credit'):
        check = indicative_check(h)
        v.update(single_parent.pdf_values(h, check['taxable income'] - check['childcare abatement'] - check['medical abatement'], f))
    return {k: (float(x) if isinstance(x, Decimal) else x) for k, x in v.items()}


def _add(v, key, amount):
    v[key] = D(v.get(key, 0)) + D(amount)


def _dmy(iso):
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"
