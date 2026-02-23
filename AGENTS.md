# AGENTS.md
AI Agent Operating Specification

Project: Kiro × MkDocs Docs-as-Code Validation System

Chat conversations with AI agents must is mainly Japanese, but may include English technical terms.

---

## 0. Purpose
This document defines strict behavioral rules for AI agents working in this repository.

Goal:
Ensure agents make safe, deterministic, non-destructive changes while preserving
documentation integrity guarantees.

This file is authoritative.
If any instruction elsewhere conflicts with this file, this file wins.

---

## 1. Core Principle (Non‑Negotiable)

The validation system is the single source of truth.

Agent MUST treat:

    tools/validate_docs.py

as the only location where validation logic may exist.

Agent MUST NOT duplicate validation logic anywhere else.

---

## 2. Responsibility Boundaries

Layer responsibilities:

Kiro:
    Generates and edits documents

Validator:
    Decides validity

MkDocs:
    Displays only

CI:
    Final enforcement

Agent MUST preserve this architecture.

Agent MUST reject any task that violates these boundaries.

---

## 3. Allowed Changes

Agent MAY:

- Add new Markdown docs
- Edit docs content
- Improve wording
- Add new validation rules inside validate_docs.py
- Add tests
- Refactor code WITHOUT changing behavior
- Improve performance

---

## 4. Forbidden Changes

Agent MUST NOT:

- Move validation logic outside validate_docs.py
- Add validation inside hooks
- Add validation inside MkDocs config
- Auto-update last_reviewed
- Remove required metadata
- Disable validation
- Change STRICT mode default
- Modify directory structure without instruction

If asked to do any of the above:

Agent must refuse.

---

## 5. Metadata Rules

Approved documents MUST contain:

title
owner
status
last_reviewed

Constraints:

status must equal "approved"
owner must be real team or person
last_reviewed must be <= 90 days

Agent must enforce these rules.

---

## 6. Editing Rules

When modifying a document:

Agent MUST:

1. Preserve existing metadata
2. Not reorder metadata fields
3. Not delete metadata keys
4. Not change status unless instructed

---

## 7. last_reviewed Rule (Critical)

last_reviewed means:

    Last human verification date

It does NOT mean:

    Last edit date

Agent MUST NEVER auto-update last_reviewed.

Only humans may change it.

---

## 8. Failure Handling

If validation fails:

Agent MUST:

- stop immediately
- explain why
- propose fix

Agent MUST NOT:

- silently fix metadata
- bypass validation
- downgrade rule severity

---

## 9. STRICT Mode Policy

Default mode = STRICT

Meaning:

Validation failure must stop execution.

Agent MUST NOT change this default.

Optional warning mode may exist,
but must never be default.

---

## 10. Determinism Requirement

Agent outputs must be:

- reproducible
- deterministic
- idempotent

Running the same instruction twice must produce identical results.

---

## 11. Safety Rules

Agent must assume:

Docs = production artifact

Therefore:

Invalid docs = production defect

Agent must treat validation errors as critical failures.

---

## 12. When Unsure

If the agent is uncertain about any instruction:

Agent MUST:

1. Stop
2. Ask clarification
3. Not guess

---

## 13. Logging Requirement

When making changes, agent should describe:

- what changed
- why it changed
- what rule allowed it

---

## 14. Expansion Rule

When adding new features:

Agent MUST extend existing systems,
NOT create parallel systems.

Bad:
    new_validator.py

Good:
    extend validate_docs.py

---

## 15. Design Philosophy

This repository enforces:

    Quality through enforcement, not convention.

Agent must preserve this philosophy.

---

## 16. Summary Directive

If a requested action would:

- weaken validation
- bypass validation
- fragment validation
- hide validation failures

Agent MUST refuse.

---

END OF SPEC
