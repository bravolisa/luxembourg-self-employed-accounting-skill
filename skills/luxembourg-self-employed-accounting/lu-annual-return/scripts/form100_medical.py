# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Bounded actual article127 medical costs; preserve gross, refunds and burden separately."""
from decimal import Decimal as D
import form100_family as family
need, money = family.need, family.money


def patient_label(h, row):
    """Keep the patient distinct from the payer in the supporting calculation."""
    if row['patient'] == 'child':
        child = h['children'][row['child_index']]
        return 'child: ' + child['first_name'] + ' ' + child['last_name']
    return row['patient']


def _patient(h, row):
    side, patient = row.get('paid_by'), row.get('patient')
    need(side in ('taxpayer', 'spouse') and h.get(side),
         'medical_expenses: payer must be a declared adult')
    if patient == side:
        return
    need(row.get('patient_identity_evidence') and row.get('household_bears_cost') is True
         and row.get('no_other_household_claim') is True,
         'medical_expenses: different patient needs invoice identity, household cost and no-other-claim evidence')
    if patient in ('taxpayer', 'spouse'):
        need(h.get(patient) and h.get('spouse') and family.joint_status_supported(h),
             'medical_expenses: cross-paid adult must belong to the supported joint assessment')
        return
    need(patient == 'child', 'medical_expenses: patient outside supported household needs review')
    index = row.get('child_index')
    need(type(index) is int and 0 <= index < len(h.get('children', [])),
         'medical_expenses: child_index must identify an existing child')
    child = h['children'][index]
    born = family.birth(child)
    need(child.get('in_tax_household') is True and born > family.date(int(h['tax_year']) - 18, 12, 31),
         'medical_expenses: child patient must be a minor throughout2025 in this tax household')
    need(born <= family.iso(row.get('payment_date'), 'medical payment_date'),
         'medical_expenses: child treatment payment before birth needs separate review')
    need(row.get('extraordinary_child_treatment') is True and row.get('treatment_evidence'),
         'medical_expenses: evidence of extraordinary unavoidable child treatment required; ordinary maintenance is excluded')


def _refunds(h, row):
    gross, refunds = money(row.get('gross'), 'medical gross'), money(row.get('refunds'), 'medical refunds')
    need(refunds <= gross, 'medical_expenses: refunds exceed paid costs; reconcile before deduction')
    need(row.get('pending_refunds') is False and row.get('refund_review_evidence')
         and money(row.get('expected_refunds'), 'medical expected refunds') == 0,
         'medical_expenses: pending/expected coverage or missing final reimbursement review requires review')
    items = row.get('refund_items')
    need(isinstance(items, list), 'medical_expenses: dated refund_items required, use [] only for no refunds')
    total = D(0)
    seen = set()
    for item in items:
        need(isinstance(item, dict) and isinstance(item.get('refund_id'), str)
             and item['refund_id'].strip() and item['refund_id'] not in seen and item.get('evidence'),
             'medical_expenses: each refund needs a unique refund_id and evidence')
        seen.add(item['refund_id'])
        need(item.get('recipient') in ('taxpayer', 'spouse') and h.get(item['recipient']),
             'medical_expenses: refund recipient must be an identified adult in the household')
        need(family.iso(item.get('date'), 'medical refund date').year == int(h['tax_year']),
             'medical_expenses: cross-year reimbursement requires review of correction/year treatment')
        total += money(item.get('amount'), 'medical refund amount')
    need(total == refunds, 'medical_expenses: dated refund items must reconcile to refunds')


