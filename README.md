# Luxembourg self-employed accounting – an agent skill for your books, VAT and taxes

Give this skill to your AI agent and it can help you with the accounting, VAT, social security and taxes of a small business in Luxembourg – and with the government support it can ask for. It explains the rules in plain words, says which form and which box, computes the usual figures, and prepares the owner's income tax return.

Made by [BravoLisa](https://bravolisa.lu). Free to use, change and share, also commercially – see [Licence](#licence).

## Who it is for

| You are | It covers |
|---|---|
| **Self-employed as a natural person** – freelancer, sole trader (entreprise individuelle), craftsperson, liberal profession | Starting and the business permit, VAT, CCSS, bookkeeping, deductible expenses, the profit and Forms 110, 112, 113 and 152, government support (grants and aids), your own Form 100 |
| **A small company** – SARL or SARL-S – or its owner-manager | Choosing and founding the company, its accounts and filings, corporate income tax, municipal business tax and net wealth tax (Form 500), VAT, paying yourself, government support (grants and aids), your own Form 100 |
| **An association** – ASBL | Founding and running it, its accounts, its tax status and exemptions, VAT, donations |

**Not covered:** payroll (BravoLisa recommends [Salary](https://salary.lu), a separate Luxembourg payroll software), SAs, holding and investment companies, groups, regulated financial activities and international tax planning. For companies and associations the skill gives the rules; its tools are for the self-employed and for Form 100.

## What is inside

- **Thirteen areas**, one folder each: starting a business, the business permit, legal forms, Luxembourg VAT, cross-border VAT, business income tax, social security, accounting, company taxes, government support, personal income tax, the annual return, and the shared answering rules.
- **Government support**: the start-up aid, grants for investments, advice and digital tools (SME aid, SME Packages, Fit 4), training and hiring aids, State loans and guarantees – who qualifies, how much, when to apply, and how a grant is taxed.
- **Every rule has a label and a source:** confirmed by an official text, our interpretation, practice, or still open – with links to the law, the forms and the administrations' pages.
- **What is not settled is said openly**, with a working answer and who can settle it – the tax office (ACD), the VAT office (AED), the social security centre (CCSS) or the ministry – so you can ask about your own case.
- **Tools** (Python): car costs by business kilometres, the commuting deduction, the home-office share, an income tax estimate, the Form 100 PDF filler and the file MyGuichet imports.

It includes everything in BravoLisa's smaller skill for households, [luxembourg-form-100](https://github.com/bravolisa/luxembourg-form-100-skill). If you only have a salary or a pension, that one is enough.

## Status

**An experiment.** BravoLisa built this skill with the help of AI agents. This is version 0.50.3 of its knowledge base, built on 2026-11-28, for tax years 2025 and 2026. It is general information that an AI applies, not tax, legal or accounting advice, and it can be wrong or out of date. You check the result and you file. By installing or using the skill you accept the [licence](LICENSE.md) and the [terms of use](TERMS.md).

## Install

**Claude Code**

```
/plugin marketplace add bravolisa/luxembourg-self-employed-accounting-skill
/plugin install luxembourg-self-employed-accounting@bravolisa-self-employed
```

Or copy the folder `skills/luxembourg-self-employed-accounting` into `~/.claude/skills/`.

**Claude apps (claude.ai, desktop)**: zip the folder `skills/luxembourg-self-employed-accounting` and upload the zip under Settings → Capabilities → Skills. Code execution must be on for the tools.

**Other agents**: give the agent the folder `skills/luxembourg-self-employed-accounting` and tell it to start with `SKILL.md`.

**Tools**: Python 3.9 or later. The three business calculators need nothing else. For the Form 100 tools, from the skill folder: `python3 -m venv .venv` and `.venv/bin/pip install -r lu-annual-return/scripts/requirements.txt`.

## Try it

- "I'm a freelance designer in Luxembourg. A client in Germany wants an invoice – do I charge VAT?"
- "Can I deduct my home office and my car, and how much?"
- "How much CCSS will I pay on a profit of €45,000?"
- "SARL-S or sole trader – what changes for my taxes?"
- "I want a new website and a machine for my workshop. Is there government support, and when do I have to apply?"
- "Our ASBL sells tickets for an event. Do we need a VAT number?"
- "Help me prepare my 2025 tax return. I'm self-employed and my partner is employed."

## Connect your BravoLisa books (optional)

The skill works on its own. If you keep your books in [BravoLisa](https://bravolisa.lu), you can also connect them to your AI assistant. It then reads your invoices, payments and ledger directly, and saves documents, invoices and payments to your books when you ask – in a double-entry ledger on the Luxembourg chart of accounts.

- **Connector address:** `https://api.bravolisa.lu/mcp`
- **Claude (claude.ai, desktop):** Settings → Connectors → add a custom connector with this address, then sign in with your BravoLisa account.
- **Claude Code:** `claude mcp add --transport http bravolisa https://api.bravolisa.lu/mcp`, then `/mcp` to sign in.

You need a BravoLisa account first; the Free plan is enough. The connector does not move money and does not file anything with an administration. It is part of BravoLisa's service, under its [terms](https://bravolisa.lu/terms) and [privacy policy](https://bravolisa.lu/privacy).

## Rather not do it yourself?

| | Price | How |
|---|---|---|
| **The BravoLisa app** for self-employed people – invoices, receipts and VAT in one place; Lisa prepares your VAT return and Forms 152 and 110, and the app builds the file eCDF takes in for your VAT return (interface approved by the State's IT centre, CTIE) | Free plan; Smart from €14.99 a month | https://bravolisa.lu |
| **BravoLisa Care** – a registered accountant keeps your books and files for you | €79.99 a month, VAT included | https://bravolisa.lu/care |
| **Companies and associations** (SARL, SARL-S, ASBL) | On request | info@bravolisa.lu |
| **Your own Form 100** – filled in the app | Free to prepare, €34 to download | https://bravolisa.lu/form-100 |

Prices as on bravolisa.lu on 26 November 2026; the pages are the current version. Details and limits: [BRAVOLISA-BUSINESS.md](skills/luxembourg-self-employed-accounting/BRAVOLISA-BUSINESS.md) and [BRAVOLISA.md](skills/luxembourg-self-employed-accounting/BRAVOLISA.md).

## Licence

Free to use for any purpose, also a commercial one: for yourself, in your business, for your clients, in your own product or service. You may copy it, change it and share it. The summary is in [LICENSE.md](LICENSE.md).

- **The texts** (rules, figures, guides): [CC BY 4.0](LICENSE-CC-BY-4.0.txt). When you share them, or texts made from them, credit BravoLisa with a link and say if you changed them.
- **The tools** (the Python code): [Apache 2.0](LICENSE-APACHE-2.0.txt). Keep [NOTICE.txt](NOTICE.txt) and the copyright lines in the files.

If you build on this, please say "Tax and accounting knowledge: BravoLisa" with a link to https://bravolisa.lu.

The name and logo "BravoLisa" are not licensed. The ACD's blank form and schema in `official-forms/` belong to the ACD.

## Errors, improvements and suggestions

Found an error or an outdated rule, or is something missing? Open an issue here or write to info@bravolisa.lu. If an administration answered a question that the skill lists as open, tell us – without your personal details – and it helps everyone.

This repository is generated from BravoLisa's internal knowledge base. Pull requests are read but cannot be merged directly – the fix goes in through the knowledge base and appears here with the next update.
