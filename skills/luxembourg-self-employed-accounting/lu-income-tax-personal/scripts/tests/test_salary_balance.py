#!/usr/bin/env python3
"""End-to-end salary estimates against independent literal hand calculations; no external services."""
import copy
import json
import re
import subprocess
import sys
import tempfile
from decimal import Decimal as D
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import tax_estimate as te
import salary_balance as sb

results = []
def check(name, ok):
    results.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name)
def fixture(name):
    raw = (HERE / "salary_households" / (name + ".json")).read_text()
    return json.loads(re.sub(r'@ID:(\d{4})-(\d{2})-(\d{2})', lambda m: ''.join(m.groups()) + '0'*5, raw))
def estimate(h):
    with tempfile.TemporaryDirectory() as tmp:
        path=Path(tmp)/'household.json';path.write_text(json.dumps(h))
        return te.estimate(**te.from_household(path))
def rejects(name, h, snippet=None):
    try: estimate(h)
    except SystemExit as e: check(name, snippet is None or snippet in str(e))
    else: check(name, False)
expected=json.loads((HERE/'salary_households/expected.json').read_text())
keys={'taxable_income':'taxable','adjusted_income':'adjusted','scale_base':'base',
      'tariff_tax':'scale_tax','tax_before_credits':'tax','salary_adjustment':'salary_credit_adjustment',
      'balance_raw':'balance_before_rounding','balance':'balance'}
for name in ('SB-A','SB-B','SB-C','SB-D','SB-E','SB-F'):
    r=estimate(fixture(name))
    for want,key in keys.items():
        if want in expected[name]:check(name+' '+want,r[key]==D(expected[name][want]))
    rows=r['salary_reconciliation'].values()
    if 'salary_paid' in expected[name]:
        check(name+' credits paid',sum((sum(x['paid'].values(),D(0)) for x in rows),D(0))==D(expected[name]['salary_paid']))
    if 'salary_retained' in expected[name]:
        check(name+' credits retained',sum((sum(x['retained'].values(),D(0)) for x in rows),D(0))==D(expected[name]['salary_retained']))
check('low spouse allowance zero',estimate(fixture('SB-E'))['extra_professional_abatement']==0)
check('full qualifying spouse allowance',estimate(fixture('SB-D'))['extra_professional_abatement']==4500)
check('separate spouses retain both categories',sum(estimate(fixture('SB-F'))['credits'].values())==792)

# R1–R3: independent cases in research NOTE: floor positive amount only, keep refund cents.
for name,source,delta,raw,final in [('positive-floor','SB-B','0.75','167.25','167'),
                                ('refund-cents','SB-A','0.75','-13.75','-13.75'),
                                ('small-final-balance','SB-A','-19.75','6.75','6')]:
    h=fixture(source);h['salaries'][0]['withheld']=str(D(h['salaries'][0]['withheld'])+D(delta))
    r=estimate(h);check(name,r['balance_before_rounding']==D(raw) and r['balance']==D(final))

# Net-of-CIS/CO2 withholding is algebraically equivalent, and does not change credit gross.
h=fixture('SB-B')
for s in h['salaries']:
    s['withheld']=str(D(s['withheld'])-D(str(s['cis']))-D(str(s['co2'])))
    s['withholding_basis']='after_cis_co2'
check('net withholding normalises once',estimate(h)['balance']==168)
sys.path.insert(0,str(HERE.parents[2]/'lu-annual-return/scripts'))
import form100_household as hh
import build_form100_xml as xml
check('PDF uses the same pre-credit withholding',hh.to_pdf_values(h)['N.1901']==5000)
schema=xml.Schema(HERE.parents[2]/'official-forms/F100-XSD-2025.txt')
root=xml.build(h,schema).to_xml()
check('XML uses the same pre-credit withholding',sum((D(e.text) for e in root.iter() if e.tag.endswith('SAL_MNT_RETENUE')),D(0))==5000)
h=fixture('SB-B');h['salaries'].reverse()
check('certificate order does not change balance',estimate(h)['balance']==168)
h=fixture('SB-B');h['salaries'][0]['taxable_base']=1
check('payroll base does not replace credit gross',estimate(h)['salary_reconciliation']['taxpayer']['retained']=={'cis':D(450),'co2':D(144)})

