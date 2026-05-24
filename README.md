# Marginalia Fellow

An add-only research vault companion for scholarly notes, templates, and quiet judgment.

Marginalia Fellow is a reusable scaffold for an Obsidian-based research vault. It gives an AI assistant a clear scholarly workspace: where to put ideas, where to keep reusable theory, where active projects live, how paper notes should be shaped, and how to audit the vault without rewriting history.

The central rule is simple:

> Agents may add new files, but they must not modify, delete, rename, or move existing notes.

When a note does not match its folder template, the agent creates a new companion rewrite instead of editing the original. That keeps provenance visible and makes the vault safer to use with AI collaborators.

## What This Provides

- A reusable folder scaffold for scholarly Obsidian vaults.
- Folder-specific Markdown templates for `Ideas/`, `Library/`, `Projects/`, and `Archive/`.
- A machine-readable template policy in `Archive/Templates/vault/template-rules.json`.
- A pre-commit hook that blocks non-additive commits and checks newly added notes.
- Full-vault audits for template drift, missing folder README files, invalid assets, conflict markers, duplicate identities, and broken wiki links.
- Add-only rewrite scripts that create companion files with `source: <old-path>` frontmatter.
- A Codex skill, `marginalia-fellow/`, that tells AI agents which folder and template to use.
- A GitHub Actions workflow that runs the template and vault integrity checks in CI.

## Philosophy

Marginalia Fellow is designed for research work where notes have different levels of maturity.

Raw thoughts should not pretend to be durable theory. A project meeting note should not be filed like a classic paper. A reusable method belongs somewhere different from a live paper draft. The structure is meant to help an AI assistant respect those distinctions.

The name comes from two ideas:

- **Marginalia**: the small, situated judgments written near the text rather than over it.
- **Fellow**: a quiet academic companion, closer to a peer than a generic filing bot.

## Repository Layout

```text
.
├── Ideas/
│   ├── Current Reflections/
│   ├── Guiding Principles/
│   └── Idea Concepts/
├── Library/
│   ├── Classic Papers/
│   ├── Core Theories/
│   └── Research Method/
├── Projects/
│   └── _project-template/
│       ├── paper/
│       ├── meeting/
│       └── reference/
│           └── literature/
│               └── _citekey/
├── Archive/
│   ├── Paper Outputs/
│   ├── Project Records/
│   ├── Talk Materials/
│   └── Templates/
│       └── vault/
├── scripts/
├── .githooks/
├── .github/workflows/
└── marginalia-fellow/
```

## Folder Model

| Folder | Purpose | Typical contents |
| --- | --- | --- |
| `Ideas/` | Work that is still forming. | Current reflections, guiding principles, early project concepts. |
| `Library/` | Stable knowledge worth reusing across projects. | Classic papers, core theories, research methods. |
| `Projects/` | Active research work. | Project index notes, paper drafts, meetings, references, literature notes. |
| `Archive/` | Completed outputs and reusable historical material. | Submitted papers, project records, talk materials, templates. |

Each content folder includes a `Readme.md` that explains what belongs there. Folder README files are directory guides and are exempt from note-template enforcement. All other governed Markdown notes must match the template for their folder.

## Template Matrix

The source of truth is `Archive/Templates/vault/template-rules.json`. The table below summarizes the default mapping.

| Path pattern | Template |
| --- | --- |
| `Ideas/*.md` | `ideas-root-note.md` |
| `Ideas/Guiding Principles/*.md` | `ideas-guiding-principle.md` |
| `Ideas/Current Reflections/*.md` | `ideas-current-reflection.md` |
| `Ideas/Idea Concepts/*.md` | `idea-concept.md` |
| `Library/*.md` | `library-root-note.md` |
| `Library/Classic Papers/*.md` | `library-classic-paper.md` |
| `Library/Core Theories/*.md` | `library-core-theory.md` |
| `Library/Research Method/*.md` | `library-method.md` |
| `Projects/*.md` | `projects-root-note.md` |
| `Projects/<project>/*.md` | `project-index.md` |
| `Projects/<project>/paper/*.md` | `project-paper-draft.md` |
| `Projects/<project>/meeting/*.md` | `project-meeting-note.md` |
| `Projects/<project>/reference/*.md` | `project-reference-note.md` |
| `Projects/<project>/reference/literature/**/*.md` | `project-literature-note.md` |
| `Archive/*.md` | `archive-index-note.md` |
| `Archive/Paper Outputs/**/*.md` | `archive-paper-output.md` |
| `Archive/Project Records/**/*.md` | `archive-project-record.md` |
| `Archive/Talk Materials/**/*.md` | `archive-talk-material.md` |

## Install In An Obsidian Vault

From your vault root, copy the scaffold and tools into place.

```bash
cp -R /path/to/Marginalia-Fellow/Ideas .
cp -R /path/to/Marginalia-Fellow/Library .
cp -R /path/to/Marginalia-Fellow/Projects .
cp -R /path/to/Marginalia-Fellow/Archive .
cp -R /path/to/Marginalia-Fellow/scripts .
cp -R /path/to/Marginalia-Fellow/.githooks .
cp -R /path/to/Marginalia-Fellow/marginalia-fellow .
```

If your vault is already a git repository, enable the pre-commit hook:

```bash
git config core.hooksPath .githooks
```

If the vault is not yet a git repository:

```bash
git init
git config core.hooksPath .githooks
```

## Start A New Project

Copy the project template and rename it:

```bash
cp -R Projects/_project-template Projects/my-project
```

Then add project files into the appropriate subfolders:

```text
Projects/my-project/
├── paper/
├── meeting/
└── reference/
    └── literature/
```

For a new paper note, use:

```text
Projects/my-project/reference/literature/<citekey>/<citekey>.md
```

For a new meeting note, use:

```text
Projects/my-project/meeting/YYYYMMDD.md
```

## Validate Templates

Check that the configured templates exist and satisfy their own rules:

```bash
python3 scripts/check_new_note_templates.py --self-test
```

Check specific new notes:

```bash
python3 scripts/check_new_note_templates.py --paths "Ideas/Current Reflections/example.md"
python3 scripts/check_new_note_templates.py --paths "Projects/my-project/meeting/20260524.md"
```

Run the full vault audit:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py --no-fail
```

Ignore the current git working tree and focus only on vault contents:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py --skip-git-policy --no-fail
```

## Add-Only Rewrites

If an existing note does not match its folder template, do not edit it in place. Preview a companion rewrite:

```bash
python3 scripts/create_template_rewrite_2026_05_23.py "Ideas/Current Reflections/example.md" --dry-run
```

Create the companion rewrite:

```bash
python3 scripts/create_template_rewrite_2026_05_23.py "Ideas/Current Reflections/example.md"
```

Bulk-preview unremediated Markdown notes with template or wiki-link issues:

```bash
python3 scripts/rewrite_nonconforming_notes_2026_05_23.py --dry-run
```

Bulk-create companion rewrites:

```bash
python3 scripts/rewrite_nonconforming_notes_2026_05_23.py
```

Companion rewrites include:

```yaml
source: path/to/original.md
```

The original note is left untouched.

## AI Agent Contract

When using this vault with an AI assistant, give it these rules:

1. Only add new files.
2. Do not modify, delete, rename, or move existing files.
3. Read the relevant folder `Readme.md` before adding a note.
4. Use the template matching the destination folder.
5. If a file does not match the template, create a new companion rewrite instead of changing it.
6. Run validation before reporting completion.

The bundled Codex skill at `marginalia-fellow/SKILL.md` encodes this behavior for Codex-style agents.

## Git Hook Behavior

The pre-commit hook runs:

```bash
python3 scripts/check_new_note_templates.py
```

It blocks commits that include staged modifications, deletions, renames, copies, type changes, or unresolved conflicts for existing files. New files are allowed, but governed Markdown notes must match their folder templates.

This is intentionally strict. If the vault rule is "AI can only add files," enforcement should happen before changes enter history.

## Full Audit Behavior

The full audit checks:

- template self-test status
- folder README coverage
- governed Markdown template compliance
- allowed non-Markdown asset placement
- empty or malformed bibliography files
- image assets without neighboring literature notes
- git conflict markers
- duplicate same-folder titles
- duplicate citekeys
- duplicate meeting dates
- unresolved wiki links
- git add-only policy violations

Run it regularly:

```bash
python3 scripts/audit_vault_integrity_2026_05_23.py --no-fail
```

## GitHub Actions

This repository includes `.github/workflows/vault-integrity.yml`.

On push or pull request, CI runs:

```bash
python3 scripts/check_new_note_templates.py --self-test
python3 scripts/audit_vault_integrity_2026_05_23.py --skip-git-policy
```

The workflow validates the reusable kit itself. In a personal vault, you may remove `--skip-git-policy` if you want CI to enforce add-only git state as well.

## Customize The Vault

To change folder rules:

1. Add or edit a template in `Archive/Templates/vault/`.
2. Update `Archive/Templates/vault/template-rules.json`.
3. Run:

```bash
python3 scripts/check_new_note_templates.py --self-test
python3 scripts/audit_vault_integrity_2026_05_23.py --skip-git-policy --no-fail
```

To add a new top-level area, update:

- the folder scaffold
- its `Readme.md`
- `template-rules.json`
- `marginalia-fellow/SKILL.md`
- `marginalia-fellow/references/template-routing.md`

## Public-Safe Design

This repository is a reusable scaffold. It should contain templates, scripts, folder guides, and agent instructions. It should not contain private research notes, active paper drafts, local Obsidian workspace state, or personal literature assets.

The `.gitignore` excludes common local clutter:

```text
.DS_Store
__pycache__/
*.py[cod]
.obsidian/workspace.json
```

## License

MIT License. See `LICENSE`.
