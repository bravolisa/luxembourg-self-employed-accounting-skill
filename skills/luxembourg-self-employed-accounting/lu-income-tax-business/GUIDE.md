# Luxembourg business income tax

_Figures in this file: 2025–2026. The year files in `references/figures/` win if they differ._

Follow lu-tax-core for triage, labels and answer shape. **[C]** Confirmed, **[I]** Interpretation, **[P]** Practice, **[O]** Open, **[B]** BravoLisa convention; source ids in [references/sources.md](references/sources.md).

## Before answering

1. **Tax year** → [2025](references/figures/2025.md), [2026](references/figures/2026.md), known changes for [2027 and later](references/figures/2027.md) (never for current answers), [2023–2024 history](references/figures/history-2023-2024.md) for assets bought then; form lines in `references/forms/<year>/`.
2. **Category**: commercial or craft profit (art. 14 LIR, Form 110) or liberal-profession profit (art. 91 LIR, Form 100 + 152)?
3. **Method**: regular accounts (art. 18(1)), accrual without regular accounts (Form 110 route B), or simplified receipts and expenses (art. 18(3))?
4. Topic facts: rented or owned home; private or business car; VAT profile (franchise users carry VAT as a cost).

## Where to look

| Question | Read |
|---|---|
| Which category, which forms, where profit lands in Form 100 | [categories-and-forms.md](references/categories-and-forms.md) |
| Which profit method, the €100,000 bookkeeping test, cash vs accrual timing, stock on the cash method, switching method (catch-up) | [profit-methods.md](references/profit-methods.md) |
| Is a cost deductible? Mixed private/business costs, fines; the optional flat rate for a side activity | [mixed-expenses.md](references/mixed-expenses.md) |
| Home office (rented, owned, working from home, landlord, permit) | [home-office.md](references/home-office.md) |
| Car: kilometres, logbook, commuting, business trips, per diem; depreciation period, leasing, selling the car, the electric-car subsidy | [car-and-travel.md](references/car-and-travel.md) |
| Depreciation, €870 write-off, investment tax credit | [depreciation-and-investment-credit.md](references/depreciation-and-investment-credit.md) |
| A phone, laptop, software or other equipment bought for the business – step by step | [equipment.md](references/equipment.md) |
| Putting equipment into your own company (contribution in kind or sale): gain, cessation of the sole trade, the art. 59 roll-over, the shares received, renting instead | [contribution-to-a-company.md](references/contribution-to-a-company.md) |
| Municipal business tax (ICC) | [municipal-business-tax.md](references/municipal-business-tax.md) |
| VAT in the income-tax figures (gross/net, VAT paid to the AED) | [vat-in-income-tax.md](references/vat-in-income-tax.md) |
| A specific line of a form | [forms/2025/form-152.md](references/forms/2025/form-152.md) · [form-112.md](references/forms/2025/form-112.md) · [form-110.md](references/forms/2025/form-110.md) · [form-113-and-800.md](references/forms/2025/form-113-and-800.md) |
| What is not settled | [open-questions.md](references/open-questions.md) |

CCSS contributions in the income-tax return (special expenses, dependency insurance, Mutualité reimbursements): lu-social-security, `certificate-and-tax.md`.

## Calculators

Use the scripts for arithmetic; they return JSON and show their working. They apply the rules in the references and do not decide eligibility.

- `python scripts/commuting_deduction.py --units 18 [--year 2026]` → commuting flat deduction (figures from lu-tax-core `data/tool-figures.json`).
- `python scripts/car_km_share.py --costs 4500 --total-km 20000 --business-km 6000 --direct 150` → deductible car costs.
- `python scripts/home_office_share.py --office-m2 10 --living-m2 80 --costs 21600` → office share of housing costs.

## Rules people get wrong most often

- Mixed private/business costs are private by default; only a share split by "critères objectifs et retraçables" is deductible, and the business owner carries the proof. [C · S1]
- A home office: the only official criteria (ACD, for employees) require a separate room with a door, used at least 90% for work, and no office elsewhere. Use them as the benchmark for self-employed people too, and say so. [C for employees · S2; I for self-employed]
- An owner cannot charge rent to himself; « le loyer fictif … constitue un prélèvement privé ». [C · S1]
- Car costs: the 2025 forms ask for total km and business km; anyone claiming car costs needs a km record. [C · S4, S5]
- Commuting to a fixed place of business is not a business trip: €99 per distance unit, first 4 not counted, at most €2,574 (2025). Working only from home: no commuting deduction. [C · S4, S5]
- €0.30/km is an employer-to-employee allowance; using it instead of actual car costs is not confirmed for self-employed people. [O]
- The €870 rule is an immediate write-off for small items, not a maximum purchase price: dearer assets are depreciated. [C · S7]
- Fines are never deductible (art. 12 n° 4 LIR). [C · S3]
- On top of the profit rules, a self-employed person gets the **tax credit for the self-employed** (CII) and a CO2 credit – only by filing Form 100. Amounts, conditions and the rest of the return (household, special expenses, credits): lu-income-tax-personal. [C · lu-income-tax-personal S2, lu-income-tax-personal S43]

## Related skills

lu-tax-core · lu-vat (VAT side of the same costs) · lu-social-security (CCSS in the return) · lu-accounting (books, BS and P&L) · lu-annual-return (step-by-step filing).