f=te.figures(2025)
for gross,cis,co2 in [('935.99','0','0'),('936','300','192'),('11265.99','599.55','192'),
                      ('11266','600','192'),('40000.99','600','192'),('40001','599.99','192'),
                      ('79999.99','.02','.01'),('80000','0','0')]:
    check('gross boundary '+gross,sb.annual_credits(gross,f)=={'cis':D(cis),'co2':D(co2)})

# Missing evidence, unsupported regimes/categories and duplicate logical certificates must not yield a balance.
mutations=[
 ('no balance facts',lambda h:h.pop('salary_balance'),'provide salary_balance'),
 ('unknown class',lambda h:h['salary_balance'].pop('tax_class'),'tax class'),
 ('class1a',lambda h:h['salary_balance'].update(tax_class=3),'class 1a'),
 ('unknown residence',lambda h:h.pop('resident_full_year'),'full-year resident'),
 ('incomplete scope',lambda h:h['salary_balance'].update(income_and_deductions_complete=False),'all income'),
 ('unknown affiliation',lambda h:h['salary_balance']['people']['taxpayer'].pop('compulsory_affiliation'),'affiliation'),
 ('unknown paid credit',lambda h:h['salaries'][0].pop('cis'),'missing is not zero'),
 ('null credit',lambda h:h['salaries'][0].update(co2=None),'missing is not zero'),
 ('negative annual paid total',lambda h:h['salaries'][0].update(cis=-10),'non-negative'),
 ('unknown withholding',lambda h:h['salaries'][0].pop('withheld'),'missing is not zero'),
 ('unknown withholding basis',lambda h:h['salaries'][0].pop('withholding_basis'),'before or after'),
 ('net includes other credits',lambda h:h['salaries'][0].update(withholding_basis='after_all_credits'),'before or after'),
 ('unknown advances',lambda h:h.pop('advances_paid'),'missing is not zero'),
 ('unknown card history',lambda h:h['salaries'][0].pop('tax_card_id'),'tax-card identity'),
 ('unknown regime',lambda h:h['salaries'][0].pop('tax_regime'),'ordinary employee'),
 ('domestic regime',lambda h:h['salaries'][0].update(tax_regime='domestic_flat_137_5'),'flat-tax'),
 ('exempt salary',lambda h:h['salaries'][0].update(all_pay_luxembourg_taxable=False),'Luxembourg-taxable'),
 ('unknown credit period',lambda h:h['salary_balance']['people']['taxpayer'].pop('full_year_eligible'),'eligibility period'),
 ('duplicate ID',lambda h:h['salaries'].append(copy.deepcopy(h['salaries'][0])),'duplicate logical'),
 ('replaced certificate still included',lambda h:h['salaries'][1].update(replaces=h['salaries'][0]['certificate_id']),'replaced version'),
 ('same-person mixed categories',lambda h:h.update(businesses=[{'owner':'taxpayer','kind':'liberal','method':'BILA','profit':5000}]),'mixed salary/business')]
for name,change,reason in mutations:
    h=fixture('SB-A' if name=='duplicate ID' else 'SB-B');change(h);rejects(name,h,reason)
h=fixture('SB-B')
for s in h['salaries']:s['start']='2025-07-01'
rejects('residence is not full-year credit eligibility',h,'do not cover a full eligible year')
h=fixture('SB-B');h['salaries'][0]['end']='2025-04-30';h['salaries'][1]['start']='2025-06-01'
rejects('gap between successive jobs',h,'do not cover a full eligible year')
h=fixture('SB-A');h['salary_balance']['people']['taxpayer']['payroll_final']=False
rejects('one-card discrepancy requires correction route',h,'final/corrected payroll')
h=fixture('SB-F');h.pop('ccss_self_employed')
rejects('unknown business contributions are not zero',h,'explicit deductible business contributions')
h=fixture('SB-D');h['individual_taxation']=True
rejects('individual spouses do not get joint household calculation',h,'individual spouse taxation')
for group in ('pension_plans','home_savings'):
    for holder in ('spouse','other'):
        h=fixture('SB-A');h[group]=[{'holder':holder,'amount':3200}]
        rejects(group+' invalid '+holder,h,'holder')
