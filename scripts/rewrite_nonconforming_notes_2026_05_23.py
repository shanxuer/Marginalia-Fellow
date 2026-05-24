#!/usr/bin/env python3
"""Bulk-create add-only rewrites for unremediated Markdown audit issues."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from audit_vault_integrity_2026_05_23 import audit, valid_rewrite_sources
from check_new_note_templates import load_rules, match_rule, repo_root
from create_template_rewrite_2026_05_23 import build_rewrite, next_output_path, posix


DEFAULT_CATEGORIES = {"template", "link"}


def selected_sources(root: Path, categories: set[str]) -> list[Path]:
    config = load_rules(root)
    issues, _stats = audit(root, skip_git_policy=True)
    markdown_paths = sorted(path for path in root.rglob("*.md") if ".git" not in path.parts)
    covered = valid_rewrite_sources(root, config, [path.relative_to(root) for path in markdown_paths])
    sources: set[str] = set()
    for issue in issues:
        if issue.category not in categories or not issue.path.endswith(".md"):
            continue
        if issue.path in covered:
            continue
        if match_rule(issue.path, config.get("rules", [])) is None:
            continue
        sources.add(issue.path)
    return [Path(path) for path in sorted(sources)]


def main() -> int:
    parser = argparse.ArgumentParser(description="Create companion rewrites for nonconforming Markdown notes.")
    parser.add_argument(
        "--categories",
        default=",".join(sorted(DEFAULT_CATEGORIES)),
        help="Comma-separated audit categories to rewrite. Defaults to template,link.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned rewrites without creating files.")
    args = parser.parse_args()

    root = repo_root()
    categories = {item.strip() for item in args.categories.split(",") if item.strip()}
    config = load_rules(root)
    sources = selected_sources(root, categories)

    if not sources:
        print("No unremediated Markdown sources need add-only rewrites.")
        return 0

    print(f"Planned add-only rewrites: {len(sources)}")
    for rel_source in sources:
        rule = match_rule(posix(rel_source), config.get("rules", []))
        if rule is None:
            print(f"Skipping without template rule: {posix(rel_source)}", file=sys.stderr)
            continue
        rel_output = next_output_path(rel_source)
        print(f"- {posix(rel_source)} -> {posix(rel_output)}")
        if args.dry_run:
            continue
        content = build_rewrite(root, rel_source, rule)
        with (root / rel_output).open("x", encoding="utf-8") as handle:
            handle.write(content)

    return 0


if __name__ == "__main__":
    sys.exit(main())
