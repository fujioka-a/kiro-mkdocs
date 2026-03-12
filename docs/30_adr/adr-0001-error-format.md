---
title: ADR-0001 Error Format
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# ADR-0001 Error Format

## Context

本プロジェクトのAPIは複数のエンドポイントを提供していますが、エラーレスポンスの形式が統一されていません。これにより以下の問題が発生しています：

- クライアント実装側で複数のエラー形式に対応する必要がある
- ログ/トレースシステムでのエラー追跡が困難
- 運用チームがエラーの原因特定に時間を要する
- APIドキュメントの保守性が低下している

## Decision

すべてのAPIエラーレスポンスを以下の統一JSON形式で返却します：

```json
{
  "code": "ERROR_CODE",
  "message": "Human-readable error message",
  "requestId": "uuid-v4-format",
  "timestamp": "2026-03-12T10:30:00Z",
  "details": {
    "field": "optional_field_name",
    "reason": "optional_detailed_reason"
  }
}
```

### 仕様詳細

- **code**: エラーの種類を識別する一意の文字列（例：`VALIDATION_ERROR`, `RESOURCE_NOT_FOUND`, `INTERNAL_SERVER_ERROR`）
- **message**: エンドユーザーに表示可能な日本語メッセージ
- **requestId**: リクエスト追跡用のUUID v4形式の識別子
- **timestamp**: ISO 8601形式のUTC時刻
- **details**: オプション。バリデーションエラーなど詳細情報が必要な場合のみ含めます

### HTTPステータスコードとの対応

| code | HTTPステータス | 説明 |
|------|---------------|------|
| VALIDATION_ERROR | 400 | リクエストパラメータの検証失敗 |
| UNAUTHORIZED | 401 | 認証失敗 |
| FORBIDDEN | 403 | 権限不足 |
| RESOURCE_NOT_FOUND | 404 | リソースが見つからない |
| CONFLICT | 409 | リソースの競合（重複など） |
| INTERNAL_SERVER_ERROR | 500 | サーバー内部エラー |

## Consequences

### 利点

- クライアント実装の統一化により開発効率が向上
- requestIdによるログ/トレースとの紐付けが容易になり、問題解決時間が短縮
- エラーハンドリングの標準化により、運用チームの負担が軽減
- APIドキュメントの一貫性向上

### 課題と対応

- **既存API対応**: 既存のエラー形式を使用しているエンドポイントについては、段階的に新形式へ移行する必要があります。移行期間中は両形式をサポートします。
- **実装コスト**: すべてのエラーハンドリング箇所で新形式への対応が必要です。
- **ドキュメント更新**: APIドキュメント（`docs/10_api/errors.md`）を更新し、エラーコード一覧と対応方法を明記します。

## Related Documents

- `docs/10_api/errors.md` - エラーコード詳細仕様
- `docs/00_overview/api-boundary.md` - API設計原則