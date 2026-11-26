# Luxembourg tax – core conventions

_Figures in this file: 2025–2026. The year files of the domain skills (lu-vat, lu-income-tax-business, lu-social-security) win if they differ._

These rules sit under every answer the Luxembourg skills give. The domain skills hold the law; this skill says how to use it. Tax answers are only useful if the reader knows how firm each statement is, which year it applies to, and where it comes from, so that is what these conventions protect.

## 1. Before answering: find the profile

Ask only the questions that change the answer. If something is missing and the user is not there to ask, answer with the assumption stated in the first line ("Assuming tax year 2025 and a liberal profession on the cash method…").

The usual five, in order of importance:

1. **Tax year** (the income year, not the year of filing). Rates, thresholds and form line numbers change every year.
2. **Status**: sole trader (commercial, craft or liberal profession), company (SARL, SARL-S, SA), employee with a side activity, or not registered.
3. **VAT profile**: normal regime (and filing frequency), franchise (art. 57bis), exempt activity (art. 44), cross-border SME scheme (EX number).
4. **Profit method** (income tax): regular accounts, accrual without regular accounts, or the simplified receipts-and-expenses method.
5. **Residence**: Luxembourg resident or not; cross-border situations change both tax and social security.

Details and defaults: [references/triage.md](references/triage.md).

## 2. Which skill holds the answer

| Question is about | Skill |
|---|---|
| Charging or deducting VAT, franchise, purchase invoices, VAT returns and boxes, invoices, thresholds | lu-vat |
| Where a cross-border sale or purchase is taxed, reverse charge, foreign VAT refunds, OSS, EU SME scheme | eu-vat |
| Profit, deductible expenses, home office, car, depreciation, commuting, municipal business tax, Forms 110/112/113/152/800 | lu-income-tax-business |
| CCSS contributions, exemptions, the CCSS certificate | lu-social-security |
| Bookkeeping duties, balance sheet and P&L, records, bank account, VAT journal entries (PCN) | lu-accounting |
| Preparing the annual income tax return step by step | lu-annual-return |
| Form 100 beyond the profit: tax class, household, other income, special expenses, abatements, tax credits (incl. the CII for the self-employed), own home, non-residents, advances, the bulletin | lu-income-tax-personal |
| Whether an activity needs a business permit, qualifications, the fixed place, RCS and RBE of a sole trader | lu-business-permit |
| Starting an activity step by step (permit → RCS → CCSS → VAT → ACD) | lu-business-start |
| Subsidies, grants and aids for small businesses; de minimis | lu-subsidies |
| Sole trader or company; SARL, SARL-S, ASBL; managers' liability; RCS and RBE of companies | lu-entity-profiles |
| Taxes of a SARL, SARL-S or ASBL: corporate tax, municipal business tax, net wealth tax, Form 500, dividends, paying the owner-manager | lu-corporate-tax |

Where two skills meet:
- The whole return → lu-annual-return; one deduction, credit or box → lu-income-tax-personal (household) or lu-income-tax-business (profit).
- All the steps to start → lu-business-start; whether a permit is needed and which one → lu-business-permit.
- Which legal form → lu-entity-profiles leads and loads lu-corporate-tax for the tax figures.
- A company's accounts and their filing → lu-accounting; founding and running the company → lu-entity-profiles.
- Grants and aids → lu-subsidies; the investment tax credit stays with lu-income-tax-business.

A question often needs two skills (leaving the VAT franchise touches lu-vat and lu-income-tax-business). Load both rather than guessing.

## 3. How to state a rule

Every rule in these skills carries one of five labels. Keep the label when you pass the rule on, in words the reader understands:

