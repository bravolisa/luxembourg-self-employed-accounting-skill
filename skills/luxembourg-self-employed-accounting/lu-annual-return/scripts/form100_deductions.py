"""Reviewed 2025 deduction inputs, shared ceilings and official PDF/XML positions.

Rules and contract: references/forms/2025/form100-deductions.md. Amounts are certificate
amounts, never inferred eligibility. Unknown evidence is not a zero amount.
"""
from decimal import Decimal
from datetime import date
import form100_family as family

D = Decimal
need = family.need
money = family.money
SIDE = {'taxpayer': 'CONT', 'spouse': 'CONJ'}
PURPOSES = {'A': 'Voiture', 'B': 'Besoins personnels', 'C': 'Prêt à la consommation',
            'D': 'Financement études', 'I': 'Autre'}


def validate(h):
    for item in h.get('insurance', []):
        money(item.get('amount'), 'insurance amount')
        need(item.get('paid_by') in SIDE and h.get(item['paid_by']), 'insurance: payer must belong to this household')
    loans = h.get('consumer_loans', [])
    validate_premiums(h)
    validate_donations(h)
    if not loans:
        return
    scope(h)
    need(isinstance(loans, list) and len(loans) <= 7,
         'consumer_loans: at most seven certificate rows fit the PDF')
    seen = set()
    for loan in loans:
        identifier = loan.get('loan_id')
        need(isinstance(identifier, str) and identifier.strip() and identifier not in seen,
             'consumer_loans: missing or duplicate loan_id; reconcile certificate copies first')
        seen.add(identifier)
        need(loan.get('creditor') and loan.get('creditor_address') and loan.get('evidence'),
             'consumer_loans: creditor, address and certificate evidence required')
        need(loan.get('purpose') in ('A', 'B', 'C', 'D'),
             'consumer_loans: supported private car, personal, consumption or study loan only')
        need(loan.get('fully_private') is True and loan.get('no_property_or_exempt_income') is True
             and loan.get('no_other_deduction') is True,
             'consumer_loans: mixed/business, property, exempt-income or duplicate claims require review')
        need(loan.get('borrower') in SIDE and h.get(loan['borrower'])
             and loan.get('paid_by') == loan['borrower'],
             'consumer_loans: establish the household borrower who paid; third-party payment requires review')
        money(loan.get('balance_31_dec'), 'consumer_loans balance_31_dec')
        paid = money(loan.get('interest'), 'consumer_loans interest')
        refunds = money(loan.get('subsidies_and_refunds'), 'consumer_loans subsidies_and_refunds')
        need(refunds <= paid and loan.get('refunds_same_year_only') is True,
             'consumer_loans: net current-year interest only; prior-year recovery requires review')


def scope(h):
    need(int(h['tax_year']) == 2025 and h.get('resident_full_year') is True,
         'new deductions: supported for full-year Luxembourg residents in 2025 only')
    need(not any(s.get('all_pay_luxembourg_taxable') is False for s in h.get('salaries', [])),
         'new deductions: foreign/exempt income needs a separate assessment route')
    for child in h.get('children', []):
        need(child.get('moderation') not in ('foreign_only', 'zero_differential') and child.get('moderation_evidence') and
             ((child.get('benefits') and child.get('moderation_origin') == 'lu_positive_benefit') or
              (child.get('request_rebate') and child.get('moderation_origin') == 'reviewed_tax_rebate')),
             'new deductions: establish child moderation origin; foreign-only/zero-differential cases require review (PIT-O-27)')
    need(not h.get('individual_taxation'), 'new deductions: individual spouse taxation requires separate preparation')
    if h.get('spouse'):
        need(family.joint_status_supported(h), 'new deductions: spouse/partner multiplier requires reviewed joint taxation')


def interest(h):
    return sum((money(x['interest'], 'interest') - money(x['subsidies_and_refunds'], 'refunds')
                for x in h.get('consumer_loans', [])), D(0))


