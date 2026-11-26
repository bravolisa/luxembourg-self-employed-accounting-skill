# VAT returns and boxes – 2025 forms (also valid for the 2026 periodic returns)

Box numbers come from the official eCDF forms: the 2025 annual return (DECA), the 2025 simplified annual return (DECAS) and the Q1 2026 quarterly return (DECT). Every field code in the 2025 eCDF field lists appears on these forms. [C · S2, S3, S13, S14]

The Q1 2026 quarterly form uses the same field codes as the 2025 lists [C · S14], and the 2026 annual (2026M1V003) and simplified (2026M1V002) field lists are identical to the 2025 ones (compared byte for byte, 26 Oct 2026): every box in this file holds for 2026. [C · S47]

Pick a box by the **legal category** of the transaction, not by the wording on the invoice. [I]

## Contents
1. Simplified annual return (franchise and art. 44 users)
2. Annual return – section I, turnover
3. Annual return – output tax by rate (II.A)
4. VAT owed as the buyer: intra-EU goods, imports, services from abroad (all four forms)
5. Input tax – annual return (III)
6. Monthly and quarterly returns
7. Annual return appendix – operating costs, private use of cars, stock
8. Where a sale goes – quick table
9. Where a purchase goes – quick table and worked example

## 1. Simplified annual return (TVA_DECAS 2025)

