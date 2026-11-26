# Copyright 2026 BravoLisa (https://bravolisa.lu) – https://github.com/bravolisa/luxembourg-self-employed-accounting-skill
# SPDX-License-Identifier: Apache-2.0
"""A change of civil status or address during the tax year (2025): checks, paper boxes, XML blocks.

Field map and sources: references/forms/2025/family-events.md. Who is taxed jointly, and in which
class: lu-income-tax-personal family-changes.md. The household file states every status and date;
this module checks that they fit together and writes them. It never picks a status for the person.
Two paper choices the ACD has not confirmed follow the working answers of PIT-O-42: the paper form
shows the status after the event, and the separation boxes stay filled beside "divorced".
"""
import sys
from datetime import date

CODES = ("CE", "MA", "DI", "VE", "PA", "SF", "SV", "DE")
PAPER = {"CE": "/celibataire", "MA": "/marie", "DI": "/divorce", "VE": "/veuf"}
# Paper boxes 306-308 are one radio group (R.0306). Only the state of box 308 has a plain name;
# 306 and 307 carry an accented letter stored in Latin-1 and are left to be ticked by hand.
GROUNDS = {"court": "/judic", "judgment": None, "legal": None}
SIGNATURES = {"each": "CONT_CONJ", "taxpayer_for_both": "CONT_CONT", "on_screen": None}
SIDES = ("taxpayer", "spouse")


def need(ok, message):
    if not ok:
        sys.exit("status and addresses: " + message)


def iso(value, label):
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        need(False, label + " must be a date YYYY-MM-DD")


def people(h):
    return [(side, h[side]) for side in SIDES if h.get(side)]


def status_used(h):
    """True when a person has a status that began during the year."""
    return any(p.get("status_changes") for _, p in people(h))


def used(h):
    return (status_used(h) or h.get("spouse_address") is not None or h.get("signature") is not None
            or any(p.get("separation") or p.get("earlier_addresses") for _, p in people(h)))


def sequence(h, side):
    """[(status, since)]: the status on 1 January, then each status that began in the year."""
    p = h[side]
    first = p.get("status", "MA" if h.get("spouse") else "CE")
    return [(first, p.get("status_since"))] + [(c.get("status"), c.get("since")) for c in p.get("status_changes", [])]


def _jointly_taxable(seq):
    # Art. 3 LIR: married and not separated under a decision on 1 January, or married during the year.
    return seq[0][0] in ("MA", "SF") or any(s == "MA" for s, _ in seq[1:])


def joint_married(h):
    return bool(h.get("spouse")) and all(_jointly_taxable(sequence(h, side)) for side in SIDES)


def death_date(h):
    """Date of the spouse's death in the tax year, or None."""
    if not h.get("spouse"):
        return None
    last, since = sequence(h, "spouse")[-1]
    return iso(since, "date of death") if last == "DE" else None


def _check_address(a, label):
    need(isinstance(a, dict) and a.get("postcode") and a.get("locality"),
         label + ": a Luxembourg address with postcode and locality is required (a foreign address needs manual entry)")


