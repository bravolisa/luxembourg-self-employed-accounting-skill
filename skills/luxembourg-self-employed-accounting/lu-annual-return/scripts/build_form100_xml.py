#!/usr/bin/env python3
# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""Build the XML that pre-fills the MyGuichet procedure « ACD (Modèle 100) » for one household.

Usage:
    python build_form100_xml.py --household household.json --xsd ACD_PP_2025-Modele_100_XSD_Import.xsd --out return.xml
    ... --minimal   identity-only file for an early test upload (references/forms/2025/form100-tools.md, step 2)

- household: the household in MyGuichet's terms (salary certificates, business method, insurance,
  home savings, CCSS certificate, agent) – format and an invented example: references/forms/2025/form100-tools.md.
- xsd: the ACD's import schema for the tax year (2025: the zip on
  https://impotsdirects.public.lu/fr/echanges_electroniques/decl_pph.html, or the copy in
  this skill, official-forms/F100-XSD-2025.txt – its two header lines are skipped).

The schema drives the build: each field is found by the end of its name under the right person
(taxpayer and spouse fields differ only in their code, e.g. S0380_SAL_MNT_COTSOC_NEX and
S1440_SAL_MNT_COTSOC_NEX), elements are put in the schema's order, and the file is validated before
it is written. It is written the way MyGuichet accepted it in October 2026: a double-quoted XML
declaration, CRLF line ends, UTF-8 without BOM and the ACD example's root element.

