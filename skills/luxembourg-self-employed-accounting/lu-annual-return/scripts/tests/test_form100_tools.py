#!/usr/bin/env python3
"""Regression tests for the Form 100 tools, on invented households (no real person).

Usage:
    python scripts/tests/test_form100_tools.py [--blank 100f-2025.pdf]

Per household in households/, against the hand calculation in expected.json:
- the indicative taxable income (form100_household.indicative_check);
- the PDF boxes the household maps to (to_pdf_values) and, when the blank form is found, the
  filled PDF: box 2038 must equal the indicative taxable income;
- the MyGuichet XML: valid against the 2025 schema, its key elements, and the --minimal test file;
- the receipts annex: its total, and the PDF make_receipts_annex.py writes.
Once: every figure in lu-tax-core/data/tool-figures.json appears in its source markdown; the
invented example household still builds; and the checks that must stop a run do stop it.

ID numbers: the households say "@ID:<birth date>"; the test turns them into 13 digits that start
with the birth date and end in 00000, so no real-looking matricule is stored in the skills.

Needs lxml (XML) and pypdf (PDF); a part is skipped, not failed, when its package, the schema or
the blank form is missing. Blank form: --blank, or the environment variable BL_FORM100_BLANK, or
official-forms/100f-2025.pdf in this skill.
Exit code 1 when a check fails.
"""
import argparse
import copy
import json
import os
import re
import subprocess
import sys
import tempfile
from decimal import Decimal
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent
SKILLS = SCRIPTS.parents[1]
XSD = SKILLS / "official-forms" / "F100-XSD-2025.txt"
DEFAULT_BLANK = SKILLS / "official-forms" / "100f-2025.pdf"

sys.path.insert(0, str(SCRIPTS))
import form100_household as hh  # noqa: E402

results = []


def check(name, ok, detail=""):
    results.append(("PASS" if ok else "FAIL", name, "" if ok else detail))


def skip(name, why):
    results.append(("SKIP", name, why))


def has(module):
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def same(a, b):
    if isinstance(b, str) and not re.fullmatch(r"-?\d+(?:\.\d+)?", b):
        return str(a) == b
    return abs(Decimal(str(a)) - Decimal(str(b))) < Decimal("0.005")


def with_ids(h):
    text = re.sub(r'"@ID:(\d{4})-(\d{2})-(\d{2})"', lambda m: f'"{m[1]}{m[2]}{m[3]}00000"', json.dumps(h))
    return json.loads(text)


def stops(fn, *args):
    """The message a check stops with, or None when it runs through."""
    try:
        fn(*args)
    except SystemExit as e:
        return str(e.code)
    return None


def run(*args):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True)


def local(el):
    return el.tag.split("}")[-1] if isinstance(el.tag, str) else ""


# ---------------------------------------------------------------- once

def test_figures():
    data = json.loads(hh.FIGURES_SOURCE.read_text(encoding="utf-8"))["years"]
    for year, table in data.items():
        for key, f in table.items():
            src = SKILLS / f["source"]
            name = f"figures {year} {key}"
            if not src.exists():
                check(name, False, f"source missing: {f['source']}")
                continue
            text = src.read_text(encoding="utf-8")
            ok = f["match"] in text
            if isinstance(f["value"], list):  # a scale: every band edge and rate must be in the source
                value_ok = all((top is None or f"€{top:,}" in text) and f"| {rate}% |" in text for top, rate in f["value"])
            else:
                value_ok = f["value"] is None or f"{f['value']:,}" in f["match"]
            check(name, ok and value_ok,
                  f"'{f['match']}' not in {f['source']}" if not ok else f"value {f['value']} not in '{f['match']}'")


def test_stops(base):
    h = copy.deepcopy(base)
    h["insurance"] = [{"insurer": "Example insurer", "risk": "PU", "paid_by": "taxpayer", "amount": 9000}]
    for name, fn in (("household validation", hh.validate), ("deduction calculation", hh.allowed),
                     ("taxable-income estimate", hh.indicative_check), ("PDF field preparation", hh.to_pdf_values)):
        msg = stops(fn, h)
        check(f"stops: single premium before {name}", msg is not None and "single-premium" in msg,
              f"got {msg!r}; must not silently use the ordinary insurance ceiling")

    h = copy.deepcopy(base)
    h["rental"] = [{"amount": 100}]
    msg = stops(hh.validate, h)
    check("stops: a not-covered item (rental)", msg is not None and "rental" in msg, f"got {msg!r}")

    h = copy.deepcopy(base)
    h["businesses"][0]["receipts_breakdown"]["customers"] += 1
    msg = stops(hh.validate, h)
    check("stops: a receipts breakdown that does not add up", msg is not None and "receipts_breakdown" in msg, f"got {msg!r}")

    h = copy.deepcopy(base)
    h["spouse"]["national_id"] = "YYYYMMDDNNNNN"
    msg = stops(hh.validate, h)
    check("stops: a placeholder ID number", msg is not None and "national_id" in msg, f"got {msg!r}")

    h = copy.deepcopy(base)
    h["ccss_self_employed"][0]["mutualite"]["illness"] = 50
    msg = stops(hh.validate, h)
    check("stops: Mutualité differing from the CCSS certificate", msg is not None and "Mutualité" in msg, f"got {msg!r}")


