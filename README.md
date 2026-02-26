# Kiro × MkDocs Docs-as-Code 検証プロジェクト

## 概要
本プロジェクトは APIサーバー仕様ドキュメントの品質を自動保証する Docs 基盤の PoC です。

目的は単なるドキュメント生成ではありません。

達成したい状態：
- 仕様が腐らない
- 正式仕様が常に明確
- AI生成でも品質保証される

---

## 🎯 目的
この検証のゴールは次の責務分離を成立させることです。

| レイヤ | 役割 |
|------|------|
| Kiro | 真実の生成主体 |
| MkDocs | 表示 |
| Validator | 品質保証 |
| CI | 最終防衛線 |

---

## ❗ 解決したい課題

従来のMarkdown運用は以下の問題を持ちます。

- 古い仕様が残る
- 正式仕様が分からない
- 誰が責任者か不明
- 更新されたか判断不能

---

## 📜 ドキュメントポリシー

正式仕様条件：

status: approved

必須メタ：

title  
owner  
status  
last_reviewed  

追加制約：

last_reviewed は 90日以内

違反時挙動：

→ 保存・コミット失敗（STRICTモード）

---

## 🧠 設計思想（最重要）

設計原則：

表示ツールに品質責任を持たせない  
生成主体に品質責任を持たせる

NG設計：
MkDocs が検証

正設計：
Kiro が検証

理由：
- 表示層は責任境界外
- 編集時検知できない
- AI生成直後検知できない

---

## 🏗 システム構成

### ローカル開発フロー（個別品質保証）

docs編集
↓
Kiro hooks
↓
validate_docs.py（個別ドキュメント検証）
↓
OK → 保存
NG → 拒否

＋

docs変更
↓
watcher
↓
validate_docs.py

### CI統合フロー（全体整合性保証）

PR/Push
↓
CI実行
├─ validate_docs.py（個別品質）
├─ validate_integration.py（統合品質）
└─ mkdocs build --strict（ビルド検証）

---

## 📁 ディレクトリ構造
```shell
.
├── docs/
├── tools/
│   ├── validate_docs.py          # 個別ドキュメント品質検証
│   ├── validate_integration.py   # 統合品質検証（CI専用）
│   └── watch_docs.py
├── .kiro/
│   ├── config.yaml
│   └── hooks/
│       └── validate_docs.py
└── mkdocs.yml
```

---

## 🔍 validate_docs.py の役割

個別ドキュメントの品質判定を担当します。

検証内容：
- 必須メタデータ（title, owner, status, last_reviewed）
- owner妥当性（placeholder禁止）
- last_reviewed期限（90日以内）

呼び出し元：
- Kiro hooks
- watcher
- CI

---

## 🔗 validate_integration.py の役割

リポジトリ全体の整合性を検証します（CI専用）。

検証内容：
- ドキュメント間リンク切れ
- owner一覧の妥当性
- 重複title検出
- 統計レポート（承認率、期限切れ数）

呼び出し元：
- CI のみ

理由：
統合チェックはリポジトリ全体を対象とするため、
ローカル編集時には不要。mainブランチ統合時のみ実行。

---

## ⏱ watcher の役割

リアルタイム検知。

保存 → 即検証

効果：
- 手戻り削減
- ミス即発見
- AI生成直後検知

---

## 🤖 Kiro Hooks の役割

検証タイミング：

- pre_write
- pre_commit

防止できる問題：

- stale仕様
- owner未設定
- approved条件違反

---

## 🧪 テスト済み検証ケース

確認済み：

- 期限切れ → 失敗
- owner不正 → 失敗
- メタ欠落 → 失敗
- 正常 → 成功

---

## 🧾 運用ルール

| 項目 | 更新主体 |
|------|------|
| last_modified | 自動 |
| last_reviewed | 人間レビュー |

理由：

編集日 ≠ 妥当性確認日

---

## 🚀 開発コマンド

```bash
# 仮想環境を有効化
source .venv/bin/activate

# テスト実行
pytest tests/test_validate_docs.py -v

# 検証実行
python tools/validate_docs.py

# MkDocs起動
mkdocs serve
```

---

## 📊 STRICTモードについて

本プロジェクトはデフォルトで STRICT = true です。

理由：
警告だけでは品質保証は成立しないため。

ただしブログ解説用に警告モードも切替可能にできます。

---

## 📈 今後の拡張候補

優先順：

1. リンク整合性検証
2. ADR参照チェック
3. owner存在検証
4. OpenAPI同期
5. 差分検知

---

## 🤖 エージェント作業ルール

必須：

- 検証ロジックは validate_docs.py のみ変更可
- hooksにはロジックを書かない
- MkDocs側に検証を入れない

禁止：

- 複数validator作成
- last_reviewed自動更新
- 検証処理分散

---

## 🏁 最終目標

人間がレビューした仕様のみが正式仕様として存在する状態を
システム的に保証する。
