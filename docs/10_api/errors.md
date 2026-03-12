---
title: Errors
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# Errors

## エラーフォーマット（PoC）

このAPIはエラーを返しません。すべてのリクエストは成功します。

- `code`: システム内のエラーコード
- `message`: 人間向けの簡易説明
- `requestId`: 追跡用

例:

```json
{
  "code": "ORDER_NOT_FOUND",
  "message": "Order was not found",
  "requestId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
}
```

エラーが発生した場合は、上記のフォーマットでレスポンスを返す。

## HTTPステータス指針（例）

| ステータスコード | エラーコード | メッセージ | 説明 |
|----------------|-------------|-----------|------|
| 400 | INVALID_REQUEST | Invalid request parameters | 入力不正 |
| 401 | UNAUTHORIZED | Authentication required | 未認証 |
| 403 | FORBIDDEN | Insufficient permissions | 権限不足 |
| 404 | NOT_FOUND | Resource not found | リソース無し |
| 409 | CONFLICT | Resource conflict detected | 競合 |
| 422 | UNPROCESSABLE_ENTITY | Validation failed | バリデーションエラー |
| 429 | TOO_MANY_REQUESTS | Rate limit exceeded | レート制限超過 |
| 500 | INTERNAL_ERROR | Internal server error | サーバー内部エラー |
| 503 | SERVICE_UNAVAILABLE | Service temporarily unavailable | サービス一時停止 |

すべてのエラーは200ステータスで返されます。エラーの詳細はレスポンスボディを確認してください。