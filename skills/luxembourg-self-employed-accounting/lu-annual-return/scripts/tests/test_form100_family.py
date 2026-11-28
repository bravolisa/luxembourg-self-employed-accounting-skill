#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Independent 2025 family boundary, failure, XML-attribution and PDF-widget checks."""
import copy
import json
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import form100_household as hh
import test_form100_tools as base
sys.path.insert(0,str(HERE.parents[2]/'lu-income-tax-personal/scripts'))
import tax_estimate as te
results=[]
def check(name,ok):results.append((bool(ok),name))
def fixture(name):return base.with_ids(json.loads((HERE/'households'/f'{name}.json').read_text()))
def rejects(name,change,source=None):
 h=copy.deepcopy(source or family);change(h)
 try:hh.validate(h)
 except SystemExit:check(name,True)
 else:check(name,False)
family=fixture('couple_child_home_childcare')
f=hh.figures(2025)
hh.validate(family)
check('child raises insurance and home savings ceilings',hh.allowed(family)['insurance']==2016 and hh.allowed(family)['home_savings_taxpayer']==4032)
check('childcare monthly cap 450+100+450=1000 after 2038',hh.indicative_check(family)['childcare abatement']==1000 and hh.indicative_check(family)['taxable income']==60372)
# January 700 + another provider 300 => household January 1000 still capped 450, not 900.
h=copy.deepcopy(family);extra=copy.deepcopy(h['childcare'][0]);extra.update(provider='Second example',paid_by='spouse',monthly={'1':{'paid':300,'reimbursed':0}});h['childcare'].append(extra)
check('monthly ceiling shared across providers, children and payer columns',hh.family.childcare_allowed(h,f)==1000)
h=copy.deepcopy(family);h['childcare'][0]['monthly']={str(i):{'paid':600,'reimbursed':0} for i in range(1,13)}
check('twelve 600 months => 5400',hh.family.childcare_allowed(h,f)==5400)
# One child+couple members 3, actual 16000: 2014 cap 6000; 2015/2019 cap 9000; 2020/2023 cap 12000; 2024 full 16000.
for year,want in [(2014,6000),(2015,9000),(2019,9000),(2020,12000),(2023,12000),(2024,16000),(2025,16000)]:
 h=copy.deepcopy(family);h['own_home'].update(available_since=f'{year}-12-31',occupied_since=f'{year}-12-31')
 check(f'home availability boundary{year}',hh.family.home_allowed(h,f)['allowed']==want)
h=copy.deepcopy(family);h['own_home']['loans'][0].update(interest=2000,subsidies=500)
check('home below cap and subsidy once: 1500',hh.family.home_allowed(h,f)['allowed']==1500)
for birthday,kind in [('2004-01-02','young'),('2004-01-01','student'),('2025-12-31','young')]:
 h=copy.deepcopy(family);h.pop('childcare');c=h['children'][0];c['birth_date']=birthday
 if kind=='student':c.update(education='university',institution='Example University',continuous_full_time_over_year=True)
 hh.validate(h);check('age boundary '+birthday,hh.family.group(c, h['tax_year'])==kind)
rejects('age 21 requires studies or continued allowance',lambda h:h['children'][0].update(birth_date='2004-01-01'))
rejects('child born after taxyear',lambda h:h['children'][0].update(birth_date='2026-01-01'))
rejects('rebate cannot duplicate allowance',lambda h:h['children'][0].update(request_rebate=True))
rejects('married child cannot silently count',lambda h:h['children'][0].update(married_or_partnered=True))
rejects('child with own child cannot silently count',lambda h:h['children'][0].update(has_children=True))
rejects('shared custody needs assignment review',lambda h:h['children'][0].update(custody='alternating'))
rejects('missing ID not confused with unassigned ID',lambda h:h['children'][0].pop('national_id_not_assigned'))
rejects('missing assignment proof',lambda h:h['children'][0].pop('assignment_evidence'))
rejects('continued allowance string rejected',lambda h:h['children'][0].update(continued_allowance='false'))
rejects('incomplete education rejected',lambda h:h['children'][0].update(education='university'))
rejects('parttime not asserted as fulltime',lambda h:h['children'][0].update(education='vocational',institution='Course',continuous_full_time_over_year=False))
rejects('inconsistent spouse status',lambda h:h['spouse'].update(status='CE'))
rejects('unknown/missing residence status',lambda h:h.pop('resident_full_year'))
rejects('unknown home availability',lambda h:h['own_home'].pop('available_since'))
rejects('different occupation date',lambda h:h['own_home'].update(occupied_since='2021-01-01'))
rejects('unequal mortgage outside supported scope',lambda h:h['own_home'].update(ownership='unequal'))
rejects('home reimbursement exceeds interest',lambda h:h['own_home']['loans'][0].update(subsidies=18000))
rejects('no loan balance is not zero',lambda h:h['own_home']['loans'][0].pop('balance_31_dec'))
rejects('mixed-use home review',lambda h:h['own_home'].update(fully_private=False))
rejects('2026 family rules not inferred',lambda h:h.update(tax_year=2026))
rejects('childcare reimbursement exceeds cost',lambda h:h['childcare'][0]['monthly']['1'].update(reimbursed=1000))
rejects('childcare missing reimbursement not assumed zero',lambda h:h['childcare'][0]['monthly']['1'].pop('reimbursed'))
rejects('duplicate childcare certificate rejected',lambda h:h['childcare'].append(copy.deepcopy(h['childcare'][0])))
rejects('fully reimbursed empty childcare claim rejected',lambda h:h['childcare'][0].update(monthly={'1':{'paid':100,'reimbursed':100}}))
rejects('ambiguous childcare payment timing',lambda h:h['childcare'][0].update(payment_timing='arrears'))
rejects('childcare missing provider approval',lambda h:h['childcare'][0].pop('approval_evidence'))
rejects('childcare prior to birth',lambda h:h['children'][0].update(birth_date='2025-12-31'))
rejects('childcare 14 on Jan 1 excluded',lambda h:h['children'][0].update(birth_date='2011-01-01'))
rejects('XML 11 distinct cost groups not truncated',lambda h:h['childcare'][0].update(monthly={str(i):{'paid':100+i,'reimbursed':0} for i in range(1,12)}))
rejects('CIM outside scope even without family fields',lambda h:h.update(single_parent_credit=True),fixture('single_liberal'))
def duplicate_id(h):
 c=h['children'][0];c['national_id']='20180601'+'0'*5;c['national_id_not_assigned']=False
 d=copy.deepcopy(c);d['first_name']='Different spelling';h['children'].append(d)
rejects('duplicate child ID cannot inflate ceilings',duplicate_id)
def too_many(h):
 h['children']=[{**h['children'][0],'first_name':'Child'+str(i)} for i in range(5)]
