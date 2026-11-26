#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Known special payments must not silently become ordinary salary or net interest."""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import form100_household as hh

base = {'tax_year': 2025, 'file_number': '00000000000',
        'taxpayer': {'last_name': 'Example', 'national_id': '19800101' + '0' * 5, 'status': 'CE'},
        'salaries': [{'owner': 'taxpayer', 'pay': [{'kind': 'S', 'amount': 30000}],
                      'contributions': 3000, 'travel': 0, 'workplaces': ['LUXEMBOURG']}]}
results=[]
def check(label, ok):
    results.append(ok)
    print(('PASS ' if ok else 'FAIL ') + label)
check('ordinary baseline remains supported', hh.indicative_check(copy.deepcopy(base))['net salaries'] == 29460)
cases=[]
for code in ('PPPH','IDPT','IDEP','IDCC','REX1','REX2'):
    h=copy.deepcopy(base); h['salaries'][0]['pay'].append({'kind':code,'amount':1000})
    cases.append((code,h))
    h=copy.deepcopy(base);h['salaries'][0]['exemptions']=[{'kind':code,'amount':1000}]
    cases.append((code+' exemption',h))
for field in ('employer_interest_support','termination_payment'):
    for level in ('household','certificate'):
        h=copy.deepcopy(base)
        (h if level=='household' else h['salaries'][0])[field]={'evidence':'Synthetic certificate'}
        cases.append((level+' '+field,h))
for location in ('own_home','consumer_loans'):
    h=copy.deepcopy(base)
    loan={'employer_interest_support':{'kind':'cash','amount':1000}}
    h[location]={'loans':[loan]} if location=='own_home' else [loan]
    cases.append((location+' employer benefit',h))
for label,h in cases:
    try:
        hh.indicative_check(h)
    except SystemExit as exc:
        check(label+' routes to the specific manual review',
              'special employment payments' in str(exc) or 'employer interest support' in str(exc))
    else:
        check(label+' must stop',False)
# The source code survives normalising a component into an ordinary salary row.
for code in ('PPPH', 'IDPT', 'IDEP', 'IDCC', 'REX1', 'REX2'):
    h=copy.deepcopy(base);h['salaries'][0]['pay'][0]['source_code']=' '+code.lower()+' '
    try: hh.indicative_check(h)
    except SystemExit as exc: check('embedded source '+code, 'special employment payments' in str(exc))
    else: check('embedded source '+code, False)
for location in ('household','certificate'):
    for value in ({'status':'unclear','evidence':'Synthetic unreadable amount'},
                  {'status':'present','evidence':'Synthetic employer benefit'},
                  {'status':'clear'}, {'status':'clear','evidence':' '},
                  {'status':'unknown','evidence':'Synthetic'}, 'clear', None):
        h=copy.deepcopy(base);record=h if location=='household' else h['salaries'][0]
        record['special_payment_review']=value
        try: hh.indicative_check(h)
        except SystemExit as exc: check(location+' incomplete review '+str(value), 'special-payment review' in str(exc))
        else: check(location+' incomplete review', False)
    h=copy.deepcopy(base);record=h if location=='household' else h['salaries'][0]
    record['special_payment_review']={'status':'clear','evidence':'Synthetic annual certificate and household answers checked'}
    check(location+' evidenced clear review', hh.indicative_check(h)['net salaries']==29460)
    h['salaries'][0]['pay'][0]['source_code']='PPPH'
    try: hh.indicative_check(h)
    except SystemExit as exc: check(location+' clear cannot override explicit code', 'special employment payments' in str(exc))
    else: check(location+' clear cannot override explicit code', False)

print(f'{sum(results)} passed, {len(results)-sum(results)} failed, 0 skipped')
sys.exit(0 if all(results) else 1)
