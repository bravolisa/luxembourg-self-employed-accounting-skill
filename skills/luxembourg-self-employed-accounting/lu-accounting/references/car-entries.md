# A car in the books – journal entries

Tax rules for the car: lu-income-tax-business car-and-travel.md (income tax) and lu-vat cars.md (VAT). This file gives the entries. Part of them rests on BravoLisa's decision log; the rest has no decision yet and is shown as a proposal. Account codes and names are those of the official chart. [C · S21] Amounts are invented.

## 1. Decided

| Event | Entry | Status |
|---|---|---|
| Buying a car that is a business asset – normal regime, 30,000 + 5,100 VAT | Dr 2232 Motor vehicles 30,000; Dr 421611 VAT paid and recoverable 5,100 / Cr 44111 Suppliers 35,100 | [B · S7; S10] |
| The same under the franchise | Dr 2232 35,100 / Cr 44111 35,100 – the VAT is part of the cost | [B · S7; S10] |
| Seller abroad invoices without VAT (new car, EU dealer on the VAT number) | Dr 2232 30,000; Dr 421611 5,100 / Cr 461411 VAT received 5,100; Cr 44111 30,000 | [B · S7] |
| Paying the invoice | Dr 44111 / Cr 5131 – a payment never touches the VAT or the asset | [B · S7] |
| Depreciation of the year | Dr 6333 (depreciation on other fixtures, tools and equipment, rolling stock included) / Cr 2232 – net method: no accumulated-depreciation account | [B · S7] |
| Fuel, 100 + 17 VAT | Dr 6036 Motor fuels 100; Dr 421611 17 / Cr 44111 117. Franchise: Dr 6036 117 | [B · S7; S8] |
| Repairs and servicing; tyres; garage rent | 612231; 612232; 611128 – BravoLisa sub-accounts under 61223 Rolling stock and 61112 | [B · S7] |
| Road tax | 6466 Motor-vehicle taxes, no VAT line | [B · S7; S27] |
| Lease instalment, 500 + 85 VAT | Dr 6112 (official leaf 61123 Rolling stock) 500; Dr 421611 85 / Cr 44111 585 | [B · S7; S8] |
| A wholly private line on a business invoice | The whole gross to 106178 (vat-entries.md §3) | [B · S7] |
| Commuting flat deduction; the kilometre record | Not booked: computed on the tax return | [B · S27] |

- **Depreciation period:** the design uses five years for a passenger car and gives no source; Guichet's example for vehicles is four years (lu-income-tax-business car-and-travel.md §9). [B · S27; reported to the owner]
- **Form 152 with VAT included:** the deductible VAT paid on the car is an expense of the year it is paid; the price without VAT comes in through depreciation. [B · S7]

## 2. Not decided yet – proposals

No decision exists for these. The proposals use accounts the official chart names. [I – proposal; needs a BravoLisa decision · ACC-O-08]

| Event | Proposed entry |
|---|---|
| Private share of the year's car costs and depreciation (30% private) | Dr 106166 Car / Cr each cost account for 30% of its balance (6036, 612231, 612232, 61412, 6466, 6333) |
| VAT on the private use (normal regime, full deduction) | Dr 106166 Car / Cr 461411 VAT received – base: lu-vat cars.md §6 |
| Private car used for business trips, costs paid privately | Dr the cost accounts for the business share / Cr 10629 Business share in private expenses |
| Car insurance | 61412 Rolling stock |
| Electricity for charging the business car | With fuel (6036), so that it reaches the car block of Forms 112 / 152 |
| Parking on a business trip, tolls | 615211 (the owner's travel), outside the car block |
| Higher first lease instalment, regular accounts | Dr 481 Deferred charges, released to 61123 over the lease |
| Sale of the car | Dr 4011 Customers / Cr 74422 (gain) or 64422 (loss) for the price, Cr 461411 for the VAT; then the book value: Dr 74421 or 64421 / Cr 2232 |
| Car taken into private property | Dr 106172 Private car / Cr 74422 for the value of the day, Cr 461411 for the VAT; the book value as for a sale |

Example of the first two lines (invented): fuel 2,000, repairs 800, tyres 400, insurance 900, road tax 200, depreciation 6,000; 30% private. Private share of the costs: Dr 106166 3,090 / Cr 6036 600, 612231 240, 612232 120, 61412 270, 6466 60, 6333 1,800. VAT on private use: 30% × (2,000 + 800 + 400 + 6,000) = 2,760 × 17% = 469.20 → Dr 106166 469.20 / Cr 461411 469.20. A franchise user has only the first entry, with amounts including VAT.

Not designed at all: a car loan, a trade-in, a deposit before delivery, a finance lease shown as an asset, the VAT adjustment after a change of regime. [O · ACC-O-08]

## 3. Not counting the private share twice

- One kilometre share, used once. The current design computes the business share of the car block on the tax form, outside the ledger. [B · S27] So either no private-share entry is posted and the split happens on the form, or the entry is posted and the form starts from the total costs before it. Doing both takes the private share out twice. [I]
- Home-to-office km are never in the business share: they go with the private share, or the costs are added back on the return, and the flat commuting deduction replaces them (lu-income-tax-business car-and-travel.md §3). [C for the tax rule; I for the entry]
- If home-to-office km turn out to be business km for VAT (lu-vat VAT-O-20), the VAT private share differs from the income-tax one and the VAT base needs its own percentage. [I]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
