#!/usr/bin/env python3
"""Read-only full-vault audit for templates, README coverage, and conflicts."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from check_new_note_templates import (
    RULES_PATH,
    extract_headings,
    is_markdown,
    is_skipped,
    load_rules,
    parse_frontmatter,
    repo_root,
    self_test,
    validate_path,
)


CONTENT_ROOTS = ("Ideas", "Library", "Projects", "Archive")
README_ROOTS = CONTENT_ROOTS
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
DISALLOWED_GIT_FILTER = "BCDMRTUX"
WIKILINK_RE = re.compile(r"!?\[\[([^\]|#]+)")
CONFLICT_MARKERS = ("<<<<<<< ", "=======", ">>>>>>> ")


@dataclass(frozen=True)
class Issue:
    category: str
    path: str
    message: str

    def format(self) -> str:
        if self.path:
            return f"[{self.category}] {self.path}: {self.message}"
        return f"[{self.category}] {self.message}"


def run_git(args: list[str], root: Path) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if not result.stdout:
        return []
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def posix(path: Path) -> str:
    return path.as_posix()


def is_under_content_root(path: Path) -> bool:
    return bool(path.parts) and path.parts[0] in CONTENT_ROOTS


def is_readme(path: Path) -> bool:
    return path.name.lower() == "readme.md"


def is_hidden_or_operational(path: Path) -> bool:
    return any(part.startswith(".") for part in path.parts)


def vault_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for content_root in CONTENT_ROOTS:
        start = root / content_root
        if not start.exists():
            continue
        for path in start.rglob("*"):
            rel = path.relative_to(root)
            if path.is_file() and not is_hidden_or_operational(rel):
                files.append(rel)
    return sorted(files)


def vault_dirs(root: Path) -> list[Path]:
    dirs: list[Path] = []
    for content_root in README_ROOTS:
        start = root / content_root
        if not start.exists():
            continue
        for path in [start, *start.rglob("*")]:
            rel = path.relative_to(root)
            if path.is_dir() and not is_hidden_or_operational(rel):
                dirs.append(rel)
    return sorted(dirs)


def has_readme(root: Path, rel_dir: Path) -> bool:
    directory = root / rel_dir
    return any(child.is_file() and child.name.lower() == "readme.md" for child in directory.iterdir())


def check_readmes(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    for rel_dir in vault_dirs(root):
        if not has_readme(root, rel_dir):
            issues.append(
                Issue(
                    "readme",
                    posix(rel_dir),
                    "missing Readme.md explaining the folder's purpose.",
                )
            )
    return issues


def is_literature_asset(path: Path) -> bool:
    return (
        len(path.parts) >= 6
        and path.parts[0] == "Projects"
        and path.parts[2] == "reference"
        and path.parts[3] == "literature"
        and path.suffix.lower() in IMAGE_EXTENSIONS
    )


def is_project_bib(path: Path) -> bool:
    return (
        len(path.parts) == 4
        and path.parts[0] == "Projects"
        and path.parts[2] == "reference"
        and path.suffix.lower() == ".bib"
    )


def is_template_json(path: Path) -> bool:
    return (
        len(path.parts) >= 4
        and path.parts[0] == "Archive"
        and path.parts[1] == "Templates"
        and path.suffix.lower() == ".json"
    )


def check_non_markdown(root: Path, rel_path: Path) -> list[Issue]:
    issues: list[Issue] = []
    path = root / rel_path
    path_text = posix(rel_path)

    if is_template_json(rel_path):
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            issues.append(Issue("asset", path_text, f"template JSON does not parse: {error}"))
        return issues

    if is_project_bib(rel_path):
        text = path.read_text(encoding="utf-8", errors="replace")
        if not text.strip():
            issues.append(Issue("asset", path_text, "bibliography file is empty."))
        if "@" not in text:
            issues.append(Issue("asset", path_text, "bibliography file has no BibTeX entry marker."))
        return issues

    if is_literature_asset(rel_path):
        if path.stat().st_size == 0:
            issues.append(Issue("asset", path_text, "literature image asset is empty."))
        sibling_notes = [
            item
            for item in path.parent.glob("*.md")
            if item.name.lower() != "readme.md"
        ]
        if not sibling_notes:
            issues.append(
                Issue(
                    "asset",
                    path_text,
                    "literature image asset must live beside at least one paper note.",
                )
            )
        return issues

    issues.append(
        Issue(
            "asset",
            path_text,
            "no non-Markdown asset rule matched this file; add a folder-specific rule before ingest.",
        )
    )
    return issues


def check_markdown_templates(root: Path, config: dict, rel_path: Path) -> list[Issue]:
    path_text = posix(rel_path)
    if is_readme(rel_path) or is_skipped(path_text, config.get("skip", [])):
        return []
    return [
        Issue("template", path_text, error.removeprefix(f"{path_text}: "))
        for error in validate_path(root, path_text, config)
    ]


def valid_rewrite_sources(root: Path, config: dict, markdown_paths: list[Path]) -> set[str]:
    sources: set[str] = set()
    for rel_path in markdown_paths:
        path_text = posix(rel_path)
        if is_readme(rel_path) or is_skipped(path_text, config.get("skip", [])):
            continue
        text = (root / rel_path).read_text(encoding="utf-8", errors="replace")
        frontmatter, _body = parse_frontmatter(text)
        source = frontmatter.get("source", "").strip()
        if not source:
            continue
        if validate_path(root, path_text, config):
            continue
        if (root / source).exists():
            sources.add(posix(Path(source)))
    return sources


def check_conflict_markers(root: Path, rel_path: Path) -> list[Issue]:
    if rel_path.suffix.lower() not in {".md", ".json", ".bib", ".yaml", ".yml"}:
        return []
    text = (root / rel_path).read_text(encoding="utf-8", errors="replace")
    issues: list[Issue] = []
    for marker in CONFLICT_MARKERS:
        if marker in text:
            issues.append(Issue("conflict", posix(rel_path), f"contains git conflict marker `{marker.strip()}`."))
    return issues


def first_heading(text: str) -> str | None:
    headings = extract_headings(text)
    return headings[0] if headings else None


def canonical_title(path: Path, frontmatter: dict[str, str], text: str) -> str:
    return (
        frontmatter.get("title")
        or first_heading(text)
        or path.stem
    ).strip().lower()


def check_identity_conflicts(root: Path, markdown_paths: list[Path]) -> list[Issue]:
    title_by_folder: dict[tuple[str, str], list[str]] = defaultdict(list)
    citekey_paths: dict[str, list[str]] = defaultdict(list)
    meeting_dates: dict[tuple[str, str], list[str]] = defaultdict(list)
    issues: list[Issue] = []

    for rel_path in markdown_paths:
        text = (root / rel_path).read_text(encoding="utf-8", errors="replace")
        frontmatter, _body = parse_frontmatter(text)
        folder = posix(rel_path.parent)
        title = canonical_title(rel_path, frontmatter, text)
        title_by_folder[(folder, title)].append(posix(rel_path))

        citekey = frontmatter.get("citekey", "").strip().lower()
        if citekey:
            citekey_paths[citekey].append(posix(rel_path))

        if (
            len(rel_path.parts) >= 4
            and rel_path.parts[0] == "Projects"
            and rel_path.parts[2] == "meeting"
            and frontmatter.get("date")
        ):
            meeting_dates[(folder, frontmatter["date"])].append(posix(rel_path))

    for (_folder, title), paths in sorted(title_by_folder.items()):
        if title != "readme" and len(paths) > 1:
            issues.append(
                Issue("conflict", paths[0], f"same-folder title collision `{title}` with: {', '.join(paths[1:])}")
            )

    for citekey, paths in sorted(citekey_paths.items()):
        if len(paths) > 1:
            issues.append(
                Issue("conflict", paths[0], f"duplicate citekey `{citekey}` also appears in: {', '.join(paths[1:])}")
            )

    for (_folder, date), paths in sorted(meeting_dates.items()):
        if len(paths) > 1:
            issues.append(
                Issue("conflict", paths[0], f"duplicate meeting date `{date}` also appears in: {', '.join(paths[1:])}")
            )

    return issues


def build_link_index(root: Path, files: list[Path]) -> set[str]:
    index: set[str] = set()
    for rel_path in files:
        path = root / rel_path
        index.add(rel_path.name.lower())
        index.add(rel_path.stem.lower())
        index.add(posix(rel_path).lower())
        if path.suffix.lower() == ".md":
            text = path.read_text(encoding="utf-8", errors="replace")
            frontmatter, _body = parse_frontmatter(text)
            if frontmatter.get("title"):
                index.add(frontmatter["title"].strip().lower())
    return index


def check_wikilinks(root: Path, markdown_paths: list[Path], files: list[Path]) -> list[Issue]:
    index = build_link_index(root, files)
    issues: list[Issue] = []
    for rel_path in markdown_paths:
        text = strip_fenced_code((root / rel_path).read_text(encoding="utf-8", errors="replace"))
        for target in WIKILINK_RE.findall(text):
            normalized = target.strip().lower()
            if not normalized or normalized in index:
                continue
            if normalized.endswith(".md") and normalized[:-3] in index:
                continue
            issues.append(Issue("link", posix(rel_path), f"unresolved wiki link `[[{target}]]`."))
    return issues


def strip_fenced_code(text: str) -> str:
    lines: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append(line)
    return "\n".join(lines)


def parse_name_status(entries: list[str]) -> list[str]:
    changes: list[str] = []
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
        changes.append(f"{status}: {' -> '.join(paths)}")
    return changes


def check_git_add_only(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    staged_added = set(run_git(["diff", "--cached", "--name-only", "--diff-filter=A", "-z"], root))
    staged_changes = parse_name_status(
        run_git(["diff", "--cached", "--name-status", f"--diff-filter={DISALLOWED_GIT_FILTER}", "-z"], root)
    )
    unstaged_entries = run_git(["diff", "--name-status", f"--diff-filter={DISALLOWED_GIT_FILTER}", "-z"], root)

    for change in staged_changes:
        issues.append(Issue("add-only", "", f"staged disallowed change: {change}"))

    index = 0
    while index < len(unstaged_entries):
        status = unstaged_entries[index]
        index += 1
        if status.startswith(("R", "C")):
            paths = unstaged_entries[index : index + 2]
            index += 2
        else:
            paths = unstaged_entries[index : index + 1]
            index += 1
        if status == "M" and paths and paths[0] in staged_added:
            continue
        issues.append(Issue("add-only", "", f"unstaged disallowed change: {status}: {' -> '.join(paths)}"))
    return issues


def audit(root: Path, skip_git_policy: bool, strict_template_sources: bool = False) -> tuple[list[Issue], dict[str, int]]:
    config = load_rules(root)
    files = vault_files(root)
    markdown_paths = [path for path in files if is_markdown(posix(path))]
    covered_sources = valid_rewrite_sources(root, config, markdown_paths)
    governed_markdown_paths = [
        path
        for path in markdown_paths
        if (
            not is_readme(path)
            and not is_skipped(posix(path), config.get("skip", []))
            and posix(path) not in covered_sources
        )
    ]
    non_markdown_paths = [path for path in files if not is_markdown(posix(path))]
    issues: list[Issue] = []

    issues.extend(Issue("template-self-test", "", error) for error in self_test(root, config))
    issues.extend(check_readmes(root))

    for rel_path in markdown_paths:
        if strict_template_sources or posix(rel_path) not in covered_sources:
            issues.extend(check_markdown_templates(root, config, rel_path))
        issues.extend(check_conflict_markers(root, rel_path))

    for rel_path in non_markdown_paths:
        issues.extend(check_non_markdown(root, rel_path))
        issues.extend(check_conflict_markers(root, rel_path))

    issues.extend(check_identity_conflicts(root, governed_markdown_paths))
    issues.extend(check_wikilinks(root, governed_markdown_paths, files))

    if not skip_git_policy:
        issues.extend(check_git_add_only(root))

    stats = {
        "files": len(files),
        "markdown": len(markdown_paths),
        "non_markdown": len(non_markdown_paths),
        "folders": len(vault_dirs(root)),
        "rewritten_sources": len(covered_sources),
        "issues": len(issues),
    }
    return issues, stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit the Obsidian research vault without editing files.")
    parser.add_argument(
        "--skip-git-policy",
        action="store_true",
        help="Do not check current staged/unstaged changes for add-only compliance.",
    )
    parser.add_argument(
        "--no-fail",
        action="store_true",
        help="Always exit 0 after printing the audit report.",
    )
    parser.add_argument(
        "--strict-template-sources",
        action="store_true",
        help="Report template/link issues even when a compliant add-only rewrite exists for the source.",
    )
    args = parser.parse_args()

    root = repo_root()
    issues, stats = audit(
        root,
        skip_git_policy=args.skip_git_policy,
        strict_template_sources=args.strict_template_sources,
    )

    print("Vault integrity audit")
    print(f"Root: {root}")
    print(f"Template rules: {RULES_PATH}")
    print(
        "Checked: "
        f"{stats['folders']} folder(s), "
        f"{stats['markdown']} Markdown file(s), "
        f"{stats['non_markdown']} non-Markdown file(s), "
        f"{stats['rewritten_sources']} add-only rewrite source(s)."
    )

    if issues:
        print(f"Issues: {len(issues)}")
        for issue in issues:
            print(f"- {issue.format()}")
    else:
        print("Issues: 0")

    if issues and not args.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
