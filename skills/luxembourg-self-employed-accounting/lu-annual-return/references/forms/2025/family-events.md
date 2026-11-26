# A change of civil status or address during the year – Form 100 for 2025 in MyGuichet

Marriage, a registered partnership, a separation, a divorce or a spouse's death during the tax year, or a spouse living at another address.

- Who files, jointly or alone, and in which class: lu-income-tax-personal `family-changes.md`.
- The paper boxes (page 1 addresses, page 3 status, page 20 signatures): lu-income-tax-personal `forms/2025/cross-border-and-family.md`.
- This file: the fields of the MyGuichet XML, what to enter for each event, and the household-file keys the tools write them from.

Read from the ACD's 2025 import schema (library `F100-XSD-2025`); the placement rules come from the ACD's guide for software makers of tax year 2021, the only field description the ACD has published. Nothing here was seen on a live 2025 import (RET-O-01, RET-O-05). [B]

## What the tools write (household file)

From 0.47.0 the household file carries these facts and the tools write them into the PDF and the XML. The file states every status and date; the tools check that they fit together and never choose a status. Where the ACD has not confirmed the placement (RET-O-05, PIT-O-42), the tools follow the working answers of this file – review the identity pages before filing. [B]

| Key | Content |
|---|---|
| `taxpayer.status`, `status_since` (and the same for `spouse`) | The status **on 1 January** and the date it began – codes in the table below |
| `status_changes[]` (per person) | `status`, `since`: each status that began during the year, in date order (at most ten) |
| `separation` (per person) | `ground` – `court` (paper box 308), `judgment` (307) or `legal` (306) –, `since`, `evidence`. Required with status `SV`; may stay beside `DI` in the three class-2 years |
| `married_since` | The wedding date of a person who is already separated on 1 January (paper box 305) |
| `spouse_address` | The spouse's own current address, when it is not the household's `address` |
| `earlier_addresses[]` (per person) | `from`, `to`, `address`: each other home of the year with its period |
| `signature` | `each` (default: each spouse signs), `taxpayer_for_both`, or `on_screen` (the block stays empty and the filer chooses in MyGuichet) |
| `status_review.evidence` | Which certificates and decisions were checked – required as soon as one of the keys above is used |

- **XML**: the status on 1 January and one group per later status; the spouse's own address and the other addresses with their periods; « married » and « in a partnership » answered for any time in the year; the signature answer. [B]
- **PDF**: the status after the event with its date in 305 (PIT-O-42); box 308 with the date of the court decision in 309; the spouse's own address in the right-hand column; the earlier-address block. [B]
- **The tools stop** when the two spouses do not show the same changes on the same dates; when a spouse already separated by court permission on 1 January is put in a joint file; for a marriage in the year without the spouse in the file; for more than one marriage in the year; when the person who died is entered as the taxpayer; and for a death without a signature choice (`taxpayer_for_both` or `on_screen`), unless an agent files. [B]
- **PDF only, by hand**: boxes 306 and 307 (their button names carry an accented letter the tool cannot write), a second earlier address or one that does not start on 1 January, and any foreign address. [B]
- **Balance** (`tax_estimate.py --household`): three more cases through facts in `salary_balance` – `class2_alone` for a class-2 year assessed alone, `class_1a_ground` for class 1a without a child, and the joint year of a spouse's death when the death fell on 31 December (an earlier death stops: PIT-O-40). Inputs: lu-income-tax-personal `salary-balance-calculator.md`. [B]
- **Tests**: `scripts/tests/test_form100_events.py` (hand-written expectations). Run against 17 reference households, the tools agree on PDF, XML and balance for all of them, apart from three text labels and the date « since 1 January » that the tools add for a person who was single, as the ACD's 2021 guide says. [B]

## Civil status

| What | Taxpayer | Spouse or partner | In the schema |
|---|---|---|---|
| Status on 1 January (« Situation au 01/01/YYYY ») | `G0160_SIT_1JAN_CONT` | `G0400_SIT_1JAN_CONJ` | required |
| Since when (« Depuis le ») | `G0180_DATE_SIT_1JAN_CONT` | `G0420_DATE_SIT_1JAN_CONJ` | optional in the schema, starred on screen |
| Did the situation change in the year? | `G0200_AUT_CHG_SIT_CONT` | `G0440_AUT_CHG_SIT_CONJ` | required, yes or no |
| One group per new status, up to ten | `EtatCivilAnnFiscContrib` | `EtatCivilAnnFiscConj` | optional |
| – the new status | `G0220_AUT_SIT_CONT` | `G0460_AUT_SIT_CONJ` | required in the group |
| – its start date | `G0240_DAT_AUT_SIT_CONT` | `G0480_DAT_AUT_SIT_CONJ` | required in the group |

[C · lu-income-tax-personal S75]

| Code | Schema label | Paper page 3 |
|---|---|---|
| `CE` | Célibataire | 301 |
| `MA` | Marié(e) | 302 |
| `DI` | Divorcé(e) | 303 |
| `VE` | Veuf(ve) | 304 |
| `PA` | Partenaire | no status box (only the request 312–315) |
| `SF` | Séparé(e) de fait | no box |
| `SV` | Séparé(e) under a legal dispensation, a judgment of legal separation or a court dispensation | 306, 307 and 308 as one code; date 309 |
| `DE` | Décédé(e) | no box |

[C · lu-income-tax-personal S75 for the codes; I for the match with the paper boxes]

- A status is a code and the date it began. The schema has no end date, no kind of event, no date of death, no court decision, no date of the partnership declaration (paper 313) and no tax class. Court decisions travel as attachments. [C · lu-income-tax-personal S75; lu-income-tax-personal S171 for the attachment types of 2021]
- The schema checks none of the logic: « changed = yes » without a group validates, and so does any date. [C · lu-income-tax-personal S75 – tested offline] The ACD's guide of 2021 made the group compulsory when the answer is yes and kept `DE` out of the 1-January field. [C · lu-income-tax-personal S171; I for 2025]
- **Rule.** Enter the status the person held on 1 January, with the date that status began (for a single person the guide gives 1 January of the tax year). Answer yes and add one group per status that began during the year, in date order. The ACD's own example: married since an earlier year, then `VE` from February and `PA` from March of the tax year – two groups. [C · lu-income-tax-personal S171 for the example; I – high – for 2025]
- The assistant asks for every situation of the year because « la situation fiscale au 1er janvier de l'année d'imposition ne suffit pas toujours pour déterminer correctement l'imposition ». [C · lu-income-tax-personal S156]
- In 2021 the assistant opened the spouse pages when a person was `MA` or `SF`, on 1 January or during the year. Whether the 2025 assistant decides the same way is not published. [C · lu-income-tax-personal S171; O for 2025]

| Event in 2025 | 1 January (code, since) | Groups to add (code, from) | Spouse block | Status |
|---|---|---|---|---|
| Marriage on a day in 2025, both single before | each: `CE`, 1 January 2025 | each: `MA`, the wedding day | yes – joint return | [I – high] |
| Partnership declared in 2025 | `CE`, 1 January 2025 (or `DI` / `VE` with its own date) | `PA`, the day of the declaration | no – each files alone | [I – high] |
| Moving apart without a court decision | each: `MA`, the wedding day | each: `SF`, the day of the separation | yes – joint return | [I – high] |
| Court permission to live apart in 2025 | each: `MA`, the wedding day | each: `SV`, the day of the decision | yes – last joint return | [I – high] |
| Divorce in 2025 after a court permission of an earlier year | `SV`, the day of that permission | `DI`, the day of the divorce | no – files alone | [I – medium · RET-O-05] |
| A spouse dies in 2025 – the survivor | `MA`, the wedding day | `VE`, the day of the death | yes | [I – high] |
| – the deceased spouse | `MA`, the wedding day | `DE`, the day of the death | – | [I – medium · RET-O-05] |
| Widowed in an earlier year | `VE`, the day of the death | none – answer no | no | [I – high] |

In the year of death the survivor is the « contribuable » – the person who is logged in and signs – and the deceased is the « conjoint ». [I]

## Addresses