- **[C] Confirmed**: stated in an official source we opened (law text, official form of that year, ACD/AED/CCSS/Guichet page, a written answer from the administration, a judgment of the CJEU or of an appeal court – a first-instance judgment is only an Interpretation). A firm, the press or our own documents never confirm a rule on their own. Say it plainly.
- **[I] Interpretation**: our reading of the law where no text addresses this exact case; reasonable but not stated. Say "in our reading" or "most likely".
- **[P] Practice**: what tax offices, the administration's helpdesks or accountants actually do, written down nowhere official. The source names who reported it and when. Say "in practice … but this is not guaranteed and cannot be relied on against the administration". Never upgrade it to Confirmed without a text.
- **[O] Open**: not settled, including bills that are not law yet (their status: [references/watchlist.md](references/watchlist.md)). Never state it as fact. Answer with the current law and mention a bill only as a proposal.
- **[B] BravoLisa convention**: a choice BravoLisa made where the law leaves room – which account, which workflow (for example private purchases on 106178, the net depreciation method). It is not law: say "BravoLisa books it this way", never "the law requires". Another business may choose differently.

When a point is **Open**, answer like this:
1. Say plainly that it is not settled.
2. Give the working answer from the skill's open-items record, if there is one, with its own label.
3. Say who can settle it (the AED, the ACD, the CCSS, an adviser). If the person wants to ask, help them write one short question about their own case – the facts in a line or two, then one yes/no or either/or question – and say how to reach the office ([references/sources.md](references/sources.md), « Escalation »); an e-mail answer is a position, not a ruling. An answer is worth passing on to BravoLisa, without personal details: it can settle the point for everyone ([BRAVOLISA.md](../BRAVOLISA.md), last section).
4. When money is at stake, point to the cautious option.

Further rules:

- **Name the year** for every figure – for example "€50,000 (2025)", not "€50,000". Some figures change during a year (the social minimum wage did on 1 June 2026): give the period.
- **No invented numbers.** Rates, thresholds, box and line numbers come only from the skill's year files. If the year file for the asked year does not exist, say so and give the latest known year, clearly marked.
- **Which year file:** `figures/2025.md` and `figures/2026.md` are complete years. `figures/2027.md` holds only changes already known, each marked adopted law or bill: never use it for a 2025 or 2026 answer. `figures/history-2023-2024.md` is only for old invoices, assets bought earlier and corrections of past years.
- **Sources outrank memory.** Source order and key URLs: [references/sources.md](references/sources.md). A written answer from the ACD, AED or CCSS logged by BravoLisa outranks our own inference from forms.
- **Email answers from the administration are positions, not rulings.** The ACD's own footer says « un courriel n'engage pas son expéditeur ». For a point that carries real money, suggest a written request to the tax office or an advance decision (décision anticipée).

## 4. Shape of an answer

1. The answer in one or two plain sentences.
2. The rule behind it, with its label and source.
3. What to keep or do (documents, deadlines, the box or line).
4. What is still open, if anything, and who can settle it.
5. For filing decisions, one short line: this is general information, not a tax opinion.

Write for a business person, not an accountant: "the money you paid your accountant", not "account 61342". Many readers are not native English speakers: short sentences, common words, the French term in brackets the first time it appears (franchise (régime de franchise)). Terms: [references/glossary.md](references/glossary.md).

## 5. Client data and confidentiality

- Client facts (names, amounts, matricule, addresses, bank details) come from the user or from connected data tools (for example the BravoLisa MCP server). They never go into skill files, examples or logs.
- Examples in these skills use invented, round numbers.
- If a question needs a client's figures, ask for them or read them through the connected tool; do not estimate them.

## 6. How these files are kept up to date

BravoLisa maintains these files: a rule goes in only after it has been checked against the official text, labelled and sourced, and this public copy is regenerated from BravoLisa's knowledge base. Do not change them during a conversation.

- **Bills, votes and publications we are waiting for**: [references/watchlist.md](references/watchlist.md). The other parts mention a bill and point to its row there.
- The parts keep `references/sources.md` (each source with its type and the date checked), `references/open-questions.md` (one record per undecided point: question, why it matters, working answer, who can settle it, status) and `references/figures/` (year files). The figures the scripts compute with are copied into `data/tool-figures.json`, each with the year file that owns it.
- An error or an outdated rule: the person can report it to BravoLisa ([BRAVOLISA.md](../BRAVOLISA.md), last section).
