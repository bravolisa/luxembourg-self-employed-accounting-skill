# Employee CIS, CO2 and CISSM — 2025 reconciliation

Figures in this file: 2025 – the year files win if they differ. The 2026 employee CO2 amount is different; do not import it into 2025. Salary/business/pension ranking is shared with donations-pensions-and-investments.md and tax-credits.md. [C · S82; S57; S126]

## Start with eligibility, person and period

CIS and employee CO2 require qualifying Luxembourg-taxable salary and personal compulsory social-security affiliation for that salary. They count once for all ordinary salary of the person, not once per employer; spouses are tested separately. Temporary-agency article 137(5a) has its own exception. Do not infer a manager's entitlement solely from a self-employed CCSS classification; PIT-O-12 remains open. [C · S82 art. 154quater; S57; O for manager classification]

The credit gross includes relevant benefits and exempt remuneration under articles 115/134;
it is not the certificate's withholding base after AC/FD/social deductions. The 2025 employer circular floors annual gross to whole euros before the schedule. Annual, monthly and daily credit amounts round upward to cents; monthly is annual/12, daily annual/300, for the qualifying period. A few months of work do not automatically earn a full-year credit. [C · S82; S124]

## Annual schedule — ordinary CIS/CO2, before period adjustment

| Annual gross after required flooring | CIS | Employee CO2 |
|---|---|---|
| Below 936 |0|0|
|936–11,265|300+(gross−936)×2.9%|192|
|11,266–40,000|600|192|
|40,001–79,999|600−(gross−40,000)×1.5%|192−(gross−40,000)×0.48%|
|From 80,000|0|0|

[C · S82 art. 154quater; S124]. These are 2025 figures; the statutory conditions and period calculation still apply. Do not copy the pension low-income band into the employee schedule.

## Payroll payment and assessment are separate stages

The employer uses available information to estimate annual gross and pays the appropriate fraction when the card permits CIS. On the last remuneration payment it regularises its year's payments, including relevant earlier periods. The correction may be negative: retain the certificate's net credit paid rather than adding only favourable monthly amounts. [C · S124]

For assessment, first apply the circular's gate. With **one credit category**, regularisation occurs where the taxpayer had several tax cards during the year or qualifying Luxembourg-taxable salary/pension without a tax card. Filing Form 100 alone does not universally trigger a fresh annual CIS. An erroneous one-card payroll certificate needs the employer/RTS correction route, not an invented second credit. [C · S57 p.3; S124; I for preparation]

Aggregate simultaneous/successive ordinary employment **within the salary category**, using actual periods and card history. For mixed business/salary/pension categories use the circular's monthly grid and highest average monthly income ordering; do not apply that ranking separately to each employer or choose whichever credit is most generous. [C · S57]

## Reconcile already-paid and retained credit

Keep four distinct amounts: gross remuneration; the payroll withholding base; separately certified tax withheld; CIS/CO2 already paid. A missing or unread credit is **unknown**, not zero.
Corrected certificates replace the relevant earlier version; duplicate images/bundles do not add another payment. [C · S112; S124; B for extraction]

Let P be credits already paid and E the entitlement retained after the applicable reconciliation.
The adjustment is **P−E**: positive is recovery, negative is extra relief. A positive credit recovery strictly below EUR 12 is treated as zero **per spouse**. Exactly 12 is not below 12; this is not a waiver of all small tax balances and does not erase small refunds. [C · S57 p.3]
Whether CIS and CO2 share this threshold or are tested separately is not explicit in the paid-versus-retained examples. PIT-O-24 records that uncertainty; automatic calculation stops where the two readings change the result. [O; B for the guard]

With T the assessed tax before these credits, W separately certified withholding **before** CIS/CO2, and A advances, an ordinary-salary-only indicative calculation is:

`balance = T − W − A + (P − E)`

Apply the credit-recovery rule first. This is arithmetic interpretation of the reconciliation, not a universal final assessment algorithm. If W is already net of paid credits, do not add P again. Other credits, foreign withholding and statutory final-balance rounding need their own rules. If P=E the adjustment is zero: absence of another full CIS subtraction is not itself an error. [I · S57; S82 art. 154]

