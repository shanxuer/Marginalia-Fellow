# Marginalia Fellow

An add-only research vault companion for scholarly notes, templates, and quiet judgment.

This kit provides:

- folder-specific Markdown templates for `Ideas/`, `Library/`, `Projects/`, and `Archive/`
- `Archive/Templates/vault/template-rules.json` as the folder-to-template validation source of truth
- pre-commit enforcement for add-only commits and newly added note templates
- full-vault audits for template drift, missing folder README files, invalid assets, conflict markers, duplicate identities, and broken wiki links
- add-only rewrite scripts that create companion files instead of editing old notes
- a Codex skill that teaches agents which folder and template to use

## Layout

```text
Archive/Templates/vault/        Markdown templates and template rules
scripts/                        Validation and add-only rewrite scripts
.githooks/pre-commit            Git hook for local enforcement
marginalia-fellow/              Codex skill for folder routing and audits
```

## Install In A Vault

Copy these folders into the root of an Obsidian vault:

```bash
Archive/Templates/vault
scripts
.githooks
marginalia-fellow
```

Then enable the pre-commit hook:

```bash
git config core.hooksPath .githooks
```

## Validate

Check configured templates:

```bash
python3 scripts/check_new_note_templates.py --self-test
```

Run a full vault audit:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py --no-fail
```

Preview add-only rewrites for old notes that do not match templates:

```bash
python3 scripts/rewrite_nonconforming_notes_2026_05_23.py --dry-run
```

## Add-Only Rule

Agents should only add files. They should not modify, delete, rename, or move existing notes. If a note does not match its folder template, create a new companion rewrite with `source: <old-path>` in frontmatter.

## Notes

The templates are opinionated for a research vault organized by maturity:

- `Ideas/`: early thinking, principles, and current reflections
- `Library/`: stable reusable knowledge
- `Projects/`: active research work
- `Archive/`: completed outputs and reusable history

Adjust `Archive/Templates/vault/template-rules.json` if your vault uses different folders.
