# Rules 設計・実装計画（Kiro × MkDocs Docs運用）

1. 目的

本計画は、docs/ 配下のドキュメント運用を「仕組みで維持」するための 運用ルール（Rules） を文章化し、かつ Kiro Hooks / CI / Validator と矛盾なく運用できる状態にする。

前提：
	•	ローカルのKiro Hooksは既に作成済み
	•	バリデーションは approvedのみ厳格（draft等は対象外）
	•	仕様の単一正本（SSOT）は tools/validate_docs.py

成果物：
	•	ルール文書（Rules）
	•	ルール文書のテンプレ（必要なら）
	•	PR/レビュー運用の最低限（必要なら）

非目標：
	•	OpenAPI（openapi.yaml）の導入や連携（本ブログでは扱わない）
	•	実装と仕様の完全一致を機械的に保証（初手では扱わない）

⸻

2. スコープ

2.1 対象
	•	docs/ 配下のMarkdownドキュメント（特に status: approved の正式仕様）
	•	ドキュメント更新の責務（owner、review）
	•	バリデーション結果に応じた修正フロー
	•	CIでの最終ゲート（同一Validator実行）

2.2 対象外（今回は書いても「拡張案」止まり）
	•	外部リンク切れの網羅的検証
	•	実装差分からの仕様差分推定
	•	OpenAPIのSSOT化

⸻

3. ルール体系（文書構造）

Rulesは「人に読ませる」ことを主目的としつつ、AIにも誤解されにくいように MUST / MUST NOT / SHOULD の規範語彙を用いる。

推奨ファイル：
	•	docs/99_rules/RULES.md（運用ルール本体）
	•	docs/99_rules/TEMPLATES.md（雛形集。任意）
	•	docs/99_rules/FAQ.md（よくある迷い。任意）

章立て案（RULES.md）：
	1.	このルールの目的と適用範囲
	2.	用語定義（approved / draft / owner / last_reviewed など）
	3.	正式仕様（approved）の定義
	4.	更新フロー（いつ何を更新するか）
	5.	禁止事項（last_reviewedの自動更新など）
	6.	例外と判断基準（軽微変更時など）
	7.	推奨ディレクトリ構造（docs配下の整理）
	8.	トラブルシュート（Hookで落ちたときの手順）
	9.	変更管理（ルールの改訂手順）

⸻

4. ルール内容（MVP）

4.1 正式仕様（approved）の定義
	•	status: approved を持つドキュメントのみが「正式仕様」である
	•	approvedドキュメントは、以下のfrontmatterを 必須 とする
	•	title
	•	owner
	•	status
	•	last_reviewed
	•	last_reviewed は ISO日付（YYYY-MM-DD）
	•	last_reviewed が90日超過の場合は stale とみなし、修正・レビューを促す（Validatorが失敗）

4.2 更新責務
	•	owner は必ず実在の個人またはチーム名
	•	owner は「更新の責務を持つ窓口」であり、「作成者」とは別概念
	•	owner は簡単に変更しない（引き継ぎ時のみ変更）

4.3 last_reviewed の扱い（重要）
	•	last_reviewed は「人間が内容妥当性を確認した日」
	•	last_reviewed は 自動更新してはならない
	•	編集日（last_modified）とは分離する
	•	AIによる自動更新も禁止

4.4 バリデーションと失敗時の行動
	•	Hook/CIでバリデーションが失敗した場合、以下のいずれかで解決する
	1.	frontmatter不足を補う
	2.	ownerを正しい値にする
	3.	staleであれば、内容確認の上で人間がlast_reviewedを更新する
	4.	まだ正式ではない場合、status を draft 等に変更する（approvedから外す）

⸻

5. 「実装を直したらmdも直す」ルールの扱い（今回の方針）

ブログ（今回）では OpenAPI を扱わず、まずはルール文書として以下を明記する。
	•	API実装に影響する変更を行った場合、関連する仕様ドキュメント（例：docs/10_api/）の更新を SHOULD とする
	•	更新が必要か判断に迷う場合は、ownerにレビュー依頼する
	•	具体的な強制（差分ベースのCIチェック）は「拡張案」として紹介する（実装はKiro側の次フェーズ）

注：
	•	この項目はルール本文に入れるが、現時点のHook/Validatorはapprovedのメタ整合のみを担うため、ここは「運用規範」として位置づける

⸻

6. 例外・判断基準（MVPで最低限）

例外の考え方を明文化して、運用の摩擦を減らす。

例：
	•	タイポ修正、表現調整のみ：last_reviewedは更新しない（人間レビューを伴わないため）
	•	挙動/仕様に影響する変更：原則、仕様ドキュメント更新＋人間レビューを推奨
	•	一時対応/暫定：approvedにしない（draftのまま運用）

⸻

7. 作成手順（Kiro向け実行ステップ）

Step 1: ルール文書の作成
	•	docs/99_rules/RULES.md を新規作成
	•	上記章立てに従い、MVPルールを文章化

Step 2: テンプレ（任意）
	•	docs/99_rules/TEMPLATES.md を作成し、以下を提供
	•	approvedドキュメント用 frontmatter 雛形
	•	API仕様ページの雛形（ユースケース/リクエスト/レスポンス/エラー/互換性注意 など）

Step 3: MkDocs ナビへの追加
	•	mkdocs.yml のnavに 99_rules を追加（または自動検出運用なら不要）

Step 4: 既存ドキュメントへの適用（必要最小限）
	•	まずは docs/10_api/ の代表ドキュメント1〜2個だけを approved 化し、運用を回す
	•	全面適用は後回し（初期負債が増えるため）

⸻

8. 受け入れ条件（Definition of Done）
	•	docs/99_rules/RULES.md が存在し、ルールがMVPとして一貫している
	•	approvedの定義・必須メタ・last_reviewed方針が明確
	•	Hookで落ちたときの修正手順がRULESに書かれている
	•	MkDocsで閲覧できる（最低限）
	•	ブログ本文の主張（責務分離、Validator SSOT、approvedのみ厳格）と矛盾しない

⸻

9. 将来拡張（ブログの「次回予告」用）
	•	CIで差分ベースのDocs更新検知（API変更があれば docs/10_api/ 更新必須など）
	•	内部リンク整合チェック（CIのみ）
	•	ownerの許容値リスト化（チーム運用が固まってから）
	•	deprecatedステータス導入（代替リンク必須など）

⸻

10. メモ（ルール記述のトーン）
	•	企業技術ブログ・社内標準の両方で使えるよう、断定過多を避ける
	•	ただし禁止事項（last_reviewed自動更新など）は明確に MUST NOT で記載
	•	例外や判断基準は SHOULD で柔軟性を残す
