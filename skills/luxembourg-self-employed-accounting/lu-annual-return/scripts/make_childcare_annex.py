#!/usr/bin/env python3
"""Write the monthly childcare evidence schedule accompanying Form100 page17 (2025).
Usage: python make_childcare_annex.py --household household.json --out childcare.pdf
The schedule shows actual net costs and the separately capped household abatement, never averages.
"""
import argparse
import os
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from decimal import Decimal
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import form100_household as hh


def write(h, out):
    hh.validate(h)
    font_candidates = [os.environ.get('BL_PDF_FONT', ''), '/System/Library/Fonts/Supplemental/Arial Unicode.ttf', '/Library/Fonts/Arial Unicode.ttf', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    font_path = next((p for p in font_candidates if p and Path(p).is_file()), None)
    hh.need(font_path, 'childcare annex needs a Unicode TTF font; set BL_PDF_FONT')
    pdfmetrics.registerFont(TTFont('FamilySans', font_path))
    import json
    chars = json.dumps(h.get('childcare', []), ensure_ascii=False) + json.dumps(h.get('children', []), ensure_ascii=False)
    widths = pdfmetrics.getFont('FamilySans').face.charWidths
    hh.need(all(ord(c) in widths or c.isspace() for c in chars), 'childcare annex font lacks a required character; set BL_PDF_FONT to a font covering these names')
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = 'FamilySans'
    doc = SimpleDocTemplate(str(out), pagesize=(210*mm,297*mm), leftMargin=16*mm,rightMargin=16*mm,topMargin=16*mm,bottomMargin=16*mm)
    story = [Paragraph(f"Annexe - frais de garde d'enfant - {h['tax_year']}", styles['Title']),
             Paragraph('Détail mensuel pour la rubrique CE, case 1715 du modèle 100. Joindre les attestations et justificatifs.', styles['BodyText'])]
    for item in h.get('childcare', []):
        story += [Spacer(1,5*mm),Paragraph(escape(item['provider'] + ', ' + item['provider_address']),styles['Heading2']),
                  Paragraph('Payé par : ' + ('contribuable' if item['paid_by']=='taxpayer' else 'conjoint') + '. Enfant(s) : ' + escape(', '.join(h['children'][i]['first_name'] + ' ' + h['children'][i]['last_name'] for i in item['children'])),styles['BodyText'])]
        rows = [['Mois', 'Frais payés EUR', 'Remboursés EUR', 'Coût net EUR']]
        for month,a in sorted(item['monthly'].items(),key=lambda x:int(x[0])):
            p,r=Decimal(str(a['paid'])),Decimal(str(a['reimbursed']))
            rows.append([str(month),f'{p:.2f}',f'{r:.2f}',f'{p-r:.2f}'])
        t=Table(rows,colWidths=[25*mm,50*mm,50*mm,50*mm],repeatRows=1)
        t.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'FamilySans'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef5')),('GRID',(0,0),(-1,-1),.3,colors.grey),('ALIGN',(1,1),(-1,-1),'RIGHT'),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5)]))
        story += [Spacer(1,2*mm),t]
    f=hh.figures(int(h['tax_year']))
    total=hh.family.childcare_allowed(h,f)
    rows=[['Mois','Coût net du ménage EUR','Abattement calculé EUR']]
    for m,v in hh.family.care_months(h).items(): rows.append([str(m),f'{v:.2f}',f'{min(v,Decimal(str(f["childcare_monthly_cap"]))):.2f}'])
    rows.append(['Total','',f'{total:.2f}'])
    table=Table(rows,colWidths=[25*mm,75*mm,75*mm],repeatRows=1)
    table.setStyle(TableStyle([('FONTNAME',(0,0),(-1,-1),'FamilySans'),('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e8eef5')),('GRID',(0,0),(-1,-1),.3,colors.grey),('ALIGN',(1,1),(-1,-1),'RIGHT'),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
    story += [Spacer(1,6*mm),Paragraph('Plafond mensuel commun au ménage',styles['Heading2']),table,Spacer(1,4*mm),Paragraph('Calcul proposé à vérifier : minimum du coût net et de 450 EUR pour chaque mois. Ce montant réduit le revenu imposable ajusté, après la case 2038. La décision appartient à l\'ACD.',styles['BodyText'])]
    doc.build(story)


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--household',required=True);ap.add_argument('--out',required=True)
    a=ap.parse_args();write(hh.load(a.household),a.out)

if __name__=='__main__':main()
