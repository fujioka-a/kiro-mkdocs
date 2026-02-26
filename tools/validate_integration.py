from __future__ import annotations

"""
統合品質チェックスクリプト（CI専用）

このスクリプトはリポジトリ全体の整合性と統合品質を検証します。
個別ドキュメントの品質チェックは validate_docs.py が担当します。

CI実行時の検証項目：
* ドキュメント間のリンク切れ検出
* owner一覧の妥当性チェック（存在しないチーム名の検出）
* 重複title検出
* 承認済みドキュメントの統計レポート
* 期限切れドキュメントの統計

このスクリプトは読み取り専用で、ファイルを変更しません。
"""

import sys
import pathlib
import re
import datetime
from typing import List, Dict, Set
from collections import defaultdict

import yaml  # type: ignore

# ドキュメントルート
DOCS_ROOT = pathlib.Path(__file__).resolve().parents[1] / "docs"

# 承認済みドキュメントの最大経過日数
APPROVED_MAX_AGE_DAYS = 90

# 許可されたowner一覧（実際のプロジェクトでは外部ファイルから読み込むことを推奨）
VALID_OWNERS = {
    "platform-team",
    "api-team",
    "security-team",
}


def parse_frontmatter(path: pathlib.Path) -> Dict[str, object]:
    """Markdownファイルからfrontmatterを抽出"""
    text = path.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if frontmatter_match:
        yaml_str = frontmatter_match.group(1)
        try:
            parsed = yaml.safe_load(yaml_str) or {}
            if isinstance(parsed, dict):
                return {str(k): v for k, v in parsed.items()}
        except Exception:
            pass
    return {}


def extract_markdown_links(path: pathlib.Path) -> List[str]:
    """Markdownファイルから相対リンクを抽出"""
    text = path.read_text(encoding="utf-8")
    # [text](link) 形式のリンクを抽出
    links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', text)
    # 相対パス（.md）のみを対象
    return [link for _, link in links if link.endswith('.md') and not link.startswith('http')]


def check_broken_links() -> List[str]:
    """ドキュメント間のリンク切れをチェック"""
    errors: List[str] = []
    
    for md_file in DOCS_ROOT.rglob("*.md"):
        links = extract_markdown_links(md_file)
        for link in links:
            # 相対パスを解決
            target = (md_file.parent / link).resolve()
            if not target.exists():
                rel_source = md_file.relative_to(DOCS_ROOT)
                errors.append(
                    f"リンク切れ: {rel_source} → {link} (ファイルが存在しません)"
                )
    
    return errors


def check_invalid_owners() -> List[str]:
    """存在しないowner名を検出"""
    errors: List[str] = []
    
    for md_file in DOCS_ROOT.rglob("*.md"):
        meta = parse_frontmatter(md_file)
        status = str(meta.get("status", "")).strip().lower()
        
        # approvedドキュメントのみチェック
        if status == "approved":
            owner = str(meta.get("owner", "")).strip().lower()
            if owner and owner not in VALID_OWNERS:
                rel_path = md_file.relative_to(DOCS_ROOT)
                errors.append(
                    f"無効なowner: {rel_path} → '{owner}' (許可リスト: {', '.join(sorted(VALID_OWNERS))})"
                )
    
    return errors


def check_duplicate_titles() -> List[str]:
    """重複したtitleを検出"""
    errors: List[str] = []
    title_to_files: Dict[str, List[pathlib.Path]] = defaultdict(list)
    
    for md_file in DOCS_ROOT.rglob("*.md"):
        meta = parse_frontmatter(md_file)
        title = str(meta.get("title", "")).strip()
        if title:
            title_to_files[title].append(md_file)
    
    for title, files in title_to_files.items():
        if len(files) > 1:
            file_list = ", ".join(str(f.relative_to(DOCS_ROOT)) for f in files)
            errors.append(
                f"重複title: '{title}' が複数ファイルで使用されています ({file_list})"
            )
    
    return errors


def generate_statistics() -> Dict[str, object]:
    """統計情報を生成"""
    total_docs = 0
    approved_docs = 0
    stale_docs = 0
    draft_docs = 0
    today = datetime.date.today()
    
    for md_file in DOCS_ROOT.rglob("*.md"):
        total_docs += 1
        meta = parse_frontmatter(md_file)
        status = str(meta.get("status", "")).strip().lower()
        
        if status == "approved":
            approved_docs += 1
            
            # 期限切れチェック
            last_reviewed_raw = meta.get("last_reviewed")
            if last_reviewed_raw:
                try:
                    reviewed_date = datetime.date.fromisoformat(str(last_reviewed_raw))
                    age_days = (today - reviewed_date).days
                    if age_days > APPROVED_MAX_AGE_DAYS:
                        stale_docs += 1
                except Exception:
                    pass
        elif status == "draft":
            draft_docs += 1
    
    return {
        "total": total_docs,
        "approved": approved_docs,
        "draft": draft_docs,
        "stale": stale_docs,
        "approval_rate": f"{approved_docs / total_docs * 100:.1f}%" if total_docs > 0 else "0%",
    }


def main(argv: List[str]) -> int:
    """エントリーポイント"""
    if not DOCS_ROOT.exists():
        print(f"ドキュメントルートが存在しません: {DOCS_ROOT}")
        return 1
    
    print("=== 統合品質チェック開始 ===\n")
    
    all_errors: List[str] = []
    
    # 1. リンク切れチェック
    print("[1/3] リンク切れチェック...")
    link_errors = check_broken_links()
    all_errors.extend(link_errors)
    if link_errors:
        print(f"  ⚠️  {len(link_errors)}件のリンク切れを検出")
    else:
        print("  ✓ リンク切れなし")
    
    # 2. 無効なownerチェック
    print("[2/3] owner妥当性チェック...")
    owner_errors = check_invalid_owners()
    all_errors.extend(owner_errors)
    if owner_errors:
        print(f"  ⚠️  {len(owner_errors)}件の無効なownerを検出")
    else:
        print("  ✓ すべてのownerが妥当")
    
    # 3. 重複titleチェック
    print("[3/3] 重複titleチェック...")
    title_errors = check_duplicate_titles()
    all_errors.extend(title_errors)
    if title_errors:
        print(f"  ⚠️  {len(title_errors)}件の重複titleを検出")
    else:
        print("  ✓ 重複titleなし")
    
    # 統計レポート
    print("\n=== 統計レポート ===")
    stats = generate_statistics()
    print(f"総ドキュメント数: {stats['total']}")
    print(f"承認済み: {stats['approved']} ({stats['approval_rate']})")
    print(f"ドラフト: {stats['draft']}")
    print(f"期限切れ: {stats['stale']}")
    
    # 結果判定
    print("\n=== 結果 ===")
    if all_errors:
        print(f"❌ 統合品質チェック失敗: {len(all_errors)}件のエラー\n")
        for err in all_errors:
            print(f"  - {err}")
        return 1
    else:
        print("✅ 統合品質チェック成功")
        return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
