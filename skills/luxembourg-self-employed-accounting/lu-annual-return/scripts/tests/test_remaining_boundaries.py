#!/usr/bin/env python3
"""Independent family-medical and replacement-benefit boundary regressions,2025."""
import copy,json,re,sys,tempfile,subprocess,os,shutil
from pathlib import Path
from decimal import Decimal as D
from pypdf import PdfReader
HERE=Path(__file__).resolve().parent; SKILLS=HERE.parents[2]; ROOT=SKILLS.parents[1]
sys.path.insert(0,str(HERE.parent));sys.path.insert(0,str(SKILLS/'lu-income-tax-personal/scripts'))
import form100_household as hh,build_form100_xml as xml,tax_estimate as tax,salary_balance as balance
E=json.loads((HERE/'remaining_boundaries/expected.json').read_text()); RESULTS=[]
def check(label,ok): RESULTS.append(bool(ok));print(('PASS ' if ok else 'FAIL ')+label)
def rejects(label,fn,*args,contains=None):
 try:fn(*args)
 except SystemExit as e:check(label,contains is None or contains in str(e))
 else:check(label,False)
def read(path):return json.loads(re.sub(r'@ID:(\d{4})-(\d{2})-(\d{2})',lambda m:''.join(m.groups())+'0'*5,path.read_text()))
def base():
 h=read(HERE/'four_deductions/consumer.json');h.pop('consumer_loans');h['insurance']=[{'insurer':'Example','risk':'RC','paid_by':'taxpayer','amount':500}];return h
def joint(child=False):
 h=base();h['taxpayer']['status']='MA';h['spouse']=dict(h['taxpayer'],national_id='19860202'+'0'*5,first_name='Test Spouse')
 s=copy.deepcopy(h['salaries'][0]);s.update(owner='spouse',certificate_id='ORD-SPOUSE',employer='Example spouse employer');h['salaries'].append(s)
 h['salary_balance']['tax_class']=2;h['salary_balance']['people']['spouse']=copy.deepcopy(h['salary_balance']['people']['taxpayer'])
 if child:
  h['children']=read(HERE/'households/couple_child_home_childcare.json')['children']
  h['children'][0].update(moderation_origin='lu_positive_benefit',moderation_evidence='Synthetic positive LU allowance')
 return h
def med(h,patient='taxpayer',payer='taxpayer',gross=10000,refunds=2000):
 x={'invoice_id':'MED1','paid_by':payer,'patient':patient,'kind':'medical','article127_eligible':True,'eligibility_evidence':'Synthetic necessary extraordinary treatment review','provider':'Example Clinic','payment_evidence':'Synthetic adult bank payment','payment_date':'2025-06-01','currency':'EUR','no_other_deduction':True,'no_forfait_or_childcare_overlap':True,'refunds_final_and_complete':True,'description':'Necessary medical treatment','gross':gross,'refunds':refunds,'pending_refunds':False,'expected_refunds':0,'refund_review_evidence':'Synthetic all-insurer and CNS supplementary entitlement review','refund_items':[{'refund_id':'REF1','recipient':payer,'date':'2025-07-01','amount':refunds,'evidence':'Synthetic final insurer statement'}] if refunds else []}
 if patient!=payer:x.update(patient_identity_evidence='Synthetic invoice identifies patient',household_bears_cost=True,no_other_household_claim=True)
 if patient=='child':x.update(child_index=0,extraordinary_child_treatment=True,treatment_evidence='Synthetic long and costly necessary treatment')
 h['medical_expenses']=[x];h['medical_review']={'income_complete':True,'no_foreign_or_exempt_progression':True,'all_actual_article127_costs_included':True,'evidence':'Synthetic complete income/cost review','tax_class':2 if h.get('spouse') else 1};return h
def estimate(h):
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)/'h.json';p.write_text(json.dumps(h));return tax.estimate(**tax.from_household(p))
def prepared(h):hh.validate(h);return balance.prepare(h,hh,hh.figures(2025),2025)
schema=xml.Schema(SKILLS/'official-forms/F100-XSD-2025.txt');outputs={}
for name,h,key in [('child',med(joint(True),'child'),'child_medical'),('spouse',med(joint(),'spouse'),'spouse_medical')]:
 result=hh.indicative_check(h);m=result['medical calculation'];expected=E[key]
 check(name+' independently calculated base/burden/net/relief',result['taxable income']==D(E['joint_base']['taxable']) and all(m[k]==D(expected[k]) for k in ('net','burden','allowed')))
 check(name+' final adjusted income after one household burden',estimate(h)['adjusted']==D(expected['adjusted']))
 check(name+' PDF net by actual payer',hh.to_pdf_values(h)['N.1702']==8000)
 rejects(name+' XML identity still stops',xml.build,h,schema,contains='H0020');outputs[name]=h
