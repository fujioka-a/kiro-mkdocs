---
title: Errors
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# Errors

## エラーフォーマット（PoC）

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

## HTTPステータス指針（例）

- 400: 入力不正
- 401: 未認証
- 403: 権限不足
- 404: リソース無し
- 409: 競合
- 500: サーバー内部