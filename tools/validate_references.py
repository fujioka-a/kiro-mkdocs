"""
参照整合性チェック（Reference Integrity）

Agent が参照関係を理解して以下を検証：
- リンク先ドキュメントが実在するか
- 参照先が deprecated/期限切れではないか
- 循環参照がないか
"""
import pathlib
import re
from typing import List, Set, Dict, Any

import yaml


def parse_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
    """YAML フロントマターとボディを分離"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
    if not m:
        return {}, content
    
    meta = yaml.safe_load(m.group(1)) or {}
    body = m.group(2)
    return meta, body


def extract_markdown_links(content: str) -> List[str]:
    """Markdown リンクを抽出"""
    # [text](path) 形式のリンクを抽出
    pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
    matches = re.findall(pattern, content)
    return [path for _, path in matches if not path.startswith('http')]


def validate_link_targets(file_path: pathlib.Path, docs_root: pathlib.Path) -> List[str]:
    """
    リンク先の存在確認
    
    - 相対パスのリンク先が実在するか
    - リンク切れがないか
    """
    content = file_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(content)
    
    errors = []
    links = extract_markdown_links(body)
    
    for link in links:
        # アンカーリンクは除外
        if link.startswith('#'):
            continue
        
        # 相対パスを解決
        target_path = (file_path.parent / link).resolve()
        
        if not target_path.exists():
            errors.append(f"リンク切れ: {link}")
    
    return errors


def validate_referenced_doc_status(file_path: pathlib.Path, docs_root: pathlib.Path) -> List[str]:
    """
    参照先ドキュメントのステータス確認
    
    Agent による判断が必要：
    - 参照先が deprecated ではないか
    - 参照先が期限切れではないか
    - 代替ドキュメントを提案
    """
    content = file_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(content)
    
    errors = []
    links = extract_markdown_links(body)
    
    for link in links:
        if link.startswith('#') or link.startswith('http'):
            continue
        
        target_path = (file_path.parent / link).resolve()
        
        if not target_path.exists() or not target_path.suffix == '.md':
            continue
        
        try:
            target_content = target_path.read_text(encoding="utf-8")
            target_meta, _ = parse_frontmatter(target_content)
            
            status = str(target_meta.get("status", "")).lower()
            if status == "deprecated":
                errors.append(f"非推奨ドキュメントへの参照: {link}")
            
            # TODO: Agent による期限切れチェックと代替案提案
            
        except Exception:
            pass
    
    return errors


def validate_file(file_path: pathlib.Path, docs_root: pathlib.Path) -> List[str]:
    """ファイルの参照整合性を検証"""
    errors = []
    errors.extend(validate_link_targets(file_path, docs_root))
    errors.extend(validate_referenced_doc_status(file_path, docs_root))
    return errors


def main():
    """全ドキュメントを検証"""
    docs_root = pathlib.Path(__file__).resolve().parents[1] / "docs"
    
    all_errors = []
    for md_file in docs_root.rglob("*.md"):
        errors = validate_file(md_file, docs_root)
        if errors:
            rel_path = md_file.relative_to(docs_root)
            for error in errors:
                all_errors.append(f"{rel_path}: {error}")
    
    if all_errors:
        print("参照整合性の検証に失敗しました:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    else:
        print("OK: 参照整合性の検証に合格しました。")
        return 0


if __name__ == "__main__":
    exit(main())