h=med(joint(True),'child',gross=7000,refunds=3000)
second=copy.deepcopy(med(joint(True),'spouse','spouse',5000,1000)['medical_expenses'][0]);second['invoice_id']='MED2';h['medical_expenses'].append(second)
check('mixed patients share one burden',hh.indicative_check(h)['medical abatement']==D(E['child_medical']['allowed']))
check('mixed payer columns retain each net4000',hh.to_pdf_values(h)['N.1702']==4000 and hh.to_pdf_values(h)['N.1703']==4000);outputs['mixed']=h
h=med(base(),gross=7000,refunds=3000)
root=xml.build(h,schema).to_xml();check('self-paid XML retains schema route',schema.validator.validate(root))
for label,change,part in [
 ('later refund',lambda x:x['medical_expenses'][0]['refund_items'][0].update(date='2026-01-01'),'cross-year'),
 ('old refund',lambda x:x['medical_expenses'][0]['refund_items'][0].update(date='2024-12-31'),'cross-year'),
 ('pending refund',lambda x:x['medical_expenses'][0].update(pending_refunds=True),'pending'),
 ('expected supplementary reimbursement',lambda x:x['medical_expenses'][0].update(expected_refunds=100),'pending'),
 ('missing refund dates',lambda x:x['medical_expenses'][0].pop('refund_items'),'refund_items'),
 ('wrong refund sum',lambda x:x['medical_expenses'][0]['refund_items'][0].update(amount=2999),'reconcile'),
 ('zero total with later item',lambda x:x['medical_expenses'][0].update(refunds=0),'cross-year'),
 ('unknown recipient',lambda x:x['medical_expenses'][0]['refund_items'][0].update(recipient='outside'),'recipient'),
 ('duplicate refund',lambda x:x['medical_expenses'][0]['refund_items'].append(copy.deepcopy(x['medical_expenses'][0]['refund_items'][0])),'refund_id'),
 ('missing refund review',lambda x:x['medical_expenses'][0].pop('refund_review_evidence'),'pending'),
 ('explicit foreign income',lambda x:x['salaries'][0].update(all_pay_luxembourg_taxable=False),'foreign'),
 ('prior-year payment',lambda x:x['medical_expenses'][0].update(payment_date='2024-06-01'),'payment')]:
 q=copy.deepcopy(h)
 if label=='zero total with later item':q['medical_expenses'][0]['refund_items'][0]['date']='2026-01-01'
 change(q);rejects(label,hh.validate,q,contains=part)
q=med(base(),refunds=0);hh.validate(q);check('evidenced zero refunds with empty items',True)
for label,change in [
 ('no exceptional treatment',lambda x:x['medical_expenses'][0].update(extraordinary_child_treatment=False)),
 ('missing patient invoice',lambda x:x['medical_expenses'][0].pop('patient_identity_evidence')),
 ('another household claim',lambda x:x['medical_expenses'][0].update(no_other_household_claim=False)),
 ('foreign-only moderation contradiction',lambda x:x['children'][0].update(moderation='foreign_only')),
 ('zero-differential moderation contradiction',lambda x:x['children'][0].update(moderation='zero_differential')),
 ('unknown child',lambda x:x['medical_expenses'][0].update(child_index=1)),
 ('boolean index',lambda x:x['medical_expenses'][0].update(child_index=False)),
 ('adult child',lambda x:x['children'][0].update(birth_date='2007-01-01')),
 ('before child birth',lambda x:x['children'][0].update(birth_date='2025-07-01')),
 ('duplicate invoice',lambda x:x['medical_expenses'].append(copy.deepcopy(x['medical_expenses'][0])))]:
 q=copy.deepcopy(outputs['child']);change(q);rejects(label,hh.validate,q)
# Full-cap proof: both current ordinary jobs independently qualify, all benefit-related
# contributions/costs are still subtracted. Independent arithmetic is in expected.json.
def benefits():
 h=joint();s=copy.deepcopy(h['salaries'][0]);s.update(certificate_id='BEN1',employer='Example benefit institution',cim=0,source='employee_replacement',replacement_kind='sickness',employee_replacement_eligible=True,employee_replacement_evidence='Synthetic direct employee benefit',overlap_and_duplicates_reconciled=True,contributions_reconciled=True,workplaces=[],pay=[{'kind':'A','description':'Employee sickness replacement','amount':6000}],contributions=600,withheld=0,cis=0,co2=0);h['salaries'].append(s)
 h['salary_balance']['extra_professional_review']={'evidence':'Synthetic reviewed current jobs and benefit split','people':{side:{'ordinary_activity_current_year':True,'ordinary_activity_affiliation_confirmed':True,'ordinary_gross_excludes_replacements':True,'activity_evidence':'Synthetic current job and personal compulsory affiliation','gross_split_evidence':'Synthetic salary/benefit reconciliation excludes embedded CNS advances','ordinary_article95_gross':30000} for side in ('taxpayer','spouse')}};return h
