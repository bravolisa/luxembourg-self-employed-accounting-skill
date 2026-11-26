"""2025 household children, childcare and own-home interest.

Rules: personal-tax references household-and-tax-class, extraordinary-charges-and-abatements,
home-and-rental. Input contract and explicit limits: annual-return references/forms/2025/form100-family.md.
This module takes the year's figures from its caller; it never imports another year's rules.
"""
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import sys
import json
import form100_events as events

SIDES = ('taxpayer', 'spouse')
BENEFITS = ('family_allowance', 'study_aid', 'volunteer_aid')
EU = set('AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE'.split())


def need(ok, message):
    if not ok:
        sys.exit(message)


def money(value, label):
    try:
        v = Decimal(str(value))
        valid = v.is_finite() and v >= 0 and v == v.quantize(Decimal('.01'))
    except (InvalidOperation, ValueError):
        valid = False
    need(valid, f'{label}: give a non-negative amount with at most two decimals')
    return v


def iso(value, label):
    try:
        return date.fromisoformat(value)
    except (ValueError, TypeError):
        sys.exit(f'{label}: give an ISO date YYYY-MM-DD')


def birth(child):
    if child.get('national_id'):
        s = str(child['national_id'])
        need(len(s) == 13 and s.isdigit(), 'children: national_id must have 13 digits')
        b = iso(f'{s[:4]}-{s[4:6]}-{s[6:8]}', 'children birth date')
        if child.get('birth_date'):
            need(b == iso(child['birth_date'], 'children birth_date'), 'children: birth date and national_id disagree')
        return b
    return iso(child.get('birth_date'), 'children birth_date')


def child_age(child, year):
    """Age on 1 January of the tax year."""
    b = birth(child)
    return int(year) - b.year - ((b.month, b.day) > (1, 1))


def group(child, year):
    return 'young' if child_age(child, year) < 21 else ('continued' if child.get('continued_allowance') else 'student')


def child_count(h):
    return sum(bool(c.get('benefits') or c.get('request_rebate')) for c in h.get('children', []))


def validate_partnership(h):
    is_partner = any(h.get(side, {}).get('status') == 'PA' for side in SIDES)
    facts = h.get('partnership')
    if not is_partner and not facts:
        return
    need(is_partner and h.get('spouse') and h['taxpayer'].get('status') == h['spouse'].get('status') == 'PA',
         'partnership: both adult statuses must be PA')
    need(int(h['tax_year']) == 2025 and h.get('resident_full_year') is True and h.get('tax_liability_months', 12) == 12 and not h.get('individual_taxation'),
         'partnership: full-year resident joint 2025 route only')
    need(isinstance(facts, dict) and h.get('joint_taxation_option') is True
         and facts.get('registered_in_luxembourg') is True and facts.get('both_request_joint') is True
         and facts.get('same_home_full_year') is True and facts.get('no_status_change') is True
         and facts.get('no_competing_election_or_assessment') is True
         and facts.get('evidence') and facts.get('certificate_evidence')
         and type(facts.get('certificate_already_presented')) is bool,
         'partnership: registration, joint election, full-year common home and certificate evidence required')
    start = iso(facts.get('declaration_date'), 'partnership declaration_date')
    home = iso(facts.get('common_home_since'), 'partnership common_home_since')
    need(start < date(int(h['tax_year']), 1, 1) and home <= date(int(h['tax_year']), 1, 1),
         'partnership: declaration and common home must cover the whole tax year')
    for side in SIDES:
        p = h[side]
        need(p.get('underlying_civil_status') == 'CE',
             'partnership: this bounded paper route requires evidenced never-married civil status for both partners')
        if p.get('status_since'):
            need(iso(p['status_since'], 'partnership status_since') == start,
                 'partnership: supplied status date contradicts declaration date')
    need(not h.get('single_parent_credit'), 'partnership: joint class2 cannot retain annual CIM')
    for child in h.get('children', []):
        need(child.get('custody') == 'both_parents' and child.get('common_child_of_partners') is True,
             'partnership: only reviewed common-child joint assignment supported; other parentage needs review')


def joint_status_supported(h):
    if not h.get('spouse'):
        return True
    if events.status_used(h):  # married during the year, or a separation or death in the year
        return events.joint_married(h) and not h.get('individual_taxation')
    if h['taxpayer'].get('status', 'MA') == h['spouse'].get('status', 'MA') == 'MA':
        return not h.get('individual_taxation')
    validate_partnership(h)
    return bool(h.get('partnership'))


