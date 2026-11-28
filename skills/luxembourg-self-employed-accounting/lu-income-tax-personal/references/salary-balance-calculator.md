# Salary-household annual tax balance

Figures in this file: 2025 — the year files win if they differ.

`scripts/tax_estimate.py --household household.json` computes the estimated annual amount due or refundable for the ordinary cases below. It uses the same taxable-income calculation as the Form 100 household tools, then explains tax, credits already paid/retained, withholding, advances and final-balance rounding. This is an estimate, not a live ACD assessment or filing. [B]

## Supported cases and required evidence

- Tax year 2025, full-year Luxembourg resident and tax liability; explicitly reviewed class 1 for a single household without children, or joint class 2 within the supported family model.
  The bounded class 1a/CIM extension below is supported; individual spouse taxation and other years stop.
- Ordinary Luxembourg-taxable salary and employer-advanced sickness. Standard or reviewed actual salary costs, reviewed global commuting and the existing supported insurance, savings, pension-plan, child/own-home/childcare deductions. All income and eligible deductions must fit that supported model; do not omit an unsupported category to obtain a result.
- One salary credit category per person. Separate salary-only and business-only spouses are supported with established affiliation and credit periods; the same person's mixed categories need the monthly ranking calculation and stop.
- A full eligible year for automatic annual CIS/CO2 recomputation, supported by continuous dated employment coverage. Simultaneous jobs are merged for period coverage; successive jobs may cover the year together. Full-year residence alone does not establish this condition.
- One-card cases preserve final/corrected payroll credits when that result has been checked;
  they do not receive a new annual credit merely because Form 100 is filed. This route can retain a verified partial-period payroll result without recomputing an annual entitlement. [B;
  legal boundaries: C · S57; S82 arts. 154, 154quater; S124]

The existing household JSON gains a `salary_balance` object:

```json
{
  "resident_full_year": true,
  "advances_paid": 0,
  "salary_balance": {
    "tax_class": 1,
    "income_and_deductions_complete": true,
    "evidence": "Reference to the household/class review and complete certificate/card history",
    "people": {
      "taxpayer": {
        "compulsory_affiliation": true,
        "full_year_eligible": true,
        "payroll_final": true
      }
    }
  }
}
```

These are established case facts, not switches to turn on when the evidence is missing. `people` must name exactly the income recipients (`taxpayer`, and `spouse` where relevant). A business-only spouse needs `compulsory_affiliation` and `full_year_eligible`; payroll-final is salary-specific.
The review must establish the annual tax class, including age/status/history; the calculator does not infer class 1 merely from an absent spouse. [B]

Every salary also needs these facts in addition to the usual owner/pay/contributions/dates:

| Field | Meaning |
|---|---|
| `certificate_id` | Identity of one logical annual certificate; exactly one included salary record for all equivalent PDF/image representations. |
| `tax_regime: "ordinary"` | Actual employee regime. Unknown, domestic flat, temporary flat and manager cases are not converted to ordinary. |
| `all_pay_luxembourg_taxable: true` | All pay belongs to the supported taxable category; foreign/exempt progression and extraordinary pay need other calculations. |
| `tax_card_id` | Actual card identity from card history; `null` only for evidenced absence. Count cards, not uploaded files. |
| `withholding_basis` | `before_cis_co2` for separately certified withholding, or `after_cis_co2` only when precisely those two credits have already been netted. |
| `withheld`, `cis`, `co2` | Actual certificate withholding and annual CIS/CO2 paid, including explicit zero where proved. These are source amounts, not recalculated annual entitlement. |
| `travel`, `contributions` | Known amounts; contributions are deductible amounts and travel is this record's reviewed share of the person's global commuting deduction. |
| `replaces` (optional) | ID of a superseded certificate. Remove the superseded record from the included salary list; including both stops. |
| `employment_id` (optional) | Distinguishes genuine separate contracts where otherwise identical records could be duplicates. |

