# Car and business travel

_Figures in this file: 2025–2026. The year files in `figures/` win if they differ._

## Contents
1. The rule
2. Which trips count
3. Commuting deduction
4. Car costs and km record
5. Car cases compared
6. Simplified methods (€0.30/km, per diem) – status
7. Business trips other than by car
8. VAT on cars
9. How many years, and what reduces the cost
10. Leasing
11. Selling the car, taking it private, stopping
12. Electric car: subsidy and charging

## 1. The rule

« les frais de voiture subis par le chef d'entreprise ne seront déductibles que dans la limite de l'utilisation professionnelle de la voiture » – the owner proves the business use, « par exemple sur base du carnet de route ». [C · S1]

## 2. Which trips count

| Trip | Treatment | Status |
|---|---|---|
| Home → fixed office or coworking | Commuting: flat deduction (section 3), not car costs | [C · S4, S5] |
| Home office → client, supplier, training, bank | Business trip | [I] |
| Office → client → office | Business trip | [I] |
| Shopping, school run, holidays | Private | [I] |

Never claim the same km as both commuting and business trips. [I]

## 3. Commuting deduction (tax year 2025)

- Forms 112 (lines 58–61) and 152 (lines 54–57) carry the « Déduction forfaitaire des frais de déplacement entre le domicile et le lieu d'activité »: units × €99; « les 4 premières unités ne sont pas prises en compte et la déduction est limitée à 2 574 € ». [C · S4, S5]
- Units measure the distance between the home commune and the work commune, whatever the means of transport. [C · S6] The table of units between communes was updated from tax year 2023 (ministerial regulation of 6 March 2023, after two commune mergers). [C · S55] A pair not listed in the table counts as 30 units. [I · BravoLisa app reference data]
- Maximum: 26 counted units = €2,574 – amounts set by the regulation of 21 December 2012, applying from tax year 2013. [C · S54; S8]
- Home is the only place of work → no commuting deduction. [I]
- Legal basis: art. 46 n° 9 LIR and the grand-ducal regulation of 28 December 1990 (amended 1999, 2001, 2012). Commuting costs reduce profit **only** through this flat deduction. [C · S28 art. 46 n° 9; S50 art. 1]
- It covers all home–work travel costs; actual home–work costs already booked (fuel, car costs for those km) **must be added back** to profit. Business trips stay at actual cost – keep home–work km out of the car's business share. [C · S50 art. 3]
- It may not create or increase a loss: it is cut to the extent it would produce one. [C · S28 art. 46 n° 9; S51]
- Part of the year taxable: 1/12 per month, a started month counting as a full one. Several businesses: the place farthest from home, but each business gets its own deduction when profits are determined separately. A move or a new place counts only if the units go up, from the month of the change. [C · S51]
- Calculator: `scripts/commuting_deduction.py --units <n>`.

## 4. Car costs and km record

Deductible = car costs in the form's car block × business km ÷ total km + direct trip costs.

| Cost (car block, Forms 112 lines 47–57 and 152 from line 43) | Split by business share? |
|---|---|
| Fuel and lubricants | Yes |
| Repairs and maintenance | Yes |
| Tyres | Yes |
| Leasing, rental | Yes |
| Garage rent | Yes |
| Taxes and insurance | Yes |
| Then: total km in the year, business km, % → deductible car costs | |
[C · S4, S5]

Outside the block: depreciation via Form 113 (business-asset car only; exclude the private share [I]); parking and tolls on business trips in full with receipts [I]; fines never (art. 12 n° 4 LIR) [C · S3].

Example: costs €4,500; 20,000 km, 6,000 km business = 30% → €1,350; + €150 parking = €1,500. (`scripts/car_km_share.py`)

When a km record is needed: any time car costs are claimed – the forms ask for total and business km. [C · S4, S5] Not needed when only the commuting deduction, or only parking and tolls with receipts, are claimed. [I] A car used 100% for business still needs evidence (e.g. a second private car). [I]

What the record shows: date, from → to, client or purpose, km; odometer on 1 January and 31 December (dated photo). Spreadsheet, calendar or GPS app is fine if kept as you go. [I]

## 5. Car cases compared