def validate(h):
    validate_partnership(h)
    children, home, care = h.get('children', []), h.get('own_home'), h.get('childcare', [])
    need(not h.get('child_tax_bonus'), 'child_tax_bonus: bonification needs manual review; not generated yet')
    if not (children or home or care):
        return
    need(int(h['tax_year']) == 2025, 'children, childcare and own_home: supported for tax year 2025 only')
    need(h.get('resident_full_year') is True, 'family fields need resident_full_year=true; migration/non-residents require review')
    if h.get('spouse'):
        need(joint_status_supported(h), 'family fields require reviewed married or supported partnership joint taxation')
    counts = defaultdict(int)
    identities = set()
    national_ids = {str(h[side]['national_id']) for side in SIDES if h.get(side)}
    for c in children:
        need(c.get('last_name') and c.get('first_name'), 'children: first_name and last_name required')
        need('national_id_not_assigned' not in c or type(c['national_id_not_assigned']) is bool, 'children: national_id_not_assigned must be a boolean')
        if c.get('national_id'):
            need(not c.get('national_id_not_assigned'), 'children: ID provided but marked not assigned')
        else:
            need(c.get('national_id_not_assigned') is True, 'children: missing ID is not proof it was never assigned; confirm national_id_not_assigned or obtain the ID')
        b = birth(c)
        need(b <= date(int(h['tax_year']), 12, 31), 'children: birth after tax year')
        for flag in ('continued_allowance', 'disabled', 'studies_away', 'continuous_full_time_over_year'):
            need(flag not in c or type(c[flag]) is bool, f'children: {flag} must be a boolean')
        if c.get('national_id'):
            need(str(c['national_id']) not in national_ids, 'children: duplicate national_id')
            national_ids.add(str(c['national_id']))
        if c.get('education'):
            need(c['education'] in ('university', 'vocational') and c.get('institution') and c.get('continuous_full_time_over_year') is True,
                 'children: education requires institution and continuous full-time course over a year')
        if c.get('continued_allowance'):
            need('family_allowance' in c.get('benefits', []), 'children: continued allowance needs family_allowance evidence')
        identity = (c['last_name'], c['first_name'], b)
        need(identity not in identities, 'children: duplicate child')
        identities.add(identity)
        need(c.get('in_tax_household') is True and c.get('assignment_evidence'),
             'children: confirm in_tax_household and record assignment_evidence; outside-household cases need manual entry')
        need(c.get('custody') in ('both_parents', 'sole_parent'),
             'children: shared/alternating residence needs manual assignment and entry')
        if c['custody'] == 'both_parents':
            need(bool(h.get('spouse')), 'children: two-parent unmarried households need manual assignment')
        need(c.get('married_or_partnered') is False and c.get('has_children') is False,
             'children: married/partnered children or children with their own children need separate household review')
        need(isinstance(c.get('benefits'), list) and set(c['benefits']) <= set(BENEFITS), 'children: benefits must list the actual allowance/aid types, or []')
        need(isinstance(c.get('request_rebate'), bool), 'children: request_rebate must be explicitly true or false')
        need(not (c['benefits'] and c['request_rebate']), 'children: rebate cannot duplicate family allowance/study/volunteer aid')
        need(c['benefits'] or c['request_rebate'], 'children: no child reduction established; review eligibility before generating')
        need(c.get('benefit_recipient') in ('CT', 'AP', 'DP', 'NO'), 'children: benefit_recipient must be an evidenced XSD code CT/AP/DP/NO')
        need(bool(c['benefits']) == (c['benefit_recipient'] != 'NO'), 'children: benefits and benefit_recipient disagree')
        if c['custody'] == 'sole_parent':
            need(c['benefit_recipient'] in ('CT', 'NO'), 'children: payments to another parent need assignment review')
        if c.get('previous_reduction') is not None:
            need(c['previous_reduction'] in ('CT', 'AP', 'DP', 'NO'), 'children: invalid previous_reduction code')
        kind = group(c, h['tax_year'])
        if kind == 'student':
            need(c.get('education') in ('university', 'vocational') and c.get('institution') and c.get('continuous_full_time_over_year') is True,
                 'children age 21+: continuous full-time education over a year and institution required')
        if kind == 'continued':
            need('family_allowance' in c['benefits'], 'children: continued allowance needs family_allowance evidence')
        counts[kind] += 1
    need(counts['young'] <= 4 and counts['student'] <= 3 and counts['continued'] <= 1,
         'children: exceeds physical PDF rows (4 under21, 3 students, 1 continued allowance); use manual annex')
    if home:
        need(home.get('use') == 'main_home' and home.get('country') == 'LU', 'own_home: only a Luxembourg main home is supported')
        need(home.get('ownership') == ('joint_equal' if h.get('spouse') else 'sole'),
             'own_home: support is sole owner or married equal joint mortgage; other ownership needs review')
        need(home.get('fully_private') is True, 'own_home: construction, mixed/business use, second homes and changes of home need manual review')
        av = iso(home.get('available_since'), 'own_home available_since')
        oc = iso(home.get('occupied_since'), 'own_home occupied_since')
        need(av <= date(int(h['tax_year']), 12, 31) and oc <= date(int(h['tax_year']), 12, 31), 'own_home: must be available and occupied in tax year')
        need(av == oc, 'own_home: differing availability/occupation dates need manual review in this generator')
        need(home.get('available_through_year_end') is True, 'own_home: disposal/temporary cessation needs manual review')
        need(isinstance(home.get('address'), dict) and home['address'].get('postcode') and home['address'].get('locality') and home.get('evidence'), 'own_home: structured address and evidence required')
        loans = home.get('loans', [])
        need(1 <= len(loans) <= 3, 'own_home: one to three loans fit the supported PDF rows')
        for loan in loans:
            need(loan.get('creditor') and loan.get('nature') == 'FH', 'own_home: creditor and mortgage nature FH required; bridging loans not covered')
            need(loan.get('acquisition_only') is True, 'own_home: non-acquisition/mixed loan needs review')
            need(iso(loan.get('start'), 'own_home loan start') <= date(int(h['tax_year']), 12, 31), 'own_home: loan starts after year')
            money(loan.get('balance_31_dec'), 'own_home balance_31_dec')
            paid = money(loan.get('interest'), 'own_home interest')
            subsidy = money(loan.get('subsidies'), 'own_home subsidies')
            need(subsidy <= paid, 'own_home: subsidies exceed interest')
            need(loan.get('available_period_only') is True, 'own_home: pre-availability finance costs must be reviewed separately')
    seen_certificates = set()
    for item in care:
        fingerprint = json.dumps(item, sort_keys=True)
        need(fingerprint not in seen_certificates, 'childcare: duplicate certificate entry')
        seen_certificates.add(fingerprint)
        need(item.get('payment_timing') == 'monthly', 'childcare: advance/arrears or unknown payment timing needs review')
        need(item.get('paid_by') in SIDES and h.get(item['paid_by']), 'childcare: payer must be a person in this return')
        need(item.get('provider') and item.get('provider_address') and item.get('approval_evidence') and item.get('certificate'),
             'childcare: provider/address, approval evidence and certificate required')
        need(item.get('country') in EU, 'childcare: approved provider in EU required')
        ids = item.get('children', [])
        need(ids and all(type(i) is int and 0 <= i < len(children) for i in ids), 'childcare: children must reference household child indexes')
        for i in ids:
            need(child_age(children[i], h['tax_year']) < 14 or (children[i].get('disabled') is True and children[i].get('disability_evidence')),
                 'childcare: child must be under14 on 1 January, unless disabled')
        need(item.get('no_other_claim') is True, 'childcare: confirm no double claim/other household-help or dependence-care abatement')
        monthly = item.get('monthly', {})
        need(monthly and all(str(m) in {str(i) for i in range(1, 13)} for m in monthly), 'childcare: monthly amounts use month keys 1..12')
        for m, amounts in monthly.items():
            need(all((birth(children[i]).year, birth(children[i]).month) <= (int(h['tax_year']), int(m)) for i in ids),
                 'childcare: expense month precedes a referenced child birth; split costs by eligible child')
            paid = money(amounts.get('paid'), f'childcare month {m} paid')
            reimbursed = money(amounts.get('reimbursed'), f'childcare month {m} reimbursed')
            need(reimbursed <= paid, 'childcare: reimbursement exceeds eligible cost')
    need(not care or bool(care_rows(h)), 'childcare: no net qualifying cost; remove the empty claim')
    need(len(care_rows(h)) <= 10, 'childcare: more than 10 distinct provider/monthly-cost groups; manual XML entry required')