The `salaries` list contains **one record per logical certificate**, not one record per uploaded file. A PDF, its photograph and a duplicate attachment can all represent the same certificate;
map them to that certificate in the household work log/source inventory, then include its figures once. The calculator rejects duplicate records; it does not merge their amounts automatically.
A new file name or `certificate_id` does not make a second employment or payment. A corrected certificate replaces its superseded version; retain their history outside the included salary list.
Do not change commuting deductions or invent `employment_id` values to make duplicates pass. [B]

Keep the source `cis` and `co2` values unchanged for PDF/XML preparation. The estimator aggregates those **paid** amounts and separately reports **retained** entitlement and the paid-minus-retained adjustment under `salary_reconciliation`. Never write retained entitlement back into certificate fields: doing so would erase the payroll payment history and alter the reconciliation. [B]

Negative annual credit-paid totals remain outside this supported route; preserve the sign and use reviewed manual preparation. Signed XSD fields do not remove this calculator boundary. Net withholding including CIM must use the explicit CIM-aware basis below; CISSM or other components remain unsupported and cannot be labelled `after_cis_co2`. [B]

## What the calculator does

1. Validate the facts, known amounts, dates and document identities. Combine each person's gross;
   use one salary-cost minimum and the reviewed global commuting amount. Deduct annual eligible expenses from the shared household calculation. [B; C · S82 arts. 105bis, 107, 113]
2. Compute the supported extra-professional allowance from each spouse's active professional net income, related compulsory contributions and individual special-expense minimum. Its maximum is limited by the lower relevant amount. A supplied `extra_professional_amount` must match this ordinary-case computation; extra pension/cessation or unrepresented article 110 facts need review.
   [C · S82 art. 129b; I for the supported-input computation]
3. Test the assessment gate independently for each salary recipient: more than one card, or qualifying salary without a card. For a full eligible year, floor combined gross once to a whole euro and compute CIS/CO2, rounding each up to a cent. Otherwise retain checked one-card payroll amounts, or stop for period/category review. [C · S57; S82 art. 154quater; S124]
4. Compare **paid minus retained**, separately for each spouse. Positive recovery below EUR 12 is waived. The source does not explicitly resolve whether CIS and CO2 share this small-recovery unit: the calculator stops only when pooled versus component treatment would produce different results (PIT-O-24). It does not hide that uncertainty inside a rounding choice. [C · S57 for recovery and spouse separation; I/O for component grouping; B for the stop]
5. Normalise net-of-CIS/CO2 withholding to before-credit withholding once, then compute `tax − business credits − withholding − advances + salary adjustment`. Already-correct paid salary credits therefore make a zero adjustment, not another full deduction. [I · S57; S82]
6. Preserve the raw signed balance. A **positive** final balance floors to whole euros.
   [C · S82 art. 154(2)] Refund cents are preserved: article 154(7)'s refund treatment has no matching whole-euro floor. [I · S82 art. 154(7)] These final-balance treatments are distinct from the earlier tariff-tax minimum and credit-recovery threshold.

JSON output adds `salary_reconciliation` per person, `salary_credit_adjustment`, `salary_context`, `balance_before_rounding` and `balance_rounding`. `amount_before_payments` is assessed tax less business credits plus the salary-credit adjustment, **before withholding and advances**. The legacy key `tax_after_credits` is retained as an alias for that same amount; it is not the annual retained CIS/CO2 entitlement or a final amount due. A payroll-credit recovery can make it exceed assessed tax. `balance_before_rounding` then subtracts withholding and advances. Positive `balance` means due; negative means refundable. The readable output shows the same working. No customer identity is copied into a research log; the supplied evidence description remains in that household's output. [B]

## Invented worked cases

- One settled card, gross 30,000, contributions 3,300, no FD, minima 540/480: taxable 25,680;
  tax 1,387. With withholding 1,400 and already-correct credits 792, the refund is 13.
- Two cards for a full eligible year, gross 30,000 + 20,000, contributions 5,500, global FD 1,980, minima 540/480: taxable 41,500, tax 4,970. Paid 792 versus retained 594 gives recovery 198.
  Withholding 5,000 gives an amount due of 168. Withholding 5,000.75 gives raw 167.25, final 167.
