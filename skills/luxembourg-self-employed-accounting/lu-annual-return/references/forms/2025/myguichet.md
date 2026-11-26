# MyGuichet 2025 return – branches and mandatory uploads (observed)

Observed in screenshots of the 2025 MyGuichet Form 100 during webinar preparation. These are observations of the interface, not legal conclusions; the interface can change. [P · observed October 2026]

| Branch selected | Mandatory uploads shown |
|---|---|
| Liberal profession, individual, balance sheet / P&L method | Balance sheet and P&L + social security contribution certificate |
| Liberal profession, income and expenditure method | « Operating expenses paid (Form 152 or equivalent annex) » + social security contribution certificate |
| Business profit, sole proprietorship, balance sheet / P&L | Form 110 and balance sheet / P&L (summary showed three attachments; the third was off-screen) |
| Business profit, income and expenditure | Form 110 (summary showed two attachments; the second was off-screen) – do not say there is only one |

Notes:
- "Equivalent annex" allows another presentation of the same cash-method figures; it is not permission to use accrual figures on the cash method. [I]
- Help text on gross income: its determination may be given in a free-form appendix; this does not replace a required Form 110. [P · observed]
- Both commercial and liberal branches warn that Mutualité reimbursements must be included in business profit. [P · observed]
- The special-expenses part asks, per activity (e.g. liberal profession), « Personally affiliated as a compulsorily insured person in 2025 for a declared self-employed activity? »; a separate question covers other mandatory social-security contributions. The paper Form 100 has no such question. [P · observed] Answer it: compulsory affiliation is the condition of the tax credit for the self-employed (lu-income-tax-personal, tax-credits.md). [I]
- The mapping of MyGuichet's two broad choices to Form 110 route B (accrual without regular accounts) is not established. [O]
- Upload format: PDF, under 7 MB per file. [P · observed]

## Using the electronic assistant (ACD tutorial, October 2025)

From the ACD's English « 123easy » tutorial for the MyGuichet assistant (lu-income-tax-personal, sources S61).

- **First page – consent to automated taxation**: the return can then be assessed without an ACD officer; an officer can still check it within 5 years. [C · lu-income-tax-personal S61]
- **Cases the assistant does not handle** – use the PDF or paper Form 100 instead: no LuxTrust product; no national identification number; a non-resident revoking an earlier assimilation; spouses or partners asking for individual taxation; married more than once in the year; spouses not living in the same country; a change of country of residence in the year; a request for an annual adjustment; a corrected return. [C · lu-income-tax-personal S61]
- **Who fills it in**: the taxpayer or an agent. A spouse or partner can act as the other's agent; the consent is given on Annex 101, which must be attached before sending. [C · lu-income-tax-personal S61]
- **Where a self-employed person's income goes**: business profit, capital income and miscellaneous income (including taxable capital gains) are under « Other income ». [C · lu-income-tax-personal S61]
- **Social contributions of the self-employed**: enter the amount shown under « cotisations déductibles » on the CCSS statement. [C · lu-income-tax-personal S61]
- A home-savings contract that matured or ended in the year, and a joint mortgage of spouses: lu-income-tax-personal, special-expenses.md and home-and-rental.md.

## Pre-filling with an XML file, and checking the result

The XML import (form types, agent filing with Form 101, consent and eligibility answers, file format), what MyGuichet does with an upload (commuting per salary block, required CIS and CO2 fields, the agent's answers) and how to read its PDF back: [myguichet-xml.md](myguichet-xml.md). The scripts: [form100-tools.md](form100-tools.md).

For generated 2025 family sections, read [form100-family.md](form100-family.md) and [RET-O-01](../../open-questions.md). Offline schema checks do not replace an authorised import/read-back. [B]

*Tax and accounting knowledge: BravoLisa – https://bravolisa.lu · licence [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) · https://github.com/bravolisa/luxembourg-self-employed-accounting-skill*
