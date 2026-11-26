# Children, childcare and own-home input (2025)

These extensions use the same household JSON as [form100-tools.md](form100-tools.md).
Rules belong to lu-income-tax-personal; this file defines the supported input and output. [B]

## Supported scope and explicit stops

Set `resident_full_year: true`. Supported single/married joint cases and established child assignment retain the rules below. Reviewed full-year registered partners with common children now have the additional route in [medical-and-partnership.md](medical-and-partnership.md). Alternating residence, blended partner families, individual taxation, non-residents and cross-country moves still need separate review. [B]

Bounded class 1a/CIM, current donations and own-life single-premium insurance are in [form100-deductions.md](form100-deductions.md). Actual medical costs have the separate route above. Broader extraordinary costs, rental/pension/capital income and unsupported child credits must not be omitted to obtain a balance. [B]

## `children[]`

| Input | Meaning |
|---|---|
| `last_name`, `first_name` | Actual identity; fixtures use invented names |
| `national_id` or `birth_date` | 13-digit ID or ISO birth date; if both, they must agree. Never invent an ID for a real child |
| `national_id_not_assigned` | Required `true` when no ID exists; a missing document/unknown ID does not mean the state has not assigned one. If an ID is supplied this flag cannot be true |
| `in_tax_household: true`, `assignment_evidence` | Confirmed 2025 tax-household assignment and a source reference in the private case record |
| `custody` | `both_parents` for the jointly taxed parents, or `sole_parent`; complex assignment stops |
| `married_or_partnered: false`, `has_children: false` | Required facts; either true requires separate household review |
| `benefits` | List of `family_allowance`, `study_aid`, `volunteer_aid`, or `[]` when none received |
| `benefit_recipient` | Official XML code: `CT` taxpayer, `AP` other parent, `DP` both, `NO` none. A sole-parent case permits CT/NO only |
| `request_rebate` | Explicit boolean; cannot be true if a listed allowance/aid already includes the moderation |
| `previous_reduction` | Optional evidenced XML code CT/AP/DP/NO; never infer last year's assignment |
| `education`, `institution`, `continuous_full_time_over_year` | University/vocational, school or university name, confirmed continuous full-time course over a year. Required for an adult student |
| `continued_allowance` | Boolean; actual continued family allowance, not merely disability |
| `studies_away` | Boolean; temporary absence for studies; permanent departure needs review |
| `disabled`, `disability_evidence` | Boolean and proof when the childcare age exception is needed |

A listed child increases the supported insurance/home-savings/mortgage ceilings only after the child-reduction conditions pass. A 2024 return supplies leads, not proof of 2025 entitlement.
National IDs and duplicate entries are checked. PDF capacity is four ordinary children, three adult students and one continued-allowance entry; excess rows stop rather than disappear. [B]

## `own_home`

One wholly private Luxembourg main home, available and occupied on the same date, retained through 31 December. `ownership` is `sole` for a single taxpayer or `joint_equal` for a married couple's equal joint mortgage. Other allocations are PIT-O-14. Construction/pre-availability costs, bridging loans, mixed use, another home, sale/move and unequal ownership require review. [B]

Required keys: `use: "main_home"`, `country: "LU"`, `fully_private: true`, `available_since`, `occupied_since` (ISO), `available_through_year_end: true`, `ownership`, `evidence`, and `address` with `postcode`, `locality`, `street`, `number`. `loans[]` has at most three rows:

- `creditor`, `nature: "FH"`, `start` (ISO), `balance_31_dec`;
- `interest` actually paid, `subsidies` explicitly zero or the amount received;
- `acquisition_only: true`, `available_period_only: true`.

Amounts are non-negative, at most two decimals. Principal repayments and mortgage insurance are not interest. For the supported ordinary assistance branch, net interest is interest less subsidies, once. Employer cash support and cheap employer loans require the separate personal-tax employer-interest-support.md reconciliation and are not supported by this automatic subtraction. The PDF loan table shows actual net interest; N.1021/N.1022 show the capped deduction as a negative rental-income amount. XML debt rows show actual net interest, while L0480/L0540 show allowed positive amounts. Joint amounts split half each, with a one-cent rounding remainder retained on the spouse side. [B; field evidence:
lu-income-tax-personal S1, S61, S75; calculation rules: home-and-rental.md]

## `childcare[]`

One record per certificate/provider/payer. Required:

- `paid_by`: taxpayer/spouse; `provider`, `provider_address`, `country` (EU code);
- `approval_evidence`, `certificate`: references retained in the private case;
- `children`: zero-based indexes into the household children array;
- `no_other_claim: true`: costs not claimed elsewhere, and no additional domestic-help/dependence claim omitted from this calculation; combined claims currently require review;
- `payment_timing: "monthly"`: supported regular monthly payments; advance/arrears allocation remains PIT-O-15;
- `monthly`: month keys `"1"` … `"12"`, each with `paid` and `reimbursed`, including explicit zero.
  Record the actual eligible cost paid and third-party reimbursement once; if a certificate already gives net parent contributions, do not subtract a subsidy again.

The child must be eligible for moderation and under 14 on 1 January, or have evidenced disability.
The provider must be approved; a receipt alone does not establish approval. Costs before a child's birth, missing amounts, excessive reimbursements, duplicate entries and an entirely zero-net claim stop. Multiple providers/payers share the monthly limit. [B; eligibility/calculation rules:
lu-income-tax-personal extraordinary-charges-and-abatements.md]

XML groups months with the same net cost separately per provider/payer. There are at most ten period rows; twelve different amounts cannot be averaged or truncated to fit. The PDF shows actual annual costs and a monthly amount only when it is constant. `fill_form100_pdf.py --household` also writes `<output>.childcare.pdf`, a monthly/provider annex showing reimbursements and the separate capped calculation. Attach it with the certificates. The abatement is applied **after** taxable income (box 2038), and the tax-estimate CLI preserves it. [B]

The annex uses a Unicode TTF font: system Arial Unicode (macOS), DejaVu Sans (Linux), or an explicit `BL_PDF_FONT` path. Missing glyphs cause an error. The Form 100 field writer still uses the form's Latin-1 appearance font: unsupported characters stop that output; XML preserves Unicode. Never silently change a person's spelling to make the PDF run. [B]

## Verification and remaining integration check

Invented fixtures and hand calculations are in `scripts/tests/households/` and `expected.json`;
boundary/failure and field/widget checks are in `test_form100_family.py`. Expected values are curator-verified arithmetic, **not accountant-signed acceptance returns**. [B]

The new sections have offline XSD, field and calculation checks. They have **not** been imported and read back in the 2025 MyGuichet assistant. Its semantic behaviour is RET-O-01 in [open-questions.md](../../open-questions.md). The tutorial's 2024 screenshots corroborate legacy field codes but cannot establish 2025 runtime acceptance. No synthetic real tax declaration is submitted by these tests. [I/O · lu-income-tax-personal S61, S69, S75]

## Child-credit calculation boundary

The supported full-year resident class 1a/CIM request and calculation now use [form100-deductions.md](form100-deductions.md). Child rebates, ordinary/transitional child bonuses, irregular support, foreign-only or zero-differential moderation and ambiguous annual CIM rounding remain separate review paths. The ordinary family schema does not by itself establish CIM eligibility. No live import acceptance is claimed. [B/O]