def test_example(tmp):
    """The invented example in scripts/examples must keep building once real-looking IDs are put in."""
    ex = json.loads((SCRIPTS / "examples" / "form100-2025-myguichet.example.json").read_text(encoding="utf-8"))
    msg = stops(hh.validate, ex)
    check("example: refuses its placeholder IDs", msg is not None and "national_id" in msg, f"got {msg!r}")
    ex["taxpayer"]["national_id"], ex["spouse"]["national_id"] = "19800101" + "0" * 5, "19820202" + "0" * 5  # split: no ID-like number in the file
    check("example: valid once IDs are given", stops(hh.validate, ex) is None, stops(hh.validate, ex) or "")
    if has("lxml") and XSD.exists():
        path = tmp / "example.json"
        path.write_text(json.dumps(ex), encoding="utf-8")
        r = run(SCRIPTS / "build_form100_xml.py", "--household", path, "--xsd", XSD, "--out", tmp / "example.xml")
        check("example: XML builds and validates", r.returncode == 0, (r.stdout + r.stderr)[-300:])
        ex["tax_year"] = 2026
        path.write_text(json.dumps(ex), encoding="utf-8")
        r = run(SCRIPTS / "build_form100_xml.py", "--household", path, "--xsd", XSD, "--out", tmp / "example-2026.xml")
        check("stops: a 2026 household with the 2025 schema", r.returncode != 0 and "not in this schema" in r.stderr,
              (r.stdout + r.stderr)[-300:])


    ex["tax_year"] = 2025
    ex["insurance"] = [{"insurer": "Example insurer", "risk": "PU", "paid_by": "taxpayer", "amount": 9000}]
    path = tmp / "single-premium.json"
    path.write_text(json.dumps(ex), encoding="utf-8")
    out = tmp / "single-premium.xml"
    r = run(SCRIPTS / "build_form100_xml.py", "--household", path, "--xsd", XSD, "--out", out)
    check("single premium: XML CLI stops before producing a misleading return",
          r.returncode != 0 and "single-premium" in r.stderr and not out.exists(), (r.stdout + r.stderr)[-300:])
    r = run(SKILLS / "lu-income-tax-personal/scripts/tax_estimate.py", "--household", path)
    check("single premium: tax-estimate CLI stops before a false balance",
          r.returncode != 0 and "single-premium" in r.stderr, (r.stdout + r.stderr)[-300:])


# ---------------------------------------------------------------- per household

def test_household(name, h, exp, tmp, blank):
    chk = hh.indicative_check(h)
    check(f"{name}: indicative taxable income", same(chk["taxable income"], exp["taxable_income"]),
          f"{chk['taxable income']} vs {exp['taxable_income']}")

    vals = hh.to_pdf_values(h)
    for box, want in exp.get("pdf", {}).items():
        if box.startswith("T."):
            continue  # the form's own totals: checked on the filled PDF
        got = vals.get(box)
        check(f"{name}: PDF box {box}", got is not None and same(got, want), f"{got} vs {want}")

    if "annex_total" in exp:
        total = sum((hh.receipts_breakdown(h, b)["total"] for b in h.get("businesses", [])
                     if b.get("method", "REDE") == "REDE" and b.get("receipts_breakdown")), Decimal(0))
        check(f"{name}: receipts annex total", same(total, exp["annex_total"]), f"{total} vs {exp['annex_total']}")

    path = tmp / f"{name}.json"
    path.write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")
    test_xml(name, path, exp, tmp)
    test_pdf(name, path, exp, tmp, blank)
    if "annex_total" in exp:
        test_annex(name, path, exp, tmp)


def test_annex(name, path, exp, tmp):
    if not (has("reportlab") and has("pypdf")):
        return skip(f"{name}: annex PDF", "reportlab or pypdf not installed")
    import pypdf
    out = tmp / f"{name}.annex.pdf"
    r = run(SCRIPTS / "make_receipts_annex.py", "--household", path, "--out", out)
    check(f"{name}: annex PDF written", r.returncode == 0, (r.stdout + r.stderr)[-300:])
    if r.returncode != 0:
        return
    text = " ".join(pg.extract_text() for pg in pypdf.PdfReader(str(out)).pages)
    total = f"{Decimal(str(exp['annex_total'])):,.2f}".replace(",", " ").replace(".", ",").replace(" ", ".")
    want = [total] + exp.get("annex_text", [])
    missing = [w for w in want if w not in text]
    check(f"{name}: annex shows the total and its captions", not missing, f"missing {missing}")


