---
name: marginalia-fellow
description: Enforce and audit an add-only Obsidian research vault workflow. Use when Codex needs to add a vault note, choose which Ideas/Library/Projects/Archive folder and template to use, rewrite a nonconforming incoming file as a new companion note, check folder README coverage, run full-vault template/error/conflict audits, or decide which folder's files answer a research question.
---

# Marginalia Fellow

## Overview

Use this skill before adding or auditing files in the research vault. It makes folder choice, template choice, rewrite behavior, and periodic validation explicit while preserving the vault's non-negotiable add-only rule.

## Non-Negotiables

- Only add new files. Do not modify, overwrite, rename, move, or delete existing files.
- If the desired path already exists, create a new companion file with a date/topic suffix.
- If a supplied or generated note does not satisfy the target folder template, do not patch it in place. Create a new conforming rewrite beside it or in the correct folder.
- Treat `.git/`, `.obsidian/`, `.pandoc/`, and existing skill/config files as read-only unless the user gives a newer, explicit instruction for that exact file.
- Validate any new Markdown note with `python3 scripts/check_new_note_templates.py --paths <repo-relative-path>`.
- For full-vault audits, run `python3 scripts/audit_vault_integrity_2026_05_23.py`.

## Add Workflow

1. Classify the user's request by maturity and use case.
2. Read the target folder's `Readme.md` before reading detailed notes.
3. Choose the folder template from [references/template-routing.md](references/template-routing.md).
4. Create a new file only. Use the target template's frontmatter and headings.
5. If ingesting a nonconforming file, write a new conforming rewrite and preserve the original path in a `source:` frontmatter key or in the first section. For one file, use `python3 scripts/create_template_rewrite_2026_05_23.py <source-path> --dry-run`, then rerun without `--dry-run`. For existing vault debt, use `python3 scripts/rewrite_nonconforming_notes_2026_05_23.py --dry-run`, then rerun without `--dry-run`.
6. Validate the new file path with `scripts/check_new_note_templates.py`.
7. If the user asks for broad health checks, run the full audit script and report template issues, file errors, folder README gaps, and mechanical conflicts.

## Folder Routing

Use `Ideas/` for living thoughts and early research taste.

- Stable principles, research taste, evaluation values, and long-running beliefs: `Ideas/Guiding Principles/`.
- Current synthesis, critique, reflection, conceptual sharpening, and "what do I think now?" questions: `Ideas/Current Reflections/`.
- Concrete but inactive project seeds, possible experiments, paper ideas, and research questions: `Ideas/Idea Concepts/`.

Use `Library/` for durable reusable knowledge.

- Foundational or repeatedly cited papers: `Library/Classic Papers/`.
- Reusable concepts, theories, frameworks, and problem formulations: `Library/Core Theories/`.
- Study design, evaluation design, research methods, analysis plans, validity risks: `Library/Research Method/`.

Use `Projects/` for active work.

- Active project work: `Projects/<project>/`.
- Drafting, outlining, revising, argument flow, and paper claims: `Projects/<project>/paper/`.
- Supervisor feedback, decisions, project history, and meeting reconstruction: `Projects/<project>/meeting/`.
- Related work synthesis, product comparison, writing guidance, and project-level evidence: `Projects/<project>/reference/`.
- A specific cited paper, citekey, screenshot, system feature, or literature evidence: `Projects/<project>/reference/literature/<citekey>/`.

Use `Archive/` for completed or reusable historical artifacts.

- Finished/submitted paper outputs, rebuttals, appendices, final versions: `Archive/Paper Outputs/`.
- Completed project records, experiment logs, lessons learned: `Archive/Project Records/`.
- Final or near-final slides, posters, talk scripts, presentation language: `Archive/Talk Materials/`.
- Reusable templates and governance rules: `Archive/Templates/`.

## Rewrite Rule

When an incoming note does not match its folder template:

1. Keep the original file untouched.
2. Create a new Markdown file in the correct folder using the target template.
3. Preserve the original material under the relevant heading, not as an unstructured dump unless the target template has no better place.
4. Name the rewrite clearly, for example `topic-template-rewrite-2026-05-23.md`.
5. Preview the add-only rewrite with `python3 scripts/create_template_rewrite_2026_05_23.py <source-path> --dry-run`.
6. Create it with the same command without `--dry-run`.
7. Validate the rewrite with `scripts/check_new_note_templates.py --paths <new-path>`.

## Audit Workflow

Run:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py
```

This full audit checks:

- Existing template files satisfy `Archive/Templates/vault/template-rules.json`.
- All vault content folders have a `Readme.md`.
- Markdown notes under governed folders match their folder templates.
- Non-Markdown assets follow allowed folder-specific asset rules.
- Files contain no git conflict markers.
- Same-folder files do not collide by title, citekey, or meeting date.
- Git changes respect the add-only policy unless the command is run with `--skip-git-policy`.

Use `--no-fail` for scheduled reporting where the automation should summarize issues without failing the job.

By default, the audit treats a valid add-only rewrite with `source: <old-path>` as remediation for the old source's template and wiki-link issues. Use `--strict-template-sources` when you want to see those legacy source issues anyway.

## References

- [references/template-routing.md](references/template-routing.md): folder patterns, template files, required frontmatter, required headings, and asset rules.
- [references/verification.md](references/verification.md): commands for validating a new note, the skill structure, and full-vault health.