## CISSM has a different base and payment route

For a complete full-time month in 2025, the base credit is 81 for monthly gross 1,800–3,000, 81/600×(3,600−gross) above 3,000 and below 3,600, and zero below 1,800 or from 3,600. For shorter or part-time work, determine notional full-month/full-time gross under the same remuneration conditions, then proportion the credit by hours. Round upward to cents. A low annual or actual monthly wage does not by itself establish entitlement. [C · S82 art. 139quater; S125]

Non-time-proportional benefits are not multiplied by the hours factor. Nonperiodic remuneration up to the statutory annual limit is conditionally ignored, unless replacing ordinary salary;
crossing it later affects the later month's test in the official example. This is not an annual Form 100 deduction. Retain actual and theoretical hours, normal pay, benefits and bonus history.
[C · S82; S125; B for intake]

Ordinary CISSM is granted through proper tax-card payroll. **Exception:** article 139quater(6) permits ACD payment after year end on request for qualifying Luxembourg-taxable salary not subject to tax-card withholding. Do not say it can never be requested after the year, but do not invent a Form 100 CISSM box either. The exact filing route remains RET-O-02. [C · S82 art. 139quater(4),(6);
O for the submission mechanism]

For simplified domestic employment, CCSS CISSM is per contract; CCSS CIS/CO2 instead requires all salary income to fall under 137(5). Consult domestic-employment-income.md for the household-wide income election and unresolved mixed/no-election credit case. [C · S82 arts. 139quater(5),154quater(3);
S113; O · PIT-O-21]

## Worked examples — invented components

- Full qualifying year, ordinary multi-card gross 60,000: retained CIS300 and CO296. If already paid CIS600 and CO2192, recovery396. With taxbeforecredits8,000 and withholding 7,000, indicative balance1,396, not 604. [I · S82; S57]
- Already paid 792 and correctly retained 792: adjustment0. Do not subtract792 again from tax less separately certified withholding. [I · S57]
- Recoveries 11.99 and 12 for two spouses: waive only the first; do not pool23.99 before the test.
  An extra-credit amount 11.99 is not suppressed by this recovery rule. [I · S57]
- Annual gross 40,000.99 floors to 40,000 before the 2025 schedule; a partial-year credit still needs its qualifying-period adjustment. [I · S124]
- A part-time CISSM case needs hours and fixed-benefit treatment. The official January half-time example uses92/184 hours and produces40.50; do not infer that result from annual gross alone.
  [C · S125 example 3]

## Software and source boundaries

The household balance estimator implements the ordinary 2025 salary route described in [salary-balance-calculator.md](salary-balance-calculator.md): full-year resident tax liability, reviewed class 1 without children or joint class 2, complete supported income/deductions, and explicit affiliation, credit-period and card-history evidence. A full eligible year permits annual CIS/CO2 recomputation where the assessment gate applies. Checked one-card final payroll amounts can instead be retained, including a verified partial-period payroll result. Partial-period annual recomputation, same-person mixed categories, special regimes and a result affected by the unresolved CIS/CO2 small-recovery grouping (PIT-O-24) stop for review. [B]

The supported household route computes the extra-professional allowance from each spouse's relevant net-income limit; any supplied `extra_professional_amount` must match. The direct calculator still requires a reviewed amount for joint professional income. PDF/XML salary preparation and a final tax balance have separate input and scope checks. [B]

Keep `cis` and `co2` as the actual annual certificate-paid amounts used by the return; never replace them with the calculator's retained entitlement. Known zero can be entered as 0; missing/null credits stop XML creation and balance calculation. Negative monthly corrections must remain in the annual total. A negative annual paid total requires reviewed manual preparation: the generator and balance estimator's non-negative input scope is narrower than the signed XSD fields and does not invalidate the certificate. [B]

The old ACD withholding-declaration page still reproduces 2009 credit amounts and a blanket no-assessment statement. Those passages are superseded for 2025 by the statute and March 2025 circulars; do not create an unresolved conflict from obsolete guidance. [C · S82; S57; S124]
