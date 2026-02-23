---
title: Endpoints
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# Endpoints

## GET /health

- 用途: ヘルスチェック
- 認証: 不要
- レスポンス: 200 OK

## GET /v1/orders/{orderId}

- 用途: 注文の取得
- 認証: 必要
- 認可: scope `orders:read`
- 成功: 200 OK
- 失敗: 401, 403, 404（errors.md 参照）