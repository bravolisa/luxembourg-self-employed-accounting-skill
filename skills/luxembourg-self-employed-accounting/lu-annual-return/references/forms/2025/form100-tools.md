# Form 100 tools – filled PDF and MyGuichet XML (tax year 2025)

_Figures in this file: 2025–2026. The year files of lu-income-tax-personal win if they differ._

The scripts in `scripts/` turn one household file into a filing:
- **`fill_form100_pdf.py`** fills the ACD's fillable Form 100 PDF;
- **`build_form100_xml.py`** builds the XML that pre-fills the MyGuichet procedure;
- **`make_receipts_annex.py`** writes the « Détail des recettes » annex (attachments.md);
- **`read_myguichet_summary.py`** reads back the PDF MyGuichet makes of the upload;
- `form100_household.py` is their shared part: the checks, the ceilings and the PDF box map.

They were built on a real 2025 return in October 2026 (myguichet-xml.md) and reproduced that return's PDF and its MyGuichet upload exactly. [P]

They are a BravoLisa workflow, not an ACD tool: the person or their adviser checks and signs the result. [B]

## Setup

Packages: `scripts/requirements.txt` (pypdf, lxml, reportlab, pinned; tested with Python 3.9). Install them once into a virtual environment – the skill's SKILL.md, « Tools », gives the commands – and run every script with that environment's Python. The macOS system Python has no pypdf. [B]

- **Blank form**: https://impotsdirects.public.lu/dam-assets/fr/formulaires/pers_physiques/2025/100f-2025.pdf. A copy is in this skill: `official-forms/100f-2025.pdf`. [C · lu-income-tax-personal S1]
- **Import schema**: the 2025 zip on the ACD's page (lu-income-tax-personal S69), or the copy in this skill, `official-forms/F100-XSD-2025.txt`, which the script reads as it is. [C · lu-income-tax-business S62]
- **Tax year 2026**: neither the schema nor the form is out yet (lu-tax-core watch list W-17 and W-08). The builder takes the year from the household file and stops on a schema of another year; the PDF box map is for 2025 only. When they come out: library copy, box numbers checked, tool tests, then a `--minimal` test upload. [B]
- **The household's data stays in the household's own folder** (household file, values file, outputs) – never inside this skill's folder. Keep a short work log of which document each figure comes from. [B]

## Workflow

One **household file** feeds every output (PDF, XML, receipts annex), so they cannot drift apart. The scripts share its checks, ceilings and box map (`scripts/form100_household.py`); the ceilings come from `lu-tax-core/data/tool-figures.json`. [B]

1. **Collect the documents**: salary certificates (one per employer), the CCSS certificate, the insurers' and the savings bank's yearly certificates, the business forms (110/152, 112, 113), last year's return (lu-annual-return documents.md).
2. **Write the household file** (format below) in the customer's folder. Every figure comes from a document; note which one in the work log.
3. **Early test upload** – before any figure is checked, test the file format and the identity pages:
   ```
   python scripts/build_form100_xml.py --household household.json --xsd F100-XSD-2025.txt --out test.xml --minimal
   ```
   Upload it in MyGuichet (« Déposez un document complété »), look at the first pages, then delete that procedure. A refusal here costs minutes, not a day. [P · myguichet-xml.md]
4. **PDF**:
   ```
   python scripts/fill_form100_pdf.py --blank 100f-2025.pdf --household household.json --out filled.pdf
   ```
   It applies the ceilings, recomputes the form's own totals and checks box 2038 against the household's indicative taxable income (MATCH, or it stops). `--values` instead of `--household` fills box by box (the values file, below).
5. **XML**:
   ```
   python scripts/build_form100_xml.py --household household.json --xsd F100-XSD-2025.txt --out return.xml
   ```
   It validates against the schema and prints the same indicative taxable income as box 2038.
6. **Upload** the full file, go through every page and attach the documents.
7. **Compare MyGuichet's own PDF** with your figure before signing:
   ```
   python scripts/read_myguichet_summary.py --pdf ACD_F100_2025.pdf --expect <box 2038>
   ```
   It reads both the printable summary and the dynamic (XFA) form (myguichet-xml.md). A difference: find the field, fix the household file, rebuild, upload again.