MyGuichet then shows the procedure for checking; it does not compute the commuting deduction (give
each salary's share in "travel") and applies its own ceilings. Compare its taxable income with the
indicative check this script prints. Not covered yet (the script stops if they are given): rental income, pensions, capital income, incoming donation carries, unsupported extraordinary charges.
Supported 2025 family/deduction/CIM subsets: form100-family.md and forms/2025/form100-deductions.md.

Needs: scripts/requirements.txt (the tools environment: references/forms/2025/form100-tools.md « Setup »)
"""
import argparse
import re
import sys
from decimal import Decimal
from pathlib import Path

from lxml import etree

sys.path.insert(0, str(Path(__file__).resolve().parent))
import form100_household as hh  # noqa: E402  the household file: checks, figures, indicative check

XS = "{http://www.w3.org/2001/XMLSchema}"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
PERSON_ID = {"taxpayer": "DECLARER", "spouse": "CONJOINT"}
SIDE = {"taxpayer": "CONT", "spouse": "CONJ"}



class Schema:
    def __init__(self, path):
        text = Path(path).read_text(encoding="utf-8")
        header, text = text[:text.index("<")], text[text.index("<"):]  # a library copy starts "SOURCE: ..."
        # the ACD's file name, for the root's noNamespaceSchemaLocation: the file itself or the one the header names
        named = re.search(r"ACD_PP_\d{4}-Modele_100_XSD_Import\.xsd", Path(path).name + " " + header)
        self.file_name = named.group(0) if named else None
        self.doc = etree.fromstring(text.encode("utf-8"))
        self.ctypes = {e.get("name"): e for e in self.doc.findall(XS + "complexType")}
        self.validator = etree.XMLSchema(self.doc)
        self.root = self.doc.find(XS + "element[@name='eForm']")
        years = [v.get("value") for v in self.root.iter(XS + "enumeration")]
        self.form_types = years  # e.g. ACD_F100_2025, ACD_F100_2025_PRO

    def children(self, decl):
        """Child element declarations of an element, in schema order."""
        ct = decl.find(XS + "complexType")
        if ct is None and decl.get("type") in self.ctypes:
            ct = self.ctypes[decl.get("type")]
        out = []

        def walk(node):
            for c in node:
                if c.tag == XS + "element":
                    out.append(c)
                elif c.tag in (XS + "sequence", XS + "choice", XS + "all", XS + "complexContent"):
                    walk(c)
                elif c.tag == XS + "extension":
                    if c.get("base") in self.ctypes:
                        walk(self.ctypes[c.get("base")])
                    walk(c)
        if ct is not None:
            walk(ct)
        return out


def matches(name, key):
    return name == key or name.split("_", 1)[-1] == key


class Node:
    def __init__(self, schema, decl):
        self.schema, self.decl, self.name = schema, decl, decl.get("name")
        self.kids, self.attrs, self.text = [], {}, None

    def add(self, key, value=None, **attrs):
        """Add a child found by its name, or by its name without the code (S1440_SAL_MNT_COTSOC_NEX ->
        SAL_MNT_COTSOC_NEX); value: str, bool, or a number written with 2 decimals."""
        options = [d for d in self.schema.children(self.decl) if matches(d.get("name"), key)]
        if len(options) != 1:
            sys.exit(f"schema: '{key}' under {self.name} matches {[d.get('name') for d in options] or 'nothing'}")
        node = Node(self.schema, options[0])
        node.attrs = {k: str(v) for k, v in attrs.items()}
        if isinstance(value, bool):
            node.text = "true" if value else "false"
        elif isinstance(value, (int, float, Decimal)):
            node.text = f"{Decimal(str(value)):.2f}"
        elif value is not None:
            node.text = str(value)
        self.kids.append(node)
        return node

    def one(self, key, **attrs):
        """The existing child with this key, or a new one."""
        for k in self.kids:
            if matches(k.name, key):
                return k
        return self.add(key, **attrs)

    def to_xml(self, parent=None):
        el = etree.Element(self.name) if parent is None else etree.SubElement(parent, self.name)
        for k, v in self.attrs.items():
            el.set(k, v)
        if self.text is not None:
            el.text = self.text
        order = {d.get("name"): i for i, d in enumerate(self.schema.children(self.decl))}
        for kid in sorted(self.kids, key=lambda n: order[n.name]):  # stable: repeated elements keep their order
            kid.to_xml(el)
        return el


def need(cond, msg):
    if not cond:
        sys.exit(msg)


def build(h, schema):
    year = int(h["tax_year"])
    hh.validate(h)
    tp, sp = h["taxpayer"], h.get("spouse")
    agent = h.get("filed_by", "self") == "agent"
    space = h.get("space", "private")
    form_type = f"ACD_F100_{year}" + ("_PRO" if space == "pro" else "")
    need(form_type in schema.form_types, f"{form_type} is not in this schema ({schema.form_types})")

    root = Node(schema, schema.root)
    root.add("guFile").add("eFormType", form_type)
    payload = root.add("Payload")
    names = f"{tp['last_name']} {tp.get('first_name', '')}".strip()
    if sp:
        names += f" et {sp['last_name']} {sp.get('first_name', '')}".rstrip()
    payload.add("Header").add("NomDemarche", h.get("procedure_name") or f"ACD : Déclaration pour l'impôt sur le revenu {year} - {names}")
    d = payload.add("Declaration").add("DetailDeclaration")
    for who in ("taxpayer", "spouse"):
        if who == "taxpayer" or sp:
            d.add("personne").add("ID_PERSONNE", PERSON_ID[who])
    if any(i.get("risk") == "PU" for i in h.get("insurance", [])):
        d.add("resPrincipale").add("ID_RESPRINCIPALE", "RESPRINCIPALE0")
    if h.get("consent") is not None:
        d.add("Introduction").add("CONSENTEMENT", bool(h["consent"]))
    ig = d.add("InformationsGenerales")
    ig.add("NUM_DOSSIER", h["file_number"])
    if h.get("tax_office"):
        ig.add("BUR_IMP", h["tax_office"])

    addr = h["address"]

    def lu_address(node, a=None):
        a = a or addr
        lu = node.add("AdresseAuLuxembourg")
        lu.add("CodePays", "LU")
        lu.add("CodePostal", str(a["postcode"]))
        lu.add("Localite", a["locality"])
        if a.get("street"):
            lu.add("Rue", a["street"])
        if a.get("number"):
            lu.add("Numero", str(a["number"]))

    for who, p in (("taxpayer", tp), ("spouse", sp)):
        if not p:
            continue
        s = SIDE[who]
        ident = d.add("IdentiteContribuable" if who == "taxpayer" else "IdentiteConjoint",
                      **{("G1570_ID_PERSONNE" if who == "taxpayer" else "G1645_ID_PERSONNE"): PERSON_ID[who]})
        sig = ident.add("Signaletique")
        sig.add(f"NOM_{s}", p["last_name"])
        if p.get("first_name"):
            sig.add(f"PRENOM_{s}", p["first_name"])
        sig.add(f"NUM_NAT_{s}", p["national_id"])
        if p.get("phone"):
            sig.add(f"TEL_{s}", p["phone"])
        if p.get("email"):
            sig.add(f"MAIL_{s}", p["email"])
        if hh.events.used(h):  # a status that began in the year, another address: forms/2025/family-events.md
            hh.events.xml_status(sig, h, who, s)
            hh.events.xml_address(ident.add("Adresse"), h, who, s, lu_address)
            continue
        sig.add(f"SIT_1JAN_{s}", p.get("status", "MA" if sp else "CE"))
        if h.get('partnership'):
            sig.add(f"DATE_SIT_1JAN_{s}", h['partnership']['declaration_date'])
        elif p.get("status_since"):
            sig.add(f"DATE_SIT_1JAN_{s}", p["status_since"])
        sig.add(f"AUT_CHG_SIT_{s}", False)
        ad = ident.add("Adresse")
        if who == "spouse":
            ad.add("MEME_ADR_CONJ", True)
        lu_address(ad.add(f"ADR_ACT_{s}"))
        ad.add(f"AUTRE_CHG_ADR_{s}", False)

    if h.get('partnership'):
        mode = d.add('ModeImposition')
        mode.add('ASS_DEM_3BIS', True)
        mode.add('ASS_DEM_3BIS_DOC', h['partnership']['certificate_already_presented'])
    hh.family.add_children(d, h)

    # signatures and agent
    sm = d.add("SignatureMandataire")
    if not agent:
        if sp:
            choice = hh.events.signature(h)  # default: each spouse signs in their own name
            if choice:
                sm.add("SIG_CONT_CONJ", choice)
    else:
        ag = h["agent"]
        sm.add("MAN_SIG_CONT_CONJ", "MAN_CONT_CONJ" if sp else "MAN_CONT")
        for s, prefix in (("CONT", ("G2860", "G1663", "G1661", "G1665", "G1666", "G1700", "G1720")),
                          ("CONJ", ("G2870", "G1771", "G1781", "G1782", "G1783", "G1800", "G1820"))):
            if s == "CONJ" and not sp:
                continue
            sm.add(f"MAN_PRO_AVO_PART_{s}", ag.get("capacity", "PART"))
            sm.add(f"MAN_PP_PM_{s}", ag.get("kind", "PP"))
            if ag.get("company"):
                sm.add(f"MAN_DSGN_SOC_{s}", ag["company"])
            sm.add(f"MAN_NOM_CNTCT_{s}", ag["last_name"])
            if ag.get("first_name"):
                sm.add(f"MAN_PRENO_CNTCT_{s}", ag["first_name"])
            if ag.get("phone"):
                sm.add(f"MAN_TEL_{s}", ag["phone"])
            if ag.get("email"):
                sm.add(f"MAN_MAIL_{s}", ag["email"])
        need(ag.get("phone") or ag.get("email"), "agent: give a phone or an e-mail")

    # income menu
    sal, bus = h.get("salaries", []), h.get("businesses", [])
    owners = lambda items, **kw: {i["owner"] for i in items if all(i.get(k) == v for k, v in kw.items())}
    m = d.add("MenuRevenus")
    m.add("REV_SAL", bool(sal))
    if sal:
        m.add("REV_SAL_CONT", "taxpayer" in owners(sal))
        m.add("REV_SAL_CONJ", "spouse" in owners(sal))
    m.add("REV_PEN", False)
    m.add("HAB_PRO_OCC", bool(h.get("own_home")))
    for k in ("HAB_PRO_CON", "HAB_PRO_CED", "REV_LOC"):
        m.add(k, False)
    if h.get("own_home"):
        m.add("HAB_PRO_INT_DEB", True)
        m.add("LOC_INT_DEB", True)
    m.add("AUT_REV_BEN_QST", bool(bus))
    if bus:
        com, lib = owners(bus, kind="commercial"), owners(bus, kind="liberal")
        m.add("BEN_COM", bool(com))
        if com:
            for k, v in (("BEN_COM_IND_CONT", "taxpayer" in com), ("BEN_COM_PHV_CONT", False), ("BEN_COM_EN_COM_CONT", False),
                         ("BEN_COM_IND_CONJ", "spouse" in com), ("BEN_COM_PHV_CONJ", False), ("BEN_COM_EN_COM_CONJ", False)):
                m.add(k, v)
        m.add("BEN_BFO", False)
        m.add("BEN_PLI", bool(lib))
        if lib:
            for k, v in (("BEN_PLI_IND_CONT", "taxpayer" in lib), ("BEN_PLI_COM_CONT", False), ("BEN_PLI_JET_CONT", False),
                         ("BEN_PLI_TAN_CONT", False), ("BEN_PLI_IND_CONJ", "spouse" in lib), ("BEN_PLI_COM_CONJ", False),
                         ("BEN_PLI_JET_CONJ", False), ("BEN_PLI_TAN_CONJ", False)):
                m.add(k, v)
        m.add("REV_CAP_MOB", False)
        m.add("REV_NET_DIV", False)

    data = {}
    for who in ("taxpayer", "spouse"):
        if who == "spouse" and not sp:
            continue
        mine_b = [b for b in bus if b["owner"] == who]
        mine_s = [s for s in sal if s["owner"] == who]
        if who == "spouse" and not (mine_b or mine_s):
            continue
        tag = "DonneesImpositionContribuable" if who == "taxpayer" else "DonneesImpositionConjoint"
        node = d.add(tag, **{("G3000_ID_PERSONNE" if who == "taxpayer" else "G3140_ID_PERSONNE"): PERSON_ID[who]})
        data[who] = node
        for b in mine_b:
            add_business(node, b)
        if mine_s:
            ss = node.add("Salaires")
            for s in mine_s:
                add_salary(ss, s)
            fo = ss.add("FraisObtentionSalaires")
            actual = hh.employment.actual_cost(h, who)
            fo.add("SAL_FO_MIN_FORFAIT", "MF" if actual is None else "FE")
            if actual is not None:
                fo.add("SAL_FO_REV_IMP", actual)

    hh.family.add_home(data["taxpayer"], h, hh.figures(year))

    # special expenses
    ins, hsv, ppv = h.get("insurance", []), h.get("home_savings", []), h.get("pension_plans", [])
    ccss = h.get("ccss_self_employed", [])
    ds = d.add("DepensesSpeciales")
    menu = ds.add("MenuDepensesSpeciales")
    mf = menu.add("MenuDepensesSpecialesMinFor")
    for k, v in (("DEP_SPE_MFO_ARR", False), ("DEP_SPE_MFO_INT", bool(h.get("consumer_loans"))), ("DEP_SPE_MFO_ASS", bool(ins)),
                 ("DEP_SPE_MFO_CTP", bool(h.get("voluntary_contributions"))), ("DEP_SPE_MFO_PPV", bool(ppv)), ("DEP_SPE_MFO_EPL", bool(hsv))):
        mf.add(k, v)
    hm = menu.add("MenuDepensesSpecialesHorsMinFor")
    for k, v in (("DEP_SPE_HMF_CSO", bool(ccss) or bool(sal)), ("DEP_SPE_HMF_RCS", bool(h.get("occupational_pension"))), ("DEP_SPE_HMF_RCI", False),
                 ("DEP_SPE_HMF_LIB", bool(h.get("donations"))), ("DEP_SPE_HMF_PER", False)):
        hm.add(k, v)
    hh.deductions.add_xml(ds, h)
    hh.employment.add_xml(ds, h, hh.figures(year))
    if ins:
        pa = ds.add("DepSpePrimesAssurances")
        for i in ins:
            p = pa.add("DepSpePrimesAssurancesDetail")
            p.add("PAC_NOM_ENT_ASS", i["insurer"])
            p.add("PAC_RIS_ASS", i["risk"])
            p.add(f"PAC_MNT_PRI_{SIDE[i['paid_by']]}", i["amount"])
            hh.deductions.add_premium_xml(p, i)
    if ppv:
        pv = ds.add("DepSpePrimePrevVieillesse")
        for i in ppv:
            p = pv.add("DepSpePrimePrevVieillesseDetail", D1060_ID_PERSONNE=PERSON_ID[i["holder"]])
            p.add("PPV_PEPP", bool(i.get("pepp", False)))
            p.add("PPV_ENT_ASS_MUT", i["insurer"])
            p.add("PPV_DAT_DEB_CON", i["start"])
            p.add("PPV_DAT_FIN_CON", i["end"])
            p.add("PPV_MNT_PRI_VER", i["amount"])
    if hsv:
        ep = ds.add("DepSpeEpargneLogement")
        for i in hsv:
            p = ep.add("DepSpeEpargneLogementDetail", D1300_ID_PERSONNE=PERSON_ID[i["holder"]])
            p.add("CEL_CAI_EPA_LOG", i["bank"])
            p.add("CEL_DAT_DEB_CON", i["contract_date"])
            p.add("CEL_MNT_COT_VER", i["amount"])
    if ccss:
        cs = ds.add("DepSpeCotisationSocObli")
        for c in ccss:
            s = SIDE[c["owner"]]
            kinds = {b["kind"] for b in bus if b["owner"] == c["owner"]}
            need(kinds, f"ccss_self_employed for {c['owner']} but no business of that person")
            if "commercial" in kinds:
                cs.add(f"BCI_COT_SOC_{s}", True)
            if "liberal" in kinds:
                cs.add(f"BLI_COT_SOC_{s}", True)
            cs.add(f"COTSOC_DED_{s}_NEX", c["deductible"])
            cs.add(f"COTSOC_NDU_{s}_NEX", c.get("non_deductible", 0))
            mut = c.get("mutualite", {})
            for k, key in (("MAL", "illness"), ("ACC", "work_injury"), ("CAC", "compassionate_leave"), ("FAM", "family")):
                cs.add(f"MUT_{k}_{s}_NEX", mut.get(key, 0))
        cs.add("CSO_AUT_COT_OBL", False)

    charges = d.add("ChargesExtraordinaires")
    ce = charges.add("MenuChargesExtraordinaires")
    for k in ("ABT_ART_127", "ABT_RGD_INV", "ABT_RGD_DOM", "ENF_HOR_MEN"):
        ce.add(k, bool(h.get("childcare")) if k == "ABT_RGD_DOM" else bool(h.get('medical_expenses')) if k == 'ABT_ART_127' else False)
    if h.get('medical_expenses'):
        ce.add('FRAIS_MAL', True)
    hh.family.add_childcare(charges, h)
    hh.medical.add_xml(charges, h)
    dac6 = d.add("Divers").add("DAC6")
    dac6.add("DIS_DUE_CONT", bool(h.get("dac6", False)))
    if sp:
        dac6.add("DIS_DUE_CONJ", bool(h.get("dac6_spouse", False)))

    if h.get("eligibility"):
        el = d.add("Eligibilite")
        married = bool(sp) and tp.get("status", "MA") == "MA"
        partners = bool(sp) and tp.get("status") == "PA"
        if hh.events.eligibility(h):  # « au cours de l'année »: married or in a partnership at any time in the year
            married, partners = hh.events.eligibility(h)
        for k, v in (("EL_LUXTRUST", True), ("EL_ID_RNPP", True), ("EL_DECLARANT", not agent),  # No = for a third party
                     ("EL_MARIE", married), ("EL_PARTENAIRE", partners), ("EL_REV_IMP_COL", False),
                     ("EL_IMP_INDIV", False), ("EL_MARIE_X_FOIS_AN", False)):
            el.add(k, v)
        if sp:
            el.add("EL_CONJ_MEME_PAYS", True)
        el.add("EL_CHANGE_PAYS", False)
    return root


def add_business(node, b):
    method = b.get("method", "REDE")
    if b["kind"] == "commercial":
        ind = node.one("BeneficeCommercial").one("BenComIndviduel")
        det = ind.add("BenComInd").add("BenComIndDetail")
        pre, rev_tag, ext_tag, misc_tag = "BCI", "BenComIndRevNonExo", "BenComIndRevExtNonExo", "BenComIndDemandesDiverses"
    elif b["kind"] == "liberal":
        ind = node.one("BeneficeProfLib").one("BenProfLibIndviduel")
        det = ind.add("BenProfLibInd").add("BenProfLibIndDetail")
        pre, rev_tag, ext_tag, misc_tag = "BLI", "BenProfLibIndRevNonExo", "BenProfLibIndRevExtNonExo", "BenProfLibIndDemandesDiverses"
    else:
        sys.exit(f"business kind must be 'commercial' or 'liberal', not {b['kind']!r}")
    det.add(f"{pre}_NAT_ACT", b["activity"])
    if b.get("activity_other"):
        det.add(f"{pre}_NAT_ACT_AUT", b["activity_other"])
    if b["kind"] == "commercial" and b.get("trade_name"):
        det.add("BCI_DEN_COM", b["trade_name"])
    det.add(f"{pre}_DAT_DEB_ACT", b["start"])
    det.add(f"{pre}_DAT_FIN_ACT", b["end"])
    det.add(f"{pre}_REV_NEX", True)
    det.add(f"{pre}_REV_EXO", False)
    det.add(f"{pre}_ACT_PRI_ACC", "PRIN" if b.get("main", True) else "ACCE")
    det.add(f"{pre}_DET_BEN", method)
    det.add(f"{pre}_CHO_DED", "FREF")
    rev = det.add(rev_tag)
    if b["kind"] == "commercial" and b.get("file_number"):
        rev.add("BCI_NUM_DOS_NEX", b["file_number"])
    if method == "BILA":
        rev.add(f"{pre}_MNT_PER_PRO_NEX", b["profit"])
    else:
        rev.add(f"{pre}_MNT_REC_BRU_NEX", b["receipts"])
        rev.add(f"{pre}_MNT_DEP_EFF_NEX", b["expenses"])
    rev.add(f"{pre}_CES", False)
    rev.add(ext_tag).add(f"{pre}_ART131_DEM", False)
    misc = det.add(misc_tag)
    credit = b.get("investment_credit") or {}
    if b["kind"] == "commercial":
        misc.add("BCI_DEM_AMO", False)
        misc.add("BCI_DEM_BON_INV", bool(credit))
        for key, suffix in (("software_152bis_7_1", "BON_INV_152B_71"), ("art_152bis_3", "BON_INV_152B_3"),
                            ("art_152bis_7_7a", "BON_INV_152B_77A")):
            if credit.get(key):
                misc.add(f"BCI_{suffix}", credit[key])
        ind.one("BenComDeduction").one("BenComChoixDeduction").add("BCF_CHO_DED", "FREF")
        ind.one("Deduction50TER").add("50TER_DED", False)
        ind.one("RetenuesImpot").add("BCI_RET_IMP", False)
    else:
        need(not credit, "investment credit for a liberal profession: enter it in MyGuichet")
        misc.add("BLI_DEM_AMO_BONI", False)
        ind.one("BenProfLibDeduction").one("BenProfLibChoixDeduction").add("BLF_CHO_DED", "FREF")
        ind.one("Deduction50TER").add("50TER_DED", False)
        ind.one("RetenuesImpot").add("BLI_RET_IMP", False)


def add_salary(ss, s):
    x = ss.add("Salaire")
    x.add("SAL_GEN_ACT", s.get("occupation", "SALA"))
    if s.get("employer"):
        x.add("SAL_NOM_EMP", s["employer"])
    x.add("SAL_DAT_DEB_ACT", s["start"])
    x.add("SAL_DAT_FIN_ACT", s["end"])
    det = x.add("SalaireDetail")
    det.add("SAL_REV_NEX", True)
    det.add("SAL_REV_EXO", False)
    nx = det.add("SalaireDetailRevNonExo")
    if hh.salary_details.replacement(s):
        review = s.get('xml_workplace_review') or {}
        need(s.get('workplaces') and review.get('authoritative_semantics_confirmed') is True and review.get('authority_evidence'),
             'replacement benefit XML: required workplace semantics need authoritative evidence; never use issuer address as workplace')
    for commune in dict.fromkeys(s.get("workplaces", [])):  # communes of the official list, not localities (Remerschen -> SCHENGEN)
        nx.add("SAL_LIEU_TRAV_NEX").add("Commune", commune)
    for p in s["pay"]:  # S salary, IMAL sick pay advanced by the employer, ...
        line = nx.add("SalaireNonExo")
        line.add("SAL_NAT_SAL_NEX", p["kind"])
        if p.get('description'):
            line.add('SAL_DES_SAL_NEX', p['description'])
        line.add("SAL_MNT_BRUT_NEX", p["amount"])
    nx.add("SalaireRevExtNonExo").add("SAL_ART131_DEM", False)
    ded = nx.add("SalaireDeductions")
    ded.add("SAL_MNT_COTSOC_NEX", s["contributions"])
    if s.get("travel"):
        ded.add("SAL_FRAIS_DEP", s["travel"])  # MyGuichet sums these as the commuting deduction
    nx.add("PRE_EXEMP_NEX", bool(s.get('exemptions')))
    if s.get('exemptions'):
        for item in s['exemptions']:
            row = nx.add('SalaireExemptionsNonExo')
            row.add('SAL_NAT_EXEMP_NEX', item['kind'])
            row.add('SAL_MNT_EXEMPT_NEX', item['amount'])
    if s.get("taxable_base") is not None:
        nx.add("SAL_MNT_BASE_RET", s["taxable_base"])
    nx.add("SAL_MNT_RETENUE", hh.salary_withheld(s))
    for key, field in (("cis", "SAL_MNT_CIS"), ("co2", "SAL_MNT_CO2")):
        if s.get(key) is None:
            raise SystemExit(f"salary {key}: missing is not zero; obtain the amount already paid on the certificate")
        amount = Decimal(str(s[key]))
        if not amount.is_finite() or amount < 0:
            raise SystemExit(f"salary {key}: non-finite or negative annual credit-paid amount: retain the source value and use reviewed manual preparation; this generator supports non-negative totals only")
        nx.add(field, amount)
    if "cim" in s:
        nx.add("SAL_MNT_CIM", hh.family.money(s["cim"], "salary paid CIM"))
    det.add("SAL_ADM_FON_ANA", False)


def write(root_node, schema, out, year):
    el = root_node.to_xml()
    root = etree.Element("eForm", nsmap={"xsi": XSI})
    location = schema.file_name or f"ACD_PP_{year}-Modele_100_XSD_Import.xsd"
    need(str(year) in location, f"schema {location} is not for tax year {year}")
    root.set(f"{{{XSI}}}noNamespaceSchemaLocation", location)
    for kid in el:
        root.append(kid)
    etree.indent(root, space="\t")
    body = etree.tostring(root, encoding="UTF-8", xml_declaration=False).decode("utf-8")
    text = ('<?xml version="1.0" encoding="UTF-8"?>\n' + body + "\n").replace("\r\n", "\n").replace("\n", "\r\n")
    check = etree.fromstring(text.encode("utf-8"))
    if not schema.validator.validate(check):
        for e in schema.validator.error_log:
            print("  line", e.line, e.message[:300])
        sys.exit("not valid against the schema – nothing written")
    Path(out).write_bytes(text.encode("utf-8"))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--household", required=True)
    ap.add_argument("--xsd", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--minimal", action="store_true",
                    help="identity, options and signatures only – for an early test upload (delete that procedure after)")
    a = ap.parse_args()
    h = hh.load(a.household)
    if a.minimal:  # same person data, no figures: tests the file format and the identity pages first
        h = {k: v for k, v in h.items() if k not in ("businesses", "salaries", "insurance", "home_savings",
                                                      "pension_plans", "ccss_self_employed", "children", "childcare", "own_home",
                                                      "consumer_loans", "donations", "salary_costs", "occupational_pension",
                                                      "voluntary_contributions", "medical_expenses", "medical_review", "single_parent_credit")}
        h["procedure_name"] = "TEST import - identity only (delete after the test)"
    schema = Schema(a.xsd)
    write(build(h, schema), schema, a.out, int(h["tax_year"]))
    print(f"valid against the schema -> {a.out}")
    chk = hh.indicative_check(h)
    if chk:
        print("indicative check (compare with box 2038 of the PDF and MyGuichet's R1530):")
        for k, v in chk.items():
            if isinstance(v, dict):
                print(f"  {k}: " + "; ".join(f"{name}={amount}" for name, amount in v.items()))
            else:
                print(f"  {k}: {v:,.2f}")
    if h.get("salaries") and not any(s.get("travel") for s in h["salaries"]):
        print("note: no travel expenses given – MyGuichet will not compute a commuting deduction itself")


if __name__ == "__main__":
    main()