Framework: assets that « de par leur nature, sont destinés à servir à l'entreprise » are business assets (art. 19(1) LIR); only operators with regular accounts may opt to add other assets, and « le choix une fois fait ne peut être modifié arbitrairement » (art. 19(2)). No Luxembourg percentage threshold for mixed-use cars was found. [C · S3] For a car that stays private, a first-instance court held in 2016 that the costs count only in the proportion of the actual business use, which the taxpayer must prove; the ACD director had asked for receipts of the actual costs (not binding in other cases). [I · S67] For a **liberal profession** there is no option: only assets that by their nature serve the profession and are directly linked to it belong to the business (art. 93(2) LIR). [C · lu-income-tax-personal S2]

| Case | Treatment | Status |
|---|---|---|
| 1. Private car, occasional business trips | Running costs × business km share; parking and tolls in full; no depreciation. Car-loan interest stays a private special expense (within the ceiling shared with insurance premiums – lu-income-tax-personal, special-expenses.md) | Form [C · S4, S5]; ceiling [C · lu-income-tax-personal S4]; depreciation [O] |
| 2. Private car used mostly for business | Probably a business asset by nature: depreciation via Form 113, private share excluded | [I · S3] |
| 3. Car bought for the business | Business asset; straight-line depreciation, or declining balance up to 3× the straight-line rate and max 30% (art. 32(3)); loan interest a business expense; private use excluded; gain or loss on sale is business income (sections 9 and 11) | Depreciation [C · S3]; rest [I] |
| 4. Leased car, lease in own name | Lease payments in the car block × business share; no depreciation – unless the lessee counts as the owner for tax (section 10) | [C · S4, S5] |
| 5. Car owned before the business started | Stays private (case 1) or becomes a business asset. If it is brought in, it enters at its operating value on that day (« valeur d'exploitation »: the price a buyer of the whole business would give it), and that value is its cost for depreciation (arts 43(1), 27(1) LIR) | [C · lu-income-tax-personal S2] |
| 6. Electric car | Same cases; home charging: business share of kWh, best from a separate wallbox meter. Zero-emission cars were an exception to the car exclusion of the investment tax credit (commercial activities only). State purchase subsidy: section 12 | Charging [I]; credit [C · S8, check current Form 800] |
| 7. Partner's car | Only the costs you bear | [I] |
| 8. Business-asset car, normal VAT | Input VAT deducted in full with the private use declared in appendix B (box 010), or only the business share deducted – section 8; the VAT on private use is not deductible for income tax | [I] / [C · S3] |

No CO2- or price-based limit on depreciating or deducting a sole trader's car was found in the LIR: art. 32bis is special depreciation for environmental and energy-saving assets, and CO2 rules exist only for employees' company cars (benefit in kind). The only price cap found is in the investment tax credit (first €50,000 per vehicle). [C · S28, S44, S33]

For an audience: most people are case 1, and it is simple. Anyone buying or leasing a car mainly for the business should decide the setup with an adviser before signing. Private use of a business car by a sole trader is taken out by the kilometre share: the private km share of the running costs stays out of Form 112 / 152 (lines 55–57 / 51–53) and the private share of depreciation out of Form 113. [C · S4, S5, S53] A private withdrawal is valued at its operating value (art. 43(1) LIR) [C · lu-income-tax-personal S2]; the employees' flat benefit-in-kind rates are not for sole traders. [I]

## 6. Simplified methods – status

| Method | Status |
|---|---|
| Actual costs × business km share | Standard; built into the forms [C · S4, S5] |
| €0.30/km instead of actual costs | **Open, leaning no.** The rate is a tax-free mileage allowance an employer may pay an employee for business trips in the employee's own car, taken from the rules for State staff. The Government-in-Council regulation of 13 December 2024 behind it was repealed from 1 February 2026, and the text that sets the kilometre allowance for 2026 was not found – the rate is not confirmed for 2026. [C · S81, S80 for the repeal; O for 2026] No source applies it to sole traders and the forms have no line for it: their car block takes only actual costs × business km [C · S4, S5]; the regulation itself was not opened [I · S18, a firm's summary; O for self-employed] |
| Employee-style per diem for the owner's own trips | **Open.** No ACD text settles it – IT-O-07 [O · S27] |
| CO2-based limits on car costs | None found for Luxembourg income tax; the rules that show up in searches are Belgian [I] |

## 7. Business trips other than by car

