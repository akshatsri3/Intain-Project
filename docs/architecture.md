# System Architecture — Loan Data Verification Copilot

## 1. System Overview

```
 Browser (React 19 + Vite + Tailwind CSS)
                   │
                   │  REST / JSON (JWT Authenticated)
                   ▼
       FastAPI Application (Python)
        ├── Ingestion & Normalization Engine
        ├── 15-Rule Validation & Deduplication Engine
        ├── AI Suggestion & Batch Summary Service
        ├── Reviewer Decision Workflow
        ├── Verification & SHA-256 Hashing Engine
        └── Immutable Audit Trail Logger
                   │
                   │  SQLAlchemy ORM
                   ▼
         PostgreSQL Database
```

---

## 2. Complete End-to-End Pipeline

```
  ┌──────────────────┐
  │ Messy Loan CSV   │ (loan tapes, servicer updates, document manifests)
  └────────┬─────────┘
           │
           ▼
  [1. INGESTION & RAW PRESERVATION]
     ├── Store raw row in `raw_records` (JSONB) — NEVER mutated
     └── Log UPLOADED & IMPORTED audit events
           │
           ▼
  [2. NORMALIZATION ENGINE]
     ├── Currency / text / state sanitation
     ├── Interest rate fraction vs percentage conversion
     ├── Multi-format date parsing
     └── Store typed record in `loans`
           │
           ▼
  [3. VALIDATION & DEDUPLICATION]
     ├── 15 rule checks (bounds, sanity, dates, DPD consistency)
     ├── Cross-dataset duplicate & suspicious loan detection
     ├── If violations: create `validation_exceptions` (OPEN)
     └── If clean (0 exceptions): promote to `VERIFIED` + SHA-256 hash
           │
     ┌─────┴──────────────────────────────┐
     │                                    │
     ▼ (If exceptions flagged)            ▼ (If clean)
  [4. AI REVIEW ASSISTANT]                [5. VERIFIED GOLDEN RECORD]
     ├── Rule-based heuristic copilot        ├── Canonical snapshot
     ├── Confidence rating & explanation     ├── SHA-256 Record Hash
     └── Human Review Decision:              └── Exportable (CSV / JSON)
         • Accept AI Suggestion                  ▲
         • Manual Override Field                 │
         • Reject Loan                           │ (Promoted on approval)
         • Flag for Audit                        │
         └───────────────────────────────────────┘
```

---

## 3. Database Schema

```sql
users
  id (PK), name, email, password_hash, role, created_at

datasets
  id (PK), file_name, source_type, file_size, uploaded_by (FK -> users.id)
  uploaded_at, total_rows, successfully_imported_rows, failed_rows, status

raw_records
  id (PK), dataset_id (FK -> datasets.id), row_number, raw_data_json (JSONB), created_at

loans
  id (PK), dataset_id (FK -> datasets.id), source_row_number
  loan_id, borrower_id, loan_type, origination_date, maturity_date
  original_principal, current_balance, interest_rate, term_months
  borrower_state, loan_purpose, credit_grade, employment_length, income_band
  payment_status, days_past_due, servicer_name, last_payment_date, last_updated_at
  document_status, source_system, normalization_status
  verification_status [PENDING | VERIFIED | REJECTED]
  verified_by (FK -> users.id), verified_at, record_hash (SHA-256)
  created_at, updated_at

import_errors
  id (PK), dataset_id (FK -> datasets.id), row_number
  error_type, error_message, raw_data_json (JSONB), created_at

validation_exceptions
  id (PK), loan_id (FK -> loans.id), dataset_id (FK -> datasets.id)
  rule_code, severity [ERROR | WARNING | INFO], field_name
  current_value, expected_range, message
  status [OPEN | RESOLVED | DISMISSED]
  resolved_by (FK -> users.id), resolved_at, resolution_note, created_at

review_decisions
  id (PK), exception_id (FK -> validation_exceptions.id), reviewer_id (FK -> users.id)
  decision [ACCEPT_SUGGESTION | MANUAL_OVERRIDE | REJECT_LOAN | FLAG_FOR_AUDIT]
  override_value, reviewer_note, ai_suggestion_json (JSONB), decided_at

audit_events
  id (PK), entity_type [loan | dataset | exception], entity_id
  event_type, actor_id (FK -> users.id), actor_role, details_json (JSONB), created_at
```

---

## 4. Cryptographic Traceability & Lineage

1. **Source Lineage**:
   Every record in `loans` maps back to `dataset_id` + `source_row_number` $\to$ `raw_records.row_number` in `raw_records` table.
2. **Immutable Record Hash**:
   When a loan is verified, a canonical JSON representation of all verified fields is hashed using SHA-256. Any post-verification alteration invalidates the hash.
3. **Audit Trail**:
   Every action creates an immutable row in `audit_events` linking `actor_id`, `event_type`, and timestamped payload.

---

## 5. AI Controls & Safety Philosophy

- **Human-in-the-loop**: AI suggestions are presented advisory-only; they never silently alter loan records without reviewer confirmation.
- **Explainability**: Every suggestion provides an explanation of the underlying cause, the suggested fix, and a confidence rating (`HIGH`, `MEDIUM`, `LOW`).
- **Audit Logging**: The exact AI suggestion displayed to the reviewer is persisted with the review decision and in the audit trail.