def validate_premiums(h):
    used_people, used_children = set(), set()
    for item in h.get('insurance', []):
        if str(item.get('risk', '')).strip().upper() != 'PU':
            need(not item.get('single_premium'), 'single-premium facts need risk PU')
            continue
        label = 'single-premium insurance: '
        need(item.get('risk') == 'PU', label + 'risk code must be exactly PU')
        pu = item.get('single_premium')
        need(isinstance(pu, dict), label + 'contract, roles, dates and prior increases required')
        scope(h)
        side = item.get('paid_by')
        need(side in SIDE and h.get(side) and side not in used_people,
             label + 'one own-life contract per household adult is supported')
        used_people.add(side)
        need(pu.get('subscriber') == pu.get('insured') == side,
             label + 'crossed subscriber/insured/payer roles require review (PIT-O-16)')
        need(h.get('own_home') and pu.get('property') == 'own_home',
             label + 'identify the supported principal home in own_home')
        need(pu.get('decreasing_capital') is True and pu.get('personal_housing_loan') is True
             and pu.get('eligibility_evidence') and item.get('insurer'),
             label + 'qualifying decreasing-capital death cover and insurer evidence required')
        start = family.iso(pu.get('subscription_date'), label + 'subscription_date')
        payment = family.iso(pu.get('payment_date'), label + 'payment_date')
        need(start <= payment and payment.year == int(h['tax_year']),
             label + f"premium must have been paid in {h['tax_year']} after subscription")
        money(item.get('amount'), label + 'premium')
        need(pu.get('premium_fully_paid') is True and pu.get('no_other_deduction') is True,
             label + 'confirm full premium payment and no duplicate claim, including financed premiums')
        ids = pu.get('children')
        need(isinstance(ids, list) and all(type(i) is int and 0 <= i < len(h.get('children', [])) for i in ids)
             and len(ids) == len(set(ids)) and not used_children.intersection(ids),
             label + 'assign each eligible child once across contracts')
        need(all(h['children'][i].get('benefits') or h['children'][i].get('request_rebate') for i in ids),
             label + 'child must give this household an established reduction')
        used_children.update(ids)
        previous = pu.get('previous_increases')
        need(isinstance(previous, dict) and set(previous) == {str(y) for y in range(int(h['tax_year']) - 5, int(h['tax_year']))}
             and pu.get('history_complete') is True and pu.get('history_evidence'),
             label + f"provide actual increases used for this person/property in each of {int(h['tax_year']) - 5}–{int(h['tax_year']) - 1}, including zero")
        for value in previous.values():
            money(value, label + 'previous increased deduction')


def premium_increases(h, f):
    result = {}
    for item in h.get('insurance', []):
        if item.get('risk') != 'PU':
            continue
        pu, side = item['single_premium'], item['paid_by']
        birth = family.birth({'national_id': h[side]['national_id']})
        start = family.iso(pu['subscription_date'], 'subscription_date')
        need(birth <= start, 'single-premium insurance: subscription precedes birth')
        age = start.year - birth.year - ((start.month, start.day) < (birth.month, birth.day))
        extra = min(D(f['pu_age_extra_max']), D(f['pu_age_rate']) * max(age - f['pu_age_start'], 0)) / 100
        maximum = (D(f['pu_base']) + D(f['pu_child'])*len(pu['children'])) * (1 + extra)
        previous = sum((money(x, 'previous increase') for x in pu['previous_increases'].values()), D(0))
        result[side] = {'age': age, 'maximum': maximum, 'previous_used': previous,
                        'increase': min(money(item['amount'], 'premium'), max(maximum - previous, D(0)))}
    return result


def validate_donations(h):
    need(not h.get('donation_carryforward'), 'donation carryforward: vintage/order and carry-only XML need manual review (PIT-O-19)')
    gifts = h.get('donations', [])
    if not gifts:
        return
    scope(h)
    review = h.get('donation_review') or {}
    need(review.get('no_prior_carryforward') is True and review.get('income_complete') is True and review.get('evidence'),
         'donations: confirm complete net income, no prior carryforward and review evidence')
    need(isinstance(gifts, list) and len(gifts) <= 6, 'donations: at most six beneficiary rows fit the PDF')
    seen = set()
    countries = family.EU | {'IS', 'LI', 'NO', 'CH'}
    for gift in gifts:
        ident = gift.get('donation_id')
        need(isinstance(ident, str) and ident.strip() and ident not in seen, 'donations: missing or duplicate donation_id')
        seen.add(ident)
        need(gift.get('recipient') and gift.get('receipt') and gift.get('eligibility_evidence'),
             'donations: recipient, receipt and eligibility evidence required')
        need((gift.get('country') == 'LU' and gift.get('eligibility') == 'approved_lu')
             or (gift.get('country') in countries - {'LU'} and gift.get('eligibility') == 'eu_efta_equivalent'),
             'donations: recipient needs Luxembourg approval or evidenced EU/EFTA equivalence')
        need(gift.get('paid_by') in SIDE and h.get(gift['paid_by']), 'donations: payer must belong to this household')
        need(family.iso(gift.get('payment_date'), 'donation payment_date').year == int(h['tax_year']),
             'donations: only current-year payments are supported')
        need(gift.get('cash_gift') is True and gift.get('no_other_deduction') is True
             and gift.get('no_refund_or_counterbenefit') is True,
             'donations: ordinary cash gifts only; in-kind and duplicate business claims need review')
        money(gift.get('amount'), 'donation amount')


def donations(h, total_net_income, f):
    need(total_net_income >= 0, 'donations: negative total net income requires special-expense ordering review')
    actual = sum((money(x['amount'], 'donation') for x in h.get('donations', [])), D(0))
    cap = min(max(total_net_income, D(0)) * D(f['donation_percent_cap']) / 100, D(f['donation_absolute_cap']))
    # No invented rounding of the annual 20% cap: stop if a fractional cent matters.
    allowed = min(actual, cap) if actual >= D(f['donation_minimum']) else D(0)
    need(allowed == allowed.quantize(D('.01')), 'donations: fractional-cent cap requires reviewed rounding')
    carry = actual - allowed if actual >= D(f['donation_minimum']) else D(0)
    return {'actual': actual, 'net_income_base': total_net_income, 'cap': cap, 'allowed': allowed,
            'new_carryforward': carry, 'origin_year': int(h['tax_year']), 'last_usable_year': int(h['tax_year']) + 2}


def pdf_values(h):
    v = {}
    for n, loan in enumerate(h.get('consumer_loans', [])):
        start = 1401 + 5*n
        v[f'A.{start}'] = loan['creditor'] + ', ' + loan['creditor_address']
        v[f'A.{start+1}'] = PURPOSES[loan['purpose']]
        v[f'N.{start+2}'] = money(loan['balance_31_dec'], 'loan balance')
        v[f'N.{start+3+(loan["paid_by"] == "spouse")}'] = money(loan['interest'], 'interest') - money(loan['subsidies_and_refunds'], 'refunds')
    for item in h.get('insurance', []):
        if item.get('risk') == 'PU':
            side = item['paid_by']
            v['C.1474' if side == 'taxpayer' else 'C.1475'] = '/Yes'
            v['N.1476' if side == 'taxpayer' else 'N.1477'] = len(item['single_premium']['children'])
    for n, gift in enumerate(h.get('donations', [])):
        start = 1615 + 3*n
        v[f'A.{start}'] = gift['recipient']
        v[f'N.{start+1+(gift["paid_by"] == "spouse")}'] = money(gift['amount'], 'donation')
    if h.get('donations'):
        for side, field in (('taxpayer', 'N.1633'), ('spouse', 'N.1634')):
            v[field] = sum((money(g['amount'], 'donation') for g in h['donations'] if g['paid_by'] == side), D(0))
    return v


def add_xml(ds, h):
    if h.get('consumer_loans'):
        parent = ds.add('DepSpeInteretsDebiteurs')
        for loan in h['consumer_loans']:
            row = parent.add('DepSpeInteretsDebiteursDetail')
            row.add('IDE_NOM_CRE', loan['creditor'])
            row.add('IDE_REL_ECO', loan['purpose'])
            row.add('IDE_MNT_DETTE_31DEC', money(loan['balance_31_dec'], 'loan balance'))
            row.add('IDE_MNT_INT_' + SIDE[loan['paid_by']], money(loan['interest'], 'interest') - money(loan['subsidies_and_refunds'], 'refunds'))

    if h.get('donations'):
        parent = ds.add('DepSpeLiberalites')
        for gift in h['donations']:
            row = parent.add('DepSpeLiberalitesDetail')
            row.add('LIB_NOM_BEN', gift['recipient'])
            row.add('LIB_VER_PAR_' + SIDE[gift['paid_by']], money(gift['amount'], 'donation'))
        parent.add('LIB_REPORT', False)


def add_premium_xml(row, item):
    if item.get('risk') != 'PU':
        return
    pu = item['single_premium']
    need(not any(money(v, 'previous increase') for v in pu['previous_increases'].values()),
         'single-premium XML: prior-used increases have no verified import path; use reviewed PDF/calculation')
    row.attrs['D0870_PAC_HAB_APU'] = 'RESPRINCIPALE0'
    row.add('PAC_DAT_DEB_CON', pu['subscription_date'])
    row.add('PAC_RIS_APU', 'HA')
    row.add('PAC_PRI_NBENF_' + SIDE[item['paid_by']], str(len(pu['children'])))