Tickets, hotels and similar costs of a business trip: actual costs with receipts, Form 152 line 11 / Form 112 line 12 (« Frais de voyage et de représentation du patron »). [C for the lines · S4, S5; I for the treatment] Meals and per diem: not settled (section 6). [O]

## 8. VAT on cars (normal regime)

Luxembourg has no special exclusion of VAT on cars. Two routes: deduct the VAT in full and declare the private use as a taxable supply in appendix B (box 010) – the route the annual return is built for – or deduct only the business share from the start, with nothing to declare. Invoices in the user's name. Details – the three ways to treat the car, buying in Luxembourg or abroad, leasing, running costs and charging, selling: lu-vat, cars.md. [C · lu-vat S24 arts 16(a), 28(1)(c); the choice: Court of Justice, lu-vat cars.md §2] The AED states the base of the private use as the private % of the car costs whose VAT was deductible (circular 807, written for cars made available to employees). [C · lu-vat S46; I for sole traders] Luxury spending is refused: the courts have applied art. 54 of the VAT law to prestige cars (lu-vat cars.md §7). [C · lu-vat S24 art. 54] Under the franchise: no VAT deduction at all; VAT is part of the cost. [C]

On the annual VAT return the private use of a business car is declared in appendix B: total and private km, private percentage, and the private share of the car costs excluding VAT (box 386, carried via 389 to box 010). Depreciation counts there only if the VAT on the car's purchase was recoverable; insurance, road tax and garage rent are not among appendix B's cost lines. [C · official 2025 annual VAT return, see lu-vat forms/2025/vat-returns.md §7] Whether home-to-office km are private km for VAT is not settled: count them as private km, as for income tax (lu-vat VAT-O-20). [O]

## 9. How many years, and what reduces the cost

- **No legal table.** « La durée usuelle d'utilisation se détermine compte tenu du genre et des conditions d'utilisation de l'immobilisation considérée. » [C · S3 art. 32]
- **Four years is the usual figure for a car.** Guichet gives examples of usual practice: « bâtiment industriel : 20 ans, mobilier de bureau : 10 ans, véhicules : 4 ans », and uses four years for a car in its leasing examples. It is an example published by the State, not a binding rate: another period is possible if it matches how long the car is really kept and used. [C · S1, S69]
- **Used car:** the useful life still left when it is bought. [I · S3 art. 32]
- **Residual value:** deducted only « le cas échéant » – not needed in the usual case. A car depreciated to zero and sold later: the whole price is a gain (section 11). [C · S3 art. 32; I]
- **First year:** pro rata, or the ACD's tolerance of a full year for a purchase in the first half of the year and half a year in the second half (depreciation-and-investment-credit.md). [C · S58]
- **Declining balance:** with four years the 30% cap applies. [C · S3 art. 32(3)]
- **A State subsidy for the car** (section 12) reduces the amount depreciated: Form 113 depreciates the price less the « subventions reçues ». [C · S53]
- The length of a lease is not the useful life. [C · S73]

## 10. Leasing

Luxembourg has no leasing law of its own: art. 19(1a) LIR only allows a regulation, and none was made. The ACD's circular of 4 January 1974 declares the principles of the German Federal Fiscal Court « valables également au Grand-Duché de Luxembourg ». [C · S3 art. 19(1a); S74; S71]

- **Ordinary lease** (the usual car lease, car handed back at the end): the leasing company keeps the car. The lessee deducts the rents × business km share in the car block (section 4); no depreciation. [C · S70; S4, S5; I for the km share]
- **Finance lease** (fixed term in which the rents pay the whole price plus financing): who owns the car for tax –

| Contract | Car stays with the leasing company if | Car counts as the lessee's if |
|---|---|---|
| No purchase option | the basic term is 40% to 90% of the usual useful life | the basic term is under 40% or over 90% |
| Purchase option | the term is 40–90% and the option price is not below the straight-line book value at that date | the term is under 40% or over 90%, or the option price is below that value |

  [C · S69, S74; S71] With four years for a car, a 36-month lease is 75% of the useful life: the car stays with the leasing company unless the option price is below 25% of the price. [I] Guichet's page words the option-price test the wrong way round in one bullet; its own example and its finance-lease page say "below". [I]