def test_xml(name, path, exp, tmp):
    if not has("lxml"):
        return skip(f"{name}: XML", "lxml not installed")
    if not XSD.exists():
        return skip(f"{name}: XML", f"schema not found: {XSD}")
    from lxml import etree
    out = tmp / f"{name}.xml"
    r = run(SCRIPTS / "build_form100_xml.py", "--household", path, "--xsd", XSD, "--out", out)
    check(f"{name}: XML builds and validates", r.returncode == 0, (r.stdout + r.stderr)[-300:])
    if r.returncode != 0:
        return
    raw = out.read_bytes()
    check(f"{name}: XML file format (declaration, CRLF)",
          raw.startswith(b'<?xml version="1.0" encoding="UTF-8"?>\r\n') and b"\n" not in raw.replace(b"\r\n", b""),
          raw[:60].decode("utf-8", "replace"))
    els = list(etree.fromstring(raw).iter())
    for key, want in exp.get("xml", {}).items():
        texts = [e.text for e in els if local(e) == key or local(e).split("_", 1)[-1] == key]
        check(f"{name}: XML {key}", want in texts, f"{texts[:4]} vs {want}")

    mini = tmp / f"{name}.minimal.xml"
    r = run(SCRIPTS / "build_form100_xml.py", "--household", path, "--xsd", XSD, "--out", mini, "--minimal")
    check(f"{name}: --minimal builds and validates", r.returncode == 0, (r.stdout + r.stderr)[-300:])
    if r.returncode == 0:
        names = {local(e) for e in etree.fromstring(mini.read_bytes()).iter()}
        figures = sorted(n for n in names if n in ("Salaire", "BenComIndDetail", "BenProfLibIndDetail",
                                                   "DepSpePrimesAssurances", "DepSpeCotisationSocObli", "Enfant",
                                                   "ResPrincipaleRevenusNonExo", "CharExtraFraisDomGardeDetail"))
        title = [e.text for e in etree.fromstring(mini.read_bytes()).iter() if local(e) == "NomDemarche"]
        check(f"{name}: --minimal has no figures and a TEST title", not figures and title and title[0].startswith("TEST"),
              f"figures {figures}, title {title}")


def test_pdf(name, path, exp, tmp, blank):
    if not has("pypdf"):
        return skip(f"{name}: PDF", "pypdf not installed")
    if not blank or not Path(blank).exists():
        return skip(f"{name}: PDF", "blank Form 100 not found (--blank or BL_FORM100_BLANK)")
    import pypdf
    out = tmp / f"{name}.pdf"
    r = run(SCRIPTS / "fill_form100_pdf.py", "--blank", blank, "--household", path, "--out", out)
    check(f"{name}: PDF fills, box 2038 = indicative taxable income", r.returncode == 0 and "MATCH" in r.stdout,
          (r.stdout + r.stderr)[-300:])
    if r.returncode != 0:
        return
    fields = pypdf.PdfReader(str(out)).get_fields()
    for box, want in exp.get("pdf", {}).items():
        got = (fields.get(box) or {}).get("/V")
        try:
            ok = got is not None and same(got, want)
        except ValueError:
            ok = False
        check(f"{name}: filled PDF {box}", ok, f"{got} vs {want}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--blank", default=os.environ.get("BL_FORM100_BLANK") or str(DEFAULT_BLANK))
    a = ap.parse_args()

    expected = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory() as t:
        tmp = Path(t)
        test_figures()
        test_example(tmp)
        for path in sorted((HERE / "households").glob("*.json")):
            name = path.stem
            if name not in expected:
                check(f"{name}: has a hand calculation in expected.json", False, "add it")
                continue
            h = with_ids(json.loads(path.read_text(encoding="utf-8")))
            msg = stops(hh.validate, h)
            check(f"{name}: household is valid", msg is None, msg or "")
            if msg is None:
                test_household(name, h, expected[name], tmp, a.blank)
                if name == "couple_commercial_salaried":
                    test_stops(h)

    for status, name, detail in results:
        print(f"{status}  {name}" + (f"  – {detail}" if detail else ""))
    count = {s: sum(1 for r in results if r[0] == s) for s in ("PASS", "FAIL", "SKIP")}
    print(f"\n{count['PASS']} passed, {count['FAIL']} failed, {count['SKIP']} skipped")
    sys.exit(1 if count["FAIL"] else 0)


if __name__ == "__main__":
    main()
