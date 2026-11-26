#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Fill the ACD's fillable Form 100 PDF (tax year 2025) from a JSON file of box values.

Usage:
    python fill_form100_pdf.py --blank 100f-2025.pdf --household household.json --out filled.pdf   (preferred)
    python fill_form100_pdf.py --blank 100f-2025.pdf --values values.json --out filled.pdf          (box by box)

- blank: the official form, https://impotsdirects.public.lu/dam-assets/fr/formulaires/pers_physiques/2025/100f-2025.pdf
- household: the same household file as build_form100_xml.py; form100_household.to_pdf_values maps it
  to the boxes and applies the ceilings, and box 2038 is checked against its indicative taxable income.
- values: {"fields": {"N.0605": {"value": 46500, "why": "..."}, ...}} or simply {"N.0605": 46500, ...}.
  Field names are the PDF's own: a prefix plus the box number – A. text, N. amount, D. date,
  F. comb box (ID or file number), R. radio button, C. check box, T. total or list
  (examples and the full rules: references/forms/2025/form100-tools.md).
- Amounts are numbers (a minus figure for own-home interest, boxes 1021-1024). Radio buttons and
  check boxes take the state name, e.g. R.0301 "/marie", C.0316 "/Yes".

The PDF adds figures up but never applies a ceiling: type the capped amounts yourself
(1471, 1527/1528, 1551/1552, 1554). Totals are recomputed here from the form's own calculation
scripts, so the file shows the totals Acrobat would show. The text is drawn in the form's format
("38.700,00") and the stored value stays a plain number. The result is not signed: both spouses
sign page 20, or the return is filed through MyGuichet.

