# Open points – lu-annual-return

## RET-O-01 · 2025 household XML import and calculation read-back
- Question: Does the 2025 MyGuichet assistant import the generated children, childcare-period and own-home records with the intended attribution, dates and allowed amounts?
- Why it matters: XSD validity checks structure, not the assistant's semantic calculation or imported summary.
- Working answer: The generated XML passes the official 2025 schema and independent value checks. [B · lu-income-tax-personal S75] The ACD tutorial's 2024 screenshots corroborate several field codes, but do not verify 2025 runtime behaviour. [I · lu-income-tax-personal S61] Actual 2025 import and read-back remain unverified. The 2025 PDF has a distinct transitional child-bonus request C.1837; the XSD bonus field G2780_ENF_DEM_BONI describes only prior household membership. Do not assume this field imports the new route correctly. CIM support and already-paid-CIM reconciliation also remain untested in the assistant. [O · lu-income-tax-personal S1; lu-income-tax-personal S75] The 2025 cross-border research adds manual PDF requests, percentage allocations and exempt-income home/contribution columns only. Non-resident eligibility/rate calculations, family transitions and live XML attribution remain unverified; forms/2025/cross-border-household.md retains the stops. [B]
- Who can settle: ACD / MyGuichet support and an authorised integration check using an appropriate test route.
- Status: open

- 2026-11-04 remaining-three review: manual PDF/XSD coverage now includes pensions, capital, donation carryforwards, rental and extraordinary charges. Raw costs, gross income, allowed relief and credits already paid are distinct. Variable care rows, pooled article-127bis totals and these additional branches have not been imported/read back live. No automation claim added. [C · lu-income-tax-personal S1; lu-income-tax-personal S75; B for coverage status]

- 2026-11-04 salary review: domestic SRF5/SALF election rendering, the contribution fields' before/after-nondeductible arithmetic, per-block FD shares and employee credits require authoritative semantics/live read-back. Flat regimes now stop in automatic tools; schema comments alone do not settle contribution subtraction. [O · lu-income-tax-personal S75]

- Automation review 2026-11-04: Added offline-valid consumer-interest, donation, regular monthly CIM support/paid-credit and zero-history own-life PU fields. The residence registry/keyref is verified. Donation gross-versus-allowed PDF convention is explicit; PU prior-use retained recap remains live-unverified and XML stops. No live acceptance claimed. Paper C0228 requests only an unpaid remainder by documented inference; XML ENF_CRE_IMP retains the separate annual-application meaning. The distinction still needs live read-back. No-income A0237 completion remains outside mapper scope. [I/B/O]

- Handoff repair2026-11-04: offline support now includes reviewed actual salary costs, occupational/voluntary contributions, PACS common-child election, self-paid adult medical costs, certified payroll exemptions and dated workplaces. Exact-date pension guards added. No live import or read-back occurred; paid/allowed/net distinctions and benefit workplace semantics remain explicit. [B]

Employer-interest and termination exemption mappings remain reviewed manual bridges; this2026-11-05 research did not verify live2025 XML or calculate a domestic election. [B/O]

## RET-O-02 · CISSM article 139quater(6) request channel
- Question: The tax credit for minimum-wage earners (CISSM) can be claimed after the end of the year for salary taxable in Luxembourg on which no tax-card withholding was made (art. 139quater(6) LIR). With which form or through which channel?
- Why it matters: The right exists, but entering it in a Form 100 box that does not exist could lose the claim.
- Working answer: Keep the evidence – monthly pay, hours, social-insurance affiliation and proof that no tax card was used – and get the procedure from the ACD (its RTS offices handle tax on wages). Do not treat it as an ordinary yearly deduction. [C · lu-income-tax-personal S82; O for the channel]
- Who can settle: ACD procedural guidance or written clarification.
- Status: open

## RET-O-03 · Mandatory XML workplace for direct replacement benefits
- Question: The MyGuichet file needs a workplace commune for every salary. For sickness, maternity, accident or unemployment pay that comes on its own certificate, with no real workplace, which commune – if any – goes there?
- Why it matters: The office that pays the benefit is not a workplace; an invented commune could distort the return.
- Working answer: Classify the benefit correctly as employee income and use paper boxes 709/710. The tools handle the calculation and the PDF for the reviewed cases. The XML file stops unless an authoritative source shows what to enter: that the schema makes the field compulsory does not say what goes in it. The commune list has had a code « AUTR » since the 2024 schema, but nothing says it means « no workplace ». [C · lu-income-tax-personal S1; lu-income-tax-personal S75; O for runtime semantics]
- Who can settle: ACD/MyGuichet support or official import documentation.
- Status: open

## RET-O-04 · Actual occupational contributions above the statutory cap in XML
- Question: Does the 2025 assistant cap RCS_COT_CONT_NEX/CONJ_NEX automatically when actual employee contributions exceed the per-person deduction cap?
- Why it matters: Writing the retained cap into an actual-paid field falsifies the certificate; writing actual paid without proven cap semantics may overstate relief.
- Working answer: The fields D1680_RCS_COT_CONT_NEX and D1700_RCS_COT_CONJ_NEX take the personal contributions **paid** (« Cotisations versées »), not the capped amount; the amount kept after the tax cap is a separate field of the 2025 schema, in the recap of special expenses – D3426_RDS_RCS_RET_CONT_NEX / D3846_RDS_RCS_RET_CONJ_NEX, « Montant retenu pour le calcul de l'impôt ». [C · lu-income-tax-personal S75] The recap need not be pre-filled: the assistant calculates it – documented for tax year 2021 and visible on the ACD's screenshots of the 2024 assistant (declared amount, ceiling and retained amount side by side). [C · lu-income-tax-personal S171, lu-income-tax-personal S61 for 2021 and 2024; I for 2025 – high confidence] So the amount actually paid is what the field asks for, also above the cap; that the 2025 assistant then retains the capped amount, and how it treats the salary-block field S0460 next to D1680, was not seen on a 2025 return. [O] Until one import and read-back shows it, preserve actual payments in the case and annex, keep the statutory deduction in calculation and paper 1605/1606, and keep the above-cap XML stop. [B]
- Who can settle: ACD/MyGuichet support and an authorised test import.
- Status: open

## RET-O-05 · MyGuichet status codes in a year of change
- Question: In the electronic return, is a person who was separated by court permission before the year entered as « Séparé(e) » or as « Marié(e) » on 1 January, and is a spouse who died in the year given the status « Décédé(e) » with the date of death?
- Why it matters: In 2021 the assistant decided from these codes whether the return has spouse pages; a wrong code could open or close them.
- Working answer: Enter the status held on 1 January with the date it began, then one entry per status that began in the year, in date order. [I – high · lu-income-tax-personal S75; lu-income-tax-personal S171] Separated by court permission before the year: `SV` on 1 January, then `DI` at the divorce. A death: the survivor `MA` then `VE`, the deceased `MA` then `DE`. [I – medium] The household file states the codes and the builder writes them as given (forms/2025/family-events.md); check the identity pages in the assistant. [B]
- Who can settle: ACD; one import with read-back.
- Status: open

## RET-O-06 · « Current » address: the day of filing or 31 December
- Question: Is the current address of the return (paper boxes 116–125, XML `G0500`) the address on the day of filing or the one on 31 December of the tax year?
- Why it matters: A move after the tax year and before filing; the earlier-address block and the XML list are only for moves inside the tax year.
- Working answer: The address on the day of filing; a move after 31 December is not an "other address" of the year. [I – medium · lu-income-tax-personal S1; lu-income-tax-personal S75]
- Who can settle: ACD.
- Status: open
