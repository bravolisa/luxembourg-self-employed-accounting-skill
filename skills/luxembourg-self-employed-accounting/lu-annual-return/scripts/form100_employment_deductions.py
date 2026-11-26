# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Evidence-led salary costs/contributions and ordinary retirement-contract checks.

2025 household extensions. Law, scope and field map: forms/2025/employment-deductions.md.
Legacy pension contracts are routed to review, not declared legally ineligible.
"""
from decimal import Decimal as D
import form100_family as family
import form100_salary_details as salary_details

need, money, iso = family.need, family.money, family.iso
SIDES = ('taxpayer', 'spouse')


def year_after(day, years, label):
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        need(False, label + ': leap-day anniversary requires explicit review')


def validate_pensions(h):
    if h.get('pension_plans'):
        need(family.joint_status_supported(h), 'pension_plans: supported joint household status required')
    seen = set()
    for p in h.get('pension_plans', []):
        side = p.get('holder')
        need(side in SIDES and h.get(side), 'pension_plans: holder must belong to household')
        money(p.get('amount'), 'pension_plans amount')
        need(type(p.get('pepp', False)) is bool, 'pension_plans: pepp must be boolean')
        if p.get('pepp'):
            need(p.get('subaccount_country') == 'LU' and p.get('subaccount_evidence'),
                 'pension_plans: Luxembourg PEPP sub-account and evidence required')
        need(p.get('qualifying_scheme', True) is True, 'pension_plans: explicitly ineligible scheme needs review')
        need(p.get('insurer'), 'pension_plans: provider required')
        start, end = iso(p.get('start'), 'pension start'), iso(p.get('end'), 'pension end')
        born = family.birth({'national_id': h[side]['national_id']})
        need(start.year >= 2002 and not p.get('legacy_contract'),
             'pension_plans: legacy/pre-2002 contract needs separate eligibility and ceiling review')
        need(born <= start < end, 'pension_plans: inconsistent birth/subscription/maturity dates')
        need(end >= year_after(start, 10, 'pension duration'), 'pension_plans: minimum ten-year term not met')
        need(start < year_after(born, 65, 'pension subscription'), 'pension_plans: subscription must precede 65th birthday')
        need(year_after(born, 60, 'pension maturity') <= end <= year_after(born, 75, 'pension maturity'),
             'pension_plans: maturity must be between the 60th and 75th birthdays inclusive')
        need(start.year <= int(h['tax_year']) <= end.year, 'pension_plans: payment year outside contract term')
        if p.get('payment_date') or start.year == int(h['tax_year']) or end.year == int(h['tax_year']):
            payment = iso(p.get('payment_date'), 'pension maturity-year payment_date')
            need(payment.year == int(h['tax_year']) and start <= payment <= end, 'pension_plans: maturity-year payment must precede or equal maturity')
        identity = (side, p.get('contract_id') or (p['insurer'], p['start'], p['end']))
        need(identity not in seen, 'pension_plans: duplicate contract; reconcile copies or supply distinct contract_id')
        seen.add(identity)


def _rows(h, key):
    rows = h.get(key, [])
    need(isinstance(rows, list), key + ': list of reviewed records required')
    return rows


def validate(h):
    validate_pensions(h)
    keys = ('salary_costs', 'occupational_pension', 'voluntary_contributions')
    if not any(h.get(k) for k in keys):
        return
    need(int(h['tax_year']) == 2025 and h.get('resident_full_year') is True
         and h.get('tax_liability_months', 12) == 12 and not h.get('individual_taxation'),
         'employment deductions: full-year resident joint/single 2025 scope required')
    need(not any(s.get('all_pay_luxembourg_taxable') is False for s in h.get('salaries', [])),
         'employment deductions: exempt/progression income needs separate review')
    need(family.joint_status_supported(h), 'employment deductions: supported joint household status required')
    salary_owners = {s['owner'] for s in h.get('salaries', [])}
    for key in keys:
        seen = set()
        for row in _rows(h, key):
            side = row.get('owner')
            need(side in SIDES and h.get(side), key + ': owner must belong to household')
            ident = side if key == 'salary_costs' else row.get('certificate_id')
            need(ident and ident not in seen, key + ': duplicate/missing record identity')
            seen.add(ident)
            amount = money(row.get('amount'), key + ' amount')
            need(row.get('evidence') and row.get('net_of_reimbursements') is True
                 and row.get('not_deducted_elsewhere') is True,
                 key + ': evidence, net payments and no duplicate deduction required')
            if key == 'salary_costs':
                need(side in salary_owners and row.get('method') == 'actual' and row.get('employment_related') is True,
                     'salary_costs: actual election for this employee and professional nexus required')
                gross = sum((money(p['amount'], 'salary receipts') for s in h['salaries'] if s['owner'] == side for p in s['pay']), D(0))
                travel = sum((money(s.get('travel', 0), 'commuting') for s in h['salaries'] if s['owner'] == side), D(0))
                need(amount >= min(D(540), max(gross-travel, D(0))), 'salary_costs: actual election cannot replace a larger minimum flat; use standard method')
                exempt = sum((salary_details.exemptions(s) for s in h['salaries'] if s['owner'] == side), D(0))
                need(amount <= gross - exempt - travel, 'salary_costs: loss/negative net salary requires review; no invented actual-cost cap')
            elif key == 'occupational_pension':
                need(side in salary_owners and row.get('employee_personal_contribution') is True
                     and row.get('qualifying_scheme') is True and row.get('scheme_evidence'),
                     'occupational_pension: qualifying employee personal contribution required, not employer/private pension')
            else:
                need(row.get('kind') in ('voluntary', 'continued', 'optional', 'buyback')
                     and row.get('qualifying_scheme') is True and row.get('scheme_evidence')
                     and row.get('not_compulsory_or_dependency') is True
                     and type(row.get('salary_related')) is bool
                     and (not row['salary_related'] or side in salary_owners),
                     'voluntary_contributions: establish article110(4) scheme and exclude mandatory/dependency insurance')


def actual_cost(h, side):
    return next((money(x['amount'], 'actual salary costs') for x in h.get('salary_costs', []) if x['owner'] == side), None)


def voluntary(h, side):
    return sum((money(x['amount'], 'voluntary contribution') for x in h.get('voluntary_contributions', []) if x['owner'] == side), D(0))


def occupational_paid(h, side):
    return sum((money(x['amount'], 'occupational pension') for x in h.get('occupational_pension', []) if x['owner'] == side), D(0))


def occupational(h, side, f):
    paid = occupational_paid(h, side)
    return min(paid, D(f['employee_occupational_pension_cap'])) if paid else D(0)


def related_salary_contributions(h, side, f):
    return occupational(h, side, f) + sum((money(x['amount'], 'salary-related voluntary payment')
        for x in h.get('voluntary_contributions', []) if x['owner'] == side and x['salary_related']), D(0))


def pdf_values(h, f):
    out = {}
    for side, column in (('taxpayer', 0), ('spouse', 1)):
        if any(x['owner'] == side for x in h.get('voluntary_contributions', [])):
            out[f'N.{1501+column}'] = voluntary(h, side)
        if any(x['owner'] == side for x in h.get('occupational_pension', [])):
            out[f'N.{1605+column}'] = occupational(h, side, f)
            # Official radio export names are unrelated to their visible yes/no labels.
            out[f'R.{1609+column}'] = '/courrier'
    return out


def add_xml(ds, h, f):
    if h.get('voluntary_contributions'):
        node = ds.add('DepSpeCotisationsPers')
        for side, suffix in (('taxpayer', 'CONT'), ('spouse', 'CONJ')):
            if any(x['owner'] == side for x in h['voluntary_contributions']):
                node.add('CTP_MNT_'+suffix, voluntary(h, side))
    if h.get('occupational_pension'):
        node = ds.add('DepSpeRegimeCompSal')
        for side, suffix in (('taxpayer', 'CONT'), ('spouse', 'CONJ')):
            if any(x['owner'] == side for x in h['occupational_pension']):
                paid = occupational_paid(h, side)
                need(paid <= D(f['employee_occupational_pension_cap']),
                     'occupational_pension: above-cap actual-paid XML semantics need live review; calculation/PDF available')
                node.add('RCS_COT_'+suffix+'_NEX', paid)
