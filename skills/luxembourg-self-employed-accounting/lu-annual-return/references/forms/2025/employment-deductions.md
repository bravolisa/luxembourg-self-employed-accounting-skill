# Employment deductions and retirement contracts — 2025

Figures in this file: 2025. The personal-tax year file owns the values. Sources below refer to lu-income-tax-personal/references/sources.md; all were reopened on 2026-11-04.

## Rules applied

Actual professional salary costs replace the minimum; they are not added to it. Commuting remains separate. Each employee has a separate election, regardless of the number of certificates. [C · lu-income-tax-personal S82 arts. 105, 107; lu-income-tax-personal S152; lu-income-tax-personal S153]

Personal employee contributions to a qualifying employer supplementary pension scheme are article 110(3), capped per employee, outside the article 113 minimum. Private retirement contracts are article 111bis/111ter and have a different shared per-holder cap. Voluntary/continued/optional statutory health or pension contributions and qualifying period buybacks are article 110(4), inside the article 113 minimum comparison, without an invented separate cap. Employer contributions and dependency contributions are not relabelled as these payments. [C · lu-income-tax-personal S82 arts. 110, 111bis, 111ter, 113; lu-income-tax-personal S154]

For the low-earning spouse's article 113 minimum, subtract actual earning costs and the related article 110 deductions. Using the deductible occupational amount in this remainder is our statutory interpretation. For article 129b's extra-professional limiter, subtract only article 110(1)/(2) compulsory contributions and the applicable minimum, not occupational or voluntary contributions. [C · lu-income-tax-personal S82 arts. 113, 129b; I for retained occupational allocation]

Ordinary retirement contracts require a qualifying product/provider, a minimum ten-year term and maturity between the exact sixtieth and seventy-fifth birthdays, cumulatively. Subscription must precede the sixty-fifth birthday. Each contract must qualify independently. A PEPP requires a Luxembourg sub-account. Prior-to-2002 contracts have separate transitional rules. [C · lu-income-tax-personal S82 arts. 111bis/111ter; lu-income-tax-personal S144 §3.1 and legacy provisions]

## Household input contract

The new deduction arrays require a full-year resident 2025 household, supported single/joint status and ordinary taxable salary. No individual assessment, foreign/progression branch or negative salary remainder is inferred. These are software scope restrictions. [B]

Every row uses `owner`, `amount`, `evidence`, `net_of_reimbursements: true`, `not_deducted_elsewhere: true`:

| Array | Additional facts |
|---|---|
| `salary_costs` | One reviewed person-year total per employee; `method: actual`, `employment_related: true`. Underlying item details and receipts remain in the private case. Amount must be at least the applicable flat; otherwise use the standard route. |
| `occupational_pension` | Unique `certificate_id`, `employee_personal_contribution: true`, `qualifying_scheme: true`, `scheme_evidence`. Aggregate all certificates before applying that employee's cap. |
| `voluntary_contributions` | Unique `certificate_id`, `kind: voluntary/continued/optional/buyback`, `qualifying_scheme: true`, `scheme_evidence`, `not_compulsory_or_dependency: true`, explicit boolean `salary_related`. |

Private `pension_plans` retain `holder`, `insurer`, `start`, `end`, `amount`, boolean `pepp`. The contract/provider's legal qualification must be reviewed upstream; valid dates alone do not establish it. An explicit `qualifying_scheme: false` is rejected. PEPP adds `subaccount_country: LU` and `subaccount_evidence`. `contract_id` distinguishes genuine separate otherwise-identical contracts; duplicate representations must not get new IDs merely to pass validation. A start/maturity-year payment requires `payment_date`; any supplied payment date must fall in both the tax year and contract term. Legacy contracts and leap-day anniversary ambiguity stop for review, not legal disqualification. [B]

## Output and limits

| Item | Paper Form 100 | XML |
|---|---|---|
| Actual salary costs | 743/744, replacing the flat | FE choice and SAL_FO_REV_IMP |
| Voluntary contributions | 1501/1502 | DepSpeCotisationsPers / CTP_MNT_CONT or CONJ |
| Employee occupational pension | 1605/1606: allowed deduction; annex preserves actual paid | DepSpeRegimeCompSal / RCS_COT_CONT_NEX or CONJ_NEX: actual paid |

Field meanings confirmed against the official form/schema. [C · lu-income-tax-personal S1; lu-income-tax-personal S75] The 2025 schema keeps the amount retained after the cap in separate recap fields (D3426 / D3846, « Montant retenu pour le calcul de l'impôt »), which the assistant calculates itself. [C · lu-income-tax-personal S75; I for the 2025 behaviour] Above-cap occupational XML still stops, because the live calculation is unverified (RET-O-04). [B] Calculation/PDF remain available with the actual/allowed annex. Paper cap treatment follows the explicitly capped printed instruction. [I · lu-income-tax-personal S1; O for live XML]

Hand examples and reproducible refusal cases: `scripts/tests/handoff_extensions/expected.json`, `test_handoff_extensions.py` and the research archive. No project acceptance-case pin is changed by a skill release. [B]

The positive reviewed employee occupational claim also fills the paper affiliation Yes for its owner: R1609/R1610 has the surprising export state `/courrier` (No is `/myguichet`). This is verified widget mapping; inferring positive affiliation from the qualifying personal contribution is an implementation inference. An absent contribution does not establish No and remains blank. [C · lu-income-tax-personal S1; I for positive affiliation inference]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
