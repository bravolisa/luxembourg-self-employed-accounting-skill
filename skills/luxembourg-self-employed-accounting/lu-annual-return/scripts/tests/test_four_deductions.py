#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Independent arithmetic, refusal, PDF and XSD tests for four 2025 branches.

Literal expected results and derivations: four_deductions/expected.json.
All identities are synthetic placeholders resolved only in temporary test outputs.
"""
import copy
import json
import re
import subprocess
import sys
import tempfile
from decimal import Decimal as D
from pathlib import Path
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
SKILLS = HERE.parents[2]
ROOT = SKILLS.parents[1]
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(SKILLS/'lu-income-tax-personal/scripts'))
import form100_household as hh
import build_form100_xml as xml
import tax_estimate as tax

results = []
def check(name, ok):
    results.append(bool(ok))
    print(('PASS ' if ok else 'FAIL ') + name)
def rejects(name, fn, *args, contains=None):
    try:
        fn(*args)
    except SystemExit as e:
        check(name, contains is None or contains in str(e))
    else:
        check(name, False)
def read(path):
    return json.loads(re.sub(r'@ID:(\d{4})-(\d{2})-(\d{2})', lambda m: ''.join(m.groups())+'0'*5, path.read_text()))
def fixture(name):
    return read(HERE/'four_deductions'/f'{name}.json')
def estimate(h):
    with tempfile.TemporaryDirectory() as tmp:
        p=Path(tmp)/'h.json';p.write_text(json.dumps(h))
        return tax.estimate(**tax.from_household(p))
def element(root, suffix):
    return [e.text for e in root.iter() if e.tag.endswith(suffix)]

expected = json.loads((HERE/'four_deductions/expected.json').read_text())
schema = xml.Schema(SKILLS/'official-forms/F100-XSD-2025.txt')
for name in ('consumer', 'donations', 'premium', 'single_parent'):
    h=fixture(name);hh.validate(h)
    check(name+' indicative income',hh.indicative_check(h)['taxable income']==D(expected[name]['taxable']))
    root=xml.build(h,schema).to_xml()
    check(name+' XSD valid',schema.validator.validate(root))
    for suffix, values in expected[name].get('xml',{}).items():
        check(name+' XML '+suffix,element(root,suffix)==values)
    for field, value in expected[name]['pdf'].items():
        check(name+' PDF '+field,hh.to_pdf_values(h).get(field)==value)

f=hh.figures(2025)
h=fixture('consumer')
for interest,insurance,allowed in [('100','0','100'),('100','600','672'),('672','0','672'),('673','0','672')]:
    h['consumer_loans'][0]['interest']=interest
    h['insurance']=[{'insurer':'Example insurer','risk':'RC','paid_by':'taxpayer','amount':insurance}]
    check('shared cap '+interest+'/'+insurance,hh.allowed(h)['insurance']==D(allowed))
h=fixture('consumer');h['consumer_loans'][0].update(interest=700,subsidies_and_refunds=100)
check('current subsidy reduces interest before cap',hh.allowed(h)['insurance']==600)
for name,mutate in [
 ('unknown interest',lambda h:h['consumer_loans'][0].pop('interest')),
 ('unknown zero balance',lambda h:h['consumer_loans'][0].pop('balance_31_dec')),
 ('property excluded',lambda h:h['consumer_loans'][0].update(no_property_or_exempt_income=False)),
 ('mixed business excluded',lambda h:h['consumer_loans'][0].update(fully_private=False)),
 ('payer not borrower',lambda h:h['consumer_loans'][0].update(paid_by='spouse')),
 ('duplicate loan',lambda h:h['consumer_loans'].append(copy.deepcopy(h['consumer_loans'][0]))),
 ('refund over interest',lambda h:h['consumer_loans'][0].update(subsidies_and_refunds=2000))]:
    h=fixture('consumer');mutate(h);rejects(name,hh.validate,h)

for actual,base,allowed,carry in [('119.99','40000','0','0'),('120','40000','120','0'),
                                ('12000','40000','8000','4000'),('2000000','10000000','1000000','1000000')]:
    h=fixture('donations');h['donations'][0]['amount']=actual
    result=hh.deductions.donations(h,D(base),f)
    check('donation limits '+actual+'/'+base,result['allowed']==D(allowed) and result['new_carryforward']==D(carry))
for name,mutate in [
 ('donation eligibility unknown',lambda h:h['donations'][0].pop('eligibility_evidence')),
 ('donation invalid recipient',lambda h:h['donations'][0].update(eligibility='unapproved')),
 ('donation below-year carry rejected',lambda h:h.update(donation_carryforward=[{'year':2024,'amount':1000}])),
 ('carry absence unknown',lambda h:h['donation_review'].pop('no_prior_carryforward')),
 ('duplicate donation',lambda h:h['donations'].append(copy.deepcopy(h['donations'][0]))),
 ('donation in kind',lambda h:h['donations'][0].update(cash_gift=False))]:
    h=fixture('donations');mutate(h);rejects(name,hh.validate,h)
h=fixture('donations');h['donations'][0].update(country='DE',eligibility='eu_efta_equivalent')
hh.validate(h);check('evidenced foreign equivalent accepted',True)
rejects('negative net-income donation review',hh.deductions.donations,fixture('donations'),D('-1000'),f)
rejects('donation fractional cent cap stops',hh.deductions.donations,fixture('donations'),D('40000.01'),f)

for born,amount,prior,ceiling,allowed in expected['premium_cases']:
    h=fixture('premium');h['taxpayer']['national_id']=born.replace('-','')+'0'*5
    item=h['insurance'][0];item['amount']=amount;item['single_premium']['previous_increases']['2024']=prior
    a=hh.allowed(h)
    check('PU age/amount/history '+born+'/'+str(amount)+'/'+str(prior),a['insurance_ceiling']==D(ceiling) and a['insurance']==D(allowed))
h=fixture('premium');h['insurance'][0]['single_premium']['previous_increases']['2024']=1000
hh.validate(h)
rejects('prior-use PU XML stops',xml.build,h,schema,contains='prior-used')
for name,mutate in [
 ('crossed roles',lambda h:h['insurance'][0]['single_premium'].update(insured='spouse')),
 ('unknown prior increases',lambda h:h['insurance'][0]['single_premium'].pop('history_complete')),
 ('missing prior year',lambda h:h['insurance'][0]['single_premium']['previous_increases'].pop('2020')),
 ('unproved payment',lambda h:h['insurance'][0]['single_premium'].update(premium_fully_paid=False)),
 ('same-person duplicate premium',lambda h:h['insurance'].append(copy.deepcopy(h['insurance'][0]))),
 ('unlinked property',lambda h:h.pop('own_home'))]:
    h=fixture('premium');mutate(h);rejects(name,hh.validate,h)

for income,want in expected['class1a_tax'].items():
    check('class1a official annual check '+income,tax.income_tax(D(income),'1a',f)['tax']==D(want))
for income,support,want in expected['cim_cases']:
    check('annual CIM '+str(income)+'/'+str(support),hh.single_parent.entitlement(D(income),D(support),f)==D(want))
rejects('ambiguous annual CIM income floor stops',hh.single_parent.entitlement,D('75001'),D(0),f,contains='PIT-O-17')
rejects('fractional-cent annual CIM stops',hh.single_parent.entitlement,D('50000'),D('2712.01'),f,contains='fractional-cent')
h=fixture('single_parent');r=estimate(h)
check('CIM paid/retained balance',r['balance']==D(expected['single_parent']['balance']) and r['single_parent_reconciliation']['retained']==3504)
h['salaries'][0]['withheld']='-1000';h['salaries'][0]['withholding_basis']='after_cis_co2_cim'
check('net CIM withholding gives same result',estimate(h)['balance']==D(expected['single_parent']['balance']))
for name,mutate in [
 ('other parent cohabits',lambda h:h['single_parent_credit']['support'][0].update(other_parent_same_home=True)),
 ('irregular support',lambda h:h['single_parent_credit']['support'][0].update(support_regular_monthly=False)),
 ('foreign-only moderation',lambda h:h['single_parent_credit']['support'][0].update(moderation='foreign_only')),
 ('unknown paid CIM',lambda h:h['salaries'][0].pop('cim')),
 ('ambiguous CIM withholding',lambda h:h['salaries'][0].update(withholding_basis='before_cis_co2')),
 ('class2 transition',lambda h:h['single_parent_credit'].update(no_class2_transition=False)),
 ('partial eligibility',lambda h:h['single_parent_credit'].update(full_year_eligibility=False)),
 ('third-party support',lambda h:h['single_parent_credit']['support'][0].update(all_support_from_other_parent=False))]:
    h=fixture('single_parent');mutate(h);rejects(name,hh.validate,h)

# The paper requests the unpaid remainder; the XML requests annual application.
for paid in (3504, 4000):
    h=fixture('single_parent');h['salaries'][0]['cim']=paid
    check('fully/overpaid CIM paper unticked '+str(paid),hh.to_pdf_values(h)['C.0228']=='/Off')
    root=xml.build(h,schema).to_xml()
    check('fully/overpaid CIM XML annual application '+str(paid),element(root,'ENF_CRE_IMP')==['true'])
    check('fully/overpaid CIM reconciliation '+str(paid),estimate(h)['single_parent_reconciliation']['adjustment']==D(paid)-3504)
h=fixture('single_parent');h['salaries']=[];h.pop('salary_balance')
rejects('no-income CIM requires subsistence completion',hh.validate,h,contains='A0237')

# Combined household multipliers and allocation; independent circular examples.
source=read(HERE/'households/couple_child_home_childcare.json')
child=copy.deepcopy(source['children'][0]);child.update(moderation_origin='lu_positive_benefit',moderation_evidence='Synthetic positive LU moderation')
h=fixture('consumer');h['taxpayer']['status']='MA';h['spouse']=copy.deepcopy(source['spouse']);h['children']=[copy.deepcopy(child)]
h['consumer_loans'][0]['interest']=700
h['insurance']=[{'insurer':'Example','risk':'RC','paid_by':'spouse','amount':900}]
check('joint child shared pool1600 below2016',hh.allowed(h)['insurance']==1600 and hh.allowed(h)['insurance_ceiling']==2016)
h['children'][0].pop('moderation_origin');rejects('unknown child origin stops multiplier',hh.allowed,h)
h['children'][0].update(moderation_origin='lu_positive_benefit',moderation='foreign_only')
rejects('contradictory foreign-only child stops',hh.validate,h)

h=fixture('premium');h['taxpayer'].update(status='MA',national_id='19780101'+'0'*5)
h['spouse']=copy.deepcopy(source['spouse']);h['spouse']['national_id']='19820101'+'0'*5
h['children']=[copy.deepcopy(child)];h['own_home']['ownership']='joint_equal';h['insurance']=h['insurance'][:1]
h['insurance'][0]['amount']=16500;h['insurance'][0]['single_premium']['children']=[0]
p=copy.deepcopy(h['insurance'][0]);p.update(paid_by='spouse',amount=13500);p['single_premium'].update(subscriber='spouse',insured='spouse',children=[]);h['insurance'].append(p)
check('two own-life policies one child',hh.allowed(h)['insurance']==30000 and hh.allowed(h)['insurance_ceiling']==30756)
root=xml.build(h,schema).to_xml();check('two-adult PU XSD registry',schema.validator.validate(root) and element(root,'ID_RESPRINCIPALE')==['RESPRINCIPALE0'])
h['insurance'][1]['single_premium']['children']=[0];rejects('PU child cannot be assigned twice',hh.validate,h)

h=fixture('single_parent');row=h['single_parent_credit']['support'][0];row.update(monthly_support=300,annual_support=3600)
root=xml.build(h,schema).to_xml();check('support exported monthly300 not annual3600',element(root,'ENF_MNT_ALL')==['300.00'] and hh.to_pdf_values(h)['N.0230']==300)
check('support reduction balances3060retained',estimate(h)['single_parent_reconciliation']['retained']==3060 and estimate(h)['balance']==-2106)
second=copy.deepcopy(h['children'][0]);second['first_name']='Second';second.pop('national_id',None);second.update(national_id_not_assigned=True,birth_date='2019-06-01');h['children'].append(second)
row2=copy.deepcopy(row);row2.update(child=1,monthly_support=100,annual_support=1200);h['single_parent_credit']['support'].append(row2)
check('lowest child support one CIM only',estimate(h)['single_parent_reconciliation']['retained']==3504)
for status,since in [('DI','2025-06-01'),('DI','2026-06-01'),('VE','2023-01-01')]:
    h=fixture('single_parent');h['taxpayer'].update(status=status,status_since=since);rejects('contradictory status '+status+since,hh.validate,h)
h=fixture('consumer');h['insurance']=[{'insurer':'Example','risk':'RC','paid_by':'taxpayer','amount':-1000}]
rejects('negative ordinary premium cannot cancel interest',hh.allowed,h)
h=fixture('donations');h['capital_income']=[{'amount':10000}];rejects('direct net-income path rejects unsupported income',hh.indicative_check,h)

# A business what-if changes the gift limit; a new year needs a fresh deduction review.
with tempfile.TemporaryDirectory() as tmp:
    path=Path(tmp)/'h.json';path.write_text(json.dumps(fixture('donations')))
    args=tax.from_household(path)
    rejects('business what-if rechecks donation cap',tax.what_if,args,[('business',D(1000))],contains='donation what-if')
    rejects('new-year deduction eligibility not carried blindly',tax.from_household,path,2026,contains='re-establish')

# Real PDF output must retain actual gift amounts but use only the allowed deduction.
# Check canonical fields, appearance streams, cap action removal, and mandatory annex.
blank=SKILLS/'official-forms/100f-2025.pdf'
with tempfile.TemporaryDirectory() as tmp:
    tmp=Path(tmp)
    for name in ('consumer','donations','premium','single_parent','donations_cents'):
        source=tmp/(name+'.json')
        h=fixture('donations' if name=='donations_cents' else name)
        if name=='donations_cents':h['donations'][0]['amount']='12000.01'
        source.write_text(json.dumps(h))
        expected_name='donations' if name=='donations_cents' else name
        out=tmp/(name+'.pdf')
        run=subprocess.run([sys.executable,str(HERE.parent/'fill_form100_pdf.py'),'--blank',str(blank),'--household',str(source),'--out',str(out)],capture_output=True,text=True)
        check(name+' filled PDF completes',run.returncode==0)
        if run.returncode:
            print(run.stdout+run.stderr);continue
        reader=PdfReader(out);fields=reader.get_fields()
        check(name+' final2038',D(fields['T.2038']['/V'])==D(expected[expected_name]['taxable']))
        if name=='donations_cents':
            check('fractional donation excess total correct',D(fields['T.1639']['/V'])==11672 and D(fields['N.1633']['/V'])==D('12000.01'))
        if name=='donations':
            check('donation genuine gross preserved',D(fields['N.1633']['/V'])==12000)
            check('donation special-expense sum capped',D(fields['T.1639']['/V'])==11672)
            check('donation stale gross calculation removed','/C' not in fields['T.1639'].get('/AA',{}))
        for field,want in (expected[expected_name]['pdf'].items() if name!='donations_cents' else []):
            got=fields[field]['/V']
            check(name+' stored '+field,str(got)==str(want) if isinstance(want,str) else D(got)==D(str(want)))
        if name in ('premium','donations'):
            check(name+' calculation annex exists',out.with_suffix('.deductions.pdf').exists())

print(f'{sum(results)} passed, {len(results)-sum(results)} failed, 0 skipped')
sys.exit(not all(results))
