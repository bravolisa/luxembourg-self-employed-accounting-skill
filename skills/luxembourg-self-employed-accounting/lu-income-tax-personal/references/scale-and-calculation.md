# Tax scale and how the tax is computed

_Figures in this file: 2025–2026. The year files in `figures/` win if they differ._

## From income to tax

1. Total net income (all categories, income-categories.md) − special expenses = **taxable income** (*revenu imposable*). [C · S2]
2. − abatements (extraordinary charges, children outside the household, extra-professional…) = **adjusted taxable income** (*revenu imposable ajusté*); the scale applies to it. [C · S2]
3. Taxable income is **rounded down to a multiple of €50** before the scale is applied. [C · S2]
4. Apply the scale for the class (below), round the tariff tax down to the euro and treat a tariff tax below €12 as nil before computing the surcharge. [C · S82 art. 124]
5. Add the **Employment Fund surcharge** (*contribution au fonds pour l'emploi*): 7% of the tax, or 9% above €150,000 of adjusted taxable income in classes 1 and 1a (€300,000 in class 2). [C · S40] The ACD's formula above the threshold is tax × 9% − €931.80 in class 1 (−€885.36 in class 1a; class 2 above €300,000: −€1,863.60) – so the 9% only bites on the tax above the threshold. [C · S42] The surcharge is a percentage of the tax from the scale articles (arts 118, 120, 120bis, 121, 131, 157–157ter); the tax credits are not in that list and come off the tax afterwards (art. 152ter(4)). [C · S65; S2]
6. Round the surcharge-inclusive result down to the euro; retain the earlier tariff-tax zero rule. [C · S89; S82 art. 124]
7. Reconcile tax credits with amounts already paid, then withholding and advances, keeping gross/net withholding semantics explicit. Do not subtract employee/pension entitlement a second time after it was paid through payroll. The paid-minus-retained adjustment and small-recovery rule are in employee-tax-credits.md; other credits retain their own rules. [C · S57; S82 art. 154; I for calculation order]

8. Round a **positive final balance**, after withholding and advances, down to a whole euro. This follows article 154(2), separately from the tariff-tax rounding and small credit-recovery waiver. [C · S82; S2, both article 154(2), re-read 2026-11-04] Preserve cents in a negative balance: article 154(7) provides for the excess to be offset against other due tax claims or refunded, without stating a matching floor. This cent treatment is our reading. [I · S82; S2 art. 154(7)] The 2025 salary calculator and its scope are in [salary-balance-calculator.md](salary-balance-calculator.md).

## The scale (class 1, from tax year 2025)

| Taxable income | Rate on that band |
|---|---|
| up to €13,230 | 0% |
| €13,230 – €15,435 | 8% |
| €15,435 – €17,640 | 9% |
| €17,640 – €19,845 | 10% |
| €19,845 – €22,050 | 11% |
| €22,050 – €24,255 | 12% |
| €24,255 – €26,550 | 14% |
| €26,550 – €28,845 | 16% |
| €28,845 – €31,140 | 18% |
| €31,140 – €33,435 | 20% |
| €33,435 – €35,730 | 22% |
| €35,730 – €38,025 | 24% |
| €38,025 – €40,320 | 26% |
| €40,320 – €42,615 | 28% |
| €42,615 – €44,910 | 30% |
| €44,910 – €47,205 | 32% |
| €47,205 – €49,500 | 34% |
| €49,500 – €51,795 | 36% |
| €51,795 – €54,090 | 38% |
| €54,090 – €117,450 | 39% |
| €117,450 – €176,160 | 40% |
| €176,160 – €234,870 | 41% |
| above €234,870 | 42% |

[C · S36] The scale has applied from 1 January 2025 (it neutralised 2.5 index tranches); 2026 uses the same scale. [C · S41, S58; S2]

- **Class 2 (splitting)**: twice the class-1 tax on half the adjusted taxable income. [C · S2]
- **Class 1a**: the scale applied to adjusted taxable income reduced by a quarter of its shortfall to €79,380, with the marginal rate capped at 39% from €51,804 (then 40% / 41% / 42% as above). [C · S2]
- **Top marginal rate** with the 9% surcharge: 42% × 1.09 = **45.78%** – the surcharge is on the tax, not on income. [I · S36, S40]
- **Marginal rate in class 2**: the band that half of the adjusted taxable income falls in, times 1.07 – e.g. half in the 34% band → 34% × 1.07 = 36.38% on the next euro deducted. A large deduction that crosses down into a lower band saves less on the part below; the €50 rounding moves small amounts by a few euros. `scripts/tax_estimate.py` computes the tax and the saving of each deduction. [I · S2, S40]
- Marginal rate (the rate on the next euro) and average rate (total tax ÷ income) are different; a self-employed person's "tax rate" in conversation is usually the marginal one. [I]
- **Foreign income exempt under a treaty with a progression clause** is added to a notional base to find the global rate that then applies to the Luxembourg taxable income. [C · S2]

## Worked example (invented figures)

A single self-employed person (class 1), net profit €60,000, special expenses €3,000 (incl. contributions), no abatements: taxable income €57,000. Tax = sum of the bands up to €54,090 plus 39% of €2,910, then +7% surcharge, then − the CII and CO2 credit if profit is below €80,000. Use the ACD's online calculator or the formulas (S42) for the exact figure. [I · S36, S40, S43]

## Class 1a checks and child-credit boundary

The 2025 ACD formula workbook, annual-income columns B–F (not salary/pension withholding), corroborates class-1a tax including the Employment Fund: adjusted income €32,500 → €746;
€65,000 → €11,548; €150,000 → €47,366; €150,050 → €47,388. Apply the income floor, tariff euro floor and small-tax zero rule in that order. These examples are checks, not a replacement for the complete scale. [C · S89; I for arithmetic]

The CIM circular's example prints “3 504 – 746 = 3 415”. The subtraction is erroneous: the refundable difference is €2,758 with those inputs and no other payments or credits. Do not use the printed result as a test oracle. [C · S80 for the printed text; I for corrected arithmetic]

The shipped estimator now supports the 2025 class 1a tariff, with the bounded CIM household route described in lu-annual-return `references/forms/2025/form100-deductions.md`. PIT-O-17 stays open:
annual CIM is calculated only where both income-base readings coincide and no fractional-cent rounding is needed. [B · S150]

## Exact class 1a annual continuation, 2025

The official annual formulas confirm that the capped continuation does not revert to ordinary class 1 at the shortfall reference income. After flooring adjusted income to the tariff step, use the transformed class 1 base below the kink, without a second income floor. Above the kink, continue at the capped marginal rate, then the ordinary higher marginal rates. Exact coefficients are in Mémorial A590, printed page 112 section 4.3; tests independently compare its explicit formulas with the implementation. Tariff euro floor, small-tax zero and Fund rounding stay in their existing order. [C · S151; I for equivalent integration implementation]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
