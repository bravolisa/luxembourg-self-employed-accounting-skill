# EU VAT – where is it taxed and who pays?

_Figures in this file: 2025–2026. The year files of the domain skills (lu-vat, lu-income-tax-business, lu-social-security) win if they differ._

Follow lu-tax-core for triage, labels and answer shape. **[C]** Confirmed, **[I]** Interpretation, **[P]** Practice, **[O]** Open, **[B]** BravoLisa convention; source ids in [references/sources.md](references/sources.md).

## Four facts decide the answer

1. **Who is the customer?** A business (VAT-identified, checked in VIES) or a private person.
2. **Where is the customer established?** Same country, another EU country, outside the EU.
3. **What is supplied?** Goods or services; for services, which kind (general, electronic, online event or education, linked to a building, transport…).
4. **Where is the supplier established**, and under which scheme (normal, franchise, EX)?

Ask for any of these that is missing; the answer usually flips on one of them.

## Where to look

| Question | Read |
|---|---|
| Where is this service or these goods taxed? | [place-of-supply.md](references/place-of-supply.md) |
| Who pays the VAT, what goes on the invoice, recapitulative statements, VIES | [reverse-charge-and-reporting.md](references/reverse-charge-and-reporting.md) |
| Sales to private customers in other EU countries, the €10,000 threshold, OSS | [oss.md](references/oss.md) |
| The EU cross-border SME scheme (EX number) | [sme-cross-border.md](references/sme-cross-border.md) |
| Changes already scheduled (ViDA from 2027, bill 8812) | [figures/2027.md](references/figures/2027.md); status of bills: lu-tax-core watch list |
| What is not settled: open points with a working answer and who can settle them | [open-questions.md](references/open-questions.md) |

## Quick answers

| Situation (supplier in Luxembourg) | Usual result | Status |
|---|---|---|
| Service to a business in another EU country | Taxed in the customer's country; customer pays (reverse charge); supplier lists it in the recapitulative statement | [C · S2, S3] |
| Service to a business outside the EU | Outside EU VAT; the customer's country may tax it locally | [I] |
| Service to a private person in the EU (general services) | Taxed where the supplier is established | [I] |
| Electronic, telecom or broadcasting service to private persons in other EU countries | Customer's country once EU-wide sales exceed €10,000; below, supplier's country | [C · S4] |
| Online event or online education for private persons (from 2025) | Customer's country | [I · S5] |
| Goods to a VAT-identified business in another EU country | Exempt intra-Community supply; the buyer taxes the acquisition (not for a seller under the Luxembourg franchise: excluded from the exemption, a Luxembourg supply under the franchise – lu-vat franchise.md) | [C · S3] |
| Goods to private persons in other EU countries above €10,000 EU-wide | Customer's country (OSS) | [C · S3, S6] |
| Goods exported outside the EU | Exempt export | [C · S3] |

| Buying (customer in Luxembourg) | Usual result | Status |
|---|---|---|
| Service from a business abroad (EU or not): software, ads, consulting | Taxed in Luxembourg; the buyer self-assesses (reverse charge), franchise users included | [C · S2, S9] |
| Hotel, restaurant, event ticket, taxi abroad | Taxed where it takes place; foreign VAT is a cost unless refundable there | [C · S10, S11] |
| Goods from another EU country | Intra-Community acquisition; franchise and art. 44 users only above the national EU-goods threshold (Luxembourg: lu-vat, franchise.md) | [C · S9] |

Then load the country skill (lu-vat) for the box, invoice wording and return; for a purchase invoice, lu-vat purchases.md.

## Related skills

lu-vat (Luxembourg boxes, invoices, franchise) · lu-tax-core (conventions).
