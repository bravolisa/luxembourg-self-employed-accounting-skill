# Home office

_Figures in this file: 2025–2026. The year files in `figures/` win if they differ._

## Contents
1. The test (and where it comes from)
2. Rented home
3. Owned home
4. Working from home as a self-employed person: address, landlord, permit
5. Proof file
6. Typical cases

## 1. The test

The only official home-office criteria are in ACD circular L.I.R. n° 105/2 (2021), written for **employees**. For self-employed people the legal test is the general one for mixed expenses (mixed-expenses.md). Use the circular as the benchmark and say so: "this is what ACD looks for". [C for employees · S2; I for self-employed]

| Criterion (circular 105/2) | Content |
|---|---|
| Use | Exclusively or almost exclusively for work: at least 90%. If private use is more than minor, **nothing** is deductible |
| Room | A separate room closed by a door; not a room crossed to reach other rooms |
| Size | Not disproportionate (e.g. the largest room as office while the living room is small) |
| Other office | Not recognised if the person has an office at the workplace |
| Evidence factors | Size of the home, furnishing (not like a living room, not unusually expensive), household size and situation |
| Allocation | Whole-home costs × office m² ÷ living area; cellar, garage, laundry room, attic excluded; office-only costs in full |
| Costs named | Rent, debit interest, depreciation, repairs and maintenance, heating, electricity; furniture depreciated, items up to €870 expensed |
[C · S2]

In practice for self-employed people [I]:
- A desk in the living room or bedroom gives no housing-cost deduction. Equipment and the business share of internet and phone stay deductible.
- Someone with an office or a dedicated coworking desk should not expect a home-office deduction unless the home office is separately needed.
- No flat rate exists; no rule requires a separate entrance.

## 2. Rented home