def validate(h):
    if not used(h):
        return
    year = int(h["tax_year"])
    need(year == 2025, "status changes, other addresses and the signature choice are mapped for tax year 2025 only")
    need(not h.get("partnership"),
         "a joint partnership return needs a partnership and a shared home for the whole year: no change, other address or signature choice with 'partnership'")
    review = h.get("status_review") or {}
    need(isinstance(review.get("evidence"), str) and review["evidence"].strip(),
         "status_review.evidence: name the certificates and decisions checked (marriage, court decision, death, addresses)")
    spouse = h.get("spouse")
    for side, p in people(h):
        seq = sequence(h, side)
        codes = [s for s, _ in seq]
        need(all(c in CODES for c in codes), f"{side}: status codes are {', '.join(CODES)}")
        need(codes[0] != "DE", f"{side}: 'DE' cannot be the status on 1 January")
        need(side == "spouse" or "DE" not in codes, "the person who died is entered as the spouse; the surviving filer is the taxpayer")
        need("DE" not in codes[:-1], f"{side}: nothing can follow 'DE'")
        changes = p.get("status_changes", [])
        need(isinstance(changes, list) and len(changes) <= 10, f"{side}: at most ten status changes")
        if changes:
            need(p.get("status") in CODES, f"{side}: 'status' (on 1 January) is required with status_changes")
            need(codes[0] == "CE" or p.get("status_since"), f"{side}: status_since (when the 1-January status began) is required")
            if p.get("status_since"):
                need(iso(p["status_since"], side + " status_since") <= date(year, 1, 1),
                     f"{side}: status_since is after 1 January – a status that began in the year goes into status_changes")
            previous, previous_code = None, codes[0]
            for c in changes:
                d = iso(c.get("since"), side + " status_changes since")
                need(d.year == year, f"{side}: a status change must be dated in {year}")
                need(previous is None or d >= previous, f"{side}: status_changes in date order")
                need(c.get("status") != previous_code, f"{side}: the same status twice in a row")
                previous, previous_code = d, c.get("status")
        need(sum(1 for s in codes[1:] if s == "MA") <= 1,
             f"{side}: married more than once in the year – MyGuichet's assistant is closed to this household; prepare the return by hand")
        sep = p.get("separation")
        if "SV" in codes or sep:
            need(isinstance(sep, dict) and sep.get("ground") in GROUNDS and sep.get("evidence"),
                 f"{side}: separation {{ground: court | judgment | legal, since, evidence}} is required for a separation under a decision")
            since = iso(sep.get("since"), side + " separation since")
            if "SV" in codes:
                need(str(since) == str(dict(seq)["SV"]), f"{side}: separation.since must be the date of the 'SV' status")
            else:
                need(codes[-1] == "DI", f"{side}: the separation boxes are for a person separated under a decision, or divorced after one")
        earlier = p.get("earlier_addresses", [])
        need(isinstance(earlier, list) and len(earlier) <= 10, f"{side}: at most ten earlier addresses")
        last_day = None
        for a in earlier:
            start, end = iso(a.get("from"), side + " earlier address from"), iso(a.get("to"), side + " earlier address to")
            need(start.year == end.year == year and start <= end, f"{side}: an earlier address needs a period inside {year}")
            need(last_day is None or start > last_day, f"{side}: earlier addresses in date order, without overlap")
            _check_address(a.get("address"), side + " earlier address")
            last_day = end
    if h.get("spouse_address") is not None:
        need(spouse, "spouse_address without a spouse")
        _check_address(h["spouse_address"], "spouse_address")
    agent = h.get("filed_by", "self") == "agent"
    signature = h.get("signature")
    if signature is not None:
        need(signature in SIGNATURES and spouse and not agent,
             "signature: 'each', 'taxpayer_for_both' or 'on_screen', for a couple that files itself")
    if spouse and status_used(h):
        need(joint_married(h),
             "a joint return needs spouses who were married and not separated under a decision on 1 January, or who married during the year")
        mine, theirs = sequence(h, "taxpayer")[1:], sequence(h, "spouse")[1:]
        died = death_date(h)
        if died:
            need(mine and mine[-1] == ("VE", str(died)) and mine[:-1] == theirs[:-1],
                 "death of the spouse: the taxpayer becomes 'VE' and the spouse 'DE' on the same date")
            need(agent or signature in ("taxpayer_for_both", "on_screen"),
                 "a spouse died in the year: choose signature 'taxpayer_for_both' (death certificate in place of the mandate) or 'on_screen'")
        else:
            need(mine == theirs, "both spouses must show the same status changes on the same dates")
    if not spouse and h["taxpayer"].get("status_changes"):
        need(not any(s in ("MA", "SF") for s, _ in sequence(h, "taxpayer")),
             "a married or informally separated person is taxed jointly: add the spouse, or prepare individual taxation by hand")


# ---------------------------------------------------------------- paper form (PDF)

def _paper_status(h):
    p = h["taxpayer"]
    seq = sequence(h, "taxpayer")
    last, since = seq[-1]
    if last in ("SF", "SV"):  # still married: box 302 with the wedding date
        wedding = next((d for s, d in reversed(seq) if s == "MA"), None) or p.get("married_since")
        need(wedding, "taxpayer: married_since is required – paper box 305 takes the wedding date of a separated spouse")
        return "MA", wedding
    if last == "PA":  # the paper form has no status for partners: the civil status underneath
        under = next(((s, d) for s, d in reversed(seq) if s != "PA"), None) or (p.get("underlying_civil_status"), p.get("underlying_status_since"))
        need(under[0] in ("CE", "DI", "VE"), "taxpayer: underlying_civil_status CE, DI or VE is required for a partner's paper status")
        return under
    return last, since


def pdf_values(h, dmy):
    """Paper boxes for a household that uses the event fields; {} otherwise."""
    if not used(h):
        return {}
    year = int(h["tax_year"])
    v = {}
    if status_used(h) or h["taxpayer"].get("separation"):
        status, since = _paper_status(h)
        need(status in PAPER, "taxpayer: no paper status for " + str(status))
        v["R.0301"] = PAPER[status]
        v["D.0305"] = dmy(since) if since and status != "CE" else None
        sep = h["taxpayer"].get("separation")
        if sep:
            state = GROUNDS[sep["ground"]]
            need(state, "paper boxes 306 and 307 (legal dispensation, judgment of legal separation) cannot be ticked by the tool: leave 'separation' out of the PDF run and tick the box by hand")
            v["R.0306"], v["D.0309"] = state, dmy(sep["since"])
    own = h.get("spouse_address")
    if own:
        v.update({"A.0118": str(own.get("number", "")), "A.0119": own.get("street", ""),
                  "A.0122": "L-" + str(own["postcode"]), "A.0123": own["locality"], "A.0125": "LU"})
    for n, (side, p) in enumerate(people(h)):
        earlier = p.get("earlier_addresses", [])
        if not earlier:
            continue
        need(len(earlier) == 1 and iso(earlier[0]["from"], "from") == date(year, 1, 1),
             f"{side}: the paper form holds one earlier address per person, from 1 January – a second move needs a note by hand")
        a = earlier[0]["address"]
        v.update({f"A.012{6 + n}": dmy(earlier[0]["to"]),
                  f"A.01{28 + 2 * n}": str(a.get("number", "")), f"A.01{29 + 2 * n}": a.get("street", ""),
                  f"A.01{32 + 2 * n}": "L-" + str(a["postcode"]), f"A.01{33 + 2 * n}": a["locality"],
                  f"A.013{6 + n}": "LU"})
    return v


# ---------------------------------------------------------------- MyGuichet XML

def xml_status(sig, h, side, s):
    """SIT_1JAN, DATE_SIT_1JAN, AUT_CHG_SIT and one group per status that began in the year."""
    seq = sequence(h, side)
    first, since = seq[0]
    sig.add(f"SIT_1JAN_{s}", first)
    if since is None and first == "CE" and len(seq) > 1:
        since = f"{int(h['tax_year'])}-01-01"  # the ACD's 2021 guide: 1 January of the tax year for a single person
    if since:
        sig.add(f"DATE_SIT_1JAN_{s}", since)
    sig.add(f"AUT_CHG_SIT_{s}", len(seq) > 1)
    group = "EtatCivilAnnFiscContrib" if s == "CONT" else "EtatCivilAnnFiscConj"
    for status, start in seq[1:]:
        g = sig.add(group)
        g.add(f"AUT_SIT_{s}", status)
        g.add(f"DAT_AUT_SIT_{s}", start)


def xml_address(ad, h, side, s, write_address):
    own = h.get("spouse_address") if side == "spouse" else None
    if side == "spouse":
        ad.add("MEME_ADR_CONJ", own is None)
    write_address(ad.add(f"ADR_ACT_{s}"), own or h["address"])
    earlier = h[side].get("earlier_addresses", [])
    ad.add(f"AUTRE_CHG_ADR_{s}", bool(earlier))
    group = "AutreAdrContrib" if s == "CONT" else "AutreAdrConj"
    for a in earlier:
        g = ad.add(group)
        g.add(f"DATE_DEB_ADR_{s}", a["from"])
        g.add(f"DATE_FIN_ADR_{s}", a["to"])
        write_address(g.add(f"AUTRE_ADR_{s}"), a["address"])


def eligibility(h):
    """(married, partners) at any time in the year, or None to keep the builder's ordinary answers."""
    if not status_used(h):
        return None
    codes = [s for s, _ in sequence(h, "taxpayer")]
    return any(c in ("MA", "SF", "SV") for c in codes), "PA" in codes


def signature(h):
    """The G2810 answer for a couple filing itself; None leaves the block empty for the filer."""
    return SIGNATURES[h.get("signature") or "each"]
