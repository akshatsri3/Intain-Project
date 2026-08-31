# API Documentation — Loan Data Verification Copilot

Base URL: `http://localhost:8000`

Authentication: `Authorization: Bearer <token>` (except `/health` and `/auth/login`)

---

## 1. Health

### `GET /health`
Check API service health.

**Response `200 OK`:**
```json
{
  "status": "healthy",
  "service": "Loan Data Verification Copilot API"
}
```

---

## 2. Authentication

### `POST /auth/login`
Authenticate with email/password and obtain a JWT access token.

**Request:**
```json
{
  "email": "operator@test.com",
  "password": "password123"
}
```

**Response `200 OK`:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsIn...",
  "token_type": "bearer"
}
```

### `GET /auth/me`
Retrieve the current authenticated user identity and role.

**Response `200 OK`:**
```json
{
  "id": 1,
  "name": "Akshat Operator",
  "email": "operator@test.com",
  "role": "DATA_OPERATOR"
}
```

---

## 3. Datasets (Ingestion)

### `POST /datasets/upload`
Upload and process a loan CSV file. Stores raw records in JSONB, normalizes data, and automatically triggers validation. Requires `DATA_OPERATOR` role.

**Content-Type:** `multipart/form-data`
* `file`: CSV file (required)
* `source_type`: `LOAN_TAPE | SERVICER_UPDATE | DOCUMENT_MANIFEST | OTHER` (default: `OTHER`)

**Response `200 OK`:**
```json
{
  "dataset": {
    "id": 1,
    "file_name": "loan_tape_sample.csv",
    "source_type": "LOAN_TAPE",
    "file_size": 4089,
    "uploaded_by": 1,
    "uploaded_at": "2026-08-30T12:00:00Z",
    "total_rows": 25,
    "successfully_imported_rows": 24,
    "failed_rows": 1,
    "status": "COMPLETED"
  },
  "normalization_summary": {
    "dates_normalized": 48,
    "currency_values_normalized": 46,
    "interest_rates_normalized": 24,
    "missing_values_converted_to_null": 8
  }
}
```

### `GET /datasets`
List all datasets uploaded by the current user.

### `GET /datasets/{dataset_id}`
Retrieve dataset metadata.

### `GET /datasets/{dataset_id}/records`
Retrieve normalized loan records for a dataset.
* Query params: `limit` (default: 50), `offset` (default: 0).

### `GET /datasets/{dataset_id}/errors`
Retrieve failed import rows with raw JSON and parsing failure reasons.

---

## 4. Validation Engine

### `POST /validation/run/{dataset_id}`
Manually trigger or re-run the 15-rule validation engine and cross-dataset duplicate detection. Auto-verifies clean loans. Requires `DATA_OPERATOR`.

**Response `200 OK`:**
```json
{
  "dataset_id": 1,
  "exceptions_created": 5,
  "loans_auto_verified": 19,
  "message": "Validation complete. 5 exceptions found, 19 loans auto-verified."
}
```

### `GET /validation/exceptions`
List validation exceptions with AI suggestions and loan context.
* Query params:
  * `status`: `OPEN | RESOLVED | DISMISSED`
  * `severity`: `ERROR | WARNING | INFO`
  * `rule_code`: Filter by specific rule (e.g. `BALANCE_EXCEEDS_PRINCIPAL`)
  * `search`: Filter by `loan_id` or `borrower_id`
  * `dataset_id`: Filter by dataset
  * `limit`, `offset`

**Response `200 OK`:**
```json
[
  {
    "id": 1,
    "loan_id": 3,
    "dataset_id": 1,
    "rule_code": "BALANCE_EXCEEDS_PRINCIPAL",
    "severity": "WARNING",
    "field_name": "current_balance",
    "current_value": "510000.00",
    "expected_range": "<= 500000.00",
    "message": "Current balance (510000.00) exceeds original principal (500000.00) by 2.0%.",
    "status": "OPEN",
    "resolved_by": null,
    "resolved_at": null,
    "resolution_note": null,
    "created_at": "2026-08-30T12:00:05Z",
    "loan_loan_id": "LN-1015",
    "loan_borrower_id": "BR-015",
    "ai_suggestion": {
      "suggested_action": "Cap current_balance at original_principal value (<= 500000.00)",
      "explanation": "The current balance exceeds original principal. Likely a data entry error...",
      "confidence": "HIGH",
      "model": "rule-engine-v1",
      "generated_at": "2026-08-30T12:00:05Z"
    }
  }
]
```

### `GET /validation/stats`
Get exception counts by status and severity.

**Response `200 OK`:**
```json
{
  "total": 5,
  "open": 5,
  "resolved": 0,
  "dismissed": 0,
  "errors": 2,
  "warnings": 3,
  "info": 0
}
```

### `GET /validation/batch-summary`
AI-generated summary and recommendations across portfolio exceptions.

---

## 5. Reviewer Decisions

### `POST /reviews/decide/{exception_id}`
Submit a human review decision on an exception. If all exceptions for a loan are resolved, the loan is automatically promoted to `VERIFIED`. Requires `REVIEWER`.

**Request:**
```json
{
  "decision": "ACCEPT_SUGGESTION",
  "override_value": null,
  "reviewer_note": "Capped balance to original principal per servicer note.",
  "ai_suggestion_json": { ... }
}
```
* Decisions: `ACCEPT_SUGGESTION | MANUAL_OVERRIDE | REJECT_LOAN | FLAG_FOR_AUDIT`

### `GET /reviews/decisions`
List reviewer's past decision history.

---

## 6. Verified Loans & Export

### `GET /verified/loans`
List all verified golden loan records.
* Query params: `search`, `loan_type`, `borrower_state`, `limit`, `offset`.

### `GET /verified/stats`
Get portfolio data quality score and verification status counts.

**Response `200 OK`:**
```json
{
  "total_loans": 24,
  "verified": 20,
  "pending": 3,
  "rejected": 1,
  "quality_score": 83.3
}
```

### `GET /verified/export`
Export all verified records with SHA-256 hashes.
* Query params: `format=csv` (default) or `format=json`.

---

## 7. Audit Trail

### `GET /audit/loan/{loan_id}`
Retrieve the full chronological audit history for a loan (Upload $\to$ Normalization $\to$ Validation $\to$ AI Suggestion $\to$ Decision $\to$ Verified $\to$ Export).

### `GET /audit/trail/{entity_type}/{entity_id}`
Retrieve audit events for `loan`, `dataset`, or `exception`.

### `GET /audit/recent`
Retrieve recent global audit events. Filterable by `entity_type` or `event_type`.

---

## 8. Loans API

### `GET /loans`
List all loans with optional `search` and `verification_status` filters.

### `GET /loans/{id}`
Get details of a single loan record.

### `GET /loans/summary/global`
System-wide metrics across datasets, loans, verified counts, open exceptions, and quality score.
