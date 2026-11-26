# Four deduction and single-parent branches: supported 2025 inputs

This is the **software input contract**, not a new source of tax law. It extends the ordinary household in [form100-tools.md](form100-tools.md). The figures and eligibility rules belong to lu-income-tax-personal: special-expenses.md, donations-pensions-and-investments.md, mortgage-death-insurance.md and single-parent-and-child-relief.md. Exact field positions are in that skill's `references/forms/2025/form-100.md`. The choices and refusal boundaries here are BravoLisa implementation conventions. [B · lu-income-tax-personal S150]

All four branches require income year 2025 and evidenced full-year Luxembourg residence. The new deduction branches accept a single adult or supported married joint household; the CIM branch accepts its reviewed unmarried class-1a subset. Keep the existing income, family and salary-balance restrictions. A missing certificate amount, history or subsidy is never zero.
For every child in a new deduction case, require `moderation_origin: "lu_positive_benefit"` with existing benefits, or `"reviewed_tax_rebate"` with an independently reviewed rebate request, and `moderation_evidence`. Generic or foreign-only benefits and zero differentials do not pass this multiplier guard (PIT-O-27). Reference paths in evidence strings identify the preparer's records; never copy personal data into the skill. The complete invented inputs are in `scripts/tests/four_deductions/`. [B]

## Capability and remaining boundaries

| Branch | Calculation and PDF | XML | Explicit review boundaries |
|---|---|---|---|
| Consumer interest | Net interest combined once with insurance; shared cap and flat-minimum comparison | Actual net interest, purpose, creditor and known year-end balance | Mixed business/private, property/exempt income, third-party payment, earlier-year refunds, more than seven rows |
| Current cash donations | Eligibility review, annual minimum, both upper caps, separate allowed amount and outgoing vintage | Genuine current gifts; mandatory no-carry flag | Incoming carryforwards, in-kind gifts, refunds/counter-benefits, negative or insufficient net income, fractional-cent cap, more than six rows |
| Single-parent relief | Supported class 1a tariff; annual CIM, support reduction and paid-credit reconciliation; request/support fields | Child request, actual monthly support and salary CIM already paid | Annual rounding where readings differ, irregular/third-party support, mixed eligibility, class 2 transition, foreign-only/zero-differential moderation, child rebate/bonus |
| Housing single premium (PU) | Own-life age/child increase; previous increases used; premium limitation; shared cap; calculation annex | Own-life housing PU with confirmed zero previous use; real residence registry/reference | Crossed roles, multiple policies per adult, multiple properties, professional/mixed purpose; nonzero history stops XML only |

The new XML sections pass the official schema and offline value tests. Import, recalculation, and the assistant's summary remain **unverified** under RET-O-01. In particular, the optional retained-amount recap is not proof that MyGuichet will preserve a reduced PU ceiling. No source premium or gift is changed to impersonate its allowed deduction. [B]

## Consumer-loan interest

Add a `consumer_loans` list. Each row requires:

- `loan_id`: unique logical loan/certificate identity; reconcile duplicate scans first.
- `creditor`, `creditor_address`, `evidence`.
- `purpose`: official supported code `A` car, `B` personal needs, `C` consumption or `D` studies.
- `borrower` and `paid_by`: the same present household adult (`taxpayer` or `spouse`).
- `balance_31_dec`, `interest`, `subsidies_and_refunds`: finite non-negative cent amounts;
  a repaid loan may have an evidenced zero balance. Refunds cannot exceed current interest.
- `fully_private`, `no_property_or_exempt_income`, `no_other_deduction`, `refunds_same_year_only`: explicitly `true` after checking the contract/certificate.

Only net interest enters the shared pool, never principal or the outstanding debt. The legacy `allowed()['insurance']` key now means the **combined** allowed insurance/interest amount;
`insurance_ceiling` is their combined ceiling, including any supported PU increase. These names remain for compatibility. Do not encode interest as an insurance policy. [B]

## Donations

Add `donations` and `donation_review`. The review contains `no_prior_carryforward: true`, `income_complete: true`, and `evidence`. Every gift row requires:

- `donation_id`, `recipient`, `receipt`, `eligibility_evidence` effective for the donation year;
- `country`, `eligibility`: `LU`/`approved_lu`, or an evidenced EU/EFTA recipient with `eu_efta_equivalent`. Being a foreign charity does not itself establish equivalence;
- `paid_by`, `payment_date` inside 2025, `amount` in cents;
- `cash_gift`, `no_other_deduction`, `no_refund_or_counterbenefit`: explicitly `true`.

A nonempty `donation_carryforward` or unconfirmed absence of old carries stops the tool. The published rules still permit carryforward; the personal-vintage ordering question PIT-O-19 remains open, and pure carry-only XML has a mandatory current-detail-row problem. [B/O]

`indicative_check` now exposes `total net income` and `donations` (allowed deduction).
`deductions.donations(h, total_net_income, figures)` also returns actual gifts, ceiling, allowed amount, outgoing 2025 excess and last usable year 2027. This is a **new-vintage calculation**, not a tax-authority-approved carry balance or automatic use in a later return. Gifts below the annual minimum do not produce an upper-limit carryforward. [I · lu-income-tax-personal S82]

The percentage uses total category net income **before special expenses**, including the supported own-home category result. Compulsory contributions treated as special expenses do not reduce this percentage base. The tool requires enough income remaining after preceding special-expense categories to absorb the donation; otherwise it stops for ordering review. Business what-if options stop for donation households because changed category income requires a fresh donation cap; compare regenerated complete cases. A year override also stops these new fields until eligibility and ceilings are re-established.
[C · lu-income-tax-personal S82; B for the refusal boundary]

### PDF calculation convention

The official form's current-gift totals mean amounts paid, but its default special-expense sum adds those totals without applying donation limits. Generated PDFs therefore preserve actual payments, adjust only their contribution to deductible special expenses, and recompute taxable income. The conflicting calculation action on the affected total is removed from that generated snapshot. A `.deductions.pdf` annex explains actual gifts, base, cap, deduction and outgoing vintage.
This is our output convention, not an observed ACD instruction. Regenerate the form and annex after changing any input. The original official blank remains untouched. [B]

## Housing single-premium insurance

Keep each actual premium in the existing `insurance` list with exact risk `PU`, insurer, `paid_by` and amount. Add a `single_premium` object:

- `subscriber`, `insured`: equal to `paid_by` for the supported own-life case;
- `property: "own_home"`: references the validated principal-home object already in the household;
- `subscription_date`, `payment_date`: valid dates in order; payment must be in 2025;
- `decreasing_capital`, `personal_housing_loan`, `premium_fully_paid`, `no_other_deduction`:
  explicitly `true`; `eligibility_evidence` must establish the qualifying contract and allocation;
- `children`: child indexes assigned to this adult's increase, each child used once across policies;
- `previous_increases`: every year key `2020` through `2024`, with the increase **actually allowed** for this person and property, including evidenced zeros; `history_complete: true` and `history_evidence`. Do not enter the old premium or old theoretical maximum.

Only one qualifying own-life policy per adult and the supported single property are automated.
A bank-financed premium still needs evidence that the insurer received it; loan principal cannot be deducted again. Mixed-purpose finance, other housing, crossed subscriber/insured roles and uncertain allocations remain review cases. [B; PIT-O-16]

The calculation takes completed age **at subscription**, applies each adult's assigned child increase, deducts five-year actual use, and limits the remaining increase by that adult's actual premium. It then adds the ordinary household cap and limits the combined deduction by actual qualifying interest/premiums. `allowed()['premium_increases']` shows the individual working.
A calculated available increase is **not automatically the increase actually consumed** for a future year's history. Keep the final assessment. [C/I · lu-income-tax-personal S74, S77]

Nonzero earlier use is supported in calculations and PDF, with an annex; XML stops because the live retained-cap semantics have not been verified. Zero-history XML emits the official PU purpose/child fields and a real residence registry entry satisfying the schema key reference. [B]

## Single parent and CIM

Add `single_parent_credit`, an object rather than a boolean. It requires:

- `tax_class: "1a"`, `unmarried_full_year: true`, `no_class2_transition: true`, `full_year_eligibility: true`, and `evidence` of the child-based class/eligibility;
- `paid_outside_salary`: actual CIM already received outside supplied salary certificates, including known zero, plus `paid_credit_evidence` confirming completeness;
- `support`: exactly one record per assigned child, at most four across all child categories.

Each support record contains `child` index, `annual_support`, `monthly_support`, `support_regular_monthly: true`, `same_situation_full_year: true`, `all_support_from_other_parent: true`, `support_complete: true`, `support_evidence`, `other_parent_same_home: false`, `moderation: "positive_lu_benefit"` and `moderation_evidence`.
Annual support must equal twelve monthly amounts. Include relevant maintenance and direct upkeep/education payments, excluding family benefits and orphan pensions. This regular-support scope avoids mislabelling annual or third-party amounts in the XML's monthly-other-parent field.
An unrelated new partner is not automatically disqualifying; the fact above concerns the child's other parent. Mixed/common-child households and changing arrangements remain outside this scope.
[B; eligibility rules in lu-income-tax-personal single-parent-and-child-relief.md]

Children must already pass the ordinary fiscal-household validation, be assigned to the sole parent, and have existing Luxembourg moderation paid to the taxpayer. Separate child rebates, bonuses and foreign-only/zero-differential cases remain unsupported; do not fabricate positive benefit evidence to pass the guard. [B/O · PIT-O-27]

Each salary additionally needs known non-negative `cim`, and a new explicit `withholding_basis`:
`before_cis_co2_cim` or `after_cis_co2_cim`. The latter is normalized once by adding all three paid credits. Keep `cis`, `co2`, `cim` as **paid certificate values**, never overwrite them with calculated entitlement. The existing `salary_balance.tax_class` is also `"1a"` for this branch.
A CIM reconciliation occurs even with one tax card; the CIS/CO2 recalculation gate is separate.
The balance adds paid-minus-final CIM, not a second full credit. [B; statutory reconciliation:
lu-income-tax-personal S82 arts154bis/154ter]

The annual formula uses adjusted income after abatements. PIT-O-17 remains open: the tool calculates only if unrounded-income and tariff-floored-income readings give the same credit and the credit is already exact to cents. Otherwise it stops, without importing payroll rounding.
The lowest relevant per-child support determines the one household credit. Output exposes `single_parent_reconciliation` with paid, retained, adjustment and support. [B/O]

Direct `tax_estimate.py --year 2025 --taxable ... --class 1a` computes the tariff only unless a reviewed CIM context is supplied through the household route. Class1a alone is not CIM eligibility.
No paid credit is silently assumed in a complete household balance. [B]

The bounded household mapper requires nonzero declared supported salary or business income.
A no-income return needs the means-of-subsistence explanation in paper field A0237, which this mapper does not yet supply. This is a software boundary, not denial of CIM eligibility. [B]

For paper C0228, the generator requests an unpaid remainder only when annual retained CIM exceeds all CIM already paid. It still supplies support details and reconciles fully paid/overpaid CIM.
This is an **implementation inference** from the paper wording and Article 154ter(5)/circular §1.2.2, not an ACD-published checkbox algorithm. XML G1070_ENF_CRE_IMP instead asks whether annual CIM application is requested: it remains true for these reviewed cases, alongside actual paid S0640_SAL_MNT_CIM. Do not copy the paper predicate into XML; live interpretation remains unverified.
[I/B/O; personal S82/S80, official 2025 PDF p2 and XSD]

## Special employment payments require review

Known employer interest support and termination compensation remain manual branches. Preserve `employer_interest_support` on the household, salary or loan record, and `termination_payment` on the household or salary record when present. The tools stop for those markers and for PPPH/IDPT/IDEP/IDCC/REX1/REX2 pay or exemption codes. Read lu-income-tax-personal employer-interest-support.md and termination-compensation.md; do not hide the benefit in ordinary salary or subtract all employer support in `subsidies`. Unmarked embedded components still require document review. [B]
