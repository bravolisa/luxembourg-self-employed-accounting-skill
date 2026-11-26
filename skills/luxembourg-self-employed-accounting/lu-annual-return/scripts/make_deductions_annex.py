"""Attach the deduction working, preserving gross certificates and distinct annual limits."""
from decimal import Decimal
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def write(h, output, check, allowed):
    import form100_household as hh
    styles = getSampleStyleSheet()
    story = [Paragraph(f"Form 100 - {h['tax_year']}: deduction calculation", styles['Title']),
             Paragraph('Supporting calculation for the amounts declared. Eligibility is based on the supplied review evidence; the ACD assessment decides.', styles['Normal']), Spacer(1, 6*mm)]
    rows = [['Item', 'EUR']]
    fmt = lambda x: f'{Decimal(str(x)):,.2f}'
    if h.get('donations'):
        d = hh.deductions.donations(h, check['total net income'], hh.figures(int(h['tax_year'])))
        rows += [['Current-year donations paid', fmt(d['actual'])],
                 ['Total net income before special expenses', fmt(d['net_income_base'])],
                 ['Annual donation ceiling', fmt(d['cap'])],
                 ['Donation deduction included in total special expenses', fmt(d['allowed'])],
                 [f"{d['origin_year']} excess: potentially available in {d['origin_year'] + 1}-{d['last_usable_year']}", fmt(d['new_carryforward'])]]
    if allowed.get('premium_increases'):
        rows += [['Shared interest/insurance ceiling, including increases', fmt(allowed['insurance_ceiling'])],
                 ['Deductible interest and insurance combined', fmt(allowed['insurance'])]]
        for side, p in allowed['premium_increases'].items():
            rows += [[side + ': age-based maximum increase', fmt(p['maximum'])],
                     [side + f": actual earlier increases used, {int(h['tax_year']) - 5}-{int(h['tax_year']) - 1}", fmt(p['previous_used'])],
                     [side + ': current available increase, limited to premium', fmt(p['increase'])]]
    for x in h.get('salary_costs', []):
        rows.append([x['owner'] + ': actual salary costs, replacing the minimum', fmt(x['amount'])])
    for side in ('taxpayer', 'spouse'):
        if any(x['owner'] == side for x in h.get('occupational_pension', [])):
            rows += [[side + ': employee occupational pension actually paid', fmt(hh.employment.occupational_paid(h, side))],
                     [side + ': employee occupational pension deduction', fmt(hh.employment.occupational(h, side, hh.figures(int(h['tax_year']))))]]
        if any(x['owner'] == side for x in h.get('voluntary_contributions', [])):
            rows.append([side + ': voluntary contributions inside minimum comparison', fmt(hh.employment.voluntary(h, side))])
    if h.get('medical_expenses'):
        m = check['medical calculation']
        rows += [['Actual eligible medical cost after all refunds', fmt(m['net'])],
                 ['Taxable income before abatements (box2038)', fmt(m['income_base'])],
                 ['Normal burden (' + str(m['rate']) + '%), applied once', fmt(m['burden'])],
                 ['Medical abatement, after normal burden', fmt(m['allowed'])]]
    table = Table([[Paragraph(escape(str(c)), styles['BodyText']) for c in row] for row in rows], colWidths=[137*mm, 33*mm])
    table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8edf6')),
                              ('GRID',(0,0),(-1,-1),.35,colors.HexColor('#bbc4d2')),
                              ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),
                              ('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),6),
                              ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story += [table, Spacer(1, 6*mm)]
    if h.get('donations'):
        story.append(Paragraph('Donation rows and boxes 1633/1634 retain amounts actually paid. Total special expenses and taxable income include only the allowed deduction. Gifts below the annual minimum create no carryforward. Previous vintages are not included in this calculation.', styles['Normal']))
    if allowed.get('premium_increases'):
        story.append(Paragraph('A calculated available insurance increase is not a certified increase actually used for future five-year history. Keep the final assessment. Loan principal, interest and financed premium must not be counted twice.', styles['Normal']))
    if h.get('salary_costs') or h.get('occupational_pension') or h.get('voluntary_contributions'):
        story.append(Paragraph('The underlying certificates and cost evidence remain necessary. Occupational pension boxes show the allowed deduction, while source payments remain listed above. Voluntary contributions are included in the special-expense minimum comparison, not added to an unreduced minimum.', styles['Normal']))
    if h.get('medical_expenses'):
        story += [Spacer(1, 6*mm), Paragraph('Medical costs: gross payments and reimbursements', styles['Heading2'])]
        for item in h['medical_expenses']:
            detail = ('Payer: ' + item['paid_by'] + '; patient: ' + hh.medical.patient_label(h, item) +
                      ' / ' + item['invoice_id'] + ' / ' + item['payment_date'] + ': ' +
                      item['provider'] + ' - ' + item['description'] + '. Gross EUR ' + fmt(item['gross']) +
                      '; refunds EUR ' + fmt(item['refunds']) + '; net EUR ' + fmt(Decimal(str(item['gross']))-Decimal(str(item['refunds']))))
            story += [Paragraph(escape(detail), styles['BodyText']), Spacer(1, 3*mm)]
            for refund in item['refund_items']:
                detail = 'Refund ' + refund['refund_id'] + ' on ' + refund['date'] + ' to ' + refund['recipient'] + ': EUR ' + fmt(refund['amount'])
                story.append(Paragraph(escape(detail), styles['BodyText']))
        story.append(Paragraph('Paper boxes 1702/1703 show net actual costs by payer before the normal burden. The abatement reduces adjusted income after box 2038. This calculation includes only reviewed household medical costs, final same-year reimbursements and no overlapping care or disability claim.', styles['Normal']))
        if any(item['patient'] != item['paid_by'] for item in h['medical_expenses']):
            story.append(Paragraph('The patient and payer differ. This paper calculation preserves both identities; electronic import requires separate confirmation of the person field.', styles['Normal']))
    story += [Spacer(1, 5*mm), Paragraph('Generated form totals are a reviewed snapshot. After changing any input, regenerate the form and this annex together.', styles['Normal'])]
    SimpleDocTemplate(str(output), pagesize=(210*mm,297*mm), leftMargin=20*mm, rightMargin=20*mm,
                      topMargin=18*mm, bottomMargin=18*mm).build(story)
