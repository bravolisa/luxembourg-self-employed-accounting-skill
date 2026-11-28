# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Bounded 2025 resident single-parent request and annual CIM reconciliation.

PIT-O-17 remains open: automatic credit only when both income-base readings agree
and the result is already an exact cent. No invented annual rounding convention.
"""
from decimal import Decimal as D, ROUND_FLOOR
import form100_family as family

need, money = family.need, family.money


def validate(h):
    claim = h.get('single_parent_credit')
    if not claim:
        return
    need(isinstance(claim, dict), 'single_parent_credit: reviewed facts required, not a boolean')
    need(int(h['tax_year']) == 2025 and h.get('resident_full_year') is True
         and h.get('tax_liability_months', 12) == 12,
         'single_parent_credit: full-year resident 2025 liability required')
    need(not h.get('spouse') and not h.get('individual_taxation')
         and h['taxpayer'].get('status') in ('CE', 'DI', 'VE'),
         'single_parent_credit: unmarried household without joint or individual spouse taxation required')
    need(claim.get('tax_class') == '1a' and claim.get('unmarried_full_year') is True
         and claim.get('no_class2_transition') is True and claim.get('full_year_eligibility') is True
         and claim.get('evidence'),
         'single_parent_credit: establish child-based class 1a, full-year eligibility and no class 2 transition')
    if h['taxpayer'].get('status_since'):
        since = family.iso(h['taxpayer']['status_since'], 'single_parent_credit status_since')
        need(h['taxpayer']['status'] != 'VE' or since.year < int(h['tax_year']) - 3,
             'single_parent_credit: widowhood in the preceding three years has class 2 priority')
        need(since.year < int(h['tax_year']), 'single_parent_credit: current-year or future civil-status event contradicts the full-year supported scope')
    declared_income = any(D(p['amount']) != 0 for salary in h.get('salaries', []) for p in salary.get('pay', [])) or any(
        (D(b['profit']) if b.get('method') == 'BILA' else D(b['receipts']) - D(b['expenses'])) != 0
        for b in h.get('businesses', []))
    need(declared_income, 'single_parent_credit: no declared supported income; means-of-subsistence field A0237 requires manual completion')
    children = h.get('children', [])
    support = claim.get('support')
    need(children and isinstance(support, list)
         and all(isinstance(row, dict) and type(row.get('child')) is int for row in support)
         and sorted(row['child'] for row in support) == list(range(len(children))),
         'single_parent_credit: one support record for each child required')
    need(len(children) <= 4, 'single_parent_credit: at most four child support rows fit the PDF')
    for row in support:
        child = children[row['child']]
        need(child.get('custody') == 'sole_parent' and child.get('benefit_recipient') == 'CT'
             and child.get('benefits') and not child.get('request_rebate'),
             'single_parent_credit: established sole-parent assignment and existing moderation required; rebate stays separate')
        need(row.get('other_parent_same_home') is False and row.get('same_situation_full_year') is True,
             'single_parent_credit: cohabiting other parent or changing eligibility requires review')
        need(row.get('moderation') == 'positive_lu_benefit' and row.get('moderation_evidence'),
             'single_parent_credit: foreign-only/zero-differential moderation requires review (PIT-O-27)')
        need(row.get('support_complete') is True and row.get('support_evidence') and row.get('all_support_from_other_parent') is True,
             'single_parent_credit: include maintenance and direct upkeep/education payments; exclude benefits/orphan pensions')
        annual = money(row.get('annual_support'), 'single_parent_credit annual_support')
        monthly = money(row.get('monthly_support'), 'single_parent_credit monthly_support')
        need(row.get('support_regular_monthly') is True and annual == monthly * 12,
             'single_parent_credit: irregular support requires separate annual/monthly review')
    money(claim.get('paid_outside_salary'), 'single_parent_credit paid_outside_salary')
    need(claim.get('paid_credit_evidence'), 'single_parent_credit: all paid CIM needs evidence, including zero')
    for salary in h.get('salaries', []):
        money(salary.get('cim'), 'single_parent_credit salary paid cim')
        need(salary.get('withholding_basis') in ('before_cis_co2_cim', 'after_cis_co2_cim'),
             'single_parent_credit: establish withholding before or after CIS/CO2/CIM explicitly')


def entitlement(adjusted, support, f):
    def amount(income):
        income = max(D(income), D(0))
        if income < D(f['cim_phaseout_from']):
            credit = D(f['cim_full'])
        elif income <= D(f['cim_phaseout_to']):
            credit = D(f['cim_full']) - (income - D(f['cim_phaseout_from'])) * D(str(f['cim_phaseout_rate']))
        else:
            credit = D(f['cim_minimum'])
        reduction = max(support - D(f['cim_support_threshold']), D(0)) * D(f['cim_support_reduction_percent']) / 100
        return max(credit - reduction, D(0))
    raw = amount(adjusted)
    tariff_base = (D(adjusted)/50).to_integral_value(rounding=ROUND_FLOOR)*50
    need(raw == amount(tariff_base), 'single_parent_credit: income-base rounding changes annual CIM (PIT-O-17); manual review required')
    need(raw == raw.quantize(D('.01')), 'single_parent_credit: annual fractional-cent rounding unresolved (PIT-O-17)')
    return raw


def context(h):
    validate(h)
    claim = h['single_parent_credit']
    return {'support': min(money(row['annual_support'], 'support') for row in claim['support']),
            'paid': money(claim['paid_outside_salary'], 'CIM paid outside salary') +
                    sum((money(s['cim'], 'paid salary CIM') for s in h.get('salaries', [])), D(0)),
            'evidence': claim['evidence']}


def reconcile(adjusted, facts, f):
    retained = entitlement(adjusted, money(facts['support'], 'support'), f)
    paid = money(facts['paid'], 'paid CIM')
    return {'paid': paid, 'retained': retained, 'adjustment': paid - retained,
            'support': facts['support'], 'method': 'annual_CIM_exact_cent_and_income_base_invariant'}


def pdf_values(h, adjusted, f):
    if not h.get('single_parent_credit'):
        return {}
    validate(h)
    facts = context(h)
    # Paper requests unpaid CIM; XML separately asks for annual application.
    # This paper convention is documented as an inference, not a portal rule.
    remaining = reconcile(adjusted, facts, f)['retained'] - facts['paid']
    values = {'C.0228': '/Yes' if remaining > 0 else '/Off'}
    for n, row in enumerate(h['single_parent_credit']['support']):
        child = h['children'][row['child']]
        values[f'A.{229+2*n:04d}'] = child['last_name'] + ' ' + child['first_name']
        values[f'N.{230+2*n:04d}'] = money(row['monthly_support'], 'monthly support')
    return values
