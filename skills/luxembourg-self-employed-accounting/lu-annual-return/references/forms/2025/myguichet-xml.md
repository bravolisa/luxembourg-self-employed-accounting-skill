# MyGuichet 2025 return – pre-filling with an XML file and checking the result

_Figures in this file: 2025–2026 (the commuting maximum is unchanged in 2026). The year files of lu-income-tax-business win if they differ._

The assistant itself (branches, mandatory uploads, what the ACD tutorial says): [myguichet.md](myguichet.md). The scripts that write the file and read the result back: [form100-tools.md](form100-tools.md). Tax year 2026: the schema is not published yet (lu-tax-core watch list W-17).

## Pre-filling the assistant with an XML file (tax year 2025)

From the ACD's page on electronic filing (lu-income-tax-personal S69) and the 2025 import schema (lu-income-tax-business S62; library F100-XSD-2025). Learned by building a file for a real household in October 2026; it uploaded once written as described under « File format ». [P]

- **Upload**: in MyGuichet, « Déposez un document complété »; the file creates the procedure « ACD (Modèle 100) » and fills it in. Two form types, same content: `ACD_F100_2025` for a private space, `ACD_F100_2025_PRO` for a PRO space. [C · lu-income-tax-personal S69; lu-income-tax-business S62]
- **Agent**: the return can be filed « par un intermédiaire (mandataire, fiduciaire ou autre) »; then « un formulaire (Mandat de dépôt ACD) doit être rempli et joint à la démarche ». That form is Form 101 « Contrat de mandat »: one per taxpayer, for one tax year, the agent being a natural or a legal person. [C · lu-income-tax-personal S69; lu-income-tax-personal S70] The schema records the agent's capacity (professional, lawyer, or private person « Particulier ») and who signs: each spouse in their own name, one spouse for both, or the agent for one or both. [C · lu-income-tax-business S62]
- **It follows the assistant, not the PDF's boxes**:
  - salaries are entered per salary certificate – employer, period, workplace **commune** from the official list (not the locality), pay by nature (« Salaire »; employer-paid sick pay has its own code, « Indemnités pécuniaires de maladie avancées par l'employeur »), social contributions, « Frais de déplacement », the taxable base and the tax withheld;
  - a commercial profit is given by method (« Bilan et P&P » or « Recettes et dépenses ») with gross receipts and actual expenses;
  - the CCSS certificate's deductible and non-deductible contributions and Mutualité reimbursements;
  - insurance premiums by insurer, risk code and payer – the deductible lines of a car policy under « Véhicule (montants fiscalement déductibles) » (`VV`) [I];
  - home savings by savings-bank code, contract date and contributions – BHW Bausparkasse is `BB`, while `BH` is Bausparkasse Schwäbisch Hall.
  
  Ceilings and totals are computed by the assistant. [C · lu-income-tax-business S62 – field labels]
- **No bank-account block** in the 2025 schema (the 2021 example had one) – matching the 2025 PDF. [C · lu-income-tax-business S62]
- **First page and eligibility can be pre-filled, both optional**:
  - `Introduction/G0010_CONSENTEMENT` is the consent to automated taxation – the return can be assessed without an ACD officer and checked by one within 5 years. [C · lu-income-tax-personal S61] The ACD's 2021 guide calls it the RGPD consent and its example leaves it `false`, so that the filer ticks it in MyGuichet. [C · lu-income-tax-personal S69] An agent gives it under Form 101 (« la signature et le consentement RGPD au nom et pour le compte du mandant »). [C · lu-income-tax-personal S70]
  - `Eligibilite` holds ten yes/no questions, G9010–G9090: LuxTrust product, national ID number for each spouse, filing for the household, married or in a partnership during the year, revoking an assimilation, individual taxation, married more than once, same country of residence, change of country. [C · lu-income-tax-business S62] A wrong answer sends the filer to the PDF or paper return; the ineligible cases are listed in the tutorial (myguichet.md). [C · lu-income-tax-personal S61]
- **File format** – write it like the ACD's example file: `<?xml version="1.0" encoding="UTF-8"?>` with double quotes, Windows line ends (CRLF), UTF-8 without BOM, and the root `<eForm xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="…xsd">`. A file that was valid against the XSD but had a single-quoted declaration, Unix line ends, no `xsi` root attributes and no « Introduction » block was refused with « The service is temporarily unavailable. (code: SyntaxError) ». The same content written as above uploaded fine (October 2026). Which detail mattered is not known, so keep all four. [P]

## What MyGuichet does with an upload

[P · MyGuichet, October 2026] Seen on a real 2025 return:

- **Commuting is not computed from the communes.** In the observed return, the salary summary summed the « Frais de déplacement » (S1500) supplied in the salary blocks. That observation does not establish a per-job entitlement or a universal monthly allocation. First determine one reviewed amount per person from periods and the multi-workplace schedule, then allocate it to the blocks without duplication. A blank certificate FD line is not proof of zero annual entitlement. See lu-income-tax-personal payroll-certificate-deductions.md. [P for the observed summary; C · lu-income-tax-personal S82, S119–S121 for the legal limits; B for allocation workflow]
- **CIS and CO2 credit fields are required** in each salary block (« Enhanced employee tax credit (CIS) », « Enhanced CO2 tax credit for employees »), although the XSD makes them optional: enter what the certificate shows, 0.00 when nothing was paid.
- **Agent**: answer **No** to « Do you file on behalf of your own household? » (G9025 – « You are declaring on behalf of a third party »). MyGuichet then says the agent gets no ACD pre-filled data (« due to GDPR constraints »), so the XML is the only pre-fill. For a couple filing themselves, MyGuichet asks for two LuxTrust products or a power of attorney.
- The summary pages show the ceilings it applies (« provided for purely indicative purposes ») and the taxable income. Compare that figure with your own calculation before signing.

## Checking what MyGuichet made of it

[P · MyGuichet, October 2026]

- **Two kinds of PDF** for the same procedure:
  - a **printable summary**: plain PDF, each value with its field code, e.g. « R1530 TAXABLE INCOME »;
  - the **dynamic form**: an XFA form that viewers other than Adobe Reader show as « requires Adobe Reader 8 or higher ». Its data sit inside the file and can be read without Adobe.
- **Field codes worth checking:**

  | Code | What |
  |---|---|
  | C2460 / R3040 | business profit |
  | R3120 | liberal-profession profit |
  | S2780 | gross salaries |
  | S2900 | travel expenses |
  | S3260 | net salaries |
  | D4120 | total special expenses |
  | **R1530** | **taxable income** |

  The summary also shows MyGuichet's indicative ceilings next to each special expense.
- `scripts/read_myguichet_summary.py --pdf <file> --expect <your taxable income>` reads either kind and compares R1530 with your figure.

## New family sections: offline checked, live read-back pending

The 2025 generator now emits registered child persons/Enfant records, one taxpayer-side own-home property containing both spouses' amounts, and childcare provider/payer/month groups. Its actual costs and allowed amounts are distinct. Detailed contract: [form100-family.md](form100-family.md).
These additions are not covered by the earlier real-return observations above. RET-O-01 records the outstanding semantic import and summary comparison. [B; schema: lu-income-tax-personal S75]

Salary update: missing CIS/CO2 paid amounts now stop output instead of becoming zero. Domestic occupation/pay codes exist in the XSD but require the separate regime/election workflow; see lu-income-tax-personal forms/2025/salary-certificates.md. Contribution-field subtraction and live election/read-back remain RET-O-01. [B/O]

## Four additional supported branches, 2025

The ordinary consumer-interest and current-cash-donation sections, supported CIM requests/monthly support/paid salary credits, and own-life housing PU with confirmed zero prior increased use are now generated. The full input contract is [form100-deductions.md](form100-deductions.md).
PU adds the direct residence registry before referencing it; numeric child counts are integer strings, not decimal amounts. Prior-use PU and incoming donation carryforwards still stop XML.
Actual amounts, allowed deductions and paid credits remain distinct. XSD validation does not verify retained recap semantics or live recalculation: RET-O-01 remains open. [B]

## A change of civil status or address during the year

The schema holds the status on 1 January, then up to ten later statuses with their dates, and the other addresses of the year with their periods. Field map, codes, eligibility answers, the signature after a death and what to enter for each event: [family-events.md](family-events.md). The builder writes them from the household file (`status_changes`, `spouse_address`, `earlier_addresses`, `signature`). [B]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
