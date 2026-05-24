#!/usr/bin/env python3
"""Create an add-only template rewrite for one nonconforming Markdown note."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

from check_new_note_templates import (
    extract_headings,
    load_rules,
    match_rule,
    parse_frontmatter,
    repo_root,
)


DATE_STEM_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")


def posix(path: Path) -> str:
    return path.as_posix()


def yaml_scalar(value: str) -> str:
    value = value.strip()
    if value in {"[]", "{}"} or value.startswith("["):
        return value
    if value == "":
        return ""
    if re.fullmatch(r"[A-Za-z0-9_./:@+-]+", value):
        return value
    return json.dumps(value, ensure_ascii=False)


def infer_title(path: Path, original_text: str, original_frontmatter: dict[str, str]) -> str:
    if original_frontmatter.get("title"):
        return original_frontmatter["title"]
    headings = extract_headings(original_text)
    if headings:
        return headings[0]
    return path.stem


def infer_date(path: Path, original_frontmatter: dict[str, str]) -> str:
    if original_frontmatter.get("date"):
        return original_frontmatter["date"]
    match = DATE_STEM_RE.match(path.stem)
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return date.today().isoformat()


def infer_citekey(path: Path, original_frontmatter: dict[str, str]) -> str:
    if original_frontmatter.get("citekey"):
        return original_frontmatter["citekey"]
    if path.parent.name and path.parent.name != "literature":
        return path.parent.name
    return path.stem.removeprefix("@")


def replacement_value(
    key: str,
    value: str,
    source_path: Path,
    original_frontmatter: dict[str, str],
) -> str:
    if key == "date":
        return infer_date(source_path, original_frontmatter)
    if value == "YYYY-MM-DD" or key == "created":
        return date.today().isoformat()
    if key == "citekey":
        return infer_citekey(source_path, original_frontmatter)
    if value:
        return value
    if key in original_frontmatter:
        return original_frontmatter[key]
    return ""


def next_output_path(source_path: Path) -> Path:
    today = date.today().isoformat()
    candidate = source_path.with_name(f"{source_path.stem}-template-rewrite-{today}.md")
    if not candidate.exists():
        return candidate

    counter = 2
    while True:
        candidate = source_path.with_name(f"{source_path.stem}-template-rewrite-{today}-{counter}.md")
        if not candidate.exists():
            return candidate
        counter += 1


def build_rewrite(root: Path, rel_source: Path, rule: dict) -> str:
    source_path = root / rel_source
    original_text = source_path.read_text(encoding="utf-8")
    original_frontmatter, _body = parse_frontmatter(original_text)
    template_path = root / rule["template"]
    template_text = template_path.read_text(encoding="utf-8")
    template_frontmatter, _template_body = parse_frontmatter(template_text)

    frontmatter: dict[str, str] = {}
    for key, value in template_frontmatter.items():
        frontmatter[key] = replacement_value(key, value, rel_source, original_frontmatter)

    for key, expected in rule.get("required_frontmatter", {}).items():
        frontmatter[key] = expected

    for key in rule.get("required_frontmatter_keys", []):
        frontmatter.setdefault(
            key,
            replacement_value(key, template_frontmatter.get(key, ""), rel_source, original_frontmatter),
        )

    frontmatter["source"] = posix(rel_source)

    lines = ["---"]
    for key, value in frontmatter.items():
        lines.append(f"{key}: {yaml_scalar(value)}")
    lines.extend(["---", "", f"# {infer_title(rel_source, original_text, original_frontmatter)}", ""])

    for heading in rule.get("required_headings", []):
        lines.extend(
            [
                f"## {heading}",
                "",
                f"- Template rewrite created from `{posix(rel_source)}`.",
                "",
            ]
        )

    lines.extend(
        [
            "## Original Material",
            "",
            f"Source: `{posix(rel_source)}`",
            "",
            "````markdown",
            original_text.rstrip(),
            "````",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Create a new template-compliant rewrite without editing the source file."
    )
    parser.add_argument("source", help="Repo-relative Markdown path to rewrite.")
    parser.add_argument("--output", help="Optional repo-relative output path. Must not already exist.")
    parser.add_argument("--dry-run", action="store_true", help="Print the proposed output path and content without writing.")
    args = parser.parse_args()

    root = repo_root()
    rel_source = Path(args.source)
    if rel_source.is_absolute() or ".." in rel_source.parts:
        print("Source must be a repo-relative path inside the vault.", file=sys.stderr)
        return 2

    source_path = root / rel_source
    if not source_path.exists():
        print(f"Source does not exist: {posix(rel_source)}", file=sys.stderr)
        return 2
    if source_path.suffix.lower() != ".md":
        print("Only Markdown notes can be rewritten with this script.", file=sys.stderr)
        return 2

    config = load_rules(root)
    rule = match_rule(posix(rel_source), config.get("rules", []))
    if rule is None:
        print(f"No template rule matches {posix(rel_source)}.", file=sys.stderr)
        return 2

    rel_output = Path(args.output) if args.output else next_output_path(rel_source)
    if rel_output.is_absolute() or ".." in rel_output.parts:
        print("Output must be a repo-relative path inside the vault.", file=sys.stderr)
        return 2
    output_path = root / rel_output
    if output_path.exists():
        print(f"Output already exists: {posix(rel_output)}", file=sys.stderr)
        return 2
    if not output_path.parent.exists():
        print(f"Output parent does not exist: {posix(rel_output.parent)}", file=sys.stderr)
        return 2

    content = build_rewrite(root, rel_source, rule)
    if args.dry_run:
        print(f"Proposed output: {posix(rel_output)}")
        print(content)
        return 0

    with output_path.open("x", encoding="utf-8") as handle:
        handle.write(content)
    print(f"Created template rewrite: {posix(rel_output)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