def home_allowed(h, f):
    home = h.get('own_home')
    out = {'actual': Decimal(0), 'allowed': Decimal(0), 'taxpayer': Decimal(0), 'spouse': Decimal(0), 'ceiling': None}
    if not home:
        return out
    year = iso(home['available_since'], 'own_home available_since').year
    per = None if year >= 2024 else f['own_home_2020_2023'] if year >= 2020 else f['own_home_2015_2019'] if year >= 2015 else f['own_home_before_2015']
    cap = None if per is None else Decimal(str(per)) * (1 + bool(h.get('spouse')) + child_count(h))
    actual = sum((money(l['interest'], 'interest') - money(l['subsidies'], 'subsidies') for l in home['loans']), Decimal(0))
    amount = actual if cap is None else min(actual, cap)
    tp = (amount / 2).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) if h.get('spouse') else amount
    return {'actual': actual, 'allowed': amount, 'taxpayer': tp, 'spouse': amount - tp, 'ceiling': cap}


def care_months(h, side=None):
    totals = defaultdict(Decimal)
    for c in h.get('childcare', []):
        if side is not None and c['paid_by'] != side:
            continue
        for month, a in c['monthly'].items():
            totals[int(month)] += money(a['paid'], 'childcare paid') - money(a['reimbursed'], 'childcare reimbursement')
    return dict(sorted(totals.items()))


