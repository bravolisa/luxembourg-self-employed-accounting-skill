# 2025 manual form map: other income and extraordinary charges

_Figures and forms in this file: tax year 2025 only. These are versioned field identifiers and form labels, not 2026 figures._

Source: official 2025 Form 100 F [C · S1], Form 190/210 [C · S93], Form 200 [C · S107], and 2025 import XSD v0.18.0, modified 9 March 2026 [C · S75]. PDF pages 8, 9, 10, 16, 17 and 19 and rental page 4 were visually inspected. Supporting widget/type inventory is archived with the dated research.

This map supports manual preparation and future implementation review. It does not establish live MyGuichet acceptance, implement these branches, or resolve a substantive legal uncertainty. RET-O-01 remains open. Do not put an unresolved deduction at zero just to make an export work. [B]

## Pension, capital income, donations and tax already paid


Rendered and visually checked original blank PDF pages 8, 9, 16, 19 on 2026-11-04. **N** numeric-entry fields and **A** text fields are `/Tx`; totals use **T** (several are read-only), not independently editable money entries. Printed tax-office codes are not widget names. Do not confuse form box numbers with XSD identifiers.

| Page / topic | Paper box and actual widget | Meaning |
|---|---|---|
| 8 pension A | N.0801–N.0808, totals T.0809–T.0812 | gross; four columns taxpayer/spouse taxable then taxpayer/spouse exempt |
| 8 private annuity | N.0813–N.0816; N.0817–N.0820 | gross annuity; separate 50% exemption |
| 8 other annuity | N.0821–N.0828; A.0829 etc. | other gross/exemption; specify other exemptions |
| 8 total and costs | T.0848–T.0851; N.0852–N.0855; T.0856–T.0859 | total before category costs, costs, net pension; carry to 2017–2020 |
| 8 abatement | **C.0860 `/Btn`**; **D.0861 `/Tx`** | request; pension start date, not an amount |
| 8 dependency | printed 862–865 | **No corresponding AcroForm widgets** in this PDF; never invent N.0862–N.0865 |
| 9 dividends | N.0901–N.0902; N.0903–N.0906 | domestic qualifying dividends after 50% exemption; foreign qualifying category, taxable/exempt columns |
| 9 other categories | N.0907–N.0914; N.0915–N.0918; N.0919–N.0922 | other issuers; assessable interest; other capital income |
| 9 deductions/results | T.0923–T.0926; N.0927–N.0930; N.0931–N.0934; N.0935–N.0938 | sum; costs; income allowance; net to 2021–2024 |
| 9 dependency | printed 939–940 | **No corresponding AcroForm widgets** |
| 16 social contributions | N.1601–N.1604 | taxable/exempt, each person; exclude dependency |
| 16 gifts carryforward | N.1611–N.1612; N.1613–N.1614 | unused 2023; unused 2024, taxpayer/spouse |
| 16 gifts current | A.1615, 1618, 1621, 1624, 1627, 1630 and adjacent N amounts | six beneficiary rows; 2025 taxpayer/spouse amounts 1616/17, 1619/20, 1622/23, 1625/26, 1628/29, 1631/32 |
| 16 totals | N.1633/N.1634; T.1639 | current gifts per person; special-expense aggregate includes other sections too; attach excess ledger |
| 19 withholding | N.1901/N.1902; N.1903/N.1904 | salary; pension, each person |
| 19 capital tax | N.1905/N.1906 | Luxembourg capital withholding |
| 19 foreign credit | N.1907/N.1908; N.1909/N.1910 | treaty credit; no-treaty credit with annex; not raw foreign tax paid |
| 19 business interest | N.1911/N.1912 | non-final RELIBI business route; private final interest does not go here |

Page 9 says direct earning costs should be deducted from the related income, with detail in an annex or Form 180. Keep the annex's gross → exemption → allocated actual costs → subtotal explicit. Do not deduct the same actual costs again in the category summary. If a preparer's software places those costs in a summary box instead, reconcile net income and confirm its form-filling convention before treating it as an authoritative map. The ordinary no-actual-cost examples below avoid this presentation ambiguity. [C · S1, S75]

