# Folder Template Index

This index records which template governs each vault content folder. The executable source of truth remains `Archive/Templates/vault/template-rules.json`; this document makes the policy easy to inspect.

## Ideas

- `Ideas/`: `ideas-root-note.md`
- `Ideas/Guiding Principles/`: `ideas-guiding-principle.md`
- `Ideas/Current Reflections/`: `ideas-current-reflection.md`
- `Ideas/Idea Concepts/`: `idea-concept.md`

## Library

- `Library/`: `library-root-note.md`
- `Library/Classic Papers/`: `library-classic-paper.md`
- `Library/Core Theories/`: `library-core-theory.md`
- `Library/Research Method/`: `library-method.md`

## Projects

- `Projects/`: `projects-root-note.md`
- `Projects/<project>/`: `project-index.md`
- `Projects/<project>/paper/`: `project-paper-draft.md`
- `Projects/<project>/meeting/`: `project-meeting-note.md`
- `Projects/<project>/reference/`: `project-reference-note.md`
- `Projects/<project>/reference/literature/<citekey>/`: `project-literature-note.md`

## Archive

- `Archive/`: `archive-index-note.md`
- `Archive/Paper Outputs/`: `archive-paper-output.md`
- `Archive/Project Records/`: `archive-project-record.md`
- `Archive/Talk Materials/`: `archive-talk-material.md`
- `Archive/Templates/`: template governance area; new Markdown here should describe reusable templates or policy.

## Add-Only Rewrite Policy

If a file does not satisfy the folder template, do not edit it in place. Create a new conforming companion file using the appropriate template, preserve the original material, and validate the new path with:

```bash
python3 scripts/check_new_note_templates.py --paths "<new repo-relative path>"
```