def childcare_allowed(h, f):
    return sum((min(v, Decimal(str(f['childcare_monthly_cap']))) for v in care_months(h).values()), Decimal(0))


def care_rows(h):
    """Keep each distinct monthly net cost in its own XML period row, never average across months."""
    rows = []
    for c in h.get('childcare', []):
        groups = defaultdict(list)
        for m, a in c['monthly'].items():
            net = money(a['paid'], 'childcare paid') - money(a['reimbursed'], 'childcare reimbursement')
            if net:
                groups[net].append(int(m))
        for net, months in groups.items():
            rows.append((c, sorted(months), net * len(months)))
    return rows


def pdf_values(h, f):
    values, counts = {}, defaultdict(int)
    starts = {'young': (201, 204, 207, 210), 'student': (213, 217, 221), 'continued': (225,)}
    for c in h.get('children', []):
        kind = group(c, h['tax_year'])
        start = starts[kind][counts[kind]]
        counts[kind] += 1
        values[f'A.{start:04d}a'], values[f'A.{start:04d}b'] = c['last_name'], c['first_name']
        values[f'D.{start+1:04d}'] = c.get('national_id') or birth(c).strftime('%Y%m%d')
        if c['request_rebate']:
            values[f'C.{start+2:04d}'] = '/Yes'
        if kind == 'student':
            values[f'A.{start+3:04d}'] = c['institution']
    if h.get('own_home'):
        home = h['own_home']
        # Physical field names are verified against the 2025 AcroForm; see form-100.md.
        values['A.1048'] = str(home['address']['postcode']) + ' ' + home['address']['locality']
        values['A.1049'] = str(home['address'].get('number', ''))
        values['A.1050'] = home['address'].get('street', '')
        values['D.1051'] = iso(home['available_since'], 'available_since').strftime('%d/%m/%Y')
        a = home_allowed(h, f)
        for side, col in (('taxpayer', 0), ('spouse', 1)):
            if h.get(side):
                values[f'N.{1021+col}'] = -a[side]
        for i, loan in enumerate(home['loans']):
            start = 1033 + 5*i
            values[f'A.{start}'] = loan['creditor']
            values[f'A.{start+1}'] = 'Prêt hypothécaire'
            values[f'N.{start+2}'] = money(loan['balance_31_dec'], 'balance')
            net = money(loan['interest'], 'interest') - money(loan['subsidies'], 'subsidies')
            tp = (net/2).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) if h.get('spouse') else net
            values[f'N.{start+3}'] = tp
            if h.get('spouse'):
                values[f'N.{start+4}'] = net-tp
    if h.get('childcare'):
        values['C.1715'] = '/Yes'
        for side, col in (('taxpayer', 0), ('spouse', 1)):
            costs = care_months(h, side)
            if not costs:
                continue
            values[f'A.{1716+col}'] = 'Garde enfant - voir annexe mensuelle'
            if len(set(costs.values())) == 1:
                values[f'N.{1718+col}'] = next(iter(costs.values()))
            values[f'N.{1720+col}'] = len(costs)
            values[f'N.{1722+col}'] = sum(costs.values(), Decimal(0))
    return values