The official 2025 XSD import is **v0.18.0, last modified 09 March 2026**, from the ACD 2025 ZIP, cached evidence read 2026-11-04. Relevant elements (exact symbols; confirm surrounding required fields before emitting XML):

- `DonneesImpositionContribuable/PensionsRentes/Pension`: issuer `P0055_PEN_NOM_CAISSE`, period `P0060_PEN_DAT_DEB_ACT` / `P0080_PEN_DAT_FIN_ACT`; inside non-exempt detail, `P0160_PEN_MNT_BRUT_NEX`, `P0360_PEN_COT_SOC_DED`, `P0460_PEN_MNT_RETENUE`, **already-paid** `P0480_PEN_MNT_CIP`, `P0495_PEN_MNT_CO2`. Exempt gross `P0560_PEN_MNT_BRUT_EXO` and exempt contributions `P0640_PEN_COT_SOC_DED` are separate. Spouse nodes use their distinct P1180… identifiers; never reuse taxpayer IDs blindly.
- Private annuity: `P0760_PEN_RVI_IMP_LUX`, `P0780_PEN_RVI_111BIS`, `P0800_PEN_RVI_COM_ASS`, `P0820_PEN_RVI_MNT_BRU_AN`, `P0840_PEN_RVIA_EXP_115_14A`. Earning-cost choice `P0980_PEN_FO_MIN_FOR_EFF`, taxable/exempt amounts `P1000_PEN_FO_MNT_IMP` / `P1020_PEN_FO_MNT_EXO`.
- `AbattExtraProfPensions`: `P1040_PEN_ABATT_EXTRA_PROF` boolean; `P1060_PEN_RENT_PENS_DEPUIS` date.
- `CapitauxMobiliers/CapMobExemption50`: source country `M1000_CAP_MOB_PAYS_PROV`, company `M1020_CAP_MOB_DES_SOC`, type `M1040_CAP_MOB_TYPE_SOC`, **gross before exemption** `M1080_CAP_MOB_MNT_BRUT`; actual-cost detail `M1140...` / `M1160...` / `M1180...` / `M1200_CAP_MOB_NAT_FRA_MNT`; substantial participation `M1210_CAP_MOB_SOC_PAR_IMP`; withholding `M1220_CAP_MOB_RET_IMP_SOURCE`. Unlike paper box 901, XML gross is full gross, so do not halve twice.
- Capital recap: `M1601_CAP_MOB_REC_FOB_CHOIX`, `M1602_CAP_MOB_REC_FOB_MIN_FORF`, `M1600_CAP_MOB_REC_FOB` actual-cost summary, `M1620_CAP_MOB_REC_TRA_EXE`; foreign credit `M1680_CAP_MOB_REC_IMP_ETR_CNV` / `M1690_CAP_MOB_REC_IMP_ETR_HCNV`. Detailed and summary expense values represent the same expense, not two deductions.
- `DepensesSpeciales/DepSpeLiberalites/DepSpeLiberalitesDetail`: `D2080_LIB_NOM_BEN`, `D2100_LIB_VER_PAR_CONT`, `D2120_LIB_VER_PAR_CONJ`. Carry flag `D2220_LIB_REPORT`; 2023 `D2240_LIB_REP_ANN_MN2_CONT` / `D2260_LIB_REP_ANN_MN2_CONJ`; 2024 `D2300_LIB_REP_ANN_MN1_CONT` / `D2320_LIB_REP_ANN_MN1_CONJ`.
- Securities disposals have `RevenusNetsDivers` nodes including acquisition/disposal dates and proceeds. They are not `CapitauxMobiliers` distributions.

No CIP request box appears on paper pages 8/19; retain certificates/annex for reconciliation. Do not write a calculated entitlement into XML's credit-already-paid field. XSD shape is evidence of data structure, not proof the law permits a deduction. No XML payload or filled PDF was generated.


## Rental and complex home fields

[C · S1, S75, S93, S107]


Official form and schema evidence, inspected 2026-11-04:

- Official source: French Form 100, year 2025, p10 visually inspected. L1A 1001–1004 = direct built/nonbuilt rental and movable-property income; L1B 1005–1008 = undivided coownership share according to Forms 200 and 190/210; L1E 1017–1020 = construction-related rental loss; L1F 1021–1024 = own-home qualifying interest/annuities from L2; 1025–1028 = remaining spread costs; 1029–1032 total carried to p20 2025–2028. Columns separate taxpayer/spouse and non-exempt/exempt. The four-digit printed field IDs are not the XSD IDs.
- L2 1033–1047 = three lender/purpose/outstanding debt/interest rows with separate taxpayer/spouse amounts. Net subsidies. Addresses A/B 1048–1055 include availability dates. The form has two visible dwelling blocks, but this is not proof of two independent deduction ceilings or a law limiting ownership to two houses. Do not infer sign/rounding/auto-calculation behaviour from the blank PDF.
- Official source: **combined Form 190/210 F 2025**, four pages. Exact URL is `/2025/190-210f-2025.pdf`. p2: 200–216 acquisition/depreciation base, 217 rental months, 218–222 receipt components, 223 total gross rent. p3: A repairs 324, B1 current spreading 343–345, B2 prior years 346–350, C depreciation 351–369, D other operating costs 370–386. p4 visually inspected: 400 actual A–D total, 401 flat election, 402 selected actual/flat; E 403–421 financing interest net of subsidies and rented share; F 422–439 other excluded costs; 440 total E/F; 441 rent, 442 expenses, 443 social-rental exemption, 444 net result to Form 100 1001–1008.
- Official source: 2025 common determination for coownership. Use common result/owner allocation; do not declare the same whole property's net income once for every owner. Form 100 L1B explicitly requests Form 200 plus 190/210.
- Official source: official 2025 schema copied from existing source library. `LocationBiens/ResPrincipale` permits up to ten entries and each residence's `ResPrincipaleDettesCharges` up to ten debts. It carries country/address, occupation type, cadastral reference, simultaneous occupation, each taxpayer's start/end occupation dates, lender/purpose, debt balance, `L0230...100P_DETTE_ACQ` and `L0240...POURC_DETTE` (whether 100% / percentage of loan financed acquisition), separate taxpayer/spouse finance fees and occupied/nonoccupied interest totals. Exempt and non-exempt branches are distinct. It also has built-property aggregate and coownership-income branches.

**Important:** some XSD comments still say occupation or have inconsistent occupied/nonoccupied descriptions. Schema presence does not resolve the legal availability anchor or guarantee a product can populate and submit the branch. The parent must retain current unsupported runtime/manual-review flags. No PDF filling, XML generation, portal submission, MyGuichet acceptance test or product regression test run here.


## Extraordinary charges: PDF page 17

| Purpose | Actual AcroForm field names | Meaning and caution |
|---|---|---|
| General actual charges | `C.1701` checkbox; `N.1702` taxpayer and `N.1703` spouse amounts; `A.1704`–`A.1707` explanations | Provide actual expense detail and reimbursements. The printed instructions ask for gross medical amount, expenditure details and third-party reimbursements; for needy parents, their resources, support period, charge and household. Do not silently put a computed final abatement in a raw-cost field. `T.17021703` is a read-only total, not a user input. |
| Disability flat | `C.1708`; certificate radio groups `R.1709` and `R.1712`; percentages `N.1711`, `N.1714` | The printed boxes 1709/1710 (and 1712/1713) represent already submitted/attached certificate, but each pair is **one radio group**. No separate AcroForm fields named 1710 or 1713. Do not confuse the degree input with the euro abatement. |
| Common domestic help/dependency/childcare flat | `C.1715`; providers `A.1716`, `A.1717`; monthly costs `N.1718`, `N.1719`; month count `N.1720`, `N.1721`; annual costs `N.1722`, `N.1723` | Two person columns do not grant two common ceilings. These are costs and periods, not automatically the allowed flat amount. For variable schedules/multiple providers, retain a detailed schedule and avoid an invented average that would change the monthly cap. The form does not settle PIT-O-15. |
| Non-household child request | `C.1724` | Printed reminder excludes both parents sharing a home with the child. |
| Under 21 on 1 January or born during 2025, three rows | Names `A.1725a/b`, `A.1728a/b`, `A.1731a/b`; birth/NIN `D.1726`, `D.1729`, `D.1732`; annual costs `N.1727`, `N.1730`, `N.1733` | Printed declaration says principal support **more than 50%**. Preserve the proof for each child separately. |
| At least 21 on 1 January, two rows | Names `A.1734a/b`, `A.1738a/b`; birth/NIN `D.1735`, `D.1739`; annual costs `N.1736`, `N.1740`; education `A.1737`, `A.1741` | Full-time continuing education conditions remain substantive checks, not implied by filling a name. |