| What | Taxpayer | Spouse or partner | In the schema |
|---|---|---|---|
| Same address as the taxpayer? | – | `G0660_MEME_ADR_CONJ` | required |
| Current address | `G0500_ADR_ACT_CONT` | `G0680_ADR_ACT_CONJ` | required – for the spouse also when the address is the same |
| Other addresses during the year? | `G0580_AUTRE_CHG_ADR_CONT` | `G0760_AUTRE_CHG_ADR_CONJ` | required, yes or no |
| One group per other address, up to ten | `AutreAdrContrib` | `AutreAdrConj` | optional |
| – start date, end date, the address | `G0600`, `G0620`, `G0640` | `G0780`, `G0800`, `G0820` | all three required in the group |

[C · lu-income-tax-personal S75]

- The first address is the current home; the list holds the other homes « au cours de l'année ». A move after 31 December is not an "other address" of the year. [C · lu-income-tax-personal S75, lu-income-tax-personal S156 for the wording; I for the reading] Whether « current » means the day of filing or 31 December: RET-O-06. [O]
- An address held since before the year starts on 1 January in the list – the paper form prints « Du 1/1/2025 au ». The end date is the last day at that address. [I · lu-income-tax-personal S1]
- The 2021 guide called the spouse's address unnecessary when it is the same; the 2025 schema requires it, so repeat it. The « address on 31 December » fields of 2021 no longer exist. [C · lu-income-tax-personal S171; lu-income-tax-personal S75]
- Luxembourg addresses must match the national address register exactly; spouses in different countries, or a change of country in the year, close the assistant to the household. [C · lu-income-tax-personal S171 for the register; lu-income-tax-personal S205 for the exclusions]
- Example (invented): the spouses lived at address A; the spouse moved to address B on 1 July 2025. Taxpayer: current address A, no other address. Spouse: same address « no », current address B, other addresses « yes », one group from 1 January 2025 to 30 June 2025 with address A. [I]

## Eligibility questions

The block `Eligibilite` is optional, and so is each of its ten answers; left out, the filer answers on screen. [C · lu-income-tax-personal S75]

- `G9030` « Avez-vous été marié(e) au cours de l'année d'imposition ? » and `G9040`, the same for a partnership, ask about any time in the year: a person who married in June, divorced in January or lost a spouse in December answers yes; a partnership declared in June gives yes for `G9040`, although joint taxation is not possible for that year. [C · lu-income-tax-personal S75 for the wording; I – high]
- `G9070` « marié(e) plus d'une fois au cours de l'année » = yes ends the electronic route. [C · lu-income-tax-personal S205]
- `G9060` (individual taxation) is for jointly taxable spouses who choose it: no for a person who is taxed alone by law. `G9080` (same country) is put to jointly taxable spouses: leave it out for a person filing alone. [I – medium]
- A marriage, partnership, separation, divorce or death in the year does not by itself close the assistant: the ACD's list of exclusions names none of them. [C · lu-income-tax-personal S205 for the list; I]

## Signatures

`SignatureMandataire` is optional. [C · lu-income-tax-personal S75] Its first question, `G2810_SIG_CONT_CONJ`, has three answers: `CONT_CONT` – the taxpayer signs « en son propre nom et pour » the spouse; `CONT_CONJ` – each signs in their own name; `CONT_MAN_CONJ` – an agent signs for the spouse. No answer names a deceased spouse or heirs. [C · lu-income-tax-personal S75]

- A joint return needs one electronic signature per person; when one signs for both, the mandate (Form 101) is asked for at the end. [C · lu-income-tax-personal S205; lu-income-tax-personal S206]
- **A spouse died during the tax year:** the filer « peut joindre l'acte de décès à la place du contrat de mandat ». [C · lu-income-tax-personal S56] So the survivor chooses « signs in own name and for the spouse » (`CONT_CONT`) and attaches the death certificate where the mandate is asked for; or leave the block out and choose on screen. [I – high] What the assistant asks once the spouse's status is `DE` was not seen. [O · RET-O-01] The paper form: lu-income-tax-personal PIT-O-41.
- The partners' joint request is `G1940_ASS_DEM_3BIS` in `ModeImposition` (paper 312); not in a year in which the partnership was declared or ended. [C · lu-income-tax-personal S75; rule: lu-income-tax-personal family-changes.md]