rejects('fifth ordinary PDF row not silently dropped',too_many)
# Independent tax calculation: adjusted 60372-4500-1000=54872; rounded 54850, half 27425.
# class 1 tax through 26550=1423.80; 875*16%=140 => 1563.80*2=3127.60 => 3127*1.07=3345.89 => 3345.
with tempfile.TemporaryDirectory() as tmp:
 tmp=Path(tmp);path=tmp/'family.json';path.write_text(json.dumps(family))
 # Component calculation only: explicit reviewed allowance and childcare, not a final salary balance.
 args={'year':2025,'taxable':60372,'tax_class':2,'both_professional':True,
       'extra_professional_amount':4500,'abatement':1000,'household_help_used':1000}
 r=te.estimate(**args)
 check('component applies childcare after taxable income',r['taxable']==60372 and r['adjusted']==54872 and r['tax']==3345)
 try:te.from_household(path)
 except SystemExit as e:check('family salary balance needs credit reconciliation','reconcile credits' in str(e))
 else:check('family salary balance needs credit reconciliation',False)
 cli=subprocess.run([sys.executable,str(Path(te.__file__)),'--household',str(path),'--json'],capture_output=True,text=True)
 check('CLI does not emit an unreviewed salary balance',cli.returncode!=0 and 'reconcile credits' in cli.stderr and not cli.stdout)
 try:te.from_household(path,year=2026)
 except SystemExit:check('family ceilings cannot carry silently into another year',True)
 else:check('family ceilings cannot carry silently into another year',False)

 try:te.what_if(args,[('household-help',Decimal(5400))])
 except SystemExit:check('whatif cannot double shared childcare/help ceiling',True)
 else:check('whatif cannot double shared childcare/help ceiling',False)
 student=tmp/'student.json';student.write_text(json.dumps(fixture('older_student_child')))
 try:te.from_household(student)
 except SystemExit:check('single-parent final estimate never defaults to class 1',True)
 else:check('single-parent final estimate never defaults to class 1',False)
 # Pair and amount attribution checked by path, not by global text occurrence.
 import build_form100_xml as xml
 from lxml import etree
 schema=xml.Schema(base.XSD);root=xml.build(family,schema).to_xml();schema.validator.assertValid(root)
 check('one property with taxpayer and spouse amounts',len(root.findall('.//ResPrincipaleRevenusNonExo'))==1)
 rows=root.findall('.//CharExtraFraisDomGardeDetail')
 check('three childcare cost periods, correctly attributed',len(rows)==3 and all(e.get('H1220_ID_PERSONNE')=='DECLARER' for e in rows))
 check('raw childcare annual rows sum 1400',sum(Decimal(e.find('H1520_CFD_MNT_FRA').text) for e in rows)==1400)
 check('child identity key reference',root.find('.//Enfant').get('G1078_ID_PERSONNE')=='CHILDREN0')
 # Stored AcroForm and every matching widget must agree, with an appearance stream.
 import pypdf
 import fill_form100_pdf as fill
 out=tmp/'family.pdf';run=base.run(HERE.parent/'fill_form100_pdf.py','--blank',base.DEFAULT_BLANK,'--household',path,'--out',out)
 check('filled family PDF generated',run.returncode==0)
 if out.exists():
  reader=pypdf.PdfReader(out);fields=reader.get_fields();expected=json.loads((HERE/'expected.json').read_text())['couple_child_home_childcare']['pdf']
  for key,want in expected.items():
   found=0;ok=True
   for page in reader.pages:
    for ref in page.get('/Annots',[]) or []:
     a=ref.get_object()
     if fill.fqn(a)!=key:continue
     found+=1;field=a if '/V' in a else a.get('/Parent').get_object()
     ok &= base.same(field.get('/V'),want) and bool(a.get('/AP',{}).get('/N'))
   check('widget value+appearance '+key,found>0 and ok and base.same(fields[key].get('/V'),want))
  annex=out.with_suffix('.childcare.pdf')
  check('monthly childcare annex automatically generated',annex.exists())
  if annex.exists():
   text=' '.join(p.extract_text() for p in pypdf.PdfReader(annex).pages)
   check('annex preservesactual and capped figures',all(x in text for x in ('800.00','100.00','700.00','450.00','1000.00')))
   from make_childcare_annex import write as write_annex
   unicode_h=copy.deepcopy(family);unicode_h['childcare'][0]['provider']='Example Crèche Łódź'
   unicode_out=tmp/'unicode.pdf';write_annex(unicode_h,unicode_out)
   text=' '.join(p.extract_text() for p in pypdf.PdfReader(unicode_out).pages)
   check('annex preserves EU-provider Unicode name','Example Crèche Łódź' in text)
 try:fill.pdf_str('Łódź')
 except SystemExit:check('form font cannot silently replace unsupported name',True)
 else:check('form font cannot silently replace unsupported name',False)

for ok,name in results:print(('PASS  ' if ok else 'FAIL  ')+name)
failed=sum(not ok for ok,_ in results)
print(f'{len(results)-failed} passed, {failed} failed, 0 skipped')
sys.exit(bool(failed))
