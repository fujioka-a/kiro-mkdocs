"""
完全性チェック（Completeness）

Agent がドキュメントタイプを理解して以下を検証：
- API仕様なら必須セクションが揃っているか
- 前提条件・制約事項が明記されているか
"""
import pathlib
import re
from typing import List, Dict, Any, Set

import yaml


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """YAML フロントマターとボディを分離"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not m:
        return {}, content
    
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return meta, body


def extract_headers(content: str) -> Set[str]:
    """Markdown ヘッダーを抽出"""
    pattern = r'^#+\s+(.+)$'
    matches = re.findall(pattern, content, re.MULTILINE)
    return {h.strip().lower() for h in matches}


def validate_api_spec_completeness(file_path: pathlib.Path) -> List[str]:
    """
    API仕様ドキュメントの完全性を検証
    
    必須セクション：
    - エンドポイント
    - リクエスト
    - レスポンス
    - エラー
    """
    content = file_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(content)
    
    # ファイル名やタイトルから API 仕様かどうか判定
    title = meta.get("title", "").lower()
    file_name = file_path.name.lower()
    
    is_api_spec = (
        "api" in title or "api" in file_name or
        "endpoint" in title or "endpoint" in file_name
    )
    
    if not is_api_spec:
        return []
    
    errors = []
    headers = extract_headers(body)
    
    # 必須セクションのチェック（柔軟なマッチング）
    required_sections = {
        "エンドポイント": ["エンドポイント", "endpoint", "url", "path"],
        "リクエスト": ["リクエスト", "request", "パラメータ", "parameter"],
        "レスポンス": ["レスポンス", "response", "返り値", "戻り値"],
        "エラー": ["エラー", "error", "例外", "exception"],
    }
    
    for section_name, keywords in required_sections.items():
        if not any(keyword in h for h in headers for keyword in keywords):
            errors.append(f"API仕様に必須セクション '{section_name}' がありません")
    
    return errors


def validate_general_completeness(file_path: pathlib.Path) -> List[str]:
    """
    一般的な完全性を検証
    
    Agent による判断が必要：
    - 説明が十分か
    - 前提条件が明記されているか
    - 制約事項が記載されているか
    """
    content = file_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(content)
    
    errors = []
    
    # 最低限の内容チェック
    if len(body.strip()) < 100:
        errors.append("ドキュメントの内容が不十分です（100文字未満）")
    
    # TODO: Agent による詳細な完全性チェック
    # 実際の Agent Hooks では LLM による判断を行う
    
    return errors


def validate_file(file_path: pathlib.Path) -> List[str]:
    """ファイルの完全性を検証"""
    errors = []
    errors.extend(validate_api_spec_completeness(file_path))
    errors.extend(validate_general_completeness(file_path))
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
        print("完全性の検証に失敗しました:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    else:
        print("OK: 完全性の検証に合格しました。")
        return 0


if __name__ == "__main__":
    exit(main())