h=benefits();p=prepared(h);e=E['mixed_benefit'];check('benefit full cap independently established',p['extra_professional_amount']==D(e['allowance']) and p['salary_context']['allowance_method']=='full_cap_proved_without_replacement_income')
check('benefit contributions reduce lower bound',p['salary_context']['allowance_limits']=={'taxpayer':D(e['taxpayer_bound']),'spouse':D(e['spouse_bound'])})
check('benefits remain taxable after invariant relief',hh.indicative_check(h)['taxable income']==D(e['taxable']) and estimate(h)['adjusted']==D(e['adjusted']))
for label,change in [
 ('missing activity review',lambda x:x['salary_balance'].pop('extra_professional_review')),
 ('benefit-only spouse',lambda x:x['salaries'][1].update(source='employee_replacement',replacement_kind='unemployment',occupation='DEMP',pay=[{'kind':'A','description':'Unemployment replacement','amount':30000}],employee_replacement_eligible=True,employee_replacement_evidence='Synthetic benefit',overlap_and_duplicates_reconciled=True,contributions_reconciled=True,cim=0)),
 ('ordinary amount exceeds source',lambda x:x['salary_balance']['extra_professional_review']['people']['taxpayer'].update(ordinary_article95_gross=30001)),
 ('unconfirmed current activity',lambda x:x['salary_balance']['extra_professional_review']['people']['taxpayer'].update(ordinary_activity_current_year=False)),
 ('unconfirmed activity affiliation',lambda x:x['salary_balance']['extra_professional_review']['people']['spouse'].update(ordinary_activity_affiliation_confirmed=False)),
 ('unreconciled embedded benefit',lambda x:x['salary_balance']['extra_professional_review']['people']['taxpayer'].update(ordinary_gross_excludes_replacements=False)),
 ('unproved split',lambda x:x['salary_balance']['extra_professional_review']['people']['taxpayer'].pop('gross_split_evidence'))]:
 q=copy.deepcopy(h);change(q);rejects(label,prepared,q,contains='ordinary gross' if label=='benefit-only spouse' else None)
q=copy.deepcopy(h);q['salaries'][0]['includes_cns_advances']=True;q['salary_balance']['extra_professional_review']['people']['taxpayer']['ordinary_article95_gross']=E['cap_boundary']['ordinary_gross'];check('exact conservative4500 cap allowed',prepared(q)['extra_professional_amount']==4500)
q['salary_balance']['extra_professional_review']['people']['taxpayer']['ordinary_article95_gross']='9419.99';rejects('one cent below conservative cap stops',prepared,q,contains='below')
# Known IMAL, or CNS advances embedded in S, trigger the same guard.
for kind in ('IMAL','embedded'):
 q=joint();q['salaries'][0]['pay'].append({'kind':'IMAL','amount':1000}) if kind=='IMAL' else q['salaries'][0].update(includes_cns_advances=True)
 rejects(kind+' cannot silently grant129b',prepared,q,contains='replacement benefit')
 q['salary_balance']['extra_professional_review']=copy.deepcopy(h['salary_balance']['extra_professional_review'])
 if kind=='embedded':q['salary_balance']['extra_professional_review']['people']['taxpayer']['ordinary_article95_gross']=29000
 check(kind+' evidenced invariant works',prepared(q)['extra_professional_amount']==4500)
# Actual PDF and annex, checking logical values as well as extracted supporting text.
blank=SKILLS/'official-forms/100f-2025.pdf'
with tempfile.TemporaryDirectory() as t:
 t=Path(t)
 for name,h in outputs.items():
  source=t/(name+'.json');source.write_text(json.dumps(h));target=t/(name+'.pdf')
  run=subprocess.run([sys.executable,str(HERE.parent/'fill_form100_pdf.py'),'--blank',str(blank),'--household',str(source),'--out',str(target)],capture_output=True,text=True)
  check(name+' filled PDF created',run.returncode==0)
  if run.returncode:print(run.stdout+run.stderr);continue
  r=PdfReader(target);fields=r.get_fields();values=hh.to_pdf_values(h)
  check(name+' canonical medical values',all(D(fields[k]['/V'])==v for k,v in values.items() if k in ('N.1702','N.1703')))
  annex=target.with_suffix('.deductions.pdf');txt='\n'.join(p.extract_text() for p in PdfReader(annex).pages)
  check(name+' annex distinguishes payer and patient', 'Payer:' in txt and 'patient:' in txt and 'Refund REF1 on 2025-07-01' in txt and 'electronic import requires' in txt)
  if os.environ.get('BOUNDARY_PDF_QA'):
   dest=Path(os.environ['BOUNDARY_PDF_QA']);dest.mkdir(parents=True,exist_ok=True)
   for p in (target,annex):shutil.copy2(p,dest/p.name)
print(f'{sum(RESULTS)} passed, {len(RESULTS)-sum(RESULTS)} failed, 0 skipped');sys.exit(not all(RESULTS))
