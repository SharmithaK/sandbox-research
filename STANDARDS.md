# iSRL Research Writing Standards for IFID
**Version 1.0 — March 2026**

---

## The Boring Tuesday Test

Before publishing any report, read it twice: once as the person who wrote the regulation or ruling being discussed, and once as someone working in the food company whose label practices are being described.

If either reading produces offense — the regulation writer feels their work is being framed as inadequate or the company feels accused of deliberate evasion — the wording is biased. If either reading produces a warm feeling — the regulator feels praised for progressive policy or the company feels credited for good behaviour — the wording is trying too hard. If both readings produce nothing more than mild recognition that this is an accurate description of events, the wording is right.

Write the boring version. The boring version is the correct version.

---

## Source Standards

### Primary vs Secondary

A **primary source** is the original document: the gazette notification, the court ruling, the Codex standard, the published paper with a DOI, the official tariff schedule.

A **secondary source** is someone else's description of that document: a news article, a blog post, a legal summary, a textbook chapter, a government press release about a notification.

Secondary sources are useful for understanding a topic and finding the primary document. They are not citable in IFID research outputs.

**The rule:** if the thing you want to say can be traced to a specific primary document, cite that document. If you cannot find the primary document, do not make the claim.

### What this means in practice

| You want to cite | Find and cite instead |
|---|---|
| A news article about an FSSAI amendment | The gazette notification itself |
| A blog summarising a Supreme Court ruling | The original judgment from the court repository |
| A legal database summary of a regulation | The regulation as published in the official gazette |
| A Wikipedia article about a Codex standard | The Codex standard document directly |
| A paper that references another paper's finding | The original paper, with its DOI |

### Acceptable source categories

- Government of India official gazette notifications
- FSSAI published regulations and compendiums (fssai.gov.in)
- DGCI&S Indian Trade Classification schedules
- Supreme Court and High Court original judgments (official repositories)
- Codex Alimentarius Commission standards and guidelines (fao.org/fao-who-codexalimentarius)
- JECFA evaluation reports
- Peer-reviewed papers cited by DOI
- Official ITC-HS tariff schedules
- Previous reports on IFID by iSRL

### Not acceptable as citations

- News articles
- Blog posts
- Industry association publications
- Legal database summaries (use these to find the ruling, then cite the ruling)
- Press releases
- Undated or unattributed web pages
- AI-generated summaries of any of the above

---

## Wording Standards

### Use simple words when a simple word exists

If a sentence can be said in plain language without losing precision, say it in plain language. Jargon is appropriate when it refers to a specific technical or legal term that has no plain equivalent. It is not appropriate as a substitute for clear thinking.

Examples:

| Avoid | Use instead |
|---|---|
| utilise | use |
| stakeholder ecosystem | the companies, regulators, and researchers involved |
| operationalise | apply, implement |
| granular | detailed |
| robust framework | (just describe what the framework does) |
| paradigm shift | (say what actually changed) |

### Neutral wording

Describe what the document or ruling says. Do not editorially characterise whether it is good, bad, progressive, inadequate, or overdue. If two sources disagree, report both.

Do not use language that implies intent beyond what the document states. "The regulation requires X" is accurate. "The regulation attempts to address X" implies the attempt may have failed — only say this if there is evidence it did.

### Framing regulatory changes

When a regulation was amended or replaced, describe what changed and when. Do not frame the earlier version as a failure or the later version as a correction unless the official document itself uses that language.

Accurate: *"The 2020 Regulations introduced mandatory source qualification for edible oils, which was not present in the 2011 version."*

Avoid: *"The 2011 Regulations failed to address source qualification, a gap corrected by the 2020 amendments."*

---

## Structure Standards

Every IFID research output should be reproducible: a reader with access to the cited primary sources should be able to verify every factual claim independently.

Every table should state its source. Every score or classification should trace to a specific regulatory provision, HS heading, or judicial ruling. Every claim about implementation or practice should distinguish between what the regulation requires and what the available evidence suggests actually occurs.

When evidence is absent or ambiguous, say so. "No published data was found on X" is a valid research finding.

---

---

## AI Use Standards

Using AI to discover sources, understand a topic, or get oriented in an unfamiliar area is fine and encouraged. Using AI to understand what a regulation or ruling is saying before you read it yourself is fine. Using AI to proofread a draft for grammar and clarity is fine.

What is not acceptable: using AI to write claims you have not verified yourself, or citing a source because AI told you it exists without reading it. You are responsible for every claim in your output and every source you cite. If AI suggested a source, find it, read it, and decide for yourself whether it supports the claim. If you cannot find it, do not cite it.

The practical test: could you defend every sentence in your report in a conversation with someone who has read all the primary sources? If yes, the AI use was fine. If no, rewrite until yes.

AI has a consistent habit of replacing simple words with jargon and adding qualifiers that sound neutral but carry implicit judgment. Apply the Boring Tuesday Test to any AI-assisted draft before accepting its wording. Trust your own reading over the AI's suggestions when they differ.

---

## Submission Standards

Every research output — however small — is submitted as three files. No exceptions.

### The three files

**`report-id.C.md` — Claim list**

Before writing the report, write 5–6 bullet points (more if genuinely needed, not as a default) stating what the report is actually trying to say. One or two lines per claim. If you cannot distill the report to this, the question you are trying to answer is not yet clear enough to write the report. Stop and clarify the question first.

Once you have the claims, assign numbers by importance: C.01 is the most important claim, the last number is the least important. These numbers become the claim IDs used across all three files.

Claim IDs follow the format `report-id.C.xx` — for example, `ALLER.C.01` for the first claim in the allergen report.

**`report-id.papertable.md` — Source table**

A table with one row per source used. Columns:

| S.No | Title | DOI / Link | Claim Supported | Type of Support | Relevance |
|---|---|---|---|---|---|

- **DOI / Link:** DOI for papers. Direct URL to official government publication only where no DOI exists. No other links.
- **Claim Supported:** the claim ID(s) this source supports, e.g. `ALLER.C.01`, `ALLER.C.03`
- **Type of Support:** `direct` (the source explicitly states the claim) or `inferred` (the claim follows from what the source states but is not stated directly)
- **Relevance:** the specific paragraph, section, regulation number, or page where the support appears — precise enough that someone else can find it without reading the whole document

A source that appears in the report but not in the paper table is a problem. A source in the paper table that does not map to a claim is a problem.

**`report-id.main.md` — The report**

Written after the claim list and paper table are complete. Every factual claim in the report should correspond to a claim ID and at least one row in the paper table. The report does not need to display the claim IDs inline — they live in the claim list file. The report should be readable as a standalone document.

### Why this order

Writing the claims first forces clarity about what the report is actually arguing before any prose is written. The paper table forces you to check whether the sources you have actually support the claims you want to make — before you have written paragraphs around them that are hard to change. The report then almost writes itself, and any gap between what you want to say and what the sources support is visible before submission rather than after review.

### File naming

Use a short uppercase report ID consistently across all three files. Examples: `ALLER` for the allergen report, `PROCSTATE` for the processing state report, `FSCORE` for the F score constitutional constraints report. State the report ID at the top of each issue.
