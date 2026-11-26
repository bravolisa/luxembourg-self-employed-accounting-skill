#!/usr/bin/env python3
"""Salary preparation boundaries; independently worked art.105bis/107/113 examples."""
import copy
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from decimal import Decimal

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent))
import form100_household as hh
results=[]
def check(name, condition):
    results.append(condition)
    print(('PASS' if condition else 'FAIL')+': '+name)
def stops(name, fn):
    try: fn()
    except SystemExit: check(name,True)
    else: check(name,False)
def salary(owner,gross,travel=0,social=0):
    return {'owner':owner,'pay':[{'kind':'S','amount':gross}], 'travel':travel,
            'contributions':social,'workplaces':['LUXEMBOURG']}

def complete(h):
    # Public household calculations now reject incomplete identities/unsupported inputs.
    # Preserve the independent amount cases while supplying synthetic valid context.
    h['file_number']='0'*11
    h['taxpayer']={'last_name':'Example','national_id':'19800101'+'0'*5,'status':'CE'}
    if any(s['owner']=='spouse' for s in h.get('salaries',[])):
        h['taxpayer']['status']='MA'
        h['spouse']={'last_name':'Example spouse','national_id':'19820101'+'0'*5,'status':'MA'}
    return h

# Annual receipts400, FD100 -> remaining300: the540 flat is limited to300, net salary0.
h=complete({'tax_year':2025,'salaries':[salary('taxpayer',400,100)]})
check('low receipts: flat300',hh.salary_flat_costs(h,'taxpayer')==Decimal(300))
check('low receipts: no negative salary from flats',hh.indicative_check(h)['net salaries']==0)
h['salaries']=[salary('taxpayer',3000),salary('taxpayer',2000)]
check('two contracts: one540 flat',hh.indicative_check(h)['net salaries']==4460)
h['salaries']=[salary('taxpayer',300,301)]
stops('commuting cannot exceed receipts',lambda:hh.indicative_check(h))
h['salaries']=[salary('taxpayer',10000,1300),salary('taxpayer',10000,1300)]
stops('combined commuting cannot exceed annualcap',lambda:hh.indicative_check(h))
h['salaries']=[salary('taxpayer',10000,-1)]
stops('negative commuting stops',lambda:hh.indicative_check(h))

# Lower spouse: gross800 − flat540 − compulsory140 =120. Second DS flat120: total600.
h=complete({'tax_year':2025,'salaries':[salary('taxpayer',30000,0,3000),salary('spouse',800,0,140)]})
check('low-paid spouse: DSminimum600',hh.allowed(h)['flat_minimum']==600)
h['salaries'][1]=salary('spouse',2000,0,200)
check('sufficient spouse income: DSminimum960',hh.allowed(h)['flat_minimum']==960)
h['salaries'][1]=salary('spouse',300,0,30)
stops('negative salary remainder: DSminimum manualreview',lambda:hh.allowed(h))

for marker in ({'occupation':'SRF5'},{'occupation':'SRFA'},{'tax_regime':'domestic_flat_137_5'},
               {'pay':[{'kind':'SALF','amount':1000}]},{'pay':[{'kind':'SAFA','amount':1000}]}):
    h=complete({'tax_year':2025,'salaries':[{**salary('taxpayer',1000),**marker}]})
    stops('flat regime marked '+str(marker),lambda:hh.indicative_check(h))
h=complete({'tax_year':2025,'tax_liability_months':6,'salaries':[salary('taxpayer',10000)]})
stops('partial tax liability requires review',lambda:hh.indicative_check(h))

# Real generation path: missing credit must never become an invented zero.
template=json.loads((HERE/'households/couple_commercial_salaried.json').read_text())
raw=re.sub(r'"@ID:(\d{4})-(\d{2})-(\d{2})"',lambda m:f'"{m[1]}{m[2]}{m[3]}00000"',json.dumps(template))
template=json.loads(raw)
bl_skills=HERE.parents[4]
xsd=HERE.parents[2]/'official-forms/F100-XSD-2025.txt'
with tempfile.TemporaryDirectory() as tmp:
    for key in ('cis','co2'):
        h=copy.deepcopy(template);h['salaries'][0].pop(key,None)
        inp=Path(tmp)/'household.json';inp.write_text(json.dumps(h));out=Path(tmp)/f'{key}.xml'
        r=subprocess.run([sys.executable,str(HERE.parent/'build_form100_xml.py'),'--household',str(inp),
                          '--xsd',str(xsd),'--out',str(out)],capture_output=True,text=True)
        check('missing '+key+' is rejected before writing XML',r.returncode!=0 and 'missing is not zero' in r.stderr and not out.exists())
    h=copy.deepcopy(template);h['salaries'][0]['cis']=None
    inp.write_text(json.dumps(h));out=Path(tmp)/'null.xml'
    r=subprocess.run([sys.executable,str(HERE.parent/'build_form100_xml.py'),'--household',str(inp),
                      '--xsd',str(xsd),'--out',str(out)],capture_output=True,text=True)
    check('null CIS is unknown',r.returncode!=0 and 'missing is not zero' in r.stderr)
print(f'{sum(results)} passed, {len(results)-sum(results)} failed')
sys.exit(0 if all(results) else 1)
