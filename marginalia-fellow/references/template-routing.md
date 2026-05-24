# Template Routing

Use these rules when adding or rewriting files. The source of truth for Markdown validation is `Archive/Templates/vault/template-rules.json`; this file is the human-readable routing map.

## Ideas

| Folder | Template | Use for |
| --- | --- | --- |
| `Ideas/` | `Archive/Templates/vault/ideas-root-note.md` | Overview notes about the idea space. |
| `Ideas/Guiding Principles/` | `Archive/Templates/vault/ideas-guiding-principle.md` | Stable principles, research taste, evaluation beliefs. |
| `Ideas/Current Reflections/` | `Archive/Templates/vault/ideas-current-reflection.md` | Current synthesis, critique, conceptual reflection. |
| `Ideas/Idea Concepts/` | `Archive/Templates/vault/idea-concept.md` | Concrete but inactive research ideas. |

## Library

| Folder | Template | Use for |
| --- | --- | --- |
| `Library/` | `Archive/Templates/vault/library-root-note.md` | Library overview and durable knowledge maps. |
| `Library/Classic Papers/` | `Archive/Templates/vault/library-classic-paper.md` | Foundational or repeatedly cited papers. |
| `Library/Core Theories/` | `Archive/Templates/vault/library-core-theory.md` | Concepts, frameworks, and theory notes. |
| `Library/Research Method/` | `Archive/Templates/vault/library-method.md` | Methods, evaluations, validity, study design. |

## Projects

| Folder | Template | Use for |
| --- | --- | --- |
| `Projects/` | `Archive/Templates/vault/projects-root-note.md` | Project overview notes. |
| `Projects/<project>/` | `Archive/Templates/vault/project-index.md` | Active project index notes. |
| `Projects/<project>/paper/` | `Archive/Templates/vault/project-paper-draft.md` | Active paper drafts, outlines, argument notes. |
| `Projects/<project>/meeting/` | `Archive/Templates/vault/project-meeting-note.md` | Dated meetings, decisions, feedback, actions. |
| `Projects/<project>/reference/` | `Archive/Templates/vault/project-reference-note.md` | Project-specific references, summaries, guidelines. |
| `Projects/<project>/reference/literature/<citekey>/` | `Archive/Templates/vault/project-literature-note.md` | Individual paper notes and literature evidence. |

## Archive

| Folder | Template | Use for |
| --- | --- | --- |
| `Archive/` | `Archive/Templates/vault/archive-index-note.md` | Archive overview notes. |
| `Archive/Paper Outputs/` | `Archive/Templates/vault/archive-paper-output.md` | Submitted/final paper materials. |
| `Archive/Project Records/` | `Archive/Templates/vault/archive-project-record.md` | Completed project records and lessons. |
| `Archive/Talk Materials/` | `Archive/Templates/vault/archive-talk-material.md` | Final slides, posters, talks, scripts. |
| `Archive/Templates/` | Add-only governance/template area | Reusable templates and validation policy. |

## Asset Rules

- `Projects/<project>/reference/*.bib`: bibliography files; must be non-empty and contain at least one BibTeX entry marker such as `@article`.
- `Projects/<project>/reference/literature/<citekey>/*.{png,jpg,jpeg,gif,webp,svg}`: literature image assets; must be non-empty and live beside at least one Markdown literature note.
- `Archive/Templates/vault/*.json`: governance config; must parse as JSON.
- Other non-Markdown files should be placed only after a folder-specific rule is added.
