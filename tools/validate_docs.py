import datetime
import pathlib
import re
from typing import List

import yaml


DOCS_ROOT = pathlib.Path(__file__).resolve().parents[1] / "docs"
APPROVED_MAX_AGE_DAYS = 90
REQUIRED = ("title", "owner", "status", "last_reviewed")
ALLOWED_OWNERS = {"platform-team", "dev-team", "security-team"}

def validate_file(path: pathlib.Path, today: datetime.date) -> List[str]:
    """単一ファイルの検証エラーメッセージ一覧をリターン"""

    rel = str(path.relative_to(DOCS_ROOT)) if DOCS_ROOT in path.parents else path.name
    print(f"Validating {rel}...")
    txt = path.read_text(encoding="utf-8")

    # YAML フロントマターのインライン解析（以前は _parse_frontmatter）
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", txt, re.DOTALL)
    data = yaml.safe_load(m.group(1)) or {}
    meta = {str(k): v for k, v in data.items()} if isinstance(data, dict) else {}

    errs: List[str] = []

    for k in REQUIRED:
        if meta.get(k) is None or str(meta.get(k)).strip() == "":
            errs.append(f"{rel}: 承認済みドキュメントに必須キー '{k}' がありません。")

    status = str(meta.get("status", "")).strip().lower()
    if status != "approved":
        errs.append(f"{rel}: status は 'approved' である必要があります（現在: '{status or 'blank'}'）。")

    owner = str(meta.get("owner", "")).strip().lower()
    if owner not in ALLOWED_OWNERS: 
        errs.append(f"{rel}: owner は実在の人物またはチームである必要があります（現在: '{owner or 'blank'}'）。")

    lr = meta.get("last_reviewed")
    if lr is not None and str(lr).strip() != "":
        try:
            d = datetime.date.fromisoformat(str(lr))
        except Exception:
            errs.append(f"{rel}: last_reviewed の日付形式が無効です: '{lr}'。YYYY-MM-DD を使用してください。")
        else:
            if (today - d).days > APPROVED_MAX_AGE_DAYS:
                errs.append(f"{rel}: ドキュメントが古くなっています（last_reviewed {(today-d).days}日前 > {APPROVED_MAX_AGE_DAYS}日）。")

    return errs


def main() -> int:
    today = datetime.date.today()

    errors: List[str] = []
    for p in DOCS_ROOT.rglob("*.md"):
        errors.extend(validate_file(p, today))

    if errors:
        print("ドキュメント検証に失敗しました:")
        for e in errors:
            print(f"- {e}")
        return 1
    else:
        print("OK: ドキュメント検証に合格しました。")
        return 0


if __name__ == "__main__":
    exit(main())
