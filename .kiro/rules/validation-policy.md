# バリデーションポリシー

## 目的

このルールは、ドキュメント品質検証（バリデーション）のタイミング、失敗時の対応、例外判断の基準を定義します。

---

## バリデーションの責務分離

このプロジェクトでは、バリデーションを2層に分離しています：

### 個別ドキュメント品質（validate_docs.py）

**検証内容:**
- 必須メタデータの存在確認
- `owner` の妥当性（プレースホルダー禁止）
- `last_reviewed` の期限（90日以内）
- `status: approved` の条件充足

**実行タイミング:**
- ローカル: Kiro hooks（pre_write / pre_commit）
- ローカル: ファイル保存時（watcher）
- CI: PR/push時

**実装場所:**
- `tools/validate_docs.py`（唯一の真実の源泉）

### 統合品質（validate_integration.py）

**検証内容:**
- ドキュメント間のリンク切れ
- owner一覧の妥当性
- 重複title検出
- 統計レポート（承認率、期限切れ数）

**実行タイミング:**
- CI: PR/push時のみ

**実装場所:**
- `tools/validate_integration.py`

**理由:**
- 統合チェックはリポジトリ全体を対象とするため、ローカル編集時には不要
- mainブランチ統合時のみ実行

---

## 検証タイミング

### ローカル開発

#### 1. Kiro hooks（pre_write）

**タイミング:**
- Kiroがファイルを保存する直前

**動作:**
- `tools/validate_docs.py` を実行
- 失敗時は保存を中断

**目的:**
- 不正なドキュメントの保存を防止

#### 2. Kiro hooks（pre_commit）

**タイミング:**
- Kiroがコミットする直前

**動作:**
- `tools/validate_docs.py` を実行
- 失敗時はコミットを中断

**目的:**
- 不正なドキュメントのコミットを防止

#### 3. Watcher（watch_docs.py）

**タイミング:**
- `docs/` 配下のファイルが保存されたとき

**動作:**
- `tools/validate_docs.py` を実行
- 失敗時は警告を表示（保存は中断しない）

**目的:**
- リアルタイムフィードバック
- 手戻り削減

### CI（GitHub Actions）

#### 1. 個別品質チェック

**タイミング:**
- main/masterブランチへのPR/push時

**動作:**
- `tools/validate_docs.py` を実行
- 失敗時はCIを失敗させる

**目的:**
- ローカルでの検証漏れを防止
- 最終防衛線

#### 2. 統合品質チェック

**タイミング:**
- main/masterブランチへのPR/push時

**動作:**
- `tools/validate_integration.py` を実行
- 失敗時はCIを失敗させる

**目的:**
- リポジトリ全体の整合性確認
- リンク切れ検出

#### 3. MkDocsビルド検証

**タイミング:**
- main/masterブランチへのPR/push時

**動作:**
- `mkdocs build --strict` を実行
- 失敗時はCIを失敗させる

**目的:**
- ビルドエラーの検出
- 表示確認

---

## バリデーション失敗時の対応

### エラーメッセージの読み方

バリデーターは以下の形式でエラーを出力します：

```
<ファイルパス>: <エラー内容>
```

**例:**
```
10_api/endpoints.md: missing required key 'owner' for approved document.
00_overview/auth.md: document is stale (last_reviewed 120 days ago > 90 days).
```

### 対応手順

#### 1. 必須メタデータ不足

**エラー例:**
```
missing required key 'title' for approved document.
```

**対応:**
- frontmatterに不足しているキーを追加

```yaml
---
title: API認証仕様
owner: platform-team
status: approved
last_reviewed: 2026-03-01
---
```

#### 2. owner不正

**エラー例:**
```
owner must be a real name or team, not 'unknown'.
```

**対応:**
- `owner` を実在の個人名またはチーム名に変更

```yaml
owner: platform-team
```

#### 3. 期限切れ（stale）

**エラー例:**
```
document is stale (last_reviewed 120 days ago > 90 days).
```

**対応:**
1. ドキュメント内容を確認
2. 現在も妥当であることを確認
3. `last_reviewed` を本日の日付に更新

```yaml
last_reviewed: 2026-03-01
```

**注意:**
- 内容確認なしに日付だけを更新してはならない

#### 4. まだ正式仕様ではない

**対応:**
- `status` を `draft` に変更

```yaml
status: draft
```

---

## 例外判断基準

### バリデーションをスキップしたい場合

**原則:**
- `status: approved` のドキュメントはバリデーション必須
- スキップは推奨されない

**例外:**
- 一時的に大幅な改訂作業を行う場合
  - → `status: draft` に変更してから作業

### 期限（90日）を延長したい場合

**原則:**
- 90日は `tools/validate_docs.py` の `APPROVED_MAX_AGE_DAYS` で定義
- プロジェクト固有の事情により変更可能

**変更方法:**
1. `tools/validate_docs.py` を編集
2. `APPROVED_MAX_AGE_DAYS` の値を変更
3. 変更理由をコミットメッセージに記載

**注意:**
- 期限を延ばしすぎると、仕様が腐るリスクが高まる
- 推奨値: 60〜120日

### 特定のディレクトリを検証対象外にしたい場合

**原則:**
- すべてのMarkdownファイルが検証対象
- 対象外にする場合は、バリデーターを修正

**変更方法:**
1. `tools/validate_docs.py` を編集
2. 対象外パスを除外するロジックを追加
3. 変更理由をコミットメッセージに記載

---

## STRICTモード

このプロジェクトはデフォルトで **STRICTモード** です。

**意味:**
- バリデーション失敗時は処理を中断
- 警告だけでは品質保証は成立しない

**理由:**
- 正式仕様の品質を保証するため
- 「とりあえず」の妥協を防ぐため

**変更:**
- STRICTモードの無効化は推奨されない
- プロジェクト固有の事情により変更する場合は、README.mdに明記

---

## 参考

- バリデーションロジックは `tools/validate_docs.py` と `tools/validate_integration.py` に実装
- Hooksの設定は `.kiro/config.yaml` に記載
- CI設定は `.github/workflows/validate-docs.yml` に記載
- エージェント向けルールは `AGENTS.md` に記載
