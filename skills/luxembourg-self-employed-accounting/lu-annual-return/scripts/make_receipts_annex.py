#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Write the « Détail des recettes » annex (one A4 page in French per business) from the household file.

Usage:
    python make_receipts_annex.py --household household.json --out Annexe_Detail-des-recettes.pdf

For each business on the receipts-and-expenses method that has a "receipts_breakdown" in the
household file (format: references/forms/2025/form100-tools.md): the lines customers, VAT refunds (naming the
VAT year), Mutualité (checked against the CCSS certificate) and other receipts, and their total,
which must equal the business's receipts – the figure on Form 110 line 49 (commercial) or Form 100
box 605/606 (liberal). The refund and Mutualité lines are shown even at 0.00. Notes under the table:
how refunds are timed, the CCSS certificate's Mutualité total, then the breakdown's own "notes"
(French sentences, e.g. the VAT turnover reconciliation). What the annex is for: attachments.md.

Needs: scripts/requirements.txt (the tools environment: references/forms/2025/form100-tools.md « Setup »)
"""
import argparse
import sys
from decimal import Decimal
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parent))
import form100_household as hh  # noqa: E402  the household file: checks and the breakdown lines

NBSP = " "


def eur(x):
    s = f"{x:,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return s + NBSP + "€"


def file_number(n):
    return f"{n[:4]} {n[4:8]} {n[8:]}"


def wrap(c, text, width, font="Helvetica", size=10.5):
    words, lines, cur = text.split(" "), [], ""  # split(" ") keeps the no-break spaces
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def texts(h, b):
    """Titles, header rows, total caption and notes for one business."""
    year, owner = h["tax_year"], h[b["owner"]]
    if b["kind"] == "commercial":
        form = "modèle 110"
        subtitle = "Détail des recettes d'exploitation (modèle 110, ligne 49)"
        total = "Total des recettes = modèle 110, ligne 49"
        method = "Comparaison des recettes et des dépenses d'exploitation (art. 18, al. 3 L.I.R.), T.V.A. comprise"
    else:
        box = "605" if b["owner"] == "taxpayer" else "606"
        form = "modèle 100"
        subtitle = f"Détail des recettes de la profession libérale (modèle 100, case {box})"
        total = f"Total des recettes = modèle 100, case {box}"
        method = "Recettes et dépenses, T.V.A. comprise"
    a = h["address"]
    business = " – ".join(x for x in (b.get("trade_name"), b.get("activity_other") or b.get("description")) if x) or b["activity"]
    header = [("Nom, prénom", f"{owner['last_name']} {owner.get('first_name', '')}".strip()),
              ("Adresse", f"{a.get('number', '')}, {a.get('street', '')}, L-{a['postcode']} {a['locality']}".lstrip(", ")),
              ("N° de dossier", file_number(b.get("file_number") or h["file_number"])),
              ("Entreprise" if b["kind"] == "commercial" else "Activité", business),
              ("Année d'imposition", str(year)),
              ("Méthode", method)]
    rb = b.get("receipts_breakdown") or {}
    notes = []
    if any(r["amount"] for r in rb.get("vat_refunds", [])):
        notes.append("Les remboursements de T.V.A. sont compris dans les recettes de l'année de leur encaissement ; "
                     "un crédit de T.V.A. encore à rembourser sera compris dans les recettes de l'année où il sera remboursé.")
    ccss = [c for c in h.get("ccss_self_employed", []) if c["owner"] == b["owner"]]
    if ccss:
        mut = sum((Decimal(str(v)) for c in ccss for v in (c.get("mutualite") or {}).values()), Decimal(0))
        cert = f"Le certificat CCSS des cotisations payées en {year}"
        notes.append(f"{cert} mentionne {eur(mut)} de remboursements Mutualité." if mut else
                     f"{cert} ne mentionne aucun remboursement Mutualité (total{NBSP}: {eur(mut)}).")
    notes += rb.get("notes", [])
    return f"Annexe au {form} de l'année {year}", subtitle, header, total, notes


def page(c, h, b):
    title, subtitle, header, total_caption, notes = texts(h, b)
    rb = hh.receipts_breakdown(h, b)
    W, H = A4
    x0, x1 = 22 * mm, W - 22 * mm
    y = H - 28 * mm
    c.setFont("Helvetica-Bold", 15)
    c.drawString(x0, y, title)
    y -= 8 * mm
    c.setFont("Helvetica-Bold", 13)
    c.drawString(x0, y, subtitle)
    y -= 12 * mm
    for label, value in header:
        c.setFont("Helvetica-Bold", 10.5)
        c.drawString(x0, y, label)
        c.setFont("Helvetica", 10.5)
        for i, part in enumerate(wrap(c, value, x1 - x0 - 42 * mm)):
            if i:
                y -= 5 * mm
            c.drawString(x0 + 42 * mm, y, part)
        y -= 6.2 * mm
    y -= 6 * mm

    c.setFillColor(colors.HexColor("#E8EEF5"))
    c.rect(x0, y - 2.5 * mm, x1 - x0, 8 * mm, stroke=0, fill=1)
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(x0 + 2 * mm, y, "Nature")
    c.drawRightString(x1 - 2 * mm, y, "Montant")
    y -= 9 * mm
    c.setFont("Helvetica", 10.5)
    rows = rb["lines"]
    for n, (_, label, value) in enumerate(rows):
        parts = wrap(c, label, x1 - x0 - 40 * mm)
        c.drawRightString(x1 - 2 * mm, y, eur(value))
        for i, part in enumerate(parts):
            c.drawString(x0 + 2 * mm, y - i * 5 * mm, part)
        bottom = y - (len(parts) - 1) * 5 * mm - 3.5 * mm  # separator under the row's last line
        if n < len(rows) - 1:  # the last row closes with the total's black rule
            c.setStrokeColor(colors.HexColor("#C8D0DA"))
            c.line(x0, bottom, x1, bottom)
        y = bottom - 6 * mm
    c.setStrokeColor(colors.black)
    c.setLineWidth(1)
    c.line(x0, y + 4.5 * mm, x1, y + 4.5 * mm)
    y -= 2 * mm
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x0 + 2 * mm, y, total_caption)
    c.drawRightString(x1 - 2 * mm, y, eur(rb["total"]))
    y -= 14 * mm

    c.setFont("Helvetica", 9.5)
    for note in notes:
        for part in wrap(c, note, x1 - x0, size=9.5):
            c.drawString(x0, y, part)
            y -= 4.6 * mm
        y -= 2.5 * mm
    c.showPage()
    return rb["total"]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--household", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    h = hh.load(a.household)  # also checks that each breakdown adds up to the receipts
    todo = [b for b in h.get("businesses", []) if b.get("method", "REDE") == "REDE" and b.get("receipts_breakdown")]
    if not todo:
        sys.exit("no business on the receipts-and-expenses method with a receipts_breakdown – nothing to write")
    c = canvas.Canvas(a.out, pagesize=A4)
    c.setTitle(f"Détail des recettes de l'année {h['tax_year']}")
    for b in todo:
        total = page(c, h, b)
        print(f"{b['kind']} business of the {b['owner']}: total {eur(total)} = receipts {eur(Decimal(str(b['receipts'])))}")
    c.save()
    print(f"written {a.out} ({len(todo)} page{'s' if len(todo) > 1 else ''})")


if __name__ == "__main__":
    main()