def validate(h):
    rows = h.get('medical_expenses', [])
    if not rows:
        return
    review = h.get('medical_review') or {}
    need(int(h['tax_year']) == 2025 and h.get('resident_full_year') is True
         and h.get('tax_liability_months', 12) == 12 and not h.get('individual_taxation'),
         'medical_expenses: full-year resident single/joint 2025 route only')
    need(review.get('income_complete') is True and review.get('no_foreign_or_exempt_progression') is True
         and review.get('all_actual_article127_costs_included') is True and review.get('evidence'),
         'medical_expenses: complete reviewed income and actual article127 expenses required')
    need(all(s.get('all_pay_luxembourg_taxable', True) is True for s in h.get('salaries', [])),
         'medical_expenses: explicit foreign/exempt salary contradicts the reviewed ordinary-income scope')
    expected_class = 2 if h.get('spouse') else '1a' if h.get('single_parent_credit') else 1
    need(review.get('tax_class') == expected_class and family.joint_status_supported(h),
         'medical_expenses: reviewed tax class must match the supported household route')
    if not h.get('spouse') and not h.get('single_parent_credit'):
        born = family.birth({'national_id': h['taxpayer']['national_id']})
        need(not h.get('children') and h['taxpayer'].get('status') == 'CE' and born > family.date(1961, 1, 1),
             'medical_expenses: childless class1a/transition entitlement needs a separate supported class calculation')
    need(isinstance(rows, list) and 0 < len(rows) <= 20, 'medical_expenses: one to twenty reviewed rows required')
    seen = set()
    for row in rows:
        ident, side = row.get('invoice_id'), row.get('paid_by')
        need(ident and ident not in seen, 'medical_expenses: missing/duplicate invoice_id')
        seen.add(ident)
        _patient(h, row)
        need(row.get('kind') in ('medical', 'dental', 'prescribed_medicine')
             and row.get('article127_eligible') is True and row.get('eligibility_evidence')
             and row.get('provider') and row.get('payment_evidence') and row.get('currency') == 'EUR'
             and row.get('no_other_deduction') is True and row.get('no_forfait_or_childcare_overlap') is True
             and row.get('refunds_final_and_complete') is True,
             'medical_expenses: eligibility, payer, net cost and non-overlap evidence required')
        need(isinstance(row.get('description'), str) and 0 < len(row['description']) <= 50,
             'medical_expenses: description must fit official50-character XML field')
        need(family.iso(row.get('payment_date'), 'medical payment_date').year == int(h['tax_year']),
             'medical_expenses: payment must belong to2025')
        _refunds(h, row)
    for child in h.get('children', []):
        need(child.get('moderation') not in ('foreign_only', 'zero_differential')
             and child.get('benefits') and not child.get('request_rebate') and child.get('moderation_origin') == 'lu_positive_benefit'
             and child.get('moderation_evidence'), 'medical_expenses: positive established LU child moderation required for burden table')


def calculation(h, taxable, f):
    validate(h)
    if not h.get('medical_expenses'):
        return {'net': D(0), 'burden': D(0), 'allowed': D(0), 'rate': D(0)}
    taxable = D(taxable)
    need(taxable.is_finite() and taxable >= 0, 'medical_expenses: negative taxable income needs review')
    kids = family.child_count(h)
    need(kids <= 5, 'medical_expenses: more than five moderated children requires burden-table review')
    # First column is class1 without child; remaining columns cover1a/2 by child count.
    column = 0 if not h.get('spouse') and not h.get('children') else kids + 1
    row = 0 if taxable < 10000 else 1 if taxable < 20000 else 2 if taxable < 30000 else 3 if taxable < 40000 else 4 if taxable < 50000 else 5 if taxable <= 60000 else 6
    net = sum((money(x['gross'], 'medical gross') - money(x['refunds'], 'medical refunds') for x in h['medical_expenses']), D(0))
    rate = D(f[f'medical_burden_{row}_{column}'])
    burden = taxable * rate / 100
    allowed = max(net - burden, D(0))
    if taxable in (D(20000), D(30000), D(50000)):
        adjacent = D(f[f'medical_burden_{row-1}_{column}'])
        need(allowed == max(net - taxable*adjacent/100, D(0)),
             'medical_expenses: published burden-table endpoint changes relief; manual review required')
    need(allowed == allowed.quantize(D('.01')), 'medical_expenses: fractional-cent annual abatement requires reviewed rounding')
    need(allowed <= taxable, 'medical_expenses: abatement above income needs separate review')
    return {'net': net, 'burden': burden, 'allowed': allowed, 'rate': rate, 'income_base': taxable}


def pdf_values(h):
    if not h.get('medical_expenses'):
        return {}
    out = {'C.1701': '/Yes', 'A.1704': 'Frais de maladie - voir annexe justificative'}
    for side, key in (('taxpayer', 'N.1702'), ('spouse', 'N.1703')):
        if any(x['paid_by'] == side for x in h['medical_expenses']):
            out[key] = sum((money(x['gross'], 'gross') - money(x['refunds'], 'refunds') for x in h['medical_expenses'] if x['paid_by'] == side), D(0))
    return out


def add_xml(charges, h):
    if not h.get('medical_expenses'):
        return
    need(all(x['patient'] == x['paid_by'] for x in h['medical_expenses']),
         'medical_expenses: cross-payer/child XML H0020 semantics require confirmation; use the reviewed PDF and annex')
    node = charges.add('CharExtraFraisMaladie')
    for x in h['medical_expenses']:
        row = node.add('CharExtraFraisMaladieDetail', H0020_CFM_PRE_NOM_PER='DECLARER' if x['patient'] == 'taxpayer' else 'CONJOINT')
        row.add('CFM_DES_MAL', x['description'])
        row.add('CFM_MNT_FRA_MAL', x['gross'])
        row.add('CFM_MNT_TOT_REM', x['refunds'])
