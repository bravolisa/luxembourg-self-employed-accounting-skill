#!/usr/bin/env python3
"""Read the PDF MyGuichet gives for a Form 100 procedure and list its figures by field code.

Usage:
    python read_myguichet_summary.py --pdf ACD_F100_2025.pdf [--expect 102196.60] [--all]

MyGuichet hands out two kinds of PDF for the same procedure (seen in October 2026):
- a printable summary: a plain PDF, code and label beside each value ("R1530 TAXABLE INCOME 102 196,60");
- the dynamic form: an XFA form that viewers other than Adobe Reader show as « requires Adobe
  Reader 8 or higher ». Its data sit in the XFA « datasets » packet: one entry per field with
  label, value and code (formId).

The script reads either and prints the key figures (business and liberal profit, salaries with
the travel deduction, special expenses, taxable income). --expect compares the taxable income
(R1530) with your own figure, e.g. box 2038 of the filled PDF; --all lists every filled field.

Needs: scripts/requirements.txt (the tools environment: references/forms/2025/form100-tools.md « Setup »)
"""
import argparse
import re
import sys
from decimal import Decimal

import logging

import pypdf

logging.getLogger("pypdf").setLevel(logging.ERROR)  # font-encoding notices on MyGuichet's printable PDF

# Codes seen on a 2025 procedure; the summary page repeats the profit per category as R3040 / R3120.
KEY_CODES = [
    ("C2460", "business profit (commercial)"),
    ("R3040", "business profit (summary)"),
    ("R3120", "liberal-profession profit (summary)"),
    ("R2000", "net salaries (summary)"),
    ("S2780", "gross salaries"),
    ("S2860", "flat costs of earning income"),
    ("S2900", "travel expenses (commuting)"),
    ("S3260", "net salaries"),
    ("D2580", "insurance and loan interest allowed"),
    ("D2760", "home savings"),
    ("D3285", "special expenses under the flat minimum"),
    ("D3320", "compulsory social contributions"),
    ("D4120", "total special expenses"),
    ("R0360", "total net income"),
    ("R2120", "special expenses"),
    ("R1530", "taxable income"),
]
AMOUNT = r"-?\d{1,3}(?:[ . ]\d{3})*,\d{2}"


def to_decimal(text):
    return Decimal(re.sub(r"[ . ]", "", text).replace(",", "."))


def from_xfa(reader):
    from lxml import etree
    xfa = reader.trailer["/Root"].get("/AcroForm", {}).get_object().get("/XFA") if "/AcroForm" in reader.trailer["/Root"] else None
    if not isinstance(xfa, pypdf.generic.ArrayObject):
        return None
    packets = {str(xfa[i]): xfa[i + 1].get_object().get_data() for i in range(0, len(xfa), 2)}
    if "datasets" not in packets:
        return None
    root = etree.fromstring(packets["datasets"])
    out = []
    for e in root.iter():
        if not isinstance(e.tag, str) or not etree.QName(e).localname.startswith("dataEntry_"):
            continue
        code, value, label = e.findtext("formId"), e.findtext("value"), e.findtext("label")
        if code and re.fullmatch(r"[A-Z]\d{4}\w*", code) and value not in (None, "", "false"):
            out.append((code, (label or "").strip(), value.strip()))
    return out


def from_text(reader):
    """Printable summary: layout mode keeps the columns apart (plain mode glues them together)."""
    out = []
    for page in reader.pages:
        for line in (page.extract_text(extraction_mode="layout") or "").splitlines():
            m = re.match(r"\s*([A-Z]\d{4})\s+(.+?)\s{2,}(.*)$", line)
            if not m:
                continue
            for cell in re.split(r"\s{2,}", m.group(3).strip()):  # one amount per column
                if re.fullmatch(AMOUNT, cell):
                    out.append((m.group(1), m.group(2).strip(), cell))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--expect", help="your taxable income, to compare with R1530")
    ap.add_argument("--all", action="store_true", help="list every filled field")
    a = ap.parse_args()

    reader = pypdf.PdfReader(a.pdf)
    entries = from_xfa(reader)
    kind = "dynamic XFA form"
    if not entries:
        entries, kind = from_text(reader), "printable summary"
    if not entries:
        sys.exit("no field codes found – is this a MyGuichet Form 100 PDF?")
    print(f"{a.pdf}: {kind}, {len(entries)} filled fields")

    if a.all:
        seen = set()
        for e in entries:
            if e not in seen:
                seen.add(e)
                print(f"  {e[0]:6} {e[1][:70]:70} {e[2]}")

    found = {}
    for code, label, value in entries:
        if re.fullmatch(AMOUNT, value):
            found.setdefault(code, []).append(to_decimal(value))
    print("key figures (several values = one per person or column):")
    for code, what in KEY_CODES:
        if code in found:
            vals = list(dict.fromkeys(found[code]))
            print(f"  {code} {what:45} " + " | ".join(f"{v:,.2f}" for v in vals))

    if a.expect:
        want = Decimal(a.expect.replace(",", "."))
        got = found.get("R1530", [None])[0]
        if got is None:
            sys.exit("R1530 (taxable income) not found")
        print(f"taxable income: MyGuichet {got:,.2f}, expected {want:,.2f} -> " +
              ("MATCH" if got == want else f"DIFFERENCE {got - want:,.2f}"))
        if got != want:
            sys.exit(1)


if __name__ == "__main__":
    main()