Who: franchise users and exempt (art. 44) users who must file (see franchise.md). Deadline: before 1 March of the following year. [C · S1, S6; deadline also in the form's comment 2]

| Box | Content (2025 form) | Status |
|---|---|---|
| 012 | Tax-exempted turnover = 481 + 482 – an eCDF rule, and the box is mandatory. Art. 44 users who must file have no box for their exempt turnover: open point VAT-O-15 | [C · S2, S47] |
| 481 | Supplies under the domestic SME scheme (art. 57bis) | [C · S2] |
| 482 | Supplies under the cross-border SME scheme (art. 57quater) – only with an EX number | [C · S2] |
| 450 | Services to customers VAT-identified in another member state, customer liable for VAT (total of 423 + 424) | [C · S2] |
| 423 | – of which not exempt in the customer's member state. **Must equal the total of the recapitulative statements** for the period | [C · S2] |
| 424 | – of which exempt in the customer's member state (rare for ordinary services) | [C · S2] |
| 801 / 802 (805–840) | Flat-rate farmers only | [C · S2] |
| B – E | VAT the user owes **as a buyer**: intra-EU goods (B), imports (C), services from abroad (D), goods where the buyer is liable (E). Same box numbers as section 4 below | [C · S2] |
| 076 | F. Total tax due = 802 + 056 + 407 + 410 + 768 | [C · S2] |
| — | Services sold to customers outside the EU: **no box** | [C · S2] |

The simplified return has **no input-tax section**: VAT a franchise or art. 44 user owes on purchases is paid and cannot be deducted. Never copy normal-return deduction boxes onto it. [C · S2]

The 2025 changes: field 482 added, field 471 removed, rules on 012 changed. [C · S10]

## 2. Annual return (TVA_DECA 2025) – section I, turnover

| Box | Content (2025 form, section I.B "Exemptions and deductible amounts", total 021) | Status |
|---|---|---|
| 013 | Intra-Community supply of goods to VAT-identified customers | [C · S3] |
| 202 | New means of transport to non-identified persons in another MS | [C · S3] |
| 014 | Exports of goods (art. 43(1)(a)(b)) | [C · S3] |
| 015 | Other exemptions (art. 43 and 60bis) | [C · S3] |
| 016 | Other exemptions (art. 44 and 56quater) | [C · S3] |
| 017 | Manufactured tobacco | [C · S3] |
| 481 | Supplies under the domestic SME scheme (art. 57bis); footnote 17: for a year with both regimes, the franchise-period turnover | [C · S3] |
| 482 | Supplies under the cross-border SME scheme | [C · S3] |
| 226 | Supplies under OSS / IOSS special schemes | [C · S3] |
| 018 | Triangular supplies, customer liable in the MS of destination | [C · S3] |
| 203 | Distance sales of goods taxable in another MS | [C · S3] |
| 423 | Services to customers VAT-identified in another MS, customer liable, not exempt there | [C · S3] |
| 424 | Same, exempt in the customer's MS | [C · S3] |
| **019** | **Other supplies carried out abroad** – e.g. services to customers outside the EU | [C · S3] |
| 419 | Inland supplies where the customer is liable | [C · S3] |
| 021 | Total exemptions and deductible amounts | [C · S3] |
| 022 | Taxable turnover = 012 − 021; eCDF also requires 022 = 037 (the sum of the taxable bases by rate) | [C · S3, S47] |

Every sale goes into section I.A by line of business, whatever its VAT treatment; amounts that also go in I.B (exempt, abroad, customer liable) are entered there as well and then subtracted, so only domestic taxable sales stay in I.A alone. [C · S24 art. 64(1); S3 footnote 17] Page 1 also has ticks for the special schemes: 491 OSS, 492 IOSS, 493 cross-border SME scheme; and the staff numbers 108–110. [C · S3] Line 007 is a free "other turnover" line: its caption 206 (at most 30 characters) and amount 007 go together. [C · S3, S47]

Section I.A splits the overall turnover (012): 001 goods made in-house, 002 other goods, 003 margin under the special schemes (arts 56ter-1, 56ter-2), 004 services, 005 sales of capital assets as ancillary transactions, 471 EU distance sales and e-services under the EU threshold (eu-vat, oss.md); then the assimilated supplies 008 (private use of goods, art. 13(a)), 009 (art. 13(b)), 010 (use of business assets for non-business purposes, art. 16(a)), 011 (free services for non-business purposes, art. 16(b)); and boxes 204 / 205 to tick the accounting basis ("on sales" / "on payments received"). [C · S3]

Amounts in 013, 018 and 423 must match the recapitulative statements for the period (comment 3). [C · S3]

Watch: for **services** to non-EU customers the correct box is **019**; 014 is for exported goods. [C · S3]

## 3. Annual return – output tax by rate (section II.A)

| Rate | Base box | Tax box |
|---|---|---|
| 17% | 701 | 702 |
| 14% | 703 | 704 |
| 8% | 705 | 706 |
| 3% | 031 | 040 |
| (16% / 13% / 7%, 2023 only) | 901 / 903 / 905 | 902 / 904 / 906 |
| Total | 037 | 046 |
[C · S3]

The rate rows show which rates the form accepts; they do not say which rate applies to a given supply. [I]

## 4. VAT owed as the buyer (II.B–F on normal returns, B–E on the simplified return)

The same box numbers are used on the monthly, quarterly, annual and simplified returns. [C · S2, S3, S13, S14]

| Transaction | 17% | 14% | 8% | 3% | Base / tax total | Exempt |
|---|---|---|---|---|---|---|
| Intra-EU acquisition of goods | 711 / 712 | 713 / 714 | 715 / 716 | 049 / 054 | 051 / 056 | 194 |
| Import of goods for business purposes | 721 / 722 | 723 / 724 | 725 / 726 | 059 / 068 | 065 / 407 (all imports) | 195 |
| Import of goods for non-business purposes | 731 / 732 | 733 / 734 | 735 / 736 | 063 / 073 | in 065 / 407 | 196 |
| Services from suppliers in another EU state, not exempt in Luxembourg | 741 / 742 | 743 / 744 | 745 / 746 | 431 / 432 | 436 / 462 | 435 (exempt in Luxembourg) |
| Services from suppliers established outside the EU | 751 / 752 | 753 / 754 | 755 / 756 | 441 / 442 | 463 / 464 | 445 |
| Services from suppliers established in Luxembourg, customer liable | 761 / 762 | – | – | – | 765 / 766 | – |
| Goods where the buyer is liable | 769 / 770 | – | 763 / 764 | – | 767 / 768 | – |
| **All services where the customer is liable** | | | | | **409 / 410** | |

[C · S2, S3, S13, S14]

- The 16% / 13% / 7% rows (911/912, 941/942, 951/952…) are for 2023 corrections only. [C · S3]
- Normal returns: total output tax **076** = 046 + 056 + 407 + 410 + 768 + 227, carried to 103. Simplified return: 076 is the total tax to pay. [C · S2, S3]
- These totals are sums of the rows, not extra transactions. [C · form formulas]
- Triangular deal with the Luxembourg business as the middle party: the acquisition goes in **152** (art. 18ter(2), subpar. 2) – reported, no tax due on it; the onward supply goes in 018 and on the recapitulative statement. [C · S3] This holds only if the end customer is designated as liable for the VAT and the recapitulative statement is filed; otherwise the acquisition is taxed in Luxembourg. [C · S24 art. 18ter(2)]
- Section II.B also takes goods supplied in Luxembourg in a triangular deal where the declarant, as end customer, owes the VAT (comment 4). [C · S3]
- Monthly and quarterly returns have no box for distance sales of goods taxed in another member state (annual 203), although the law asks for their total every period: open point VAT-O-16. [C · S24 art. 64(2); O]
- Installation or assembly abroad (art. 14(1)(b)) has no box of its own; 019 is the natural place. [I]
- Not covered here: tobacco (719, 729), the suspension regime (227). [O]

## 5. Input tax – annual return (section III)

| VAT origin | Stock entries (goods for resale or production) | Capital expenditure | Operating expenditure |
|---|---|---|---|
| Invoiced by other taxable persons | 077 | 081 | 085 |
| Due on intra-EU acquisitions of goods | 078 | 082 | 086 |
| Due or paid on imports | 079 | 083 | 087 |
| Due as customer under reverse charge (II.E and F) | 404 | 405 | 406 |
| Subtotal | 080 | 084 | 088 |

- 179 "Other": 090 (art. 13(b) application of goods), 092 (tax paid as joint guarantor, art. 48), 228 (suspension regime).
- **093** total input tax.
- **097** non-deductible input tax = **094** (input tax relating to supplies exempt under art. 44, 56quater, **57bis**, 57ter and 57quater) + **095** (non-deductible proportion under the **art. 50** pro-rata) + **096** (margin scheme).
- **101** adjustments = 098 (art. 53) + 099 (option to tax real estate, regulation of 7 March 1980) + 100 (other). A decrease takes a minus sign.
- **102** deductible input tax = 093 − 097 + 101. Section IV: 103 (tax due, from 076), 104 (from 102), 105 = 103 − 104 (minus sign = refund).

[C · S3]

How to use 094 and 095 [I · follows the form's structure]:
- Enter the **full** input VAT of a purchase in its origin box, then take out the non-deductible part in 094 or 095. Entering only the deductible part and also excluding the rest would cut the deduction twice.
- 094 is for VAT linked to exempt supplies, including art. 57bis: in a year with franchise months and normal months, VAT on purchases used for franchise-period supplies goes here.
- 095 is only for the art. 50 pro-rata. Private use is not pro-rata: enter only the business share of a mixed-use purchase's VAT in the first place.

## 6. Monthly and quarterly returns (DECM / DECT)

| Section | Boxes | Status |
|---|---|---|
| Turnover | 454 total sales/receipts (471 + 472); 455 private use and application (art. 13); 456 private use (art. 16) | [C · S14] |
| Exemptions | 457 intra-Community supplies of goods; 014, 015, 016, 017, **481**, 482, 226, 018, 423, 424, 019, 419 → 021; 022 taxable turnover | [C · S14] |
| Output tax | 701–706, 031/040 → 037/046; buyer-liable boxes as in section 4; 076 | [C · S14] |
| Input tax | 458 invoiced (art. 48(1)(a)); 459 intra-EU acquisitions (b); 460 imports (c); 090 application of goods (d); **461** reverse charge (II.E, F); 092; 228 → 093 | [C · S14] |
| Non-deductible | 094 (art. 44, 56quater, 57bis, 57ter, 57quater); 095 (art. 50 pro-rata) → 097 | [C · S14] |
| Result | 102 = 093 − 097; 103 / 104 / 105 | [C · S14] |

- Periodic returns have **no** capital/operating/stock split, no 096 and no adjustment section (098–101); those exist only on the annual return. Never reuse 458–461 on the annual return. [C · S3, S14]
- Box 481 exists on periodic returns too; footnote 7 repeats the annual rule (franchise-period turnover in a mixed year). [C · S14]
- Filling 457, 018 or 423 means a recapitulative statement is due (comments 3–5). Buying services from abroad does not by itself create one. [C · S14]
- Deadline: before the 15th of the month after the period (comment 2). [C · S14]

## 7. Annual return appendix (DECA only)

**A. Operating expenditure.** Columns: total (VAT included where applicable) | business % | business portion excluding VAT | business portion of VAT invoiced. Totals: **192** (excluding VAT) and **193** (VAT invoiced). [C · S3]

- Comment 5: the VAT column takes "exclusively VAT actually invoiced; please do not show VAT due in respect of intra-Community acquisitions of goods and/or VAT due under the reverse charge." [C · S3] So a reverse-charged subscription shows its net amount and 0 in the VAT column, even when the self-assessed VAT is a real cost (franchise, pro-rata). [I]
- Example rows: 9 accounting fees 269 / 270 / 271 / 272; 12 owner's travel and representation 283 / 284 / 183 / 184; 17 telecommunications 301 / 302 / 303 / 304; 18a rent with VAT 305 / 306 / 185 / 186; 30 office expenses 332 / 333; 37 advertising 347 / 348; 41 small assets written off under art. 34 LIR 355 / 356; 44 car expenses 190 / 191. [C · S3]
- For rows 9 and 18a the accountant's and landlord's names and addresses go in the names-and-addresses section (397–402). Comment 8: deduction of VAT on operating costs can be refused if the supplier's name is not given. [C · S3]
- Costs without their own row: the "Appendix to operational expenditures" (description 411, business amount excluding VAT 412, VAT invoiced 413, totals 414 / 415), carried to line 43 (361 / 362). [C · S3]

**B. Private use of business assets (art. 16(a))** – total **389**, carried to box 010 on page 1. [C · S3]
- Cars: book values 363–367; costs 381 / 382 (fuel 368 / 369, LPG 372 / 373, repairs 374 / 375, tyres 376 / 377, leasing 378 / 379, depreciation 380); km travelled 383, private km 384, private % 385; private share of costs excluding VAT **386** = 385 × 381. [C · S3]
- Comment 10: the taxable amount is the full cost. Comment 11: depreciation counts only if VAT on the car's purchase was recoverable. [C · S3]
- The form's printed cross-reference says "point I.A.3.c", but the matching box is 010 (I.A.2.c). [I]

The appendices are part of the return: « The annexed forms are to be filled in accurately and filed jointly with the return » (comment 2); only the detailed « Appendix to Operational expenditures » is optional (comment 9). Appendix sums: 389 = 386 + 388 (other business assets used privately: 387/388); car depreciation 366 = 380; staff 110 = 108 + 109. [C · S3]

**D. Balance items at year end** (VAT excluded): stock 168 / 181, work in progress 116 / 117, receivables from clients 118 / 119, advances received from clients 120 / 121. **F.** Annual accounts filed with the RCS: yes 998 / no 999. Section V asks for the phone number (237) and, if the books are kept outside Luxembourg, where (238). [C · S3]

**C. Stock entries** (goods for resale or production, not capital or operating expenditure; comment 12) – total 154, of which for resale 155. [C · S3]
- Domestic purchases: 771 (17%), 772 (14%), 773 (8%), 124 (3%), exempt 197.
- Intra-EU acquisitions: 776, 777, 778, 134, exempt 198.
- Imports: 781, 782, 783, 142, exempt 199. Comment 16: the import value includes duties, taxes and incidental costs up to the first destination.
- 150: purchases with no chargeable event for supplier or buyer. 151: goods bought abroad and not brought into Luxembourg.

## 7b. Filing through eCDF and the other VAT forms

- The eCDF VAT domain has nine forms: the monthly, quarterly, annual and simplified returns (DECM, DECT, DECA, DECAS), the recapitulative statements (eu-vat, reverse-charge-and-reporting.md) and **AN_TABACAM**. [C · S43]
- **AN_TABACAM** is an annual table of acquisitions of depreciable capital goods (cost with VAT, VAT, cost without VAT, subsidies, value to depreciate) and a depreciation table (opening value, acquisitions, sales, depreciation, closing value; total 613, of which non-business 615 and business 616). [C · S44] Who must file it is not stated: open point VAT-O-13.
- Every eCDF file names the **agent** sending it and each **declarer** (business), each with matricule, RCS number and VAT number; a business filing for itself is both. Write « NE » when there is no RCS or VAT number (e.g. a liberal profession has no RCS number). The Luxembourg VAT number is written as its 8 digits, without « LU ». [C · S42] **Filing for a client**: an agent with a professional LuxTrust account registers each client itself under « Déclarants », with identifiers obtained from the client; there is no confirmation step – « L'Etat présume l'existence d'un accord valable entre l'agent et le déclarant ». In a dispute the client asks the CTIE, in writing, to revoke the agent's rights. A private LuxTrust account files only for its holder. The right to upload XML files is requested on the access form, with the software's eCDF code. [C · S55]
- A part year (the business stopped) uses the same forms with the shortened period; FAQ « declaration year and liquidation year ». [C · S42; I for using the same form]
- Cross-checks eCDF applies to the annual return, among others: 012 = 001 + 002 + 003 + 004 + 005 + 471 + 007 + 008 + 009 + 010 + 011; 021 = the I.B boxes (013 … 419); 022 = 012 − 021 = 037; 076 = 046 + 056 + 407 + 410 + 768 + 227 = 103; 093 = 080 + 084 + 088 + 179; 102 = 093 − 097 + 101 = 104; 105 = 103 − 104 (a minus sign for a refund). [C · S47]
- The period boxes 233–236 hold the part of the year the registration was in force – a start during the year as well as a stop. [I · CTIE FAQ]
- An error-free file is filed at once; empty boxes cannot be completed later, only through a corrected return. [I · the CTIE XML documentation]
- The validation rules of every form are published under ecdf.b2g.etat.lu/ecdf/formdocs/<year>/<form>/<version>/ (RULESDOC). [C · S47]
- BravoLisa's eCDF interface is approved for the VAT domain (all nine forms) since 1 September 2026; it is **not** approved for annual accounts. [B · S45]

## 8. Where a sale goes – quick table

| Customer | Franchise user (simplified return) | Normal regime (annual return) |
|---|---|---|
| Luxembourg | 481 | Taxable turnover by rate (701…) |
| Business in another EU country (services, reverse charge) | 423 (+ recapitulative statements) | 423 (+ recapitulative statements) |
| Outside the EU (services) | no box | 019 |
| Goods exported outside the EU | not mapped on the simplified form [O] | 014 |

## 9. Where a purchase goes – quick table and worked example

| Purchase (17%, fully business) | Normal regime, monthly / quarterly | Normal regime, annual return | Franchise or art. 44 (simplified return) |
|---|---|---|---|
| Luxembourg supplier charging Luxembourg VAT | 458 | 085 (operating), 081 (capital), 077 (stock) | Nothing: the VAT is a cost |
| Service from an EU supplier, reverse charge | 741 / 742 + 461 | 741 / 742 + 406 (or 405 / 404) | 741 / 742, no deduction |
| Service from a non-EU supplier, reverse charge | 751 / 752 + 461 | 751 / 752 + 406 (or 405 / 404) | 751 / 752, no deduction |
| Goods from an EU supplier, taxable acquisition | 711 / 712 + 459 | 711 / 712 + 086 / 082 / 078 | 711 / 712 only when above €10,000 or opted in (franchise.md) |
| Import of goods, VAT declared on the return | 721 / 722 + 460 | 721 / 722 + 087 / 083 / 079 | 721 / 722 |
| Hotel, restaurant or event abroad with foreign VAT | No Luxembourg box; foreign VAT is not Luxembourg input tax | Same | Same |

Boxes [C · S2, S3, S14]; the choice of row for a given purchase [I].

Worked example – €100 software subscription from a supplier established in Ireland, 17%:
- Normal regime, quarterly: 741 = 100, 742 = 17; 461 = 17. Net effect 0, but both sides are reported.
- Same, annual return: 741 / 742 again; 406 = 17. Appendix: €100 in an operating-cost row or the line-43 detail; 0 in the VAT-invoiced column (comment 5).
- Franchise user (supplier outside the EU instead): 751 = 100, 752 = 17; included in 076; no deduction anywhere.
- Art. 50 pro-rata of 40%, quarterly: 741 / 742 = 100 / 17; 461 = 17; 095 = 10.20; deductible 6.80.

[I · applies the verified boxes]