8. **Receipts breakdown** on the receipts-and-expenses method: attach a « Détail des recettes » when receipts include VAT refunds or Mutualité (attachments.md). From the same household file:
   ```
   python scripts/make_receipts_annex.py --household household.json --out Annexe_Detail-des-recettes.pdf
   ```
   One French page per business, its total checked against the receipts.

**Tests**: `scripts/tests/test_form100_tools.py` runs the scripts on invented households against hand calculations. Run it after any change to a script or to the figures (the curator runs it at every release). [B]

## Additional reviewed deduction routes

Insurance risk `PU` now has a supported own-life housing branch, with explicit history and role checks. Consumer interest, current cash donations and bounded class 1a/CIM support are specified in [form100-deductions.md](form100-deductions.md). Wider cases keep their review stops. [B]

Employment costs, occupational/voluntary contributions and exact retirement-contract dates: [employment-deductions.md](employment-deductions.md). Separate benefits, exemptions and workplace periods: [salary-details.md](salary-details.md). Registered partners and medical costs: [medical-and-partnership.md](medical-and-partnership.md). These guides define the required evidence and explicit stops. [B]

## The household file

Invented example: `scripts/examples/form100-2025-myguichet.example.json`; three more invented households (a single liberal profession, an agent filing from a PRO space, a balance-sheet profit) are in `scripts/tests/households/`. Three further family fixtures cover children, childcare and own-home interest; their input and boundaries are in [form100-family.md](form100-family.md). ID numbers in the example are placeholders `YYYYMMDDNNNNN`, and the scripts refuse to run until they are real 13-digit matricules.