Checkboxes/radios have PDF type `/Btn`. Amounts, names, percentages and dates have `/Tx`; a PDF text field is not legal validation. Grey printed codes such as 0603, 0605 and 0850 are not established as writable fields by this inspection. Preserve computed results in the research calculation record until the official interface's semantics are checked.

## Extraordinary charges: XML: `ChargesExtraordinaires`

All following menu switches are `xsd:boolean`, optional: `G4700_ABT_ART_127` (general actual), `G4702_FRAIS_MAL`, `G4704_PER_NEC`, `G4706_REG_DIE`, `G4708_AUTRES_CHA`, `G4710_ABT_RGD_INV` (disability), `G4720_ABT_RGD_DOM` (common care flat), `G4730_ENF_HOR_MEN` (article 127bis). They live in `MenuChargesExtraordinaires`.

### Common care flat

`CharExtraFraisDomGarde/CharExtraFraisDomGardeDetail` allows **1–10** detail records if the section is present. Each record has required attribute `H1220_ID_PERSONNE` of type `id_personne`.

| Element | Exact type | Meaning |
|---|---|---|
| `H1230_CFD_NOM_ADR_BEN` | `texte200`, required | Provider name and address |
| `H1235_CFD_MAT_DOS_BEN` | `texte30`, optional | Known provider national number/file number |
| `H1240_CFD_TYP_FRA` | `type_frais`, required | String enumeration `1` domestic help, `2` dependency help and care, `3` childcare |
| `H1260_CFD_FRA_PER_ANN` | `xsd:boolean`, required | Full-year period |
| `H1280_CFD_FRA_PER_JAN`, `H1300_CFD_FRA_PER_FEV`, `H1320_CFD_FRA_PER_MAR`, `H1340_CFD_FRA_PER_AVR`, `H1360_CFD_FRA_PER_MAI`, `H1380_CFD_FRA_PER_JUI`, `H1400_CFD_FRA_PER_JUL`, `H1420_CFD_FRA_PER_AUO`, `H1440_CFD_FRA_PER_SEP`, `H1460_CFD_FRA_PER_OCT`, `H1480_CFD_FRA_PER_NOV`, `H1500_CFD_FRA_PER_DEC` | Each `xsd:boolean`, required | Month selections; the August identifier really uses `AUO` |
| `H1520_CFD_MNT_FRA` | `decimal10_2`, required | **Annual costs**, according to the schema comment; not a field for the allowed EUR 5,400 abatement |

An annual amount plus selected months does not encode a twelve-month amount vector. Multiple rows are allowed structurally, but the correct runtime grouping of several rows for one provider/person and the resulting cap computation have not been observed. Do not infer that equal allocation, payment-month selection or service-month selection is accepted. Keep PIT-O-15 and RET-O-01 open.

### Medical actual costs

`CharExtraFraisMaladie/CharExtraFraisMaladieDetail` permits 0–20 details. Required person attribute `H0020_CFM_PRE_NOM_PER` (`id_personne`); required `H0040_CFM_DES_MAL` (`texte50`, description); `H0060_CFM_MNT_FRA_MAL` (`decimal10_2`, gross medical costs); `H0080_CFM_MNT_TOT_REM` (`decimal10_2`, reimbursements). Preserve gross and reimbursement amounts; do not replace both with one net number.

### Needy persons and other actual costs

