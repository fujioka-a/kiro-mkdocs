#!/usr/bin/env python3
"""
Kiro Hook: ドキュメント検証

このフックは pre_write および pre_commit 時に実行され、
tools/validate_docs.py を呼び出してドキュメントの品質を検証します。

検証失敗時は非ゼロ終了コードを返し、保存/コミットを中断します。
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
VALIDATE_SCRIPT = PROJECT_ROOT / "tools" / "validate_docs.py"


def main() -> int:
    """検証スクリプトを実行"""
    if not VALIDATE_SCRIPT.exists():
        print(f"エラー: 検証スクリプトが見つかりません: {VALIDATE_SCRIPT}")
        return 1

    result = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )

    # 出力を表示
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
