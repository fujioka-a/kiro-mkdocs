---
title: API Server Spec (PoC)
owner: platform-team
status: approved
last_reviewed: 2026-02-23
---

# API Server Spec (PoC)

このサイトは、APIサーバーの仕様を Docs-as-Code で管理するPoCです。

## 運用ルール

* `status=approved` のページのみを正式仕様として扱います。
* approvedページはfrontmatterの必須項目が欠けているとビルドが失敗します。
* draftページはHooksが不足メタを補完します。