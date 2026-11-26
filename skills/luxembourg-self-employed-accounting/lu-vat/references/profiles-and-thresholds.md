# VAT profiles and thresholds

_Figures in this file: 2025–2026. The year files in `figures/` win if they differ._

## The four profiles

| | Normal regime | Franchise (art. 57bis) | Exempt activity (art. 44) | Cross-border SME (EX) |
|---|---|---|---|---|
| Who | Above the franchise threshold, or by choice | Luxembourg turnover ≤ €50,000 | Activity exempt by nature, at any turnover (see exempt-art44.md) | Opted in to be exempt in other EU countries; EU-wide turnover under the EU ceiling (eu-vat, sme-cross-border.md) |
| LU VAT number | Yes | Yes – but charges no VAT | No by default; must register before the first reverse-charge purchase or EU B2B service sale | EX-suffix identification |
| Charges VAT | Yes | No – invoice carries the art. 57bis mention | No – art. 44 mention | Exempt in the other countries that offer a franchise |
| Deducts input VAT | Yes, for taxed activity | No – VAT is a cost | No | Follows the home profile |
| Returns | Annual, quarterly or monthly + annual | Simplified annual return when required (see franchise.md) | None unless self-assessing; then simplified return | Quarterly EU-turnover report |

Status: [C · S6] for the table as verified internally against Guichet and pfi.public.lu; EX details [C · S1].

## Thresholds (amounts excluding VAT)

| Threshold | Amount | Test | Effect | Status |
|---|---|---|---|---|
| Franchise | €50,000 | Luxembourg turnover, current year and previous year | Above it, franchise lost (see tolerance); a year above it also excludes the next calendar year | [C · S1; S24 art. 57bis(1), (6)] |
| Franchise tolerance | €55,000 (+10%) | Current year | ≤ €55,000: franchise holds until 31 Dec, normal regime from 1 Jan. > €55,000: normal regime from the day after the crossing sale | [C · S1] |
| EU SME scheme | EU ceiling – eu-vat, sme-cross-border.md | EU-wide turnover | Above it, EX exemption ends; final declaration within 15 working days | [C · S1, S6] |
| Intra-EU goods purchases (franchise, art. 44) | €10,000 | Current and previous year | Above it, Luxembourg VAT due on EU goods purchases (see franchise.md); an option to be taxed covers two calendar years | [C · S15 art. 2(2)(b); I · S7 detail] |
| EU distance sales and B2C e-services | EU threshold – eu-vat, oss.md | EU-wide, per year | Above it, VAT of the customer's country (OSS) | [C · S6] |
| Filing frequency | €112,000 / €620,000 | Prior year turnover, or intra-EU purchases of goods + services received | Annual / quarterly / monthly; the AED decides at year end | [C · S6] |
| Cash-basis VAT (encaissements) | €500,000 | Previous year's Luxembourg turnover (as for the franchise, art. 25(2)) not above it; on request | Applies from 1 January after the request, for at least five years; ends on 31 December of the year the condition stops being met | [C · S24 art. 25] |

## How the franchise turnover is counted

- Only supplies whose **place of supply is Luxembourg** count. [C · S1: « dont le lieu se situe à l'intérieur du pays sont pris en compte »]
- Services to **business customers** abroad, in the EU or outside it, do not count: they are taxed where the customer is (art. 17(1)(b)). [C · S1, S24]
- Services to **private customers** count whenever the general rule places them in Luxembourg (art. 17(1)(c)) – also when the private customer lives outside the EU. They do not count when a special rule taxes them elsewhere, mainly [C · S24 art. 17(2)]:
  - for private customers **outside the EU**: the services listed in art. 17(2) 8° – consultants, engineers, lawyers, accountants and similar, data processing and information, advertising, rights and licences, staff hire, rental of movable goods other than vehicles, banking and insurance;
  - electronic, telecom and broadcasting services: taxed where the private customer lives (art. 17(2) 7bis); for EU customers only above the EU-wide threshold (art. 19quater; eu-vat, oss.md);
  - online events and education streamed to private customers: taxed where the customer lives (art. 17(2) 4° b), since 2025);
  - services connected with property abroad (art. 17(2) 2°).
- Goods exported from Luxembourg do count: exports exempt under art. 43(1)(a)–(b) are part of the franchise turnover. [C · S24 art. 57(2)(b); S6]
- Among art. 44 exempt supplies only property operations (art. 44(1) f), g)), financial operations (c), d)) and insurance (i)) count, unless ancillary; medical care, teaching and the other art. 44 supplies do not. Sales of the business's own capital assets never count. [C · S24 art. 57(2)]
- It is turnover, not cash received: a supply made this year counts this year even if paid next year. Example: €61,000 of qualifying supplies, of which €12,000 paid next January, is €61,000 for this year. [I · S6]
- It is not "income": people often say "I passed €50k income"; check what was invoiced for Luxembourg-place supplies.

The EU-wide ceiling of the EX scheme (eu-vat) is a different pot: it adds turnover in all member states. [C · S1]

## Company directors (board members)

- A board member of a Luxembourg SA who does not act under their own responsibility and bears no economic risk is **not a taxable person** for the board fees (CJEU C-288/22; district court 22 Nov 2024). The AED applies this beyond SAs, to company directors in general, but each director must check the criteria for themselves. [C · S41]
- Directors who charged VAT in earlier years could regularise it; they repay the VAT to the companies, which correct their own deduction. [C · S41]
- So a director's fee is usually not a franchise question at all. Income-tax side (20% withholding, liberal-profession income): lu-corporate-tax, owner-manager-pay.md. [I]
