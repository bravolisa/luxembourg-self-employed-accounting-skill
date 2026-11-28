# Salary certificates — 2025 Form 100 mapping

Figures in this file: 2025 – the year files win if they differ.

Use payroll-certificate-deductions.md, domestic-employment-income.md and employee-tax-credits.md before mapping. Raw document fields, allowed annual amounts and credits already paid are distinct.
This map describes reviewed manual preparation; it does not expand every automatic tool branch. [B]

## Paper form

| Meaning | Page / taxpayer / spouse | Boundary |
|---|---|---|
| First ordinary employment gross |7 / 701 / 702|Gross includes employer-advanced sick pay already within the subtotal.|
| Second ordinary employment gross |7 / 705 / 706|A second certificate is not another employee cost minimum.|
| Separately paid sickness/maternity/accident/unemployment benefits |7 / 709 / 710|Obtain payer evidence; do not repeat an amount already inside employer gross.|
| Other ordinary salary contracts |7 / text 713, 714 / 715|Explain the additional contracts; flat-regime remuneration has its own row.|
| Art. 137(5)/137(5a) remuneration on a regularisation request |7 / 722 / 723; exempt 724 / 725|Row E; all relevant flat remuneration, with election and complete certificates.|
| Employee earning costs |7 / 743 / 744|One allowed actual/flat amount per person; statutory receipts and period limits.|
| Commuting |7 / 747 / 748|One reviewed global annual amount, with workplace detail 763–778.|
| Compulsory deductible contributions |16 / 1601 / 1602; exempt 1603 / 1604|Exclude dependency; do not subtract it twice from a deductible certificate amount.|
| Personal employee LRCP contributions |16 / 1605 / 1606; exempt 1607 / 1608|Separate regime and cap; outside the special-expense minimum.|
| Salary tax withheld |19 / 1901 / 1902|Do not replace it by tax less credits or include excluded flat withholding.|
| AC / FFO / FDS / FO / DS / CE inscriptions |No direct copy as a second annual claim|Reassess the underlying annual category and eligibility.|

[C · S1 pp. 7, 16, 19; S112; S82; I for the certificate bridge]. Exempt-income columns have different tax consequences; their presence is not evidence that a foreign-language certificate is foreign or treaty-exempt income.

## Domestic XML structure — manual reference, not live validation

| Meaning | Taxpayer element | Spouse element |
|---|---|---|
| Occupation |S0040_SAL_GEN_ACT = SRF5|S1100_SAL_GEN_ACT = SRF5|
| Pay nature |S0200_SAL_NAT_SAL_NEX = SALF|S1260_SAL_NAT_SAL_NEX = SALF|
| Gross pay |S0240_SAL_MNT_BRUT_NEX|S1300_SAL_MNT_BRUT_NEX|
| Social contributions |S0380_SAL_MNT_COTSOC_NEX|S1440_SAL_MNT_COTSOC_NEX|
| Non-deductible contributions |S0400_SAL_COTSOC_NDED_NEX|S1460_SAL_COTSOC_NDED_NEX|
| Tax withheld |S0600_SAL_MNT_RETENUE|S1660_SAL_MNT_RETENUE|
| CIS already paid |S0620_SAL_MNT_CIS|S1680_SAL_MNT_CIS|
| CO2 already paid |S0635_SAL_MNT_CO2|S1695_SAL_MNT_CO2|
| CIM already paid |S0640_SAL_MNT_CIM|S1700_SAL_MNT_CIM|

[C · S75 v0.18.0]. Temporary flat-regime workers use SRFA/SAFA, not domestic SRF5/SALF.
No dedicated domestic-election checkbox was established in the schema search; preserve the request explicitly in reviewed working data and supporting explanation. The comments do not prove whether the social-contribution field is before or after the separately entered non-deductible component. Do not populate both by guessing their arithmetic. RET-O-01 covers authoritative semantics and live import/read-back. [O · S75]

Ordinary XML credit fields require known certificate-paid values, including explicit zero when proved. Absence, unread OCR and a zero printed on the certificate are different states. The builder now stops for missing CIS/CO2 and for declared flat regimes. The generic box-by-box PDF filler can accept reviewed manual values, but does not decide the tax treatment. [B]

## Intake identity and coverage

Preserve issuer, person, employer, covered year/period, role, regime, source-document identity and replacement/duplicate relationships. Compare salary components to the subtotal, monthly records to the annual certificate, and corrections to their predecessor. Images and grouped PDFs can represent the same certificate. A mandate or transmission receipt is procedural evidence;
neither proves an amount or a final tax assessment. Do not carry an old-year deduction forward merely because its certificate or submission receipt was issued in the target year. [B]

Interest support, termination compensation and extraordinary amounts: see [special-employment.md](special-employment.md). Certificate pay and exemption codes are distinct; do not copy exempt employer support into a generic interest-subsidy subtraction. [B]

For benefits embedded in ordinary salary subtotals, follow lu-annual-return references/documents.md special-payment review. Retain the original component code and whether its amount is included in gross. Lack of a separate code does not establish absence. [B]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