| Cost | Deductible share | Form line (2025) | Status |
|---|---|---|---|
| Rent | Office m² ÷ living area | 152: line 18 a) « bâtiments » (landlord's name and address required); 112: line 20 (buildings without VAT) | Share [I]; lines [C · S4, S5]; which line a home-office share uses [I] |
| Heating, water, electricity | Same share | 152: electricity 12, water 14, heating 15; 112: electricity 13, water 15, heating 16 | Share [I]; printed lines [C · S4, S5] |
| Service charges, home insurance | Same share | Other general expenses | [I] |
| Internet, phone | Share of business use, not area | Telephone line | [I] |
| Desk, chair, shelves used only for work | 100% | €870 items or depreciation (Form 113) | [C · S7] |

Example: 80 m² living area (cellar excluded), 10 m² office = 12.5%. Rent and charges €1,800 a month = €21,600 a year → €2,700. (`scripts/home_office_share.py`)

**Bills in a partner's name.** The employee circular lets an employee co-owner deduct the office share of costs « même lorsqu'un autre copropriétaire (par exemple, conjoint) a réglé les frais ». [C · S2] It does not establish the self-employed private-asset mortgage branch or a general joint-return ownership allocation. For unmarried partners or contracts in the partner's name: deduct only what you actually bear, keep proof of transfers and a written split, and put business contracts (internet) in your own name. [I]

**VAT** (normal regime): residential rent is normally VAT-exempt; VAT on energy or internet is deductible for the business share with an invoice in the user's name. [I]

## 3. Owned home

- No rent to yourself: « le loyer fictif versé par l'entreprise à l'exploitant … est non déductible et constitue un prélèvement privé ». [C · S1]
- Running costs (energy, charges, insurance, repairs, property tax): office share, as for a tenant. [I]
- Interest and depreciation: listed by circular 105/2 as home-office costs for employees; a co-owner depreciates only in proportion to his own share. [C for employees · S2]
- Mortgage capital is never an expense. [I]
- Double counting: owner-occupiers already deduct home-loan interest on the private side, within ceilings against the flat rental value (lu-income-tax-personal, home-and-rental.md). The same interest cannot be claimed twice. [C · S9, S10 for the private side; I for the interaction]
- **Business asset or not** (art. 20 LIR and its regulation of 11 August 1970): a part of a building that serves the business can be a business asset only if its value is more than **one fifth** of the whole building's value or more than **€100,000** (from tax year 2018); below both limits it stays private, even when it serves only the business. Above either limit, a part that by its nature serves the business is necessarily a business asset. Liberal professions: the same. A commercial owner with regular accounts whose business part is more than half may put the whole building in the business; liberal professions may not. [C · S56 arts 1–3, 6; S57] How the part's value is measured (with or without land, on which date) is not stated. [O]
- For one office room in a family home, both limits are often not reached, so the office stays private. [I] What can then be deducted for interest and depreciation is open: IT-O-03.
- Once in the business, the part stays there even if the conditions are no longer met – unless it becomes the owner's home again (art. 5), which is a withdrawal at operating value (art. 43 LIR). [C · S56; I for the withdrawal]
- If the office part is a business asset, a later sale or the end of the activity can create a taxable gain on that part: taxed at half the global rate after an allowance of €10,000, raised to €25,000 when the gain includes a gain on a building. [C · S11, S12]

For an audience: present running costs as safe ground; interest, depreciation and the asset question as "ask your adviser".

## 4. Working from home as a self-employed person

Two separate questions: may the business be at this address, and does the room pass the tax test. Registering the business at home does not make any part of the home deductible by itself. [I]

| Check | Finding | Status |
|---|---|---|
| Business permit | A fixed place of business needs « une installation matérielle appropriée à la nature et à la dimension des activités », equipment, effective management, regular presence and records kept there. The application asks for an operating address; proof of premises comes « au plus tard dans une deuxième étape ». | [C · S14, S15] |
| Home as the fixed place | BravoLisa's wiki: usually enough for intellectual services (IT, translation, accounting, coaching); proof by residence certificate or lease; not for workshops, shops or HORECA; a domiciliation address does not count | [P · S26 – the BravoLisa wiki's summary of what is accepted in practice; open point IT-O-05] |
| Commune zoning | Varies: Leudelange residential zones admit « services professionnels (sociaux et médicaux) … compatibles avec l'habitat »; Grevenmacher admits professional services only « en relation directe avec la fonction principale qui est l'habitation » | [C · S16, S17] |
| Rented home | The residential lease law applies « quelle que soit l'affectation stipulée dans le contrat de bail, sauf opposition justifiée par le bailleur en cas de réaffectation par le locataire en cours de contrat » (art. 1(2)); premises « affectés à l'exercice d'une profession libérale » fall outside its protection (art. 1(3) a) | [C · S13]; effect [I] |
| Flat in co-ownership | Building rules may restrict professional use | [I] |
| Insurance | Home insurance may not cover business equipment or visiting clients | [I] |

Landlord agreement [I]: not a tax requirement, but the landlord may object to a change of use during the lease. Advise written consent (email or short addendum) before registering the business at the address, and always before receiving clients. It also documents the business use.

## 5. Proof file

- [ ] Floor plan or room list with m²; living area without cellar, garage, laundry room, attic
- [ ] Photos showing the door and office furniture
- [ ] One sentence: used only for work; no other office (or why the home office is still needed)
- [ ] Lease or deed; landlord's yearly charges statement
- [ ] Bills and proof of payment for each cost claimed
- [ ] Calculation note: office m² ÷ living area, costs, result – same method every year
- [ ] If costs are shared with a partner: transfers and a written split

## 6. Typical cases

| Case | Deductible |
|---|---|
| Works at home, no clients, room used only for work | Reviewed office share of running costs + equipment; privately owned-home interest/depreciation remain IT-O-03 |
| Receives clients at home in a dedicated room | Same; business use easier to prove; landlord, commune and insurance matter more |
| Works at the kitchen table or in the living room | No housing costs; equipment and business share of internet and phone |
| Also has an office or coworking desk | Normally no home office; commuting deduction to that office |
[I]

The 2026-11-04 home research reconfirmed the **value-based** asset test and 2018 amendment/grandfathering; floor area alone is not that statutory test. Circular 105/2 addresses employees and does not settle IT-O-03 for a self-employed office remaining private. Private own-home versus rental schedules: lu-income-tax-personal/complex-home-and-rental-cases.md. [C · S56, S57, S2; O for IT-O-03]
