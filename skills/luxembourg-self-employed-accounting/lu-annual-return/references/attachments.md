# Attachments and detail annexes

_Figures in this file: 2025–2026. The year files of the domain skills (lu-vat, lu-income-tax-business, lu-social-security) win if they differ._

## What is required

- Mandatory supporting documents for Form 100 are listed by the ACD: https://impotsdirects.public.lu/fr/az/p/pieces-justificatives-obligatoires-modele-100.html [C · lu-income-tax-personal S76]
- No general rule was found requiring every business receipt with Form 100, or a full annual customer/supplier list in all cases. Submit the required annexes and proofs, keep the rest; the tax office can ask for more. [I]

## Detail annexes on Forms 112 and 152

| Form | Lines with « Prière de fournir le détail en annexe » |
|---|---|
| 112 | 6 commissions; 37 (38/39) work by third parties; 45 other repairs; 46 small items written off at once (limit: lu-income-tax-business) |
| 152 | 6; 33 (34/35); 41 other repairs/supplies; 42 small items written off at once |

Footnote 3 warns that failing to identify recipients of certain payments can jeopardise the deduction; the landlord and accountant are identified on the forms. [C · lu-income-tax-business S4, lu-income-tax-business S5]

No official numbered template exists for these annexes. Recommended: a clearly labelled PDF schedule per line – taxpayer, year, form, line; supplier, invoice reference and date, description, amount excluding VAT, VAT, business amount claimed, paid date when relevant – reconciled to the line total. [I]

## Receipts breakdown (« Détail des recettes »)

On the receipts-and-expenses method:
- **Liberal professions:** Form 100 box 605 reads « + Recettes (suivant annexe) », so a receipts statement is expected. [C · lu-income-tax-personal S1 p. 6]
- **Commercial:** Form 110 line 49 is a single amount, « Recettes d'exploitation (T.V.A. comprise) », with no annex required. Accountants still attach a « Détail des recettes » when receipts are not just customer payments. [C · lu-income-tax-business S20; P · an accountant's annex to a 2024 return]

Recommended content, one page in French [B]:
- **Header:** name, address, file number, tax year, the line it supports (Form 110 line 49 or Form 100 box 605).
- **Lines:**
  - payments received from customers (VAT included);
  - VAT refunds received from the AED, naming the VAT year;
  - Mutualité reimbursements, as on the CCSS certificate;
  - other receipts, if any;
  - the total.

  Show the refund and Mutualité lines even at 0.00.
- **Reconciliation note:** the year's VAT turnover. It equals customer receipts when customer receivables are nil at both year-ends (Form 110 line 64). The difference is explained by the lines above. Add that the VAT credit of the year itself, if any, will be counted in the year it is refunded (lu-income-tax-business vat-in-income-tax.md).

Upload it as its own PDF next to Form 110 or 152 – one file per document while ACC-O-06 is open. `scripts/make_receipts_annex.py` writes it from the household file (form100-tools.md). Timing of VAT refunds: lu-income-tax-business vat-in-income-tax.md. [B]

## Balance sheet and P&L

No official form; attach your own presentation, unabridged, with PCN captions recommended (lu-accounting). [C · lu-accounting S2, lu-accounting S22; B for PCN presentation]

## Electronic filing

- MyGuichet uploads are PDFs; the dialog showed a 7 MB limit per file. [P · observed 2025 interface]
- The MyGuichet procedure for Form 100 « peut être pré-remplie à l'aide d'un fichier XML » in the ACD's own format, one XSD per tax year; the procedure is then confirmed, completed with the attachments, signed and sent. There is no ACD test platform: the XSD checks the syntax and « les règles sémantiques seront validées en ligne par l'assistant ». [C · lu-income-tax-personal S69; lu-income-tax-business S62] Details: forms/2025/myguichet-xml.md.

## Childcare detail (2025)

`fill_form100_pdf.py --household` produces a `.childcare.pdf` schedule alongside the return. It shows provider/payer, actual monthly costs, reimbursements and the separate household capped calculation. Attach the schedule and certificates; do not replace actual costs by the abatement in page-17 expense boxes. See [form100-family.md](forms/2025/form100-family.md). [B]