| Key | Content |
|---|---|
| `tax_year`, `space` | 2025; `private` or `pro` – sets the form type `ACD_F100_2025` / `_PRO` |
| `filed_by`, `agent` | `self`, or `agent` with `capacity` (`PART` private person, `PRO` professional, `AVOCAT`), `kind` (`PP` natural, `PM` legal person + `company`), `last_name`, `first_name`, `email` or `phone`. Each spouse signs a Form 101 for the agent (myguichet-xml.md) |
| `consent` | first page, consent to automated taxation: `true`, `false`, or `null` to leave it to the filer |
| `eligibility` | `true` pre-fills the eligible answers; « own household » becomes No for an agent |
| `file_number`, `tax_office` | 11 digits; office code |
| `address` | `postcode` without « L- », `locality` from the official list (e.g. `Esch-sur-Alzette`), `street`, `number` |
| `taxpayer`, `spouse` | `last_name`, `first_name`, `national_id`, `phone`, `email`, `status` on 1 January (`MA` married, `PA` partners, `CE` single; all codes and the changes during the year: family-events.md), `status_since` |
| `businesses[]` | `owner`, `kind` (`commercial` / `liberal`), `activity`: liberal codes (`TRAD`, `ARCH`, `INGE`, `EXPE`, `AUTR`…) or commercial (`AGAS`, `AUTR`); `activity_other`, `trade_name` (commercial), `start`, `end`, `main`, `method` `REDE` with `receipts` and `expenses` (VAT included, depreciation in the expenses) or `BILA` with `profit`; `file_number`; `investment_credit` (commercial) |
| `salaries[]` | one per salary certificate: `owner`, `occupation` (`SALA`), `employer`, `start`, `end`, `workplaces` (official **commune** names in capitals, e.g. `SCHENGEN` for Remerschen), `pay` (`S` salary, `IMAL` sick pay advanced by the employer – the certificate's « maladie patron »), `contributions`, **`travel`**, `taxable_base`, `withheld`, `cis`, `co2` |
| `insurance[]` | `insurer`, `risk` (code), `paid_by`, `amount` |
| `home_savings[]` | `holder`, `bank` (code), `contract_date`, `amount` (payments + credited interest) |
| `pension_plans[]` | `holder`, `insurer`, `start`, `end`, `amount`, `pepp` |
| `ccss_self_employed[]` | `owner`, `deductible`, `non_deductible` (dependency), `mutualite` reimbursements |
| `dac6` | `false` unless a reportable arrangement was used |
| `advances_paid` | Income-tax advances paid in the year – no box on the form; read only by lu-income-tax-personal `tax_estimate.py --household` for the balance |
| `receipts_breakdown` (in a business) | `customers`, `vat_refunds` (`vat_year`, `amount`), `mutualite`, `other` (`label`, `amount`), `notes` (French sentences printed under the table, e.g. the VAT-turnover reconciliation); must add up to `receipts` – the « Détail des recettes » (attachments.md) |
| PDF only | `birth_place`, `profession` (per person); `tax_office_address` (lines separated by `\r`); `joint_taxation_option` (married316/317, reviewed partner312; see partnership guide); `workplace_label` (a salary's place of work as printed, e.g. the locality); `label` (an insurance line's caption); `bank_name`, `subscriber_id` (home savings); `signature_place` |

## The values file (box by box, PDF only)

For a box or subcase the household file does not cover yet. Format: `{"fields": {"N.0605": {"value": 46500, "why": "receipts per annex"}, …}}`. The `why` is optional but keeps the return traceable. Invented example: `scripts/examples/form100-2025-pdf-values.example.json`.

| Field name | What | Example |
|---|---|---|
| `A.<box>` | text | `A.0101` name, `A.0752` place of work |
| `N.<box>` | amount (number) | `N.0702` salary; `N.1021` own-home interest as a **minus** figure |
| `D.<box>` | date `dd/mm/yyyy`; the child's date of birth `D.0202` is a 13-cell box: `YYYYMMDD` | `D.0305` married since |
| `F.<box>` | cell box | `F.0105` matricule (or `YYYYMMDD`), `F.0109` file number (11 digits), `F.1` file number at the top of every page |
| `R.<box>` | radio button, by state | `R.0301` `/marie`, `/celibataire`, `/divorce`, `/veuf`; `R.0317` `/3` joint taxation; `R.1915` `/DAC6N` |
| `C.<box>` | check box | `C.0316` `/Yes` |
| `T.Bureaux_d_imposition` | tax office code | `E2` (codes: the form's list; which office: lu-income-tax-personal forms/2025/form-100.md §8) |

Rules when filling box by box [C · lu-income-tax-personal S1]:
- Type every **capped** amount yourself – 1471, 1527/1528, 1551/1552, and the flat minimum in 1554. The script recomputes only the form's own totals.
- Commuting is one yearly amount in 747/748.

## Traps found on a real return

- **Commuting is not computed by MyGuichet**: give each salary its own share in `travel` – compute the person's global eligible amount first using lu-income-tax-personal payroll-certificate-deductions.md; the portal observation is in myguichet-xml.md. [P]
- **CIS and CO2 credit fields are required** in MyGuichet (myguichet-xml.md): the script requires known certificate-paid amounts; missing or null is not zero. [P]
- **Savings-bank codes**: BHW Bausparkasse is **`BB`**; `BH` is Bausparkasse Schwäbisch Hall. [C · lu-income-tax-business S62 – code list]
- **Insurance risk codes**: an insurer's certificate lists the premiums « déductibles au titre des dépenses spéciales » per contract. For a car policy the deductible lines – liability, protected driver, traffic accident – go under **`VV`** « Véhicule (montants fiscalement déductibles) »; private liability under `RC`; health under `AM`; life under `AV`. [C · lu-income-tax-business S62 for the codes; I for the matching]
- **Workplace**: the commune, not the locality. A wrong name fails the schema check. [C · lu-income-tax-business S62]
- **File format**: the script writes it the way MyGuichet accepted it (myguichet-xml.md « File format »). Do not reformat the file in an editor. [P]

## Not covered yet (the script stops)

Rental income, pensions, capital income, incoming donation carryforwards and extraordinary charges other than the supported childcare subset. Ordinary consumer interest, current cash gifts, own-life housing PU and bounded single-parent relief use [form100-deductions.md](form100-deductions.md). Supported 2025 children/own-home/childcare cases and explicit subcase stops are in [form100-family.md](form100-family.md). Those new sections require the later live read-back in RET-O-01; offline validity is not observed portal acceptance. [B]

**A change during the year** – marriage, partnership, separation, divorce, a spouse's death, a spouse at another address, an earlier address, who signs: the household keys `status_changes`, `separation`, `spouse_address`, `earlier_addresses`, `signature` and `status_review`. Inputs, what is written and where the tools stop: [family-events.md](family-events.md). [B]

The household keys `resident_full_year`, `children`, `own_home` and `childcare` are defined in [form100-family.md](form100-family.md). The PDF writer produces a separate monthly childcare annex when needed. [B]

## Salary safeguards added after document review

Use ordinary salary input only after classification. `tax_regime` defaults to `ordinary` for legacy inputs; intake must not use that default to conceal unknown or domestic-flat treatment. A different regime, occupation SRF5/SRFA, or pay nature SALF/SAFA stops generation pending the household election and reviewed manual route. See the personal-tax salary guides. [B]

`cis` and `co2` must be explicitly known for XML (zero is accepted when evidenced). The current generator supports non-negative annual paid amounts only. An evidenced negative annual total requires reviewed manual input; retain its sign and never coerce it to zero. The XSD itself uses signed decimals, so this is a tool boundary, not a legal prohibition. Salary FD is checked per person against receipts and the annual ceiling; that check does not calculate a multi-workplace schedule. Employee flat costs are limited to receipts after FD. The second salary-recipient special-expense minimum is limited by the lower supported net salary; a negative remainder stops for review. Other salary-related article 110 expenses not represented in the household file need manual adjustment. Partial tax liability (`tax_liability_months` other than 12) also needs manual preparation. [C · lu-income-tax-personal S82; B for supported input scope]

The personal-tax household balance estimator supports reviewed 2025 ordinary salary cases for full-year Luxembourg resident tax liability: class 1 without children, or joint class 2 within the supported family model; also a class-2 year assessed alone, class 1a without a child and the joint year of a death on 31 December (family-events.md). See [salary-balance-calculator.md](../../../../lu-income-tax-personal/references/salary-balance-calculator.md) for the required `salary_balance` facts, logical certificate/card identities, known paid credits, withholding basis and completeness review. These extra balance facts are separate from PDF/XML preparation; a generated document does not establish eligibility for a final-balance estimate. [B]

The estimator reconciles paid versus retained CIS/CO2 where the assessment gate and full eligible year are established, or retains checked final one-card payroll amounts. It does not subtract a second annual credit. Partial-period annual recomputation, same-person mixed credit categories, special regimes and material CIS/CO2 small-recovery ambiguity (PIT-O-24) require review. Keep the salary records' `cis` and `co2` as actual certificate-paid amounts for the return; the calculated retained entitlement belongs in the estimate output, never back in those source fields. [B]

For the supported salary-household route, the extra-professional allowance is computed from each spouse's relevant income limit; a supplied `extra_professional_amount` must match. Other joint professional-income estimates still need a reviewed amount (`--extra-professional-amount` in the direct calculator). Business what-if scenarios stop when a positive spouse allowance is present:
the changed profit requires a new review. Compare separately reviewed calculations instead.
Older JSON fixtures with explicit zero-credit assumptions remain component/generation fixtures, not payroll-certified complete assessments. [B]

## Four-branch automation — 2026-11-04

The owner authorised implementation after the research list. All four now have bounded automatic support in [form100-deductions.md](form100-deductions.md), including inputs, calculations, PDF/XML distinctions and independent synthetic fixtures. Annual CIM rounding, competing donation vintages, crossed insurance roles and foreign-benefit moderation remain explicit review points.
Nonzero earlier PU use is supported in calculation/PDF but stops XML pending live semantics.
The `.deductions.pdf` annex preserves gross donations and explains capped totals. RET-O-01 remains open; no acceptance-suite pins or original client documents are changed by this release. [B]

## Special employment payments require review

Known employer interest support and termination compensation remain manual branches. Preserve `employer_interest_support` on the household, salary or loan record, and `termination_payment` on the household or salary record when present. The tools stop for those markers and for PPPH/IDPT/IDEP/IDCC/REX1/REX2 pay or exemption codes. Read lu-income-tax-personal employer-interest-support.md and termination-compensation.md; do not hide the benefit in ordinary salary or subtract all employer support in `subsidies`. Unmarked embedded components still require document review. [B]

Special-payment intake: documents.md defines the optional evidenced `special_payment_review` and preserved component `source_code`. Unknown/present reviews stop; a clear review cannot override known special codes. This is structured intake validation, not automatic text recognition. [B]