`CharExtraPersNec/CharExtraPersNecDetail` permits 0–10 details. Required person attribute `H0180_CPN_PRE_NOM_PER`. Required recipient surname/given name `H0200_CPN_NOM_PNE`, `H0220_CPN_PRE_PNE` (`texte30`), no-NIN flag `H0260_CPN_NIN_NON_ATT` (`xsd:boolean`), relationship `H0320_CPN_LIEN_PAR_PNE` (`texte100`), same-household flag `H0340_CPN_PNE_HAB_MEN` (`xsd:boolean`), resources `H0500_CPN_MOY_SUB_PNE` (`decimal10_2`). Optional fields capture NIN, date/place of birth, household dates, country, annual necessary minimum, number of other support obligors, wealth and claimed annual contribution. The last three useful codes are `H0440_CPN_NBA_ENF_PNE` (`xsd:int`), `H0520_CPN_SIT_FOR_PNE` and `H0540_CPN_MNT_ANN_PNE` (`decimal10_2`).

`CharExtraAutresCharges/CharExtraAutresChargesDetail` permits 0–10 details: required `H1980_CAU_PRE_NOM_PER` person attribute, `H2000_CAU_FRA_DES` (`texte100`), `H2020_CAU_MNT_FRA` (`decimal10_2`). An available generic field does not prove substantive deductibility.

The separate dietary section includes `H1060_CRD_TYP_FRA` (`type_frais_regime`), medical-attestation dates `H1080_CRD_DAT_DEB_PER` and `H1100_CRD_DAT_FIN_PER` (`xsd:date`), already-presented certificate `H1120_CRD_CER_ACD` (`xsd:boolean`), and `H1140_CRD_MNT_FRA` (`decimal10_2`). A dietary amount does not dispense with the normal-charge test. Numeric dietary forfaits were not made a new 2025 automation rule in this pass.

### Disability

`CharExtraInvaInfirm/CharExtraInvaInfirmDetail` permits 1–10 records. Required person attribute `H2100_ID_PERSONNE`; optional separately taxed minor's taxable income `H2110_CII_REV_ENF_MNT` (`decimal10_2`); required `H2120_CII_TYP_FRA` (`type_invalidite_infirmite`, `CAT` work capacity, `VIS` vision, `IMP` incapacity requiring assistance); required `H2220_CII_ATT_REM_ACD` (`xsd:boolean`, certificate already given).

Optional `CharExtraPeriodeTauxIncapacite` permits up to 10 periods, each with required start `H2160_CII_DAT_DEB_PER` (`xsd:date`), optional end `H2180_CII_DAT_FIN_PER` (`xsd:date`), required `H2140_CII_TAU_RED_CTR` (`taux_reduction_capacite`). Its string values are `0_24`, `25_34`, `35_44`, `45_54`, `55_64`, `65_74`, `75_84`, `85_94`, `95_100`. Read the boundary descriptions: **35% belongs to `35_44`**, not `25_34`. These values are bands, not arbitrary percentage decimals; the amount for each band is in figures/2025.md.

### Non-household children

`CharExtraEnfantsHorsMenage/CharExtraEnfantsHorsMenageDetail` permits 1–10 records, each with required child reference attribute `H2480_ID_PERSONNE` (`id_personne`) and optional annual costs `H2500_CEH_MNT_FRA` (`decimal10_2`). The enclosing section separately permits `H2520_CEH_TOT` (`decimal10_2`), explicitly **total article 127bis abatement**, so record the pooled calculation separately from raw per-child cost inputs. Live population/read-back of this total remains unverified.

## Type and validation limits

`id_personne` permits `DECLARER`, `CONJOINT`, and `CHILDREN0` through `CHILDREN19`; legal eligibility and correct referential identity are additional checks. `decimal10_2` is an `xsd:decimal` strictly between -10,000,000,000 and 10,000,000,000 with at most two fractional digits. It does **not** by itself prohibit negative care costs or enforce tax ceilings. `texte30/50/100/200` only enforce maximum string lengths. A schema-valid file does not prove correct household attribution, month allocation, document sufficiency, an ACD calculation or acceptance.

All extraordinary-charge field names and types above: [C · S1, S75].

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
