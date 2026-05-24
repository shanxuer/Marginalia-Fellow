# Verification

## Validate a New Note

```bash
python3 scripts/check_new_note_templates.py --paths "Ideas/Current Reflections/example.md"
```

This checks the folder template for the provided Markdown path. It also enforces the staged add-only policy when run without `--paths`.

## Validate Template Config

```bash
python3 scripts/check_new_note_templates.py --self-test
```

This confirms every configured template exists and contains the required frontmatter and headings.

## Run the Full Vault Audit

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py
```

Use this for periodic checks. It audits folder README coverage, all governed Markdown files, allowed non-Markdown assets, conflict markers, duplicate identities, broken wiki links, template self-tests, and add-only git policy.

For scheduled jobs that should produce a report without failing the automation:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py --no-fail
```

To focus on vault content while ignoring the current git working tree state:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py --skip-git-policy
```

## Create an Add-Only Rewrite

Preview a conforming companion rewrite:

```bash
python3 scripts/create_template_rewrite_2026_05_23.py "Ideas/Current Reflections/example.md" --dry-run
```

Create it after reviewing the proposed path:

```bash
python3 scripts/create_template_rewrite_2026_05_23.py "Ideas/Current Reflections/example.md"
```

The source file is never modified. The script writes a new `*-template-rewrite-YYYY-MM-DD.md` file and preserves the source path in frontmatter.

## Bulk Rewrite Existing Debt

Preview all unremediated Markdown files with template or wiki-link issues:

```bash
python3 scripts/rewrite_nonconforming_notes_2026_05_23.py --dry-run
```

Create the companion rewrites:

```bash
python3 scripts/rewrite_nonconforming_notes_2026_05_23.py
```
