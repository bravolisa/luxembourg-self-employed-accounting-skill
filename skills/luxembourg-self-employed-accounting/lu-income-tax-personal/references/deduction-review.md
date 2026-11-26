# Reviewing a household's unused deductions

_Figures in this file: 2025–2026. The year files in `figures/` win if they differ._

For planning the next year: which deductions the household does not use yet, how much room each one has, and what it really saves. The ceilings themselves live in the files named in the table; this file says how to review and how to explain.

## The message to the person

A deduction is a **discount, not free money**: the person spends the money first and the tax office gives part of it back. Recommend an option only if the person wants or needs it anyway, and show the cost after the saving next to the saving. [B]

Show each option with four columns – what they pay, the tax saving (amount and %), the cost after the saving – and say which money is still theirs (a pension contract is savings, locked until 60) and which is spent (insurance, a cleaner, a donation). [B]

## The checklist

| Option | Room (owner of the ceiling) | Lowers | Note |
|---|---|---|---|
| Private pension contract (art. 111bis), per person | special-expenses.md; figures | tax | Usually the largest room for a self-employed couple; money locked until 60–75 |
| Insurance (life ≥ 10 years, death, accident, disability, health, liability; recognised mutual societies) and consumer-loan interest – one shared ceiling | special-expenses.md | tax | Check what the household already uses: car liability and protected-driver premiums often fill part of it |
| Mortgage death insurance paid as one premium (2025) | mortgage-death-insurance.md | tax | Check actual payment, subscription age, children and the prior five years of increased deductions for the same property |
| Home-savings contract | special-expenses.md | tax | Often already full; paying more brings nothing |
| An employee's own contributions to the employer's pension plan | special-expenses.md | tax | Only if the plan accepts personal contributions – ask the employer |
| Self-employed supplementary pension (RCPi) | special-expenses.md (20% of net professional income) | tax | Final 20% withholding on what is paid in: gain = marginal rate − 20%, plus a tax-free payout |
| Voluntary or continued health and pension insurance, buying back pension periods | special-expenses.md | tax | Only where lu-social-security says periods can be bought |
| Donations to approved bodies | special-expenses.md | tax | Money given away; the saving only lowers its cost |
| Household help (declared cleaner), childcare, care | extraordinary-charges-and-abatements.md | tax | A cleaner costs social contributions and a 10% flat tax as well – the abatement mostly offsets those |
| Genuine business costs not yet claimed (car share, liability insurance, equipment, training, home office if the room qualifies) | lu-income-tax-business mixed-expenses.md, car-and-travel.md, home-office.md | **tax and CCSS** | Only costs the business really has |
| New business equipment (commercial or craft only) | lu-income-tax-business depreciation-and-investment-credit.md | tax (credit) and, through depreciation, CCSS | Investment tax credit on top of the depreciation |

Not affected by special expenses: the self-employed tax credit and its CO2 credit depend on the profit, not on taxable income (tax-credits.md). [C · S2]

## What it saves

- **Special expenses and abatements** save the marginal rate: in class 2 the band that half of the adjusted taxable income falls in, times 1.07 (scale-and-calculation.md). Once a deduction crosses into a lower band, the rest saves less; the €50 rounding moves small amounts by a few euros. [I · S2, S40]
- **A business cost** saves CCSS and income tax together, as long as the profit stays above the minimum contribution base (lu-social-security contributions.md): CCSS × the cost, plus the marginal rate on the cost less the deductible part of the CCSS saved. At a marginal rate around 36% that is roughly half the cost. [I · our arithmetic on S2 and lu-social-security S11]
  - The CCSS saving arrives with the regularisation, one to two years later, unless the provisional base is adjusted.
  - The pension part of CCSS buys pension rights: paying less means a smaller state pension later.
- Compute it: `python scripts/tax_estimate.py … --what-if special=<amount> --what-if business=<amount> --what-if abatement=<amount>` – each option alone and all together. [B]

## Worked example (invented figures)

Married couple, class 2, both working, tax year 2026: taxable income €90,000; the self-employed spouse's profit €38,000 (CCSS 25.15% without the Mutualité).
- Adjusted: €90,000 − €4,500 = €85,500; half is €42,750, in the 30% band → marginal rate 30% × 1.07 = 32.1%.
- A private pension contract of €3,000 each (€6,000): half the base falls by €3,000, from €42,750 to €39,750 – €135 in the 30% band, €2,295 in the 28% band, €570 in the 26% band. Saving ≈ 2 × (€40.50 + €642.60 + €148.20) × 1.07 ≈ €1,779, about 30% of €6,000. Cost after the saving ≈ €4,221 – and the €6,000 stays the couple's savings.
- €3,000 of genuine business costs instead: the profit falls to €35,000, still above the minimum base, and the credits do not change (profit under €40,000). CCSS falls by about €755; taxable income falls by €3,000 less the deductible CCSS saved (23.75%), i.e. €2,288, so half the base falls by €1,144 – €135 at 30% and €1,009 at 28% – and the tax by about 2 × (€40.50 + €282.45) × 1.07 ≈ €691. Together about €1,446, roughly half of €3,000 – but money spent, not saved.

[I · our arithmetic on S2, S36, S40]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
