# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Bounded replacement benefits, certified exemptions and workplace-period output."""
from decimal import Decimal as D
import form100_family as family
need, money, iso = family.need, family.money, family.iso


def replacement(s):
    return s.get('source') == 'employee_replacement'


def exemptions(s):
    return sum((money(x['amount'], 'certified salary exemption') for x in s.get('exemptions', [])), D(0))


def validate(h):
    detailed = any(replacement(s) or s.get('exemptions') or s.get('workplace_periods') for s in h.get('salaries', []))
    if not detailed:
        return
    need(int(h['tax_year']) == 2025 and h.get('resident_full_year') is True and h.get('tax_liability_months', 12) == 12,
         'salary details: full-year resident2025 route only')
    totals = {'taxpayer': [], 'spouse': []}
    certificates, fingerprints = set(), set()
    record_ids = [s.get('certificate_id') for s in h.get('salaries', [])]
    for s in h.get('salaries', []):
        need(s.get('owner') in totals and h.get(s['owner']), 'salary details: owner must belong to household')
        need(s.get('all_pay_luxembourg_taxable') is True and s.get('tax_regime') == 'ordinary',
             'salary details: reviewed ordinary entirely Luxembourg-taxable receipts required')
        cid = s.get('certificate_id')
        need(isinstance(cid, str) and cid.strip() and cid not in certificates,
             'salary details: unique logical certificate_id required; reconcile duplicate/replacement copies')
        certificates.add(cid)
        need(not s.get('replaces') or s['replaces'] not in record_ids, 'salary details: corrected and replaced certificates cannot both be included')
        fingerprint = (s['owner'], s.get('employer'), s.get('employment_id'), s.get('start'), s.get('end'),
                       sum((money(x.get('amount'), 'salary identity gross') for x in s.get('pay', [])), D(0)),
                       money(s.get('contributions'), 'salary identity contributions'), s.get('tax_card_id'))
        need(fingerprint not in fingerprints, 'salary details: equivalent certificate copies need reconciliation')
        fingerprints.add(fingerprint)
        need(s.get('source', 'employer') in ('employer', 'employee_replacement'), 'salary details: unknown source')
        gross = sum((money(x['amount'], 'gross salary/benefit') for x in s['pay']), D(0))
        if replacement(s):
            begin, end = iso(s.get('start'), 'replacement start'), iso(s.get('end'), 'replacement end')
            need(begin.year == end.year == int(h['tax_year']) and begin <= end, 'replacement benefit: reviewed2025 payment period required')
            need('tax_card_id' in s and (s['tax_card_id'] is None or isinstance(s['tax_card_id'], str) and s['tax_card_id'].strip()),
                 'replacement benefit: known tax-card identity or explicit null required')
            need(s.get('withholding_basis') in ('before_cis_co2', 'after_cis_co2', 'before_cis_co2_cim', 'after_cis_co2_cim')
                 and 'withheld' in s, 'replacement benefit: known withholding amount and credit basis required')
            # Withholding may legitimately be negative after credits; reject non-money values here.
            from decimal import InvalidOperation
            try:
                withheld = D(str(s['withheld']))
                valid = withheld.is_finite() and withheld == withheld.quantize(D('.01'))
            except (InvalidOperation, ValueError, TypeError):
                valid = False
            need(valid, 'replacement benefit: withholding must be finite money stated to cents')
            for key in ('contributions', 'cis', 'co2', 'cim'):
                need(key in s, 'replacement benefit: known '+key+' required, including zero')
                money(s[key], 'replacement '+key)
            need(money(s['cim'], 'replacement CIM') == 0 or h.get('single_parent_credit'), 'replacement benefit: paid CIM needs a reviewed single-parent reconciliation')
            need(not s.get('cihs'), 'replacement benefit: other paid credits require separate reconciliation')
            kind = s.get('replacement_kind')
            need(kind in ('sickness', 'maternity', 'accident', 'unemployment')
                 and s.get('employee_replacement_evidence') and s.get('employee_replacement_eligible') is True
                 and s.get('overlap_and_duplicates_reconciled') is True
                 and s.get('contributions_reconciled') is True and s.get('employer'),
                 'replacement benefit: employee category, issuer, overlap and deductible-contribution evidence required')
            need(len(s['pay']) == 1 and s['pay'][0].get('kind') == ('IMAT' if kind == 'maternity' else 'A')
                 and isinstance(s['pay'][0].get('description'), str) and 0 < len(s['pay'][0]['description']) <= 50, 'replacement benefit: one explicit A/IMAT gross row and precise description required')
            need(s.get('occupation') == ('DEMP' if kind == 'unemployment' else 'SALA'),
                 'replacement benefit: occupation must match unemployment or employee branch')
            need(money(s.get('travel'), 'replacement benefit travel') == 0 and not s.get('exemptions') and not s.get('workplace_periods'),
                 'replacement benefit: no invented commuting, exemption or actual-work period')
        seen = set()
        for x in s.get('exemptions', []):
            need(not replacement(s) and x.get('kind') in ('HSUP', 'SJFE') and x['kind'] not in seen,
                 'salary exemptions: one certified HSUP/SJFE amount per certificate only')
            seen.add(x['kind'])
            money(x.get('amount'), 'exemption amount')
            need(x.get('included_in_gross') is True and x.get('eligibility_evidence')
                 and x.get('certified_exempt') is True and x.get('contributions_reconciled') is True
                 and x.get('not_deducted_elsewhere') is True,
                 'salary exemptions: certified eligibility, inclusion in gross and net deductible contributions required')
            if x['kind'] == 'HSUP':
                need(x.get('private_sector_eligible_overtime') is True and x.get('not_senior_manager') is True,
                     'salary exemptions: overtime scope/manager eligibility must be established')
        ex = exemptions(s)
        need(ex <= gross, 'salary exemptions: exempt amount exceeds source gross')
        if ex:
            need(ex + money(s.get('contributions'), 'deductible contributions') <= gross,
                 'salary exemptions: negative remainder needs separate review')
        periods = s.get('workplace_periods', [])
        for row in periods:
            begin, end = iso(row.get('start'), 'workplace period start'), iso(row.get('end'), 'workplace period end')
            need(iso(s['start'], 'employment start') <= begin <= end <= iso(s['end'], 'employment end')
                 and begin.year == end.year == int(h['tax_year']) and row.get('commune') and row.get('evidence'),
                 'workplace periods: reviewed dates must lie inside the employment interval')
            frequency = money(row.get('frequency'), 'workplace frequency')
            need(row.get('frequency_unit') in ('week', 'month') and frequency > 0
                 and frequency <= (7 if row['frequency_unit'] == 'week' else 31),
                 'workplace periods: valid days/week or days/month frequency required')
            totals[s['owner']].append(row)
        if periods:
            need(set(s.get('workplaces', [])) == {x['commune'] for x in periods},
                 'workplace periods: structured dates and official commune list must agree')
    if any(totals.values()):
        review = h.get('commuting_review') or {}
        need(review.get('periods_complete') is True and review.get('annual_amount_reviewed') is True and review.get('evidence'),
             'workplace periods: complete person-year periods and FD amounts need review; dates alone do not calculate commuting')
        for side, rows in totals.items():
            need(len(rows) <= 2, 'workplace periods: at most two rows per person fit this PDF route')
            need(not rows or all(s.get('workplace_periods') for s in h['salaries'] if s['owner'] == side and not replacement(s)),
                 'workplace periods: every employment certificate for this person must be represented')
    for side in ('taxpayer', 'spouse'):
        salaries = [s for s in h.get('salaries', []) if s['owner'] == side]
        if any(s.get('exemptions') for s in salaries):
            gross = sum((money(x['amount'], 'salary receipt') for s in salaries for x in s['pay']), D(0))
            travel = sum((money(s.get('travel', 0), 'travel') for s in salaries), D(0))
            exempt = sum((exemptions(s) for s in salaries), D(0))
            need(gross-exempt-travel >= min(D(540), max(gross-travel,D(0))),
                 'salary exemptions: low taxable-receipt flat-cost interaction needs review')


def pdf_values(h):
    values = {}
    for side, col in (('taxpayer', 0), ('spouse', 1)):
        salaries = [s for s in h.get('salaries', []) if s['owner'] == side]
        benefits = [s for s in salaries if replacement(s)]
        if benefits:
            values[f'N.{709+col:04d}'] = sum((money(p['amount'], 'benefit gross') for s in benefits for p in s['pay']), D(0))
        for kind, box in (('HSUP', 730), ('SJFE', 734)):
            amount = sum((money(x['amount'], 'exemption') for s in salaries for x in s.get('exemptions', []) if x['kind'] == kind), D(0))
            if amount:
                values[f'N.{box+col:04d}'] = amount
        rows = [x for s in salaries for x in s.get('workplace_periods', [])]
        for n, row in enumerate(rows):
            commune = 763+col if n == 0 else 771+col
            date_from = 765+2*col if n == 0 else 773+2*col
            frequency = 772+col if n == 0 else 777+col
            radio = 769+col if n == 0 else 777+col
            values[f'A.{commune:04d}'] = row['commune']
            values[f'D.{date_from:04d}'] = iso(row['start'], 'workplace start').strftime('%d/%m/%Y')
            values[f'D.{date_from+1:04d}'] = iso(row['end'], 'workplace end').strftime('%d/%m/%Y')
            values[f'N.{frequency:04d}'] = money(row['frequency'], 'frequency')
            values[f'R.{radio:04d}'] = '/semaine' if row['frequency_unit'] == 'week' else '/mois'
    return values
