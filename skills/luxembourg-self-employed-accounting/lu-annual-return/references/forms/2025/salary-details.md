# Certified salary details and replacement benefits — 2025

Figures in this file: 2025. Source identifiers belong to lu-income-tax-personal. Read 2026-11-05.

## Separate employee replacement payments

Employer-advanced sickness (`IMAL`) stays in the employer certificate, but must not automatically be treated as ordinary article 95 activity for the extra-professional allowance. Genuine statutory salary continuation and advances made for CNS are distinct. Direct employee sickness/maternity/accident benefits and unemployment have their own paper line. Classification follows articles 95/95a and the actual certificate; it is not inferred from the issuer's name. [C · lu-income-tax-personal S82; lu-income-tax-personal S112; lu-income-tax-personal S1]

For supported 2025 full-year residents, a salary record may use `source: employee_replacement`, `replacement_kind: sickness/maternity/accident/unemployment`. Require `employee_replacement_eligible: true`, `employee_replacement_evidence`, issuer in `employer`, `overlap_and_duplicates_reconciled: true`, `contributions_reconciled: true`. One gross `pay` row uses `IMAT` for maternity, otherwise `A` plus a precise description fitting the schema. Occupation is `DEMP` for unemployment, otherwise `SALA`. No commuting deduction, exemption or invented work-period row is allocated to the replacement payment. [B; XML codes C · lu-income-tax-personal S75]

The shared validator requires household ownership, ordinary regime, `all_pay_luxembourg_taxable: true`, unique logical `certificate_id`, valid 2025 dates, known `tax_card_id` (or evidenced null), `withheld`, `withholding_basis`, `contributions`, `cis`, `co2`, and `cim` including explicit zeros. Corrected/superseded copies and equivalent duplicate records stop. Nonzero paid CIM requires the supported single-parent reconciliation. Other paid credits and unexplained negative pre-credit withholding stop. These facts are required for PDF/XML as well as the balance, so unknown withholding cannot silently become zero. [B]

Paper: aggregate benefits into709/710; they do not consume employer slots701/705 or 702/706. XML contains the correct pay kind and description. The official XML requires a workplace commune even for a benefit. The tool therefore refuses XML without a nonempty commune and `xml_workplace_review` containing `authoritative_semantics_confirmed: true` and actual `authority_evidence`. Never use the CNS/ADEM office address or invent this confirmation. Calculation/PDF do not require a fabricated workplace. RET-O-03 remains open. [C · lu-income-tax-personal S1; lu-income-tax-personal S75; B/O for guard]

Annual salary-credit eligibility, tax-card history and complete periods still follow salary-balance-calculator.md. A joint household with article 95a benefits, known `IMAL`, or `includes_cns_advances: true` uses only the separately evidenced full-cap proof described in salary-balance-calculator.md; otherwise it stops the extra-professional calculation pending PIT-O-35. [B/O]

## Certified payroll exemptions

A source certificate may have `exemptions[]`: one `HSUP` and/or one `SJFE`, each with `amount`, `included_in_gross: true`, `certified_exempt: true`, `eligibility_evidence`, `contributions_reconciled: true`, `not_deducted_elsewhere: true`. HSUP additionally requires established `private_sector_eligible_overtime: true`, `not_senior_manager: true`. These are evidence assertions, not switches to make ordinary pay exempt. Review each certified exemption and deductible contribution amount. [B; C · lu-income-tax-personal S82 art.115; lu-income-tax-personal S155; lu-income-tax-personal S112]

Gross salary includes the exempt amount once. The exemption reduces taxable salary and relevant net-income limiters, but does not reduce the statutory gross salary-credit base. Never recompute compulsory contributions from the exempt amount. Paper730/731 is overtime;734/735 is night/Sunday/holiday supplementation. XML uses PRE_EXEMP and `SAL_NAT_EXEMP_NEX` / `SAL_MNT_EXEMPT_NEX`. A low taxable-receipt remainder whose flat-cost treatment is unresolved stops. [C · lu-income-tax-personal S1; lu-income-tax-personal S75; lu-income-tax-personal S82 art.154quater; lu-income-tax-personal S124; B for guarded implementation]

## Dated workplaces

For actual employer records use `workplace_periods[]` with `commune`, `start`, `end`, `frequency`, `frequency_unit: week/month`, `evidence`. Dates lie within that certificate and tax year. Require complete person-year coverage of workplace rows, at most two paper rows per person, and household `commuting_review` (`periods_complete`, `annual_amount_reviewed`, `evidence`). `workplaces` must match the unique communes. FD remains an independently reviewed annual amount; periods do not calculate distances or commute entitlement. [B; C · lu-income-tax-personal S152; lu-income-tax-personal S119; lu-income-tax-personal S120]

Paper taxpayer rows: A0763,D0765,D0766,N0772,R0769 then A0771,D0773,D0774,N0777,R0777. Spouse: A0764,D0767,D0768,N0773,R0770 then A0772,D0775,D0776,N0778,R0778. The surprising N0772 first-row frequency is the actual widget name; do not substitute the printed commune box number. XML preserves unique communes but has no equivalent period/frequency elements. [C · lu-income-tax-personal S1; lu-income-tax-personal S75]


## S-coded gross may contain advances

The official 2025 ECSP guide permits employer-advanced sickness gross to be included in salary gross with `IMAL` omitted. An employer issuer or an `S` code alone therefore cannot prove the ordinary component used in the new allowance proof. Set `includes_cns_advances: true` when such advances are known, and reconcile ordinary gross separately. Do not infer advances merely from illness or an employer reimbursement: genuine salary continuation has a different basis. [C · lu-income-tax-personal S169 §2.2.19; lu-income-tax-personal S112 note2; lu-income-tax-personal S170; B for flag]

The XSD accepts commune `AUTR`, but no authoritative direct-benefit/no-workplace meaning was established. Occupation `SANS` is not a supported bypass. The old 2021 integrator guide and the payroll ECSP prevalidation service do not establish 2025 Form100 semantic acceptance. RET-O-03 remains open. [C · lu-income-tax-personal S75; lu-income-tax-personal S171; lu-income-tax-personal S69; O for mapping]

## Special employment payments require review

Known employer interest support and termination compensation remain manual branches. Preserve `employer_interest_support` on the household, salary or loan record, and `termination_payment` on the household or salary record when present. The tools stop for those markers and for PPPH/IDPT/IDEP/IDCC/REX1/REX2 pay or exemption codes. Read lu-income-tax-personal employer-interest-support.md and termination-compensation.md; do not hide the benefit in ordinary salary or subtract all employer support in `subsidies`. Unmarked embedded components still require document review. [B]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