def add_children(d, h):
    node = d.add('Enfants')
    node.add('ENF_DECL_QST', bool(h.get('children')))
    for i, c in enumerate(h.get('children', [])):
        ident = f'CHILDREN{i}'
        d.add('personne').add('ID_PERSONNE', ident)
        child = node.add('Enfant', G1078_ID_PERSONNE=ident)
        child.add('ENF_NOM', c['last_name'])
        child.add('ENF_PRE', c['first_name'])
        if c.get('national_id'):
            child.add('ENF_NIN', c['national_id'])
        child.add('ENF_DIS_NIN', not bool(c.get('national_id')))
        child.add('ENF_DAT_NAI', birth(c).isoformat())
        child.add('ENF_MAR', False)
        child.add('ENF_PAR', False)
        child.add('ENF_MEN_CHG', 'DP' if c['custody'] == 'both_parents' else 'SP')
        child.add('ENF_MEN_ALL', c['benefit_recipient'])
        if c.get('previous_reduction'):
            child.add('ENF_MEN_MOD_ANT', c['previous_reduction'])
        child.add('ENF_HAB_CONT', 'AP' if c.get('studies_away') else 'MT')
        child.add('ENF_UNI_EXI', c.get('education') == 'university')
        child.add('ENF_FPR_EXI', c.get('education') == 'vocational')
        if c.get('education'):
            child.add('ENF_UNI_NOM' if c['education'] == 'university' else 'ENF_FPR_NOM', c['institution'])
        child.add('ENF_ALL_CON', bool(c.get('continued_allowance')))
        child.add('ENF_ALL_CED', bool(c['benefits']))
        for key, benefit in (('CAE', 'family_allowance'), ('CES', 'study_aid'), ('SNI', 'volunteer_aid')):
            child.add(f'ENF_ALL_{key}', benefit in c['benefits'])
        child.add('ENF_MOD_IMP', c['request_rebate'])
        child.add('ENF_HAB_AUT_PAR', c['custody'] == 'both_parents')
        if h.get('single_parent_credit'):
            row = next(x for x in h['single_parent_credit']['support'] if x['child'] == i)
            child.add('ENF_CRE_IMP', True)
            child.add('ENF_MNT_ALL', money(row['monthly_support'], 'monthly support'))
        # Bonification remains a separate unsupported request.


def add_home(node, h, f):
    home = h.get('own_home')
    if not home:
        return
    res = node.one('LocationBiens').add('ResPrincipale').add('ResPrincipaleRevenusNonExo', L0010_ID_RESPRINCIPALE='RESPRINCIPALE0')
    ad = res.add('NEX_ADR_HAB').add('AdresseAuLuxembourg')
    ad.add('CodePays', 'LU')
    for field, key in (('CodePostal', 'postcode'), ('Localite', 'locality'), ('Rue', 'street'), ('Numero', 'number')):
        if home['address'].get(key) is not None:
            ad.add(field, str(home['address'][key]))
    res.add('NEX_TYPE_OCC', 'TA' if home['available_since'] <= f"{int(h['tax_year'])}-01-01" else 'PA')
    res.add('NEX_OCC_CONT_CONJ', bool(h.get('spouse')))
    res.add('NEX_DATE_DEB_CONT', home['available_since'])
    if h.get('spouse'):
        res.add('NEX_DATE_DEB_CONJ', home['available_since'])
    for loan in home['loans']:
        l = res.add('ResPrincipaleDettesCharges')
        l.add('NEX_NOM_CRE', loan['creditor'])
        l.add('NEX_NAT_DETTE', loan['nature'])
        l.add('NEX_MNT_DETTE_31DEC', Decimal(str(loan['balance_31_dec'])))
        l.add('NEX_100P_DETTE_ACQ', True)
        l.add('NEX_DATE_DEB_PRET', loan['start'])
        net = money(loan['interest'], 'interest') - money(loan['subsidies'], 'subsidies')
        tp = (net/2).quantize(Decimal('.01'), rounding=ROUND_HALF_UP) if h.get('spouse') else net
        l.add('NEX_INT_OCC_CONT', tp)
        if h.get('spouse'):
            l.add('NEX_INT_OCC_CONJ', net-tp)
    allowed = home_allowed(h, f)
    res.add('NEX_MNT_OCC_CONT', allowed['taxpayer'])
    if h.get('spouse'):
        res.add('NEX_MNT_OCC_CONJ', allowed['spouse'])


def add_childcare(node, h):
    if not h.get('childcare'):
        return
    care = node.add('CharExtraFraisDomGarde')
    months = ('JAN','FEV','MAR','AVR','MAI','JUI','JUL','AUO','SEP','OCT','NOV','DEC')
    for item, period, annual in care_rows(h):
        row = care.add('CharExtraFraisDomGardeDetail', H1220_ID_PERSONNE='DECLARER' if item['paid_by'] == 'taxpayer' else 'CONJOINT')
        row.add('CFD_NOM_ADR_BEN', item['provider'] + ', ' + item['provider_address'])
        row.add('CFD_TYP_FRA', '3')
        row.add('CFD_FRA_PER_ANN', len(period) == 12)
        for i, m in enumerate(months, 1):
            row.add('CFD_FRA_PER_' + m, i in period)
        row.add('CFD_MNT_FRA', annual)