- If the same withholding is recorded net of the paid credits as 4,208, normalisation gives the same amount due of 168. Add the paid credit only once when normalising withholding.
- Two separate cards each covering the full eligible year, gross 28,000 + 22,000, contributions 3,080 + 2,420, reviewed FD 1,000 + 980, minima 540/480: taxable 41,500, tax 4,970. Actual certificate-paid CIS 600 + 0 and CO2 192 + 0 stay in the source records. Retained CIS 450 and CO2 144 give recovery 198, so the amount before payments is 5,168. Pre-credit withholding 3,000 + 2,000 and advances 200 give a refund of 32. A duplicate image adds no income or payment;
  six-month eligibility instead requires period review before recomputing entitlement.

[I · arithmetic using S57/S82/S124]. Six complete examples and boundary checks are independently hand-worked in the research archive and tested through the actual household adapter and CLI.

## Remaining scope

Domestic-flat elections, same-person business/salary/pension ranking, partial-year annual-credit recomputation, foreign/exempt/extraordinary income, unsupported class 1a/CIM cases and child rebate, negative annual paid credits and PIT-O-24 cases where component grouping changes the result remain explicit stops.
CISSM already handled in payroll is not deducted again; its separate post-year request route remains RET-O-02. Live MyGuichet semantics remain RET-O-01.
Deduction what-if calculations retain salary gross/credits; business scenarios with a positive spouse allowance stop for a new allowance review. [B/O]

## Bounded class 1a/CIM extension, 2025

The household contract in lu-annual-return `references/forms/2025/form100-deductions.md` now supports reviewed full-year resident unmarried child-based class 1a. Set the reviewed class to the string `"1a"`; supply the explicit single-parent facts and known salary `cim`. Withholding uses `before_cis_co2_cim` or `after_cis_co2_cim`, explicitly covering all three paid credits.
CIM is reconciled once, even on one card; its paid-minus-retained adjustment has no inferred CIS/CO2 small-recovery waiver. The unchanged CIS/CO2 gate runs independently. [B · S150]

The class 1a annual tariff is confirmed by S151. PIT-O-17 remains open: if raw versus tariff-rounded income changes CIM, or its annual result needs fractional-cent rounding, the balance stops.
Regular monthly support and positive documented Luxembourg moderation are required; PIT-O-27, child rebates/bonuses, event-year cases and irregular support stay manual. An unrelated new partner is not automatically excluded; another parent under the same roof affects eligibility.
[C · S80–S82; B for the supported subset]

## Handoff extensions checked 2026-11-04

The shared household model now includes employee occupational pension, voluntary contributions, exact private-pension contract checks, qualified full-year partners with common children, bounded family medical costs, certified HSUP/SJFE exemptions and separate employee replacement benefits. Input contracts and output limits are in lu-annual-return forms/2025/employment-deductions.md, forms/2025/salary-details.md and forms/2025/medical-and-partnership.md. These are bounded 2025 extensions, not generic extra-income or extra-charge support. Existing PIT-O-17 CIM and PIT-O-24 small-credit-recovery guards remain. [B]

Medical relief changes adjusted income/CIM, not gross salary credits. Certified payroll exemptions reduce net income but remain in credit gross. Occupational and voluntary payments have different article 113/129b treatment. Separate 95a benefits, known employer CNS advances and IMAL trigger the bounded full-cap proof below; cases where eligibility or the amount still depends on those benefits stop. Unknown or duplicate replacement certificates stop in every output route. [C · S82; B/O for guarded implementation]


## Full extra-professional cap independently established — 2025

PIT-O-35 is not generally settled. Article 95a employment-category classification alone does not establish both article 129b limbs. Unemployment is expressly within article 95(5); do not automatically move it into the 95a uncertainty. The current 2018 circular supersedes 1998/2002 guidance; the old 95a circular was repealed in 2022. [C · S82 arts. 95, 95a, 129b; S166; S167]

