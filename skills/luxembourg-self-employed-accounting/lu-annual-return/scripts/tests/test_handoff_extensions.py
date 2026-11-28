#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Independent 2025 handoff examples, scope refusals and real output checks.

Arithmetic is written inline from stated facts, not copied from calculator results.
Synthetic fixtures derive from the published ordinary examples; no project client files.
"""
import copy,json,re,sys,tempfile,subprocess,os,shutil
from pathlib import Path
from decimal import Decimal as D
from pypdf import PdfReader
HERE=Path(__file__).resolve().parent;SKILLS=HERE.parents[2];ROOT=SKILLS.parents[1]
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(SKILLS/'lu-income-tax-personal/scripts'))
import form100_household as hh,build_form100_xml as xml,tax_estimate as tax
EXPECTED=json.loads((HERE/"handoff_extensions/expected.json").read_text())
RESULTS=[]
def check(label,ok):RESULTS.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+label)
def rejects(label,fn,*args,contains=None):
 try:fn(*args)
 except SystemExit as e:check(label,contains is None or contains in str(e))
 else:check(label,False)
def read(p):return json.loads(re.sub(r'@ID:(\d{4})-(\d{2})-(\d{2})',lambda m:''.join(m.groups())+'0'*5,p.read_text()))
def base():
 h=read(HERE/'four_deductions/consumer.json');h.pop('consumer_loans');h['insurance']=[{'insurer':'Example','risk':'RC','paid_by':'taxpayer','amount':500}];return h
# Base: 30000 - salary 540 - social 3300 - insurance 500 = taxable 25660.
def record(amount,**extra):return {'owner':'taxpayer','amount':amount,'evidence':'Synthetic complete review','net_of_reimbursements':True,'not_deducted_elsewhere':True,**extra}
def cost(amount=1500):return record(amount,method='actual',employment_related=True)
def occupational(amount=1200):return record(amount,certificate_id='OCC1',employee_personal_contribution=True,qualifying_scheme=True,scheme_evidence='Synthetic qualifying scheme')
def voluntary(amount=200):return record(amount,certificate_id='VOL1',kind='continued',qualifying_scheme=True,scheme_evidence='Synthetic qualifying continuation',not_compulsory_or_dependency=True,salary_related=True)
def estimate(h):
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)/'h.json';p.write_text(json.dumps(h));return tax.estimate(**tax.from_household(p))
def el(root,suffix):return [x.text for x in root.iter() if x.tag.endswith(suffix)]
schema=xml.Schema(SKILLS/'official-forms/F100-XSD-2025.txt')
def tree(h,label):
 root=xml.build(h,schema).to_xml();check(label+' XSD',schema.validator.validate(root));return root
outputs={}
h=base();h['salary_costs']=[cost()];check('actual costs replace 540: taxable 24700',hh.indicative_check(h)['taxable income']==EXPECTED['actual']['taxable']);v=hh.to_pdf_values(h);check('actual PDF 743',v['N.0743']==1500);root=tree(h,'actual costs');check('actual XML FE 1500',el(root,'SAL_FO_MIN_FORFAIT')==['FE'] and el(root,'SAL_FO_REV_IMP')==['1500.00']);outputs['actual']=h
for amount in (0,400):
 h=base();h['salary_costs']=[cost(amount)];rejects('actual below minimum '+str(amount),hh.validate,h)
h=base();h['salary_costs']=[cost(),cost()];rejects('duplicate actual election',hh.validate,h)
h=base();h['occupational_pension']=[occupational(1800)];check('occupational cap separate: taxable 24460',hh.indicative_check(h)['taxable income']==EXPECTED['occupational']['taxable'] and hh.to_pdf_values(h)['N.1605']==1200 and hh.to_pdf_values(h)['R.1609']=='/courrier');rejects('above-cap occupational XML preserves review',xml.build,h,schema,contains='above-cap');outputs['occupational_above']=h
h=base();h['occupational_pension']=[occupational()];root=tree(h,'occupational');check('occupational actual 1200 XML',el(root,'RCS_COT_CONT_NEX')==['1200.00'])
h=base();h['voluntary_contributions']=[voluntary()];check('voluntary inside actual pool: taxable 25460',hh.indicative_check(h)['taxable income']==EXPECTED['voluntary']['taxable']);root=tree(h,'voluntary');check('voluntary PDF/XML',hh.to_pdf_values(h)['N.1501']==200 and el(root,'CTP_MNT_CONT')==['200.00']);outputs['voluntary']=h
h=base();h['insurance']=[];h['voluntary_contributions']=[voluntary()];check('voluntary 200 loses to minimum 480',hh.allowed(h)['covered']==480)
h=base();h['salary_costs']=[cost()];h['occupational_pension']=[occupational()];h['voluntary_contributions']=[voluntary()];check('combined independent deductions 23300',hh.indicative_check(h)['taxable income']==EXPECTED['combined']['taxable'])
# Private contracts: exact anniversaries, and malformed/legacy timing must stop.
def plan(h,born,start,end,payment=None):
 h['taxpayer']['national_id']=born.replace('-','')+'0'*5
 h['pension_plans']=[{'holder':'taxpayer','insurer':'Example pension','start':start,'end':end,'amount':2000,'pepp':False}]
 if payment:h['pension_plans'][0]['payment_date']=payment
 return h
for label,born,start,end,payment,valid in [
 ('exact60and10','1965-06-30','2015-06-30','2025-06-30','2025-01-01',True),
 ('before60and10','1965-06-30','2015-06-30','2025-06-29','2025-01-01',False),
 ('exact75','1950-06-30','2010-01-01','2025-06-30','2025-01-01',True),
 ('after75','1950-06-30','2010-01-01','2025-07-01','2025-01-01',False),
 ('subscriptioneve65','1960-06-30','2025-06-29','2035-06-29','2025-07-01',True),
 ('subscription65','1960-06-30','2025-06-30','2035-06-30','2025-07-01',False),
 ('oldmaturity','1980-01-15','2020-01-02','2056-12-31',None,False),
 ('legacy','1950-01-01','2001-01-01','2025-01-01','2025-01-01',False),
 ('wrongpaymentyear','1965-06-30','2015-06-30','2025-06-30','2024-01-01',False),
 ('paymentbeforestart','1960-06-30','2025-06-29','2035-06-29','2025-01-01',False),
 ('malformed','1985-01-01','2015-01-01','nonsense',None,False),
 ('leapdayreview','1984-02-29','2015-01-01','2045-03-01',None,False)]:
 h=plan(base(),born,start,end,payment)
 if valid:hh.validate(h);check('pension '+label,hh.allowed(h)['pension_taxpayer']==2000)
 else:rejects('pension '+label,hh.validate,h)
h=plan(base(),'1985-01-01','2015-01-01','2045-01-01');h['pension_plans'][0]['pepp']='false';rejects('PEPP must be boolean',hh.validate,h)
h=plan(base(),'1985-01-01','2015-01-01','2045-01-01');h['pension_plans'][0].update(pepp=True,subaccount_country='DE',subaccount_evidence='Foreign example');rejects('foreign PEPP subaccount',hh.validate,h)
h['pension_plans'][0].update(subaccount_country='LU');hh.validate(h);check('reviewed Luxembourg PEPP',True)
h['spouse']=dict(h['taxpayer']);rejects('pension unmarried joint household',hh.validate,h)
# PACS common-child household retains independently reviewed married-case deductions.
h=read(HERE/'households/couple_child_home_childcare.json');married_income=hh.indicative_check(h)['taxable income']
for side in ('taxpayer','spouse'):h[side].update(status='PA',underlying_civil_status='CE')
h['joint_taxation_option']=True;h['partnership']={'registered_in_luxembourg':True,'no_competing_election_or_assessment':True,'both_request_joint':True,'same_home_full_year':True,'no_status_change':True,'evidence':'Synthetic registry/election/common home','certificate_evidence':'Synthetic certificate','certificate_already_presented':False,'declaration_date':'2020-06-01','common_home_since':'2020-01-01'}
for child in h['children']:child['common_child_of_partners']=True
check('PACS same reviewed family income',hh.indicative_check(h)['taxable income']==married_income);v=hh.to_pdf_values(h);check('PACS separate paper election',v['C.0312']=='/Yes' and v['R.0301']=='/celibataire' and v['R.0314']=='/enannexe' and 'R.0317' not in v);root=tree(h,'PACS');check('PACS XML joint option',el(root,'ASS_DEM_3BIS')==['true'] and el(root,'ASS_DEM_3BIS_DOC')==['false']);outputs['pacs']=h
for label,mutate in [('eventyear',lambda x:x['partnership'].update(declaration_date='2025-01-01')),('partialyear',lambda x:x.update(tax_liability_months=11)),('noncommonchild',lambda x:x['children'][0].update(common_child_of_partners=False)),('missingcert',lambda x:x['partnership'].pop('certificate_evidence'))]:
 q=copy.deepcopy(h);mutate(q);rejects('PACS '+label,hh.validate,q)
# Medical costs: one burden on 2038, and raw/refunds kept apart in XML.
def medical(h,gross=7000,refunds=3000,cls=1):
 h['medical_expenses']=[{'invoice_id':'MED1','paid_by':'taxpayer','patient':'taxpayer','kind':'medical','article127_eligible':True,'eligibility_evidence':'Synthetic reviewed necessary medical expense','provider':'Example Clinic','payment_evidence':'Synthetic payment receipt','payment_date':'2025-06-01','currency':'EUR','no_other_deduction':True,'no_forfait_or_childcare_overlap':True,'refunds_final_and_complete':True,'description':'Medical treatment','gross':gross,'refunds':refunds}]
 h['medical_expenses'][0].update(pending_refunds=False,expected_refunds=0,refund_review_evidence='Synthetic all-insurer and supplementary entitlement review',refund_items=[{'refund_id':'REF1','recipient':'taxpayer','amount':refunds,'date':'2025-07-01','evidence':'Synthetic refund statement'}] if refunds else [])
 h['medical_review']={'income_complete':True,'no_foreign_or_exempt_progression':True,'all_actual_article127_costs_included':True,'evidence':'Synthetic complete income/cost review','tax_class':cls};return h
h=medical(base());c=hh.indicative_check(h);check('medical base 25660 burden 1539.60 relief 2460.40',c['taxable income']==25660 and c['medical abatement']==D(EXPECTED['medical']['allowed']));check('medical adjusted income 23199.60',estimate(h)['adjusted']==D(EXPECTED['medical']['adjusted']));root=tree(h,'medical');check('medical raw gross/refund XML',el(root,'CFM_MNT_FRA_MAL')==['7000.00'] and el(root,'CFM_MNT_TOT_REM')==['3000.00']);check('medical PDF net before burden',hh.to_pdf_values(h)['N.1702']==4000);outputs['medical']=h
q=copy.deepcopy(h);q['spouse']=copy.deepcopy(outputs['pacs']['spouse']);q['taxpayer']['status']='MA';q['spouse']['status']='MA';q['medical_review']['tax_class']=2
f=hh.figures(2025)
for income,rate,allowed in [(40000,7,1200),(60000,8,0),(60001,9,0)]:
 c=hh.medical.calculation(q,D(income),f);check('medical published class 2 boundary '+str(income),c['rate']==rate and c['allowed']==allowed)
rejects('medical material 20k endpoint',hh.medical.calculation,q,D(20000),f)
rejects('medical fractional-cent relief',hh.medical.calculation,h,D('25000.01'),f)
for label,change in [('refundovergross',lambda x:x['medical_expenses'][0].update(refunds=8000)),('thirdpartypatient',lambda x:x['medical_expenses'][0].update(patient='spouse')),('class1aolder',lambda x:x['taxpayer'].update(national_id='19600601'+'0'*5)),('class2transition',lambda x:x['taxpayer'].update(status='DI'))]:
 q=copy.deepcopy(h);change(q);rejects('medical '+label,hh.validate,q)
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'h.json';p.write_text(json.dumps(h));args=tax.from_household(p);rejects('medical what-if must recompute',tax.what_if,args,[('special',D(1000))],contains='medical what-if')
# Payroll exemption reduces net income but leaves salary-credit gross unchanged.
h=base();h['salaries'][0]['exemptions']=[{'kind':'HSUP','amount':1000,'included_in_gross':True,'eligibility_evidence':'Synthetic overtime exemption','certified_exempt':True,'contributions_reconciled':True,'not_deducted_elsewhere':True,'private_sector_eligible_overtime':True,'not_senior_manager':True}]
check('exemption taxable 24660',hh.indicative_check(h)['taxable income']==EXPECTED['exemption']['taxable']);check('exemption gross credit unchanged',estimate(h)['salary_reconciliation']['taxpayer']['gross']==30000);root=tree(h,'exemption');check('exemption XML exact code/amount',el(root,'SAL_NAT_EXEMP_NEX')==['HSUP'] and el(root,'SAL_MNT_EXEMPT_NEX')==['1000.00']);check('exemption PDF gross preserved',hh.to_pdf_values(h)['N.0701']==30000 and hh.to_pdf_values(h)['N.0730']==1000);outputs['exemption']=h
# Dated work locations: independent reviewed FD, no inferred geography calculation.
h=base();s=h['salaries'][0];s['workplaces']=['LUXEMBOURG','ESCH-SUR-ALZETTE'];s['workplace_periods']=[{'commune':'LUXEMBOURG','start':'2025-01-01','end':'2025-06-30','frequency':5,'frequency_unit':'week','evidence':'Synthetic employment record'},{'commune':'ESCH-SUR-ALZETTE','start':'2025-07-01','end':'2025-12-31','frequency':12,'frequency_unit':'month','evidence':'Synthetic schedule'}];h['commuting_review']={'periods_complete':True,'annual_amount_reviewed':True,'evidence':'Synthetic reconciled FD'}
v=hh.to_pdf_values(h);check('workplace unusual number/radio names',v['N.0772']==5 and v['R.0769']=='/semaine' and v['N.0777']==12 and v['R.0777']=='/mois');root=tree(h,'workplaces');check('workplaces XML unique communes',el(root,'Commune')==['LUXEMBOURG','ESCH-SUR-ALZETTE']);outputs['workplaces']=h
# Separate employee benefit: cannot masquerade as employer pay or invent a workplace.
h=base();s=h['salaries'][0];s.update(cim=0,source='employee_replacement',replacement_kind='sickness',employee_replacement_eligible=True,employee_replacement_evidence='Synthetic employee replacement certificate',overlap_and_duplicates_reconciled=True,contributions_reconciled=True,workplaces=[],pay=[{'kind':'A','description':'Direct employee sickness benefit','amount':30000}]);v=hh.to_pdf_values(h);check('replacement PDF 709 no employer 701',v['N.0709']==30000 and 'N.0701' not in v);check('replacement category net 25660',hh.indicative_check(h)['taxable income']==25660);check('replacement credit gross 30000',estimate(h)['salary_reconciliation']['taxpayer']['gross']==30000);rejects('replacement no fake XML workplace',xml.build,h,schema,contains='workplace');outputs['replacement']=h
q=copy.deepcopy(h);q['salaries'][0].update(workplaces=['LUXEMBOURG'],xml_workplace_review={'authoritative_semantics_confirmed':True,'authority_evidence':'Synthetic authoritative answer for this mapped work commune'});root=tree(q,'replacement evidenced XML');check('replacement description XML',el(root,'SAL_DES_SAL_NEX')==['Direct employee sickness benefit'])
for label,change in [('missingwithheld',lambda x:x['salaries'][0].pop('withheld')),('missingbasis',lambda x:x['salaries'][0].pop('withholding_basis')),('missingcim',lambda x:x['salaries'][0].pop('cim')),('missingperiod',lambda x:x['salaries'][0].pop('start')),('missingcard',lambda x:x['salaries'][0].pop('tax_card_id')),('foreignscope',lambda x:x['salaries'][0].update(all_pay_luxembourg_taxable=False)),('missingspouse',lambda x:x['salaries'][0].update(owner='spouse')),('duplicate',lambda x:x['salaries'].append(copy.deepcopy(x['salaries'][0])))]:
 q=copy.deepcopy(h);change(q);rejects('replacement '+label,hh.validate,q)
q=copy.deepcopy(outputs['exemption']);q['salaries'][0]['all_pay_luxembourg_taxable']=False;rejects('foreign exemption source',hh.validate,q)
# Low-spouse 113 and extra-professional 129b use different contribution subsets.
h=base();h['taxpayer']['status']='MA';h['spouse']=copy.deepcopy(h['taxpayer']);h['spouse']['national_id']='19860101'+'0'*5
s2=copy.deepcopy(h['salaries'][0]);s2.update(owner='spouse',certificate_id='LOW-SPOUSE',employer='Example second employer',pay=[{'kind':'S','amount':2000}],contributions=200,withheld=0,cis=0,co2=0);h['salaries'].append(s2)
h['salary_balance']['tax_class']=2;h['salary_balance']['people']['spouse']=copy.deepcopy(h['salary_balance']['people']['taxpayer'])
h['occupational_pension']=[dict(occupational(),owner='spouse')];h['voluntary_contributions']=[dict(voluntary(50),owner='spouse')]
check('low spouse article 113 related 490',hh.allowed(h)['flat_minimum']==EXPECTED['low_spouse']['minimum_related'])
check('extra-professional excludes occupational voluntary 780',estimate(h)['extra_professional_abatement']==EXPECTED['low_spouse']['extra_professional'])
h['voluntary_contributions'][0]['salary_related']=False;check('low spouse article 113 unrelated 540',hh.allowed(h)['flat_minimum']==EXPECTED['low_spouse']['minimum_unrelated'])
# Alternate duplicate IDs and corrected predecessor both stop, not only exact IDs.
q=copy.deepcopy(outputs['replacement']);q['salaries'].append(copy.deepcopy(q['salaries'][0]));q['salaries'][1]['certificate_id']='COPY-ID';rejects('equivalent benefit renamed',hh.validate,q)
q['salaries'][1]['employer']='Corrected example';q['salaries'][1]['replaces']=q['salaries'][0]['certificate_id'];rejects('corrected and predecessor benefit',hh.validate,q)
q=copy.deepcopy(outputs['replacement']);q['salaries'].append(copy.deepcopy(q['salaries'][0]));q['salaries'][1].update(certificate_id='FORMAT-COPY',contributions='3300.00',withheld='1400.00');q['salaries'][1]['pay'][0]['amount']='30000.00';rejects('equivalent benefit numeric formatting',hh.validate,q)
# XML command executes its reporting path as well as schema construction.
with tempfile.TemporaryDirectory() as t:
 t=Path(t);source=t/'h.json';source.write_text(json.dumps(outputs['medical']));target=t/'h.xml'
 run=subprocess.run([sys.executable,str(HERE.parent/'build_form100_xml.py'),'--household',str(source),'--xsd',str(SKILLS/'official-forms/F100-XSD-2025.txt'),'--out',str(target)],capture_output=True,text=True)
 check('medical XML CLI complete',run.returncode==0 and target.exists())
# Actual output PDF fields and totals, not only value-map tests.
blank=SKILLS/'official-forms/100f-2025.pdf'
with tempfile.TemporaryDirectory() as t:
 t=Path(t)
 for name,h in outputs.items():
  source=t/(name+'.json');source.write_text(json.dumps(h));pdf=t/(name+'.pdf')
  run=subprocess.run([sys.executable,str(HERE.parent/'fill_form100_pdf.py'),'--blank',str(blank),'--household',str(source),'--out',str(pdf)],capture_output=True,text=True)
  check(name+' PDF generated',run.returncode==0)
  if run.returncode:print(run.stdout+run.stderr);continue
  if os.environ.get('HANDOFF_PDF_QA'):
   dest=Path(os.environ['HANDOFF_PDF_QA']);dest.mkdir(parents=True,exist_ok=True)
   for artifact in t.glob(name+'.*'):shutil.copy2(artifact,dest/artifact.name)
  fields=PdfReader(pdf).get_fields();check(name+' stored 2038',D(fields['T.2038']['/V'])==hh.indicative_check(h)['taxable income'])
  if name in ('actual','occupational_above','voluntary','medical'):check(name+' calculation annex',pdf.with_suffix('.deductions.pdf').exists())
print(f'{sum(RESULTS)} passed, {len(RESULTS)-sum(RESULTS)} failed, 0 skipped')
sys.exit(not all(RESULTS))
