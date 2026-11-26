# VAT in the books – PCN accounts and journal entries

_Figures in this file: 2025–2026. The year files of the domain skills (lu-vat, lu-income-tax-business, lu-social-security) win if they differ._

For people who keep double-entry books with the Luxembourg PCN, and for BravoLisa's own bookings. Every account below exists in the PCN chart BravoLisa uses. [C · S21] The choice between accounts is BravoLisa's convention from its decision log, labelled [I]: the PCN would allow other sub-accounts. [B · S7, S8]

Which VAT is due or deductible is a VAT question: decide it first with lu-vat (purchases.md), then book it here.

## Contents
1. Accounts
2. Purchase entries
3. Assets, private use, payments, credit notes
4. Closing a VAT period
5. Link to the VAT return
6. Not covered

## 1. Accounts

| PCN | Name in the chart | Used for |
|---|---|---|
| 421611 | VAT paid and recoverable | Deductible input VAT, one line per invoice |
| 421612 | VAT receivable | Net refund due after a return |
| 421618 | VAT – Other receivables | Catch-all for other Luxembourg VAT receivables |
| 421811 / 46151 | Foreign VAT (receivable / payable) | VAT to reclaim from, or owed to, a foreign tax authority – the chart's own accounts for it [C · S21] |
| 461411 | VAT received | Output VAT, including VAT self-assessed under reverse charge |
| 461412 | VAT payable | Net VAT owed after a return |
| 6462 | Non-refundable VAT | VAT that is a business cost: reverse-charge VAT of a franchise user, the non-deductible pro-rata share on operating costs |
| 44111 | Suppliers | Amount owed to the supplier |
| 5131 | Banks and CCP: available balance | All bank accounts (the bank is identified by IBAN, not by sub-account) |
| 6413 | Software licences | Software and SaaS subscriptions |
| 6132 | IT services | Hosting, IT support, development bought as a service |
| 21213 | Software licences (acquired intangible asset) | Software that is capitalised |
| 106178 | Other acquisitions (owner's account, private withdrawals) | Private part of a purchase paid by the business |

Accounts [C · S21]. Usage is BravoLisa's convention: [B · S7, S8, S9].

## 2. Purchase entries

Amounts: €100 net, 17% VAT. Debits = credits in every entry.

| Case | Debit | Credit | Status |
|---|---|---|---|
| Luxembourg supplier, normal regime | Expense 100; 421611 17 | 44111 117 | [B · S8 §A] |
| Luxembourg supplier, franchise user (no deduction) | Expense 117 (gross, no VAT line) | 44111 117 | [B · S8 §B] |
| Reverse charge, normal regime, full deduction | Expense 100; 421611 17 | 461411 17; 44111 100 | [B · S8 §C.5] |
| Reverse charge, franchise user | Expense 100; **6462** 17 | 461411 17; 44111 100 | [B · S8 §C.6, S7] |
| Reverse charge, deduction proportion p = 40% | Expense 100; 421611 6.80; 6462 10.20 | 461411 17; 44111 100 | [B · S8 deduction proportion] |

- With reverse charge, **461411 always takes the full VAT**, whatever the deduction: 421611 = VAT × p, 6462 = VAT × (1 − p). [B · S8]
- Example: a €100 software subscription from a US company bought by a franchise user: Dr 6413 100, Dr 6462 17 / Cr 461411 17, Cr 44111 100. The user pays €100 to the supplier and €17 to the AED. [B · S8 pattern; account S9]
- Booking non-deductible VAT straight into the expense (Dr expense 117) is also seen in practice and balances; it is not BravoLisa's convention for reverse charge. [P · reviewed skill luxembourg-purchase-vat, Oct 2026]

## 3. Assets, private use, payments, credit notes

- **Assets:** non-deductible VAT is **capitalised** into the asset and depreciated with it, not booked to 6462. Example, franchise user, €1,000 + €170 Luxembourg VAT: Dr asset 1,170 / Cr 44111 1,170. With p = 40%: Dr asset 1,102, Dr 421611 68 / Cr 44111 1,170. [B · S7; S10]
- **Private line on a business invoice:** the whole gross goes to **106178**, not to an expense and not to 6462, and no asset is created. For an import of goods the import VAT is still owed: Dr 106178 117 / Cr 461411 17, Cr 44111 100. [B · S7] For a service or EU goods bought only for private use, EU rules treat the buyer as a private person, so there is normally no Luxembourg reverse charge – the supplier should have charged its own VAT; ask an accountant. [I]
- **Payment:** Dr 44111 / Cr 5131 for the amount paid. A payment never touches VAT; VAT is booked when the invoice is recognised. [B · S7] Not so for cash-basis VAT users and for advances received: there VAT is due when the money comes in (lu-vat, normal-regime.md). [C · lu-vat S24]
- **Credit note:** the same accounts as the original invoice, with opposite signs. [B · S8]
- An instalment or a later payment never creates a second VAT line for the same invoice. [I]

- **Depreciation (BravoLisa convention):** credited straight to the asset account (net method – the Luxembourg chart has no accumulated-depreciation accounts in class 2); the fixed-asset register keeps cost and accumulated depreciation for the notes. Expense accounts in the official chart (post to the leaves): 6321–6324 intangible assets (632 is a grouping; software and licences 6322); 63313 buildings and 63314 their fixtures (6331 subtree; land, 63311, only takes impairments); 6332 plant and machinery; 6333 other fixtures, tools and equipment. [C · S21] When depreciation starts in the first year: lu-income-tax-business, IT-O-20.

## 4. Closing a VAT period

| Step | Entry |
|---|---|
| Output VAT higher than input VAT | Dr 461411 (period balance) / Cr 421611 (period balance), Cr 461412 (difference) |
| Input VAT higher than output VAT | Dr 461411, Dr 421612 (difference) / Cr 421611 |
| Paying the AED | Dr 461412 / Cr 5131 |
| Refund received | Dr 5131 / Cr 421612 |

[B · S9] 421611 and 461411 carry each invoice; 421612 and 461412 are touched once per period, which keeps the gross VAT traceable to invoices.

## 5. Link to the VAT return

- The return wants the **full** input VAT of a purchase in its origin box and the non-deductible part in 094 or 095 (lu-vat forms/2025/vat-returns.md). In the books that full amount is 421611 + 6462 for that invoice, so each line must keep its VAT type. [I · lu-vat S3]
- Self-assessed VAT credited to 461411 goes to the buyer-liable boxes (741/742, 751/752, 711/712…), not to the sales boxes. [I]
- Private use (106178) is not input VAT and goes in no deduction box. [I]

## 6. Not covered

Advance payments to suppliers, suppliers on cash accounting (suspense account code not settled), imports paid at customs, foreign VAT to be reclaimed abroad (421811 in the official chart; BravoLisa has not chosen yet), and the depreciation entries. [O]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
