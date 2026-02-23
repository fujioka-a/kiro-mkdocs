from __future__ import annotations

"""
Central documentation validation script.

This script enforces a set of quality rules on Markdown documents
within the `docs` directory.  It is intended to be the single
source of truth for validation logic so that different entrypoints
(Kiro hooks, file watchers, CI) can all call the same code.

Rules enforced:

* Only documents with `status: approved` in their frontmatter are
  considered "formal" and therefore subject to strict validation.
* Approved documents must specify the following frontmatter keys:
  `title`, `owner`, `status`, `last_reviewed`.
* Approved documents must not have an unknown owner (e.g. "unknown"
  or "tbd").  The owner should be a real name or team.
* The `last_reviewed` date must be in ISO format (YYYY-MM-DD).  If
  the date is more than `APPROVED_MAX_AGE_DAYS` days in the past,
  the document is considered stale and validation fails.

When a validation error is detected the script prints a summary of
errors and exits with a non‑zero exit code.  On success it prints
a simple OK message and exits with status 0.

This script does not modify files.  It is purely a checker.
"""

import sys
import pathlib
import datetime
from typing import Iterable, List

# We avoid using the python-frontmatter package because it may not be installed
# in this environment.  Instead, we parse YAML front matter manually using
# PyYAML (which is available by default).
import re
import yaml  # type: ignore

# Relative path to the documentation root.  Change this if your docs
# live elsewhere.
DOCS_ROOT = pathlib.Path(__file__).resolve().parents[1] / "docs"

# Maximum age, in days, before an approved document is considered stale.
APPROVED_MAX_AGE_DAYS = 90

# Keys required for approved documents.
REQUIRED_KEYS: Iterable[str] = ["title", "owner", "status", "last_reviewed"]


def is_blank(value: object) -> bool:
    """Return True if the given frontmatter field is considered blank."""
    return value is None or str(value).strip() == ""


def get_display_path(path: pathlib.Path) -> str:
    """Get a display-friendly path for error messages."""
    try:
        return str(path.relative_to(DOCS_ROOT))
    except ValueError:
        # Path is not under DOCS_ROOT (e.g., in tests)
        return path.name


def validate_markdown_file(path: pathlib.Path, today: datetime.date) -> List[str]:
    """Validate a single Markdown file.

    Returns a list of error strings.  If empty, the file is valid.
    """
    errors: List[str] = []
    display_path = get_display_path(path)
    
    # Read file contents and parse YAML frontmatter manually.
    text = path.read_text(encoding="utf-8")
    fm_meta: dict[str, object] = {}
    # Look for a YAML frontmatter block at the very top of the file.  It
    # should start with "---\n" and be terminated by another line starting
    # with "---".  Anything outside these delimiters is treated as the
    # body and ignored for validation.
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if frontmatter_match:
        yaml_str = frontmatter_match.group(1)
        try:
            parsed = yaml.safe_load(yaml_str) or {}
            if isinstance(parsed, dict):
                fm_meta = {str(k): v for k, v in parsed.items()}
        except Exception as exc:
            return [
                f"{display_path}: failed to parse YAML frontmatter: {exc}"
            ]
    meta = fm_meta
    status = str(meta.get("status", "")).strip().lower()

    # Only validate approved documents.  Drafts and others are ignored.
    if status != "approved":
        return errors

    # Ensure all required keys are present and non‑blank
    for key in REQUIRED_KEYS:
        if is_blank(meta.get(key)):
            errors.append(
                f"{display_path}: missing required key '{key}' for approved document."
            )

    # Owner must not be a placeholder
    owner = str(meta.get("owner", "")).strip().lower()
    if owner in {"unknown", "tbd", ""}:
        errors.append(
            f"{display_path}: owner must be a real name or team, not '{owner or 'blank'}'."
        )

    # Validate last_reviewed date format and freshness
    last_reviewed_raw = meta.get("last_reviewed")
    if not is_blank(last_reviewed_raw):
        try:
            reviewed_date = datetime.date.fromisoformat(str(last_reviewed_raw))
        except Exception:
            errors.append(
                f"{display_path}: invalid date format in last_reviewed: '{last_reviewed_raw}'. Use YYYY-MM-DD."
            )
        else:
            age_days = (today - reviewed_date).days
            if age_days > APPROVED_MAX_AGE_DAYS:
                errors.append(
                    f"{display_path}: document is stale (last_reviewed {age_days} days ago > {APPROVED_MAX_AGE_DAYS} days)."
                )

    return errors


def main(argv: List[str]) -> int:
    """Entry point for command‑line execution."""
    today = datetime.date.today()
    all_errors: List[str] = []
    if not DOCS_ROOT.exists():
        print(f"Documentation root does not exist: {DOCS_ROOT}")
        return 1
    for md_file in DOCS_ROOT.rglob("*.md"):
        all_errors.extend(validate_markdown_file(md_file, today))
    if all_errors:
        print("Documentation validation failed:")
        for err in all_errors:
            print(f"- {err}")
        return 1
    else:
        print("OK: documentation validation passed.")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))