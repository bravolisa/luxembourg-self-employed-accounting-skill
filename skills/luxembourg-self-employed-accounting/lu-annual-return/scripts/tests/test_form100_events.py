#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""A change of civil status or address during the year: paper boxes and XML fields.

Invented households. Every expected value below was written by hand from the field map in
references/forms/2025/family-events.md and the paper map in lu-income-tax-personal
forms/2025/cross-border-and-family.md – none is copied from the tools' output.
"""
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import form100_household as hh
import build_form100_xml as xml
import test_form100_tools as base

results = []


def check(name, ok):
    results.append((bool(ok), name))


def fixture(name):
    return base.with_ids(json.loads((HERE / "households" / f"{name}.json").read_text()))


def stops(name, h, fn=hh.validate, snippet=None):
    message = base.stops(fn, h)
    check(name, message is not None and (snippet is None or snippet in message))


schema = xml.Schema(base.XSD)


def built(h):
    root = xml.build(h, schema).to_xml()
    schema.validator.assertValid(root)
    return root


def leaf(root, path):
    return [e.text for e in root.findall(".//" + path)]


REVIEW = {"evidence": "Invented certificates: marriage, court order, death, residence."}
COUPLE = fixture("couple_commercial_salaried")   # married since 1 September 2012, files itself, eligibility pre-filled
SINGLE = fixture("single_liberal")               # single
HOME = COUPLE["address"]
NEW = {"postcode": "1234", "locality": "Luxembourg", "street": "Rue Inventée", "number": "7"}


def couple(changes, spouse_last=None, **extra):
    h = copy.deepcopy(COUPLE)
    for side in ("taxpayer", "spouse"):
        h[side]["status_changes"] = [dict(status=s, since=d) for s, d in changes]
    if spouse_last:
        h["spouse"]["status_changes"][-1]["status"] = spouse_last
    h["status_review"] = REVIEW
    h.update(extra)
    return h


# 1. The court allows the spouses to live apart on 1 July 2025; the spouse moves out that day.
#    Paper: still married (302, wedding date) + box 308 with the date of the decision; the spouse's
#    new address in the right-hand column, the old shared one in the earlier-address block until 30 June.
h = couple([("SV", "2025-07-01")], spouse_address=NEW)
for side in ("taxpayer", "spouse"):
    h[side]["separation"] = {"ground": "court", "since": "2025-07-01", "evidence": "Invented court order"}
h["spouse"]["earlier_addresses"] = [{"from": "2025-01-01", "to": "2025-06-30", "address": dict(HOME)}]
v = hh.to_pdf_values(h)
check("court permission: paper status stays married with the wedding date", v["R.0301"] == "/marie" and v["D.0305"] == "01/09/2012")
check("court permission: box 308 and the date of the decision", v["R.0306"] == "/judic" and v["D.0309"] == "01/07/2025")
check("spouse's own address in the right-hand column", (v["A.0118"], v["A.0119"], v["A.0122"], v["A.0123"], v["A.0125"]) == ("7", "Rue Inventée", "L-1234", "Luxembourg", "LU"))
check("taxpayer's column keeps the household address", v["A.0116"] == str(HOME.get("number", "")) and v["A.0120"] == "L-" + str(HOME["postcode"]))
check("earlier address of the spouse: boxes 127, 130, 131, 134, 135, 137",
      (v["A.0127"], v["A.0130"], v["A.0131"], v["A.0134"], v["A.0135"], v["A.0137"])
      == ("30/06/2025", str(HOME.get("number", "")), HOME.get("street", ""), "L-" + str(HOME["postcode"]), HOME["locality"], "LU"))
check("no earlier address for the taxpayer", "A.0126" not in v and "A.0128" not in v)
root = built(h)
for side, s, person in (("Contribuable", "CONT", "Contrib"), ("Conjoint", "CONJ", "Conj")):
    check(f"court permission XML {s}: married on 1 January since the wedding, changed, then SV",
          leaf(root, f"Identite{side}/Signaletique/G0{'160' if s == 'CONT' else '400'}_SIT_1JAN_{s}") == ["MA"]
          and leaf(root, f"Identite{side}/Signaletique/G0{'180' if s == 'CONT' else '420'}_DATE_SIT_1JAN_{s}") == ["2012-09-01"]
          and leaf(root, f"Identite{side}/Signaletique/G0{'200' if s == 'CONT' else '440'}_AUT_CHG_SIT_{s}") == ["true"]
          and leaf(root, f"EtatCivilAnnFisc{person}/G0{'220' if s == 'CONT' else '460'}_AUT_SIT_{s}") == ["SV"]
          and leaf(root, f"EtatCivilAnnFisc{person}/G0{'240' if s == 'CONT' else '480'}_DAT_AUT_SIT_{s}") == ["2025-07-01"])
check("XML spouse address: not the same, own number, one earlier address 1 January to 30 June",
      leaf(root, "G0660_MEME_ADR_CONJ") == ["false"] and leaf(root, "G0680_ADR_ACT_CONJ/AdresseAuLuxembourg/Numero") == ["7"]
      and leaf(root, "G0760_AUTRE_CHG_ADR_CONJ") == ["true"] and leaf(root, "AutreAdrConj/G0780_DATE_DEB_ADR_CONJ") == ["2025-01-01"]
      and leaf(root, "AutreAdrConj/G0800_DATE_FIN_ADR_CONJ") == ["2025-06-30"]
      and leaf(root, "AutreAdrConj/G0820_AUTRE_ADR_CONJ/AdresseAuLuxembourg/CodePostal") == [str(HOME["postcode"])])
check("XML taxpayer address: no other address", leaf(root, "G0580_AUTRE_CHG_ADR_CONT") == ["false"] and not root.findall(".//AutreAdrContrib"))
check("each spouse still signs in their own name; married during the year", leaf(root, "G2810_SIG_CONT_CONJ") == ["CONT_CONJ"] and leaf(root, "G9030_EL_MARIE") == ["true"])

# 2. Informal separation on 1 July 2025: still married on paper, no separation box; XML status SF.
h = couple([("SF", "2025-07-01")])
v = hh.to_pdf_values(h)
check("informal separation: married with the wedding date, no separation box", v["R.0301"] == "/marie" and v["D.0305"] == "01/09/2012" and "R.0306" not in v)
check("informal separation XML: SF from the day of the separation", leaf(built(h), "EtatCivilAnnFiscContrib/G0220_AUT_SIT_CONT") == ["SF"])

# 3. Marriage on 14 June 2025 of two single people.
h = couple([("MA", "2025-06-14")])
for side in ("taxpayer", "spouse"):
    h[side]["status"] = "CE"
    h[side].pop("status_since")
v = hh.to_pdf_values(h)
check("marriage: paper shows married since the wedding day", v["R.0301"] == "/marie" and v["D.0305"] == "14/06/2025")
root = built(h)
check("marriage XML: single since 1 January of the tax year, then MA on the wedding day",
      leaf(root, "G0160_SIT_1JAN_CONT") == ["CE"] and leaf(root, "G0180_DATE_SIT_1JAN_CONT") == ["2025-01-01"]
      and leaf(root, "G0200_AUT_CHG_SIT_CONT") == ["true"] and leaf(root, "EtatCivilAnnFiscConj/G0460_AUT_SIT_CONJ") == ["MA"]
      and leaf(root, "EtatCivilAnnFiscConj/G0480_DAT_AUT_SIT_CONJ") == ["2025-06-14"] and leaf(root, "G0660_MEME_ADR_CONJ") == ["true"])
check("marriage: joint status accepted for the couple's deductions", hh.family.joint_status_supported(h))

# 4. The spouse dies on 31 December 2025: the survivor is the taxpayer and signs for both.
h = couple([("VE", "2025-12-31")], spouse_last="DE", signature="taxpayer_for_both")
v = hh.to_pdf_values(h)
check("death: paper shows widowed since the day of the death, no separation box", v["R.0301"] == "/veuf" and v["D.0305"] == "31/12/2025" and "R.0306" not in v)
root = built(h)
check("death XML: survivor MA then VE, deceased MA then DE, same day",
      leaf(root, "EtatCivilAnnFiscContrib/G0220_AUT_SIT_CONT") == ["VE"] and leaf(root, "EtatCivilAnnFiscConj/G0460_AUT_SIT_CONJ") == ["DE"]
      and leaf(root, "EtatCivilAnnFiscConj/G0480_DAT_AUT_SIT_CONJ") == ["2025-12-31"] and leaf(root, "G0400_SIT_1JAN_CONJ") == ["MA"])
check("death XML: the survivor signs in own name and for the spouse", leaf(root, "G2810_SIG_CONT_CONJ") == ["CONT_CONT"])
h2 = copy.deepcopy(h); h2["signature"] = "on_screen"
root = built(h2)
check("death XML: 'on_screen' leaves the signature block empty", root.find(".//SignatureMandataire") is not None and not root.findall(".//G2810_SIG_CONT_CONJ"))
h2 = copy.deepcopy(h); h2.pop("signature")
stops("death without a signature choice stops", h2, snippet="signature")
h2 = copy.deepcopy(h); h2["taxpayer"]["status_changes"][0]["since"] = "2025-12-30"
stops("death: survivor and deceased need the same date", h2)

# 5. One person, separated by court permission since 10 March 2024, divorced on 15 January 2025.
h = copy.deepcopy(SINGLE)
h["taxpayer"].update(status="SV", status_since="2024-03-10", status_changes=[{"status": "DI", "since": "2025-01-15"}],
                     separation={"ground": "court", "since": "2024-03-10", "evidence": "Invented court order"})
h["status_review"] = REVIEW
v = hh.to_pdf_values(h)
check("divorce after an earlier permission: divorced since the judgment, box 308 with the date of the permission",
      v["R.0301"] == "/divorce" and v["D.0305"] == "15/01/2025" and v["R.0306"] == "/judic" and v["D.0309"] == "10/03/2024")
root = built(h)
check("divorce XML: SV on 1 January since the permission, then DI; no spouse block; married during the year",
      leaf(root, "G0160_SIT_1JAN_CONT") == ["SV"] and leaf(root, "G0180_DATE_SIT_1JAN_CONT") == ["2024-03-10"]
      and leaf(root, "EtatCivilAnnFiscContrib/G0220_AUT_SIT_CONT") == ["DI"] and root.find(".//IdentiteConjoint") is None
      and leaf(root, "G9030_EL_MARIE") == ["true"] and leaf(root, "G9040_EL_PARTENAIRE") == ["false"])
h2 = copy.deepcopy(h); h2["taxpayer"]["separation"]["ground"] = "judgment"
check("a judgment of legal separation (box 307) validates and builds the XML", base.stops(hh.validate, h2) is None and built(h2) is not None)
stops("box 307 cannot be ticked by the tool: the PDF run stops", h2, fn=hh.to_pdf_values, snippet="306 and 307")
h2 = copy.deepcopy(h); h2["taxpayer"].pop("separation")
stops("status SV without the separation facts stops", h2, snippet="separation")

# 6. One person declares a partnership on 14 June 2025: no joint taxation that year, files alone.
h = copy.deepcopy(SINGLE)
h["taxpayer"]["status_changes"] = [{"status": "PA", "since": "2025-06-14"}]
h["status_review"] = REVIEW
v = hh.to_pdf_values(h)
check("partnership declared: paper keeps the civil status single, no date, no joint request",
      v["R.0301"] == "/celibataire" and "D.0305" not in v and "C.0312" not in v and "D.0313" not in v)
root = built(h)
check("partnership XML: single since 1 January, then PA; in a partnership during the year",
      leaf(root, "G0160_SIT_1JAN_CONT") == ["CE"] and leaf(root, "G0180_DATE_SIT_1JAN_CONT") == ["2025-01-01"]
      and leaf(root, "EtatCivilAnnFiscContrib/G0220_AUT_SIT_CONT") == ["PA"] and leaf(root, "EtatCivilAnnFiscContrib/G0240_DAT_AUT_SIT_CONT") == ["2025-06-14"]
      and leaf(root, "G9040_EL_PARTENAIRE") == ["true"] and leaf(root, "G9030_EL_MARIE") == ["false"] and not root.findall(".//G1940_ASS_DEM_3BIS"))

# 7. Checks that must stop.
h = couple([("SV", "2025-07-01")]); h.pop("status_review")
stops("no status_review evidence", h, snippet="status_review")
h = couple([("SF", "2025-07-01")]); h["spouse"].pop("status_changes")
stops("only one spouse shows the change", h, snippet="both spouses")
h = couple([("SF", "2024-12-31")])
stops("a change dated outside the tax year", h)
h = couple([("SF", "2025-07-01")]); h["taxpayer"]["status_since"] = "2025-02-01"; h["spouse"]["status_since"] = "2025-02-01"
stops("status_since after 1 January with changes", h, snippet="status_changes")
h = couple([("DI", "2025-03-01"), ("MA", "2025-05-01"), ("DI", "2025-08-01"), ("MA", "2025-11-01")])
stops("married more than once in the year", h, snippet="more than once")
h = couple([("VE", "2025-12-31")], signature="on_screen"); h["taxpayer"]["status_changes"][0]["status"] = "DE"; h["spouse"]["status_changes"][0]["status"] = "VE"
stops("the person who died cannot be the taxpayer", h, snippet="spouse")
h = copy.deepcopy(SINGLE); h["taxpayer"]["status_changes"] = [{"status": "MA", "since": "2025-06-14"}]; h["status_review"] = REVIEW
stops("a marriage in the year needs the spouse in the file", h, snippet="add the spouse")
h = copy.deepcopy(COUPLE); h["taxpayer"].update(status="SV", status_since="2024-03-10", status_changes=[{"status": "DI", "since": "2025-01-15"}],
                                                 separation={"ground": "court", "since": "2024-03-10", "evidence": "x"})
h["spouse"].update(status="SV", status_since="2024-03-10", status_changes=[{"status": "DI", "since": "2025-01-15"}],
                   separation={"ground": "court", "since": "2024-03-10", "evidence": "x"}); h["status_review"] = REVIEW
stops("separated by court permission before the year: no joint return", h, snippet="joint return")
h = couple([("SF", "2025-07-01")], signature="for_everyone")
stops("unknown signature choice", h, snippet="signature")
h = couple([("SF", "2025-07-01")])
h["spouse"]["earlier_addresses"] = [{"from": "2025-01-01", "to": "2025-03-31", "address": dict(HOME)}, {"from": "2025-04-01", "to": "2025-06-30", "address": dict(NEW)}]
h["spouse_address"] = dict(NEW, number="9")
check("two earlier addresses validate and go into the XML", base.stops(hh.validate, h) is None and len(built(h).findall(".//AutreAdrConj")) == 2)
stops("two earlier addresses have no place on the paper form", h, fn=hh.to_pdf_values, snippet="one earlier address")
h["spouse"]["earlier_addresses"][1]["from"] = "2025-03-15"
stops("overlapping earlier addresses", h, snippet="overlap")

# 8. A household without any of the new fields is written as before.
root = built(copy.deepcopy(COUPLE))
check("unchanged household: no change, same address, each signs",
      leaf(root, "G0200_AUT_CHG_SIT_CONT") == ["false"] and leaf(root, "G0660_MEME_ADR_CONJ") == ["true"]
      and leaf(root, "G0760_AUTRE_CHG_ADR_CONJ") == ["false"] and leaf(root, "G2810_SIG_CONT_CONJ") == ["CONT_CONJ"]
      and not root.findall(".//EtatCivilAnnFiscContrib"))
v = hh.to_pdf_values(copy.deepcopy(COUPLE))
check("unchanged household: paper status as before", v["R.0301"] == "/marie" and v["D.0305"] == "01/09/2012" and "R.0306" not in v and "A.0127" not in v)

for ok, name in results:
    print(("PASS  " if ok else "FAIL  ") + name)
failed = sum(not ok for ok, _ in results)
print(f"{len(results) - failed} passed, {failed} failed, 0 skipped")
sys.exit(bool(failed))
