---
title: ADR-0001 Error Format
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# ADR-0001 Error Format

## Context

APIのエラー形式がバラバラだと、クライアント実装と運用が破綻する。

## Decision

エラーは `code/message/requestId` を持つ統一JSONとする。

## Consequences

- ログ/トレースとの紐付けが容易になる。
- 既存APIがある場合は移行が必要。