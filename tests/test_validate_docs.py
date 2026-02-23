"""
validate_docs.py のユニットテスト

各検証ルールが正しく動作することを確認します。
"""

import datetime
import tempfile
from pathlib import Path

import pytest

# テスト対象モジュールをインポート
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from validate_docs import validate_markdown_file, is_blank, APPROVED_MAX_AGE_DAYS


class TestIsBlank:
    """is_blank関数のテスト"""

    def test_none_is_blank(self):
        assert is_blank(None) is True

    def test_empty_string_is_blank(self):
        assert is_blank("") is True

    def test_whitespace_is_blank(self):
        assert is_blank("   ") is True

    def test_non_blank_string(self):
        assert is_blank("platform-team") is False


class TestValidateMarkdownFile:
    """validate_markdown_file関数のテスト"""

    def create_temp_md(self, content: str) -> Path:
        """一時的なMarkdownファイルを作成"""
        tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
        tmp.write(content)
        tmp.close()
        return Path(tmp.name)

    def test_valid_approved_document(self):
        """正常なapprovedドキュメント"""
        content = """---
title: Valid Document
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# Valid Document
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert errors == []

    def test_draft_document_not_validated(self):
        """draftドキュメントは検証されない"""
        content = """---
title: Draft Document
status: draft
---

# Draft Document
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert errors == []

    def test_missing_required_key(self):
        """必須キーが欠けている"""
        content = """---
title: Missing Owner
status: approved
last_reviewed: 2026-02-23
---

# Missing Owner
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        # ownerが欠けているため、missing keyとinvalid ownerの2つのエラーが出る
        assert len(errors) == 2
        assert any("missing required key 'owner'" in e for e in errors)

    def test_unknown_owner(self):
        """ownerがunknown"""
        content = """---
title: Unknown Owner
owner: unknown
status: approved
last_reviewed: 2026-02-23
---

# Unknown Owner
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 1
        assert "owner must be a real name or team" in errors[0]

    def test_tbd_owner(self):
        """ownerがtbd"""
        content = """---
title: TBD Owner
owner: tbd
status: approved
last_reviewed: 2026-02-23
---

# TBD Owner
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 1
        assert "owner must be a real name or team" in errors[0]

    def test_stale_document(self):
        """期限切れドキュメント"""
        content = """---
title: Stale Document
owner: platform-team
status: approved
last_reviewed: 2025-01-01
---

# Stale Document
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 1
        assert "document is stale" in errors[0]
        assert f"> {APPROVED_MAX_AGE_DAYS} days" in errors[0]

    def test_invalid_date_format(self):
        """不正な日付フォーマット"""
        content = """---
title: Invalid Date
owner: platform-team
status: approved
last_reviewed: 2026/02/23
---

# Invalid Date
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 1
        assert "invalid date format" in errors[0]

    def test_multiple_errors(self):
        """複数のエラーが同時に発生"""
        content = """---
title: Multiple Errors
owner: unknown
status: approved
last_reviewed: 2025-01-01
---

# Multiple Errors
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 2
        assert any("owner must be a real name" in e for e in errors)
        assert any("document is stale" in e for e in errors)

    def test_no_frontmatter(self):
        """frontmatterがない場合"""
        content = """# No Frontmatter

This document has no frontmatter.
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        # statusがないのでapprovedではない → 検証されない
        assert errors == []

    def test_invalid_yaml(self):
        """不正なYAML"""
        content = """---
title: Invalid YAML
owner: [unclosed
status: approved
---

# Invalid YAML
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 1
        assert "failed to parse YAML frontmatter" in errors[0]

    def test_blank_owner(self):
        """ownerが空白"""
        content = """---
title: Blank Owner
owner: ""
status: approved
last_reviewed: 2026-02-23
---

# Blank Owner
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 2
        assert any("missing required key 'owner'" in e for e in errors)
        assert any("owner must be a real name" in e for e in errors)

    def test_future_last_reviewed(self):
        """last_reviewedが未来の日付（許容される）"""
        content = """---
title: Future Review
owner: platform-team
status: approved
last_reviewed: 2026-12-31
---

# Future Review
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        # 未来の日付でもエラーにならない（負の日数）
        assert errors == []

    def test_exactly_90_days_old(self):
        """ちょうど90日前（境界値）"""
        content = """---
title: Exactly 90 Days
owner: platform-team
status: approved
last_reviewed: 2025-11-25
---

# Exactly 90 Days
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        # 90日ちょうどはOK（> 90でエラー）
        assert errors == []

    def test_91_days_old(self):
        """91日前（期限切れ）"""
        content = """---
title: 91 Days Old
owner: platform-team
status: approved
last_reviewed: 2025-11-24
---

# 91 Days Old
"""
        path = self.create_temp_md(content)
        today = datetime.date(2026, 2, 23)
        errors = validate_markdown_file(path, today)
        path.unlink()
        assert len(errors) == 1
        assert "document is stale" in errors[0]