h=fixture('SB-A')
child=json.loads((HERE.parents[2]/'lu-annual-return/scripts/tests/households/couple_child_home_childcare.json').read_text())['children'][0]
child=copy.deepcopy(child);child.update(custody='sole_parent',request_rebate=False)
h['children']=[child]
rejects('class1 cannot override assigned-child facts',h,'class 1a/CIM')
check('clear payment-bridge alias',estimate(fixture('SB-B'))['amount_before_payments']==D(5168))
try:
    te.what_if({'year':2025}, [('business',D(-1))])
except SystemExit as e:
    check('negative what-if cannot bypass allowance review','non-negative' in str(e))
else:
    check('negative what-if cannot bypass allowance review',False)
h=fixture('SB-B');h['salaries'][0]['end']='2025-06-30';h['salaries'][1]['start']='2025-07-01'
check('successive jobs cover one eligible year',estimate(h)['balance']==168)
h=fixture('SB-C')
for s in h['salaries']:s['tax_card_id']=None
check('evidenced no-card salary opens reconciliation gate',estimate(h)['balance']==-805)

# Only ambiguous small-recovery grouping stops. Unambiguous spouse cases are exercised by SB-D.
for cis,co2 in [('457','151'),('462','133')]:
    h=fixture('SB-B');h['salaries'][0].update(cis=cis,co2=co2)
    rejects('ambiguous credit-recovery unit '+cis+'/'+co2,h,'PIT-O-24')

# Real CLI: readable breakdown and JSON agree; incomplete input produces no result.
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'household.json';path.write_text(json.dumps(fixture('SB-B')))
    args=[sys.executable,str(HERE.parent/'tax_estimate.py'),'--household',str(path)]
    r=subprocess.run(args+['--json'],capture_output=True,text=True)
    check('CLI JSON full result',r.returncode==0 and json.loads(r.stdout)['estimate']['balance']=='168')
    r=subprocess.run(args,capture_output=True,text=True)
    check('CLI shows paid/retained reconciliation',r.returncode==0 and 'paid €792.00, retained €594.00' in r.stdout and 'balance to pay' in r.stdout)
    h=fixture('SB-B');h['salaries'][0].pop('cis');path.write_text(json.dumps(h))
    r=subprocess.run(args+['--json'],capture_output=True,text=True)
    check('CLI unknown credits emits no balance',r.returncode!=0 and not r.stdout)
