---
name: write-natural-docs
description: Write or rewrite natural, concise Chinese workplace documents while preserving facts and the author's intent. Use for technical proposals, design documents, retrospectives, reports, notices, summaries, PRDs, Markdown or Yuque documents when the user asks to draft, polish, simplify, improve readability, reduce template-like wording, or “去 AI 味”.
---

# Natural document writing

Produce text that reads like it was written by a person who understands the work: specific, restrained, useful, and appropriate for the intended audience. Improve the writing itself; do not claim or attempt to evade AI-detection systems.

## Choose the editing mode

- For a new document, identify its audience, purpose, known facts, desired decision, and target format before drafting. Ask only when missing information would materially change the result.
- For a rewrite, preserve facts, conclusions, technical terms, status, uncertainty, and ownership. Change meaning only when the user requests substantive revision.
- For a partial edit, modify the requested section without unnecessarily rewriting the rest.
- For a file, preserve its format and identity unless the user requests a copy or a different format.

## Write from information, not a template

Organize the document around what the reader needs to understand or decide. Do not force every document into the same background-problem-analysis-solution-summary structure.

- Lead with the result, current situation, or concrete issue when that helps the reader.
- Give each paragraph one useful job. Merge headings that contain only one short sentence.
- Use headings that describe the actual topic or question, not generic labels repeated in every section.
- Keep evidence, examples, constraints, status, owners, risks, and next actions close to the claim they support.
- Use tables for exact comparisons, mappings, permissions, or status. Use a flowchart only when branching or sequence is hard to explain in prose.
- Match the user's original level of detail. Do not expand a short note into a grand framework without a reason.

## Remove common AI-writing signals

Revise these patterns when they do not add meaning:

- ceremonial openings such as “随着……不断发展”“在当今时代背景下”;
- empty claims such as “具有重要意义”“全面提升”“有效赋能”“形成完整闭环” without evidence;
- repeated transitions such as “首先、其次、再次、最后” or “一方面、另一方面” in every section;
- overly symmetrical lists, identical paragraph lengths, and repeated sentence patterns;
- repeated conclusions that merely restate the preceding paragraph;
- excessive bold text, quotation blocks, emojis, separators, and nested headings;
- inflated labels such as “核心抓手”“底层逻辑”“全方位”“系统性” when a concrete noun or action is clearer;
- disclaimers such as “需要注意的是”“值得一提的是” when the sentence can state the point directly;
- false precision, invented causes, invented personal experience, fabricated quotations, or emotions not supplied by the user.

Do not ban individual words mechanically. Keep them when they are accurate and natural in context.

## Make the language sound natural

- Prefer concrete subjects and verbs: state who did what, what changed, what remains, and what happens next.
- Mix short and medium sentences. Split sentences that carry several unrelated claims.
- Use ordinary professional Chinese instead of translated English syntax or slogan-like phrasing.
- Keep necessary technical terms; explain only those the target reader may not know.
- Retain uncertainty with language such as “当前确认”“仍需验证”“暂未覆盖”. Do not turn assumptions into facts.
- Allow mild variation in paragraph shape and list length. Natural writing does not need perfect visual symmetry.
- Match the author's voice. For internal technical documents, be direct and practical; for reports to management, foreground outcomes, impact, risks, and decisions.

## Format for the destination

- Use the minimum formatting needed for scanning.
- In Markdown, keep heading levels continuous, tables valid, code fences paired, and lists consistently indented.
- For Yuque Markdown, prefer standard Markdown constructs. When a diagram is useful, use basic `flowchart TB` syntax with short labels; avoid `sequenceDiagram` unless the user confirms that the target document can render it.
- Do not add a title page, metadata table, table of contents, status badges, or decorative icons unless they improve the requested document.

## Final pass

Before returning the document, check:

1. Does the opening reach the subject quickly?
2. Can every paragraph justify its place?
3. Are claims supported by facts from the source?
4. Did any rewrite change status, responsibility, scope, or uncertainty?
5. Are headings and lists shaped by the content rather than a fixed template?
6. Can any sentence be shorter or more concrete without losing meaning?
7. Does the target format render correctly?

Return the finished text or edited file. Keep the change summary brief unless the user asks for reasoning or a detailed comparison.
