"""
コンテキスト依存チェック（Context-Aware Validation）

Agent が全ドキュメントを理解して以下を検証：
- 既存ドキュメント群との重複がないか
- 同じトピックで異なる記述がないか
- 用語定義が他ドキュメントと矛盾していないか
"""
import pathlib
import re
from typing import List, Dict, Any

import yaml


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """YAML フロントマターとボディを分離"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not m:
        return {}, content
    
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return meta, body


def check_duplicate_titles(docs_root: pathlib.Path) -> List[str]:
    """重複タイトルの検出"""
    title_map: Dict[str, List[pathlib.Path]] = {}
    
    for md_file in docs_root.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(content)
        
        title = meta.get("title", "").strip()
        if title:
            if title not in title_map:
                title_map[title] = []
            title_map[title].append(md_file)
    
    errors = []
    for title, files in title_map.items():
        if len(files) > 1:
            file_names = [f.relative_to(docs_root) for f in files]
            errors.append(f"重複タイトル '{title}': {', '.join(map(str, file_names))}")
    
    return errors


def check_cross_document_consistency(docs_root: pathlib.Path) -> List[str]:
    """
    ドキュメント間の整合性を検証
    
    Agent による判断が必要：
    - 同じ用語が異なる意味で使われていないか
    - 同じトピックで矛盾した記述がないか
    - 例: ドキュメントAでは「トークン有効期限24時間」、ドキュメントBでは「1時間」
    """
    errors = []
    
    # TODO: Agent による全ドキュメント横断的な整合性チェック
    # 実際の Agent Hooks では LLM による判断を行う
    
    return errors


def main():
    """全ドキュメントを検証"""
    docs_root = pathlib.Path(__file__).resolve().parents[1] / "docs"
    
    all_errors = []
    all_errors.extend(check_duplicate_titles(docs_root))
    all_errors.extend(check_cross_document_consistency(docs_root))
    
    if all_errors:
        print("コンテキスト依存の検証に失敗しました:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    else:
        print("OK: コンテキスト依存の検証に合格しました。")
        return 0


if __name__ == "__main__":
    exit(main())