# ---- Family changes, tax year 2025 (rules: family-changes.md; inputs: salary-balance-calculator.md) ----
# Hand calculations, 11 November 2026. 2025 scale (art. 118), tax on each band:
#   13,230-15,435 at 8% = 176.40; -17,640 at 9% = 198.45; -19,845 at 10% = 220.50; -22,050 at 11% = 242.55;
#   -24,255 at 12% = 264.60; -26,550 at 14% = 321.30; -28,845 at 16% = 367.20; -31,140 at 18% = 413.10 (sum 2,204.10);
#   -33,435 at 20% = 459.00; -35,730 at 22% = 504.90; -38,025 at 24% = 550.80; -40,320 at 26% = 596.70;
#   -42,615 at 28% = 642.60; -44,910 at 30% = 688.50 (sum 5,646.60); -47,205 at 32% = 734.40; -49,500 at 34% = 780.30;
#   -51,795 at 36% = 826.20; -54,090 at 38% = 872.10 (sum 8,859.60); 39% above 54,090.
# Every case: one salary of 72,000 (SB-I: two of 80,000). Taxable = gross - contributions - 540 flat costs - 480 minimum.
# SB-G  class 2 assessed alone (court permission 2024, divorce 2025): 72,000 - 5,980 - 540 - 480 = 65,000.
#       Half 32,500: 2,204.10 + 1,360 at 20% (272.00) = 2,476.10; twice = 4,952.20 -> 4,952; + 7% (346.64) = 5,298.64 -> 5,298.
#       Credits on 72,000: CIS 600 - 32,000 x 1.5% = 120; CO2 192 - 32,000 x 0.48% = 38.40; paid = retained.
#       Balance 5,298 - 9,000 withheld = -3,702. No extra-professional abatement, one person's minimum.
# SB-H  class 1a, widowed in 2021, no child: 65,000 - (79,380 - 65,000)/4 = 61,405 at the scale, capped at 39% above 51,804:
#       at 51,804 the reduced base is 44,910 -> 5,646.60; + 39% x 13,196 = 5,146.44 -> 10,793.04 -> 10,793; + 7% (755.51) -> 11,548.
#       (The ACD prints 11 548 euros for this case.) Balance 11,548 - 12,000 = -452. No single-parent credit.
# SB-I  a spouse dies on 31 December 2025, joint return: 2 x (80,000 - 8,800 - 540) = 141,320; - 2 x 480 = 140,360;
#       - 4,500 extra-professional abatement = 135,860 -> base 135,850; half 67,925: 8,859.60 + 13,835 x 39% (5,395.65) = 14,255.25;
#       twice = 28,510.50 -> 28,510; + 7% (1,995.70) -> 30,505. No employee credits at 80,000. Balance 30,505 - 31,000 = -495.
for name in ('SB-G','SB-H','SB-I'):
    r=estimate(fixture(name))
    for want,key in keys.items():
        if want in expected[name]:check(name+' '+want,r[key]==D(expected[name][want]))
    rows=list(r['salary_reconciliation'].values())
    check(name+' credits paid and retained',sum((sum(v['paid'].values(),D(0)) for v in rows),D(0))==D(expected[name]['salary_paid']) and sum((sum(v['retained'].values(),D(0)) for v in rows),D(0))==D(expected[name]['salary_retained']))
check('SB-G class 2 without a spouse, no extra-professional abatement',estimate(fixture('SB-G'))['class']==2 and estimate(fixture('SB-G'))['extra_professional_abatement']==0)
check('SB-H class 1a without the single-parent credit',estimate(fixture('SB-H'))['class']=='1a' and not estimate(fixture('SB-H'))['single_parent_reconciliation'])
check('SB-I joint class 2 with the full extra-professional abatement',estimate(fixture('SB-I'))['class']==2 and estimate(fixture('SB-I'))['extra_professional_abatement']==4500)
h=fixture('SB-G');h['salary_balance']['class2_alone']['event_year']=2021
rejects('class 2 alone ends after three years',h,'three tax years')
h=fixture('SB-G');h['salary_balance']['class2_alone'].pop('no_use_in_five_years_before')
rejects('class 2 alone needs the five-year condition',h,'five years')
h=fixture('SB-G');h['salary_balance'].pop('class2_alone')
rejects('class 2 without a spouse needs the reviewed transition',h,'class-2')
h=fixture('SB-G');h['salary_balance']['class2_alone']['ground']='widowed'
rejects('class 2 alone as widowed needs the status VE',h,'VE')
h=fixture('SB-H');h['taxpayer']['status_since']='2022-03-15'
rejects('class 1a as widowed only from the fourth year after the death',h,'fourth year')
h=fixture('SB-H');h['salary_balance'].pop('class_1a_ground')
rejects('class 1a without a child needs a reviewed ground',h,'class 1a')
h=fixture('SB-H');h['taxpayer'].update(status='CE');h['taxpayer'].pop('status_since');h['salary_balance']['class_1a_ground']='age'
rejects('class 1a by age: not yet 64 on 1 January',h,'64')
h['taxpayer']['national_id']='19610101'+'0'*5  # invented: born 1 January 1961
check('class 1a by age: 64 completed on 1 January 2025, same tax as SB-H',estimate(h)['tax']==D('11548'))
h=fixture('SB-I')
for side,code in (('taxpayer','VE'),('spouse','DE')):h[side]['status_changes']=[{'status':code,'since':'2025-06-30'}]
rejects('death during the year: balance not calculated (PIT-O-40)',h,'PIT-O-40')
print(f'{sum(results)} passed, {len(results)-sum(results)} failed, 0 skipped')
sys.exit(not all(results))
