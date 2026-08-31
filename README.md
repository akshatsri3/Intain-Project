# Loan Data Verification Copilot

> **Intain Campus FinTech Challenge 2026 — Full Stack Track**

An AI-assisted full-stack console that turns messy loan records into validated, traceable, trusted golden data.

---

## 🌟 Core Modules & Capabilities

### 📥 Ingestion & Normalization
- **JWT Authentication & RBAC**: Roles for `DATA_OPERATOR`, `REVIEWER`, and `DATA_CONSUMER` with protected routes and backend authorization dependencies.
- **Raw Record Preservation**: Original CSV rows stored verbatim in JSONB before any transformations for legal and regulatory auditability.
- **Robust Normalization Pipeline**: Currency stripping, interest rate conversion (percentages vs. decimals), flexible multi-format date parsing, state code standardization, text sanitation, and error tracking.
- **Source Lineage**: Every normalized record maintains an immutable link back to `dataset_id` + `source_row_number` + file name.

### ⚙️ Validation Engine & Duplicate Detection
- **15 Rule Validation Engine**:
  - Missing field checks (`loan_id`, `original_principal`, `document_status`).
  - Boundary & sanity checks (negative balances/terms, `current_balance > original_principal`, out-of-range rates, maturity before origination).
  - Business consistency checks (payment status vs. days past due mismatch, excessive DPD > 360, stale records > 1 yr, closed loans with remaining balance).
- **Cross-Dataset Duplicate Detection**: Flag duplicate `loan_id` across uploads or suspicious duplicate borrower + principal + origination date combinations.
- **Auto-Verification of Clean Loans**: Loans with zero validation exceptions are automatically verified upon ingestion.

### 🤖 AI Review Assistant & Reviewer Workflow
- **Rule-Based AI Copilot Engine**: Generates context-aware resolution recommendations with confidence ratings (`HIGH`, `MEDIUM`, `LOW`) and transparent reasoning (no external API keys required).
- **Interactive Exception Queue UI**: Filter by severity (`ERROR`, `WARNING`, `INFO`), status (`OPEN`, `RESOLVED`, `DISMISSED`), or search by loan ID / borrower ID.
- **Reviewer Decision Actions**: Accept AI suggestion, manual field override, reject loan, or flag for audit.
- **Batch AI Summary**: Aggregate summary of portfolio exceptions with top actionable recommendations.

### 🛡️ Verified Golden Records, Audit Trail & Export
- **Golden Verified Records**: Verified records stamped with reviewer ID, timestamp, and **SHA-256 canonical record hash**.
- **Portfolio Data Quality Score**: Real-time percentage score of verified vs. total portfolio loans.
- **Full Immutable Audit Trail**: Detailed audit event history capturing every action (upload, normalization, validation, AI suggestion generation, review decision, field edit, export).
- **Data Export**: One-click download of verified loan portfolios in standard **CSV** or **JSON** formats.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | React 19 + Vite + Tailwind CSS + Lucide Icons + React Router |
| **Backend** | Python + FastAPI + SQLAlchemy ORM |
| **Database** | PostgreSQL (Production / Docker), SQLite (In-Memory Testing) |
| **Security** | JWT + bcrypt (python-jose + passlib) |
| **Data Processing** | Pandas + SHA-256 Hashing |

---

## 🚀 Quick Start

### 1. Start PostgreSQL via Docker

```bash
docker compose up -d
```

### 2. Set Up and Run the Backend

```bash
cd backend

# Create .env from template
cp .env.example .env

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed test users
python -m app.seed

# Start the API server
uvicorn app.main:app --reload
```

* API available at: **http://localhost:8000**
* Interactive Swagger Docs: **http://localhost:8000/docs**

### 3. Set Up and Run the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

* Frontend available at: **http://localhost:5173**

---

## 👥 Test Credentials

| Role | Email | Password | Allowed Capabilities |
|---|---|---|---|
| **Data Operator** | `operator@test.com` | `password123` | CSV upload, dataset history, loan records, view audit trail |
| **Reviewer** | `reviewer@test.com` | `password123` | Exception queue, AI suggestions, accept/override/reject decisions |
| **Data Consumer** | `consumer@test.com` | `password123` | Portfolio quality score, verified loans browser, CSV/JSON export |

---

## 🧪 Running Automated Tests

```bash
cd backend
pytest tests/ -v
```

All backend test suites run against an in-memory SQLite database without requiring a live PostgreSQL instance.

---

## 📡 API Overview

| Method | Endpoint | Description | Access |
|---|---|---|---|
| `POST` | `/auth/login` | Login, returns JWT token | Public |
| `GET` | `/auth/me` | Current user profile | Authenticated |
| `POST` | `/datasets/upload` | Ingest CSV, normalize, and auto-validate | Operator |
| `GET` | `/datasets` | List uploaded datasets | Operator |
| `GET` | `/datasets/{id}` | Dataset metadata & import stats | Operator |
| `GET` | `/datasets/{id}/records` | Normalized loan records | Operator |
| `GET` | `/datasets/{id}/errors` | Failed import rows (raw JSON) | Operator |
| `POST` | `/validation/run/{id}` | Manually trigger validation on dataset | Operator |
| `GET` | `/validation/exceptions` | List/search exceptions with AI suggestions | All |
| `GET` | `/validation/stats` | Exception counts by severity and status | All |
| `GET` | `/validation/batch-summary` | AI-generated batch summary & recommendations | All |
| `POST` | `/reviews/decide/{id}` | Submit review decision (accept/override/reject) | Reviewer |
| `GET` | `/reviews/decisions` | Reviewer decision history | Reviewer |
| `GET` | `/verified/loans` | List & filter verified golden records | All |
| `GET` | `/verified/stats` | Portfolio data quality score & metrics | All |
| `GET` | `/verified/export` | Export verified records as CSV or JSON | All |
| `GET` | `/audit/trail/{type}/{id}` | Full audit trail for an entity | All |
| `GET` | `/audit/loan/{loan_id}` | Complete lifecycle audit trail for a loan | All |
| `GET` | `/audit/recent` | Recent global audit events | All |
| `GET` | `/loans` | List all loan records with status filters | All |
| `GET` | `/loans/{id}` | Single loan record detail | All |
| `GET` | `/loans/summary/global` | Global system summary | All |

See [`docs/API.md`](docs/API.md) for full API request/response specifications.

---

## 🎬 5-Minute Demo Walkthrough Flow

1. **Data Operator Flow**:
   - Log in as `operator@test.com`.
   - Upload `sample_data/loan_tape_sample.csv` (contains raw, messy records).
   - View Ingestion Summary and Normalization statistics.
   - Inspect Normalized Records and Lineage details.
2. **Reviewer Flow**:
   - Log in as `reviewer@test.com`.
   - Open **Exception Queue** to see flagged anomalies (e.g. balance exceeding principal, rate anomaly, missing doc status).
   - View **AI Recommendation Panel** with explanation and confidence score.
   - Click **AI Batch Summary** for a macro view of portfolio health.
   - Submit review decisions (e.g. Accept Suggestion, Override Value, Reject Loan).
3. **Data Consumer Flow**:
   - Log in as `consumer@test.com`.
   - View **Portfolio Quality Score** & verification breakdown.
   - Inspect **Verified Loan Records** with their immutable **SHA-256 Record Hashes**.
   - Open a loan's **Audit Trail** to see the full timeline (Upload $\to$ Import $\to$ Validation $\to$ AI Suggestion $\to$ Reviewer Approval $\to$ Verified Record Created).
   - Download the verified dataset via **Export CSV** or **Export JSON**.
