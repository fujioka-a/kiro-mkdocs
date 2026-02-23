---
title: Auth
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# Auth

## 前提

- Bearer Token を Authorization ヘッダで受け取る

## 認可

- 権限は `scope`（または `role`）で表現する
- エンドポイントごとに要求権限を定義する（詳細は endpoints.md）