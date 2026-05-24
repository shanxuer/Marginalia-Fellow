#!/usr/bin/env python3
"""Check add-only vault commits and new note templates."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path


RULES_PATH = Path("Archive/Templates/vault/template-rules.json")
DISALLOWED_STAGED_FILTER = "BCDMRTUX"


def run_git(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if not result.stdout:
        return []
    return [
        item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    ]


def repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return Path(result.stdout.strip())


def posix_path(path: Path) -> str:
    return path.as_posix()


def load_rules(root: Path) -> dict:
    with (root / RULES_PATH).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def is_markdown(path: str) -> bool:
    return path.lower().endswith(".md")


def is_skipped(path: str, skip_patterns: list[str]) -> bool:
    return any(fnmatch.fnmatchcase(path, pattern) for pattern in skip_patterns)


def match_rule(path: str, rules: list[dict]) -> dict | None:
    for rule in rules:
        for pattern in rule.get("patterns", []):
            if fnmatch.fnmatchcase(path, pattern):
                return rule
    return None


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---", 4)
    if end == -1:
        return {}, text

    raw = text[4:end].strip()
    body = text[end + 4 :]
    values: dict[str, str] = {}

    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value

    return values, body


def extract_headings(text: str) -> list[str]:
    headings: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if match:
            headings.append(match.group(2).strip())
    return headings


def missing_headings_in_order(headings: list[str], required: list[str]) -> list[str]:
    missing: list[str] = []
    cursor = 0
    for expected in required:
        try:
            cursor = headings.index(expected, cursor) + 1
        except ValueError:
            missing.append(expected)
    return missing


def validate_path(root: Path, path: str, config: dict) -> list[str]:
    errors: list[str] = []

    if not is_markdown(path) or is_skipped(path, config.get("skip", [])):
        return errors

    rule = match_rule(path, config.get("rules", []))
    if rule is None:
        return [
            f"{path}: no template rule matched this Markdown file. "
            f"Add a rule in {RULES_PATH} or place the note in a templated folder."
        ]

    file_path = root / path
    if not file_path.exists():
        return [f"{path}: staged as added, but file is missing from the working tree."]

    text = file_path.read_text(encoding="utf-8")
    frontmatter, _body = parse_frontmatter(text)
    headings = extract_headings(text)

    for key, expected in rule.get("required_frontmatter", {}).items():
        actual = frontmatter.get(key)
        if actual != expected:
            errors.append(
                f"{path}: frontmatter `{key}` must be `{expected}` "
                f"for template `{rule['name']}`."
            )

    for key in rule.get("required_frontmatter_keys", []):
        if key not in frontmatter:
            errors.append(
                f"{path}: missing frontmatter key `{key}` "
                f"for template `{rule['name']}`."
            )

    missing = missing_headings_in_order(headings, rule.get("required_headings", []))
    if missing:
        template = rule.get("template", "(template path missing)")
        errors.append(
            f"{path}: missing required headings, in template order: "
            f"{', '.join(missing)}. Use {template}."
        )

    return errors


def staged_added_paths() -> list[str]:
    return run_git(["diff", "--cached", "--name-only", "--diff-filter=A", "-z"])


def staged_disallowed_changes() -> list[tuple[str, list[str]]]:
    entries = run_git(
        [
            "diff",
            "--cached",
            "--name-status",
            f"--diff-filter={DISALLOWED_STAGED_FILTER}",
            "-z",
        ]
    )
    changes: list[tuple[str, list[str]]] = []
    index = 0
    while index < len(entries):
        status = entries[index]
        index += 1
        if status.startswith(("R", "C")):
            paths = entries[index : index + 2]
            index += 2
        else:
            paths = entries[index : index + 1]
            index += 1
        changes.append((status, paths))
    return changes


def validate_add_only_policy() -> list[str]:
    changes = staged_disallowed_changes()
    if not changes:
        return []

    errors = [
        "Only new files may be committed in this vault. "
        "Do not modify, delete, rename, copy from, type-change, or commit conflicted old files."
    ]
    for status, paths in changes:
        joined_paths = " -> ".join(paths)
        errors.append(f"{status}: {joined_paths}")
    return errors


def self_test(root: Path, config: dict) -> list[str]:
    errors: list[str] = []
    for rule in config.get("rules", []):
        template = rule.get("template")
        if not template:
            errors.append(f"{rule.get('name', '(unnamed rule)')}: missing template path.")
            continue
        template_path = root / template
        if not template_path.exists():
            errors.append(f"{rule['name']}: template does not exist: {template}")
            continue
        template_text = template_path.read_text(encoding="utf-8")
        frontmatter, _body = parse_frontmatter(template_text)
        headings = extract_headings(template_text)
        for key, expected in rule.get("required_frontmatter", {}).items():
            if frontmatter.get(key) != expected:
                errors.append(
                    f"{rule['name']}: template {template} has wrong `{key}` frontmatter."
                )
        for key in rule.get("required_frontmatter_keys", []):
            if key not in frontmatter:
                errors.append(
                    f"{rule['name']}: template {template} is missing `{key}` frontmatter."
                )
        missing = missing_headings_in_order(headings, rule.get("required_headings", []))
        if missing:
            errors.append(
                f"{rule['name']}: template {template} is missing headings: "
                f"{', '.join(missing)}."
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate add-only commits and newly added Markdown notes."
    )
    parser.add_argument(
        "--paths",
        nargs="*",
        help="Explicit repo-relative paths to validate instead of staged added files.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Validate that the template files satisfy their own configured rules.",
    )
    args = parser.parse_args()

    root = repo_root()
    config = load_rules(root)

    if args.self_test:
        errors = self_test(root, config)
        if errors:
            print("Template self-test failed:")
            for error in errors:
                print(f"- {error}")
            return 1
        print("Template self-test passed.")
        return 0

    policy_errors = validate_add_only_policy()
    if policy_errors:
        print("Add-only policy failed:")
        for error in policy_errors:
            print(f"- {error}")
        print("Create a new companion note instead of changing an existing file.")
        return 1

    paths = args.paths if args.paths is not None else staged_added_paths()
    paths = [posix_path(Path(path)) for path in paths]
    errors = []
    checked = 0
    for path in paths:
        if is_markdown(path) and not is_skipped(path, config.get("skip", [])):
            checked += 1
        errors.extend(validate_path(root, path, config))

    if errors:
        print("Template check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Template check passed ({checked} new Markdown note(s) checked).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