Needs: scripts/requirements.txt (the tools environment: references/forms/2025/form100-tools.md « Setup »)
"""
import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

import pypdf
from pypdf.generic import (ArrayObject, BooleanObject, DictionaryObject, FloatObject, NameObject,
                           NumberObject, StreamObject, TextStringObject)

# Helvetica character widths (per 1000 units of font size), standard AFM values
_W = dict(zip(" !\"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~",
              [278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278] + [556] * 10 +
              [278, 278, 584, 584, 584, 556, 1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556,
               833, 722, 778, 667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
               333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556, 556, 556, 333,
               500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584]))


def text_width(text, size):
    total = 0
    for ch in text:
        w = _W.get(ch) or _W.get(unicodedata.normalize("NFD", ch)[0], 556)
        total += w
    return total * size / 1000


def fqn(annot):
    """Full field name of a widget, e.g. N.0605."""
    parts, o = [], annot
    while o is not None:
        if "/T" in o:
            parts.append(str(o["/T"]))
        o = o.get("/Parent").get_object() if o.get("/Parent") else None
    return ".".join(reversed(parts))


def scripts(reader):
    """Calculation scripts and the names of fields the form shows or hides by script."""
    calcs, shown = {}, set()
    for page in reader.pages:
        for ref in page.get("/Annots", []) or []:
            a = ref.get_object()
            name = fqn(a)
            for holder in (a, a.get("/Parent").get_object() if a.get("/Parent") else None):
                aa = holder.get("/AA") if holder is not None else None
                if not aa:
                    continue
                for key, action in aa.get_object().items():
                    action = action.get_object()
                    if "/JS" not in action:
                        continue
                    js = action["/JS"].get_object()
                    js = js.get_data().decode("latin-1") if hasattr(js, "get_data") else str(js)
                    if key == "/V" and "event.target.hidden" in js:
                        shown.add(name)
                    if key != "/C" or name in calcs:
                        continue
                    bv = re.search(r"BVCALC (.*?) EVCALC", js)
                    if bv:
                        calcs[name] = bv.group(1).replace("\\.", ".").replace(" ", "")
                    elif "AFSimple_Calculate" in js:
                        op = re.search(r'AFSimple_Calculate\("(\w+)"', js).group(1)
                        calcs[name] = (op, re.findall(r'"([A-Z0-9]+\.[\w]+)"', js))
                    elif "totDeductions" in js:  # net salary: total minus deductions, never below 0
                        a_, b_ = re.findall(r'getField\("(T\.\w+)"\)', js)[:2]
                        calcs[name] = ("NET", [a_, b_])
    return calcs, shown


def recompute(vals, calcs):
    def num(v):
        return 0.0 if v in (None, "", " ") else float(v)

    for _ in range(12):  # totals feed totals: repeat until nothing changes
        changed = False
        for name, expr in calcs.items():
            if not name.startswith("T."):
                continue
            if isinstance(expr, str):
                total, used = 0.0, False
                for sign, ref in re.findall(r"([+-]?)([A-Z]\.\w+|\d+(?:\.\d+)?)", expr):
                    if re.fullmatch(r"\d+(?:\.\d+)?", ref):
                        v = float(ref)
                    else:
                        v = num(vals.get(ref))
                        used = used or vals.get(ref) not in (None, "")
                    total += -v if sign == "-" else v
                new = total if used else None
            elif expr[0] in ("SUM", "MAX"):
                present = [num(vals[n]) for n in expr[1] if vals.get(n) not in (None, "")]
                new = (sum(present) if expr[0] == "SUM" else max(present)) if present else None
            else:  # NET
                a, b = (vals.get(n) for n in expr[1])
                new = None if a in (None, "") and b in (None, "") else max(num(a) - num(b), 0.0)
            if new is not None and vals.get(name) != round(new, 2):
                vals[name] = round(new, 2)
                changed = True
        if not changed:
            return
    sys.exit("totals did not settle – check the values file")


def eu(x):
    s = f"{abs(x):,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    return ("-" if x < 0 else "") + s


def pdf_str(t):
    try:
        b = t.encode("latin-1")
    except UnicodeEncodeError:
        sys.exit("Form 100 PDF font cannot render a supplied character; use the Unicode XML/manual form route, never transliterate silently")
    return b.replace(b"\\", b"\\\\").replace(b"(", b"\\(").replace(b")", b"\\)").decode("latin-1")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--blank", required=True, help="official blank Form 100 PDF (2025)")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--household", help="household file (one source for PDF, XML and annex)")
    src.add_argument("--values", help="JSON file of box values")
    ap.add_argument("--out", required=True, help="filled PDF to write")
    a = ap.parse_args()

    household = None
    if a.household:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import form100_household as hh
        household = hh.load(a.household)
        inputs = hh.to_pdf_values(household)
    else:
        raw_values = json.load(open(a.values, encoding="utf-8"))
        raw_values = raw_values.get("fields", raw_values)
        inputs = {k: (v["value"] if isinstance(v, dict) else v) for k, v in raw_values.items()}

    reader = pypdf.PdfReader(a.blank)
    all_fields = reader.get_fields() or {}
    if "A.0101" not in all_fields or "T.2038" not in all_fields:
        sys.exit("this does not look like the fillable Form 100 (2025)")
    unknown = sorted(set(inputs) - set(all_fields))
    if unknown:
        sys.exit(f"unknown field names: {unknown}")

    calcs, shown = scripts(reader)
    vals = dict(inputs)
    donation_adjustment = 0
    if household is not None and household.get("donations"):
        check = hh.indicative_check(household)
        actual = sum(hh.D(g["amount"]) for g in household["donations"])
        donation_adjustment = float(actual - check["donations"])
        # The printed donor rows/totals are actual payments. Only the allowed amount
        # enters special expenses; retain that distinction instead of falsifying a receipt.
        if donation_adjustment:
            calcs["T.1639"] += "-" + str(donation_adjustment)
    recompute(vals, calcs)
    computed = {k: vals[k] for k in calcs if k in vals and k.startswith("T.")}

    def is_amount(name):  # T.Bureaux_d_imposition is a list, not an amount
        return name not in ("N.1476", "N.1477", "N.0772", "N.0773", "N.0777", "N.0778") and name[:2] in ("N.", "T.") and isinstance(vals.get(name), (int, float))

    choice_text = {}
    for name, f in all_fields.items():
        if f.get("/FT") == "/Ch" and "/Opt" in f:
            for o in f["/Opt"]:
                if isinstance(o, (list, pypdf.generic.ArrayObject)):
                    choice_text.setdefault(name, {})[str(o[0])] = str(o[1])

    display, stored = {}, {}
    for name, v in vals.items():
        if v is None or v == "":
            continue
        if is_amount(name):
            display[name], stored[name] = eu(float(v)), f"{float(v):.2f}"
        elif name in ("N.0772", "N.0773", "N.0777", "N.0778"):
            display[name], stored[name] = format(float(v), "g").replace(".", ","), format(float(v), "g")
        else:
            display[name] = choice_text.get(name, {}).get(v, str(v))
            stored[name] = str(v)
    if vals.get("F.0105") and not vals.get("F.0109"):  # header line the form shows without a file number
        display["T.matricule"] = stored["T.matricule"] = "n° d'identification personnelle: " + str(vals["F.0105"])

    writer = pypdf.PdfWriter(clone_from=reader)
    # keep our appearances: viewers that regenerate them would show raw numbers
    writer._root_object["/AcroForm"][NameObject("/NeedAppearances")] = BooleanObject(False)
    helv = writer._root_object["/AcroForm"]["/DR"]["/Font"]["/Helv"]
    font_res = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/Helv"): helv})})

    def appearance(annot, field, text, size, bg):
        x1, y1, x2, y2 = [float(v) for v in annot["/Rect"]]
        w, h = abs(x2 - x1), abs(y2 - y1)
        q = int(annot.get("/Q", field.get("/Q", 0)))
        maxlen = annot.get("/MaxLen", field.get("/MaxLen"))
        ff = int(field.get("/Ff", 0))
        comb = bool(ff & (1 << 24)) and maxlen
        lines = re.split(r"\r\n|\r|\n", text) if ff & (1 << 12) else None
        if lines:
            size = 7
            while size > 4 and (max(text_width(t, size) for t in lines) > w - 4 or len(lines) * size * 1.15 > h - 2):
                size -= 0.5
        elif not comb:
            while size > 5 and text_width(text, size) > w - 4:
                size -= 0.5
        ops = ["/Tx BMC", "q"]
        if bg:
            ops.append(f"{bg[0]} {bg[1]} {bg[2]} rg 0 0 {w:.2f} {h:.2f} re f")
        bc = annot.get("/MK", {}).get("/BC")
        if comb and bc:  # the cell grid of comb boxes
            cell = w / int(maxlen)
            ops.append(f"{bc[0]} {bc[1]} {bc[2]} RG 1 w 0.5 0.5 {w - 1:.2f} {h - 1:.2f} re S")
            ops += [f"{cell * i:.2f} 0 m {cell * i:.2f} {h:.2f} l S" for i in range(1, int(maxlen))]
        ops += ["BT", f"/Helv {size} Tf", "0 g"]
        base = (h - size * 0.72) / 2
        if lines:
            for i, t in enumerate(lines):
                ops.append(f"1 0 0 1 2 {h - 1 - size * (i + 1) * 1.15 + size * 0.2:.2f} Tm ({pdf_str(t)}) Tj")
        elif comb:
            cell = w / int(maxlen)
            for i, ch in enumerate(text[: int(maxlen)]):
                ops.append(f"1 0 0 1 {cell * i + (cell - text_width(ch, size)) / 2:.2f} {base:.2f} Tm ({pdf_str(ch)}) Tj")
        else:
            tw = text_width(text, size)
            x = {0: 2, 1: (w - tw) / 2, 2: w - tw - 2}.get(q, 2)
            ops.append(f"1 0 0 1 {x:.2f} {base:.2f} Tm ({pdf_str(text)}) Tj")
        ops += ["ET", "Q", "EMC"]
        stream = StreamObject()
        stream.set_data("\n".join(ops).encode("latin-1"))
        stream.update({NameObject("/Type"): NameObject("/XObject"), NameObject("/Subtype"): NameObject("/Form"),
                       NameObject("/BBox"): ArrayObject([FloatObject(0), FloatObject(0), FloatObject(w), FloatObject(h)]),
                       NameObject("/Resources"): font_res})
        return writer._add_object(stream)

    done = set()
    # Freeze the affected total calculation in this generated snapshot, so a viewer
    # cannot silently restore the gross donation deduction from the official default JS.
    # Its downstream income total still uses this stored, capped special-expense total.
    for page in writer.pages:
        for ref in page.get("/Annots", []) or []:
            annot = ref.get_object()
            if annot.get("/Subtype") != "/Widget":
                continue
            name = fqn(annot)
            if name not in display:
                continue
            field = annot if "/T" in annot else annot["/Parent"].get_object()
            if donation_adjustment and name == "T.1639":
                for target in (annot, field):
                    actions = target.get("/AA")
                    if actions is not None:
                        actions.pop(NameObject("/C"), None)
                field[NameObject("/Ff")] = NumberObject(int(field.get("/Ff", 0)) | 1)
            if (field.get("/FT") or annot.get("/FT")) == "/Btn":
                state = stored[name]
                states = list(annot["/AP"]["/N"].keys())
                annot[NameObject("/AS")] = NameObject(state if state in states else "/Off")
                field[NameObject("/V")] = NameObject(state)
            else:
                field[NameObject("/V")] = TextStringObject(stored[name])
                bg = None if name in computed else [float(c) for c in annot.get("/MK", {}).get("/BG", [])] or None
                annot[NameObject("/AP")] = DictionaryObject(
                    {NameObject("/N"): appearance(annot, field, display[name], 8 if is_amount(name) else 9, bg)})
            if name in shown or name == "T.matricule":  # helpers such as T.1553max stay hidden
                annot[NameObject("/F")] = NumberObject(int(annot.get("/F", 0)) & ~2)
            done.add(name)
    if set(display) - done:
        print("not drawn:", sorted(set(display) - done))

    with open(a.out, "wb") as fh:
        writer.write(fh)
    print(f"filled {len(display)} fields, {len(computed)} totals recomputed -> {a.out}")
    for key, label in (("T.2033", "net income, taxpayer"), ("T.2034", "net income, spouse"),
                       ("T.1639", "special expenses (2037)"), ("T.2038", "taxable income (2038)")):
        if key in computed:
            print(f"  {key} {label}: {eu(computed[key])}")
    if household is not None and household.get("childcare"):
        from make_childcare_annex import write as write_childcare
        annex = Path(a.out).with_suffix(".childcare.pdf")
        write_childcare(household, annex)
        print(f"childcare monthly annex -> {annex}")
    if household is not None and (any(household.get(k) for k in ("donations", "salary_costs", "occupational_pension", "voluntary_contributions", "medical_expenses")) or any(i.get("risk") == "PU" for i in household.get("insurance", []))):
        from make_deductions_annex import write as write_deductions
        annex = Path(a.out).with_suffix(".deductions.pdf")
        write_deductions(household, annex, hh.indicative_check(household), hh.allowed(household))
        print(f"deduction calculation annex -> {annex}")
    if household is not None:
        want = float(hh.indicative_check(household)["taxable income"])
        got = computed.get("T.2038")
        print(f"box 2038 vs the household's indicative taxable income {eu(want)}: " +
              ("MATCH" if got is not None and abs(got - want) < 0.005 else "DIFFERENCE – check the household file"))
        if got is None or abs(got - want) >= 0.005:
            sys.exit(1)


if __name__ == "__main__":
    main()