- **Lessee counted as the owner:** the car is entered at the leasing company's cost and depreciated (Form 113, business share); of each rent only the interest and cost part is an expense. [C · S69; S71]
- **Buying the car at the end of an ordinary lease:** from that day it is the lessee's own asset at the option price – for a commercial business it « fera obligatoirement partie de l'actif net investi ». [C · S72]
- **Higher first rent:** « généralement fiscalement déductible par le locataire ». Whether at once or spread over the lease is not said: on the receipts-and-expenses method when paid, with regular accounts spread over the lease – always × the business km share. [C · S74; I – medium · IT-O-28]
- **Investment tax credit:** under a finance lease in the sense of the regulation of 29 October 1987 the lessee, not the leasing company, claims it; not under an operating lease. For a car the other conditions stay: commercial business, zero-emission car, first €50,000. [C · S73, S72; S3 art. 152bis]
- In doubt, ask the ACD before signing – Guichet advises it. [C · S74]
- VAT on a lease, also from a foreign lessor: lu-vat cars.md §4.

## 11. Selling the car, taking it private, stopping

For a car that is a business asset. No article names « the sale of a fixed asset »: the gain falls into profit through the profit formula. [I – high · S3 arts 18, 23]

| Event | Regular accounts | Receipts-and-expenses method |
|---|---|---|
| Sale | Gain or loss = price without VAT − book value; part of the year's profit [I – high] | The price is a receipt; the cost not yet depreciated is deducted at that moment [C · S61, S21; I for the receipt] |
| Trade-in for a new car | A sale of the old car at its value, then a purchase of the new one [C · S3 art. 22] | The same [I] |
| Car taken into private property | Withdrawal at the operating value of that day; the difference to the book value is profit [C · S3 arts 42, 43; I] | Added to profit the same way [C · S61; I] |
| Business stopped or sold | The car kept privately counts at its estimated sale value; part of the cessation gain [C · S3 art. 55] | As if the business had moved to regular accounts just before [C · S61] |

- **The private km share does not reduce the gain:** a movable asset belongs to the business as a whole, and Form 113 writes the book value down by the full depreciation before the private share is taken out. Not stated in any text. [I – medium · S53 · IT-O-27]
- A car brought in from private property and taken out again within two years: the withdrawal value cannot be lower than the contribution value less normal depreciation. [C · S3 art. 43]
- A car that stayed private: its sale is not business income; a gain is taxable only if the car is sold within six months of buying it. [I – high; C · S3 art. 99bis]
- Replacement relief does not help: art. 54 covers buildings and non-depreciable assets; art. 53 covers a car destroyed or stolen, with regular accounts only. [C · S3 arts 53, 54]
- Example (invented): bought for €40,000 without VAT, depreciated over four years, sold after three years for €15,000 without VAT. Book value €10,000 → gain €5,000 in the year of the sale. [I]
- VAT on the sale or the withdrawal: lu-vat cars.md §8.

## 12. Electric car: subsidy and charging

**State purchase subsidy** (contract signed between 1 October 2024 and 30 June 2026): [C · S75]

| Car | Subsidy |
|---|---|
| New pure electric car using up to 160 Wh/km | €6,000, at most 50% of the cost without VAT |
| New pure electric car using up to 180 Wh/km, or up to 200 Wh/km with at most 150 kW | €3,000, same cap |
| Used pure electric car at least 3 years old | €1,500; keep it 24 months |
| Plug-in hybrid | None |

- A new car must be kept 36 months. A natural person applies on MyGuichet after registration; a lessee may apply if the owner waives the aid. The page makes no difference between a private car and a business car of a self-employed person. [C · S75; I for the business car]
- **From 1 July 2026:** the law prolonging the scheme was voted (announced 11 November 2026); the published text was not read – lu-tax-core watch list W-19. [C · S76 for the announcement; O]
- A private charging point has its own aid for natural persons. [C · S79]
- **Income tax:** for a business-asset car the subsidy reduces the cost that is depreciated – it is not income of the year. The ACD says the same of a subsidised photovoltaic installation: the capital subsidy « diminue le prix d'acquisition ». [C · S53; I by analogy · S78] The investment tax credit is computed on the price less subsidies. [C · S33] A subsidy paid in a later year, or repaid because the car is sold too early: no text. [O · IT-O-29] For a private car the subsidy changes nothing. [I]
- **Charging at home:** the business share of the electricity, from the kWh charged (wallbox meter or the car's charging log) × the business km share; no official text on the proof. [I]
- VAT on charging: lu-vat cars.md §5.
