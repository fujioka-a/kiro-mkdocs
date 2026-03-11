"""
トーン・文体一貫性チェック（Tone Consistency）

Agent が文体を理解して以下を検証：
- 敬体（です・ます）と常体（だ・である）の混在
- プロジェクト全体での文体統一
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


def detect_writing_style(content: str) -> Dict[str, int]:
    """
    文体を検出
    
    - 敬体: です・ます
    - 常体: だ・である
    """
    # コードブロックを除外
    content_without_code = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
    content_without_code = re.sub(r'`[^`]+`', '', content_without_code)
    
    # 敬体のパターン
    polite_patterns = [
        r'です[。、\s]',
        r'ます[。、\s]',
        r'ません[。、\s]',
        r'でした[。、\s]',
        r'ました[。、\s]',
    ]
    
    # 常体のパターン
    plain_patterns = [
        r'だ[。、\s]',
        r'である[。、\s]',
        r'でない[。、\s]',
        r'だった[。、\s]',
        r'であった[。、\s]',
    ]
    
    polite_count = sum(len(re.findall(p, content_without_code)) for p in polite_patterns)
    plain_count = sum(len(re.findall(p, content_without_code)) for p in plain_patterns)
    
    return {
        "polite": polite_count,
        "plain": plain_count,
    }


def validate_style_consistency(file_path: pathlib.Path) -> List[str]:
    """
    ファイル内の文体一貫性を検証
    """
    content = file_path.read_text(encoding="utf-8")
    _, body = parse_frontmatter(content)
    
    style_counts = detect_writing_style(body)
    polite = style_counts["polite"]
    plain = style_counts["plain"]
    
    errors = []
    
    # 両方が一定数以上ある場合は混在と判定
    if polite >= 3 and plain >= 3:
        errors.append(
            f"敬体（です・ます）と常体（だ・である）が混在しています "
            f"(敬体: {polite}箇所, 常体: {plain}箇所)"
        )
    
    return errors


def validate_file(file_path: pathlib.Path) -> List[str]:
    """ファイルの文体一貫性を検証"""
    return validate_style_consistency(file_path)


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
        print("文体一貫性の検証に失敗しました:")
        for error in all_errors:
            print(f"- {error}")
        return 1
    else:
        print("OK: 文体一貫性の検証に合格しました。")
        return 0


if __name__ == "__main__":
    exit(main())
