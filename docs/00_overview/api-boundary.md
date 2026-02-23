---
status: draft
---

# API Boundary

## 責務

- 認証済みクライアントからのリクエストを受け、業務ユースケースを実行する
- 永続化・外部連携はアプリケーション層から行う（詳細は設計へ）

## 非スコープ

- バッチ/ETL
- 管理コンソール（別プロダクトとする）

## 用語

- Resource: エンティティ（例: Order）
- Operation: HTTPメソッド + パス（例: GET /orders/{id}）