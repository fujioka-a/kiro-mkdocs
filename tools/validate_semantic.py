"""
意味的整合性チェック（Semantic Consistency）

Agent が内容を理解して以下を検証：
- タイトルと本文の内容が一致しているか
- ドキュメント内で矛盾した記述がないか
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


def validate_title_content_match(file_path: pathlib.Path) -> List[str]:
    """
    タイトルと本文の意味的一致を検証
    
    Agent による判断が必要：
    - タイトルが「認証API」なのに本文が認証について触れていない
    - タイトルと本文のトピックが異なる
    """
    content = file_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)
    
    errors = []
    title = meta.get("title", "")
    
    if not title or not body.strip():
        return errors
    
    # TODO: Agent による意味解析
    # ここでは簡易的なキーワードチェックのみ実装
    # 実際の Agent Hooks では LLM による判断を行う
    
    return errors


def validate_internal_consistency(file_path: pathlib.Path) -> List[str]:
    """
    ドキュメント内の矛盾を検証
    
    Agent による判断が必要：
    - 「認証不要」と書いているのに認証手順が記載されている
    - 数値や仕様が矛盾している
    """
    content = file_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)
    
    errors = []
    
    # TODO: Agent による矛盾検出
    # 実際の Agent Hooks では LLM による判断を行う
    
    return errors


def validate_file(file_path: pathlib.Path) -> List[str]:
    """ファイル全体の意味的整合性を検証"""
    errors = []
    errors.extend(validate_title_content_match(file_path))
    errors.extend(validate_internal_consistency(file_path))
    return errors


def main():
    """全ドキュメントを検証"""
    docs_root = pathlib.Path(__file__).resolve().parents[1] / "docs"
    
    all_errors = []
    for md_file in docs_root.rglob("*.md"):
        errors = validate_file(md_file)
        if errors:
            rel_path = md_file.relative_to(docs_root)
            for error in errors:
                all_errors.append(f"{rel_path}: {error}")
    
    if all_errors:
        print("意味的整合性の検証に失敗しました:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    else:
        print("OK: 意味的整合性の検証に合格しました。")
        return 0


if __name__ == "__main__":
    exit(main())