For a full-year resident joint household where **both have ordinary employment**, a sufficient-condition proof can still establish the full joint cap. For each adult take evidenced ordinary article 95 gross excluding all direct replacements and CNS advances, then subtract **all** earning costs, payroll exemptions, commuting and relevant compulsory contributions, including those attached to excluded benefits, and the article 113 minimum from the year file. If both conservative bounds reach the full cap, the unresolved inclusion of positive benefit income cannot change the allowance. These bounds are not asserted to be the definitive legal 129b net incomes. If either is below the cap, stop; do not return the lower bound as a guessed allowance. Benefit-only spouses and a mixed business route remain outside this extension. [I · S82 art. 129b(2)–(3); S166; B for narrower subset]

Add `salary_balance.extra_professional_review` with `evidence` and `people` containing exactly `taxpayer` and `spouse`. Each person needs:

- `ordinary_activity_current_year: true`, `ordinary_activity_affiliation_confirmed: true`, `activity_evidence`;
- `ordinary_article95_gross`, `ordinary_gross_excludes_replacements: true`, `gross_split_evidence` reconciling all known/embedded advances.

Gross must be positive and cannot exceed the person's ordinary-record S components; known IMAL and direct replacements cannot support that maximum. **S can conceal advances** under the 2025 ECSP guide, so a code is not evidence of an entirely ordinary amount. Unknown embedded amounts require review. The result marks `allowance_method: full_cap_proved_without_replacement_income` and reports the conservative `allowance_limits`. The ordinary income, contributions and benefits all remain in the complete tax base and credit reconciliation. No automatic monthly/credit assumption is relaxed. [C · S169 for source representation; B for contract]

Invented example: ordinary 30000 each, direct benefit 6000 for taxpayer, costs 540 each, compulsory contributions 3900/3300, minimum 480 each. Bounds 25080 and 25680 both exceed 4500, so 4500 is established. With the same taxpayer deductions, ordinary 9420 gives exactly 4500; 9419.99 does not. The prototype treats these as reviewed arithmetic, not an official assessment. [I/B]

Fresh review on 5 November 2026 retained PIT-O-17 and PIT-O-24. The 2025 CIM payroll example is not an express annual-assessment rounding instruction. The 19 October 2026 assessment circular repeats the recovery wording but applies from 2026 only; it must not replace 2025 rules. [C · S80; S57; S161; S162; O for unresolved conventions]

## Family changes: three more supported cases (2025)

The rules are in family-changes.md; the status fields of the household file are in lu-annual-return forms/2025/family-events.md. Each case needs its reviewed facts in `salary_balance`; without them the estimate stops. [B]

| Case | Facts in `salary_balance` | What the estimate does |
|---|---|---|
| A class-2 year assessed alone – the three years after a court-authorised separation, or after a spouse's death | `tax_class` 2, no spouse in the file, and `class2_alone`: `ground` (`separation` or `widowed`), `event_year` (year of the court's permission or of the death), `evidence`; for a separation also `no_use_in_five_years_before: true`. The person's status must be `SV` or `DI` (separation) or `VE` (widowed) | Class 2 on this one person's income, one person's ceilings and minimum, no extra-professional abatement, no single-parent credit. Stops outside the three years |
| Class 1a without a child | `tax_class` "1a", no single-parent request, no child, and `class_1a_ground`: `widowed` (status `VE` with `status_since`, from the fourth year after the death) or `age` (64 completed on 1 January), with `class_1a_evidence` | Class 1a scale, no single-parent credit |
| The joint year of a spouse's death | A joint file whose taxpayer becomes `VE` and whose spouse becomes `DE` on the same day (`status_changes`) | Joint class 2 with the couple's ceilings and the extra-professional abatement. Only for a death on 31 December: for an earlier death the estimate stops, because whether the deceased spouse's flat amounts are cut to months is open (PIT-O-40) |

Hand-calculated test households: SB-G, SB-H and SB-I in `scripts/tests/salary_households/`; SB-H gives the ACD's own figure for class 1a. [B]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
