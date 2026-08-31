# AI Development Log

## Project
**Loan Data Verification Copilot**  
*Intain Campus FinTech Challenge 2026 — Full Stack Track*

---

## 1. AI / Agentic Tools Used

| Tool | Used | Role & Notes |
|---|---|---|
| **Antigravity (Google DeepMind)** | ✅ Yes | Primary agentic AI coding environment for full-stack build, architecture, and testing |
| **Claude / Gemini models** | ✅ Yes | Reasoning, schema synthesis, validation rule heuristics, and code generation |
| **ChatGPT / Copilot** | ❌ No | Not used |

---

## 2. Development Use Cases

| Category | AI Involvement | Description |
|---|---|---|
| **Architecture Design** | ✅ Full | Multi-stage pipeline: Ingestion $\to$ Normalization $\to$ Validation $\to$ AI Review $\to$ Verification $\to$ Audit Trail |
| **Database Schema** | ✅ Full | Designed all 8 SQLAlchemy models (`User`, `Dataset`, `RawRecord`, `Loan`, `ImportError`, `ValidationException`, `ReviewDecision`, `AuditEvent`) |
| **API Design** | ✅ Full | RESTful endpoints with role-based security dependencies and Pydantic schemas |
| **Validation Engine** | ✅ Full | 15 business rules, cross-dataset deduplication, sanity checks, and clean loan auto-promotion |
| **AI Copilot Assistant** | ✅ Full | Rule-based heuristic copilot generating contextual fix explanations, confidence scores, and batch summaries without external API keys |
| **Cryptographic Lineage** | ✅ Full | SHA-256 canonical verified record hashing and raw-to-verified source tracing |
| **Frontend UI / UX** | ✅ Full | React 19 + Vite + Tailwind CSS dashboards for Data Operator, Reviewer, and Consumer |
| **Automated Testing** | ✅ Full | Pytest suite covering auth, normalization, validation, reviewer decisions, verified records, and audit logging |
| **Documentation** | ✅ Full | README, architecture.md, API.md, and AI Development Log |

---

## 3. Representative Prompts

### Prompt 1: System Architecture & Ingestion Scaffolding
- **Goal**: Scaffold core architecture with raw vs. normalized data separation and JWT authentication.
- **Prompt**:
  > *"Build the Loan Data Verification Copilot. Ingest messy CSV loan files, preserve raw records in JSONB before transformation, normalize currency, interest rates, dates, text, and column names into a clean internal schema, and provide JWT auth with roles: DATA_OPERATOR, REVIEWER, DATA_CONSUMER."*
- **Result**: Core FastAPI scaffolding, SQLAlchemy models, pandas ingestion pipeline with error tracking, and login/operator UI.
- **Human Review**: Verified raw vs. normalized record separation in the database. Confirmed bcrypt hashing and role-based guards.

### Prompt 2: 15-Rule Validation Engine & Duplicate Detection
- **Goal**: Implement business rule validation and cross-dataset duplicate detection.
- **Prompt**:
  > *"Implement the validation engine with 15 financial business rules: missing loan_id/principal/doc_status, negative balance/term, current_balance > original_principal, interest rate out of range (0-50%), maturity before origination, payment status vs DPD mismatch, excessive DPD (>360), invalid US state codes, stale records (>1 year), and closed loans with positive balance. Also detect duplicate loan IDs across datasets and suspicious repeated borrower combinations. Auto-verify clean records."*
- **Result**: `validation_service.py`, `ValidationException` model, and automatic execution post-ingestion.
- **Human Review**: Confirmed severity classifications (`ERROR` vs `WARNING`) and ensured duplicate detection handles cross-dataset comparisons correctly without duplicating database sessions.

### Prompt 3: AI Review Assistant & Reviewer Decision Workflow
- **Goal**: Implement interactive exception queue with AI recommendations and decision actions.
- **Prompt**:
  > *"Create an AI review assistant and reviewer workflow. Generate intelligent fix suggestions with confidence ratings (HIGH/MEDIUM/LOW) and explanatory rationale for each exception type. Build an Exception Queue in React allowing Reviewers to accept AI suggestions, manually override fields, reject loans, or flag for audit. Log all decisions and AI suggestion payloads to the audit trail."*
- **Result**: `ai_suggestion_service.py`, `reviews.py`, and `ExceptionQueue.jsx` with search, filter, and modal decision dialogues.
- **Human Review**: Enforced human-in-the-loop requirement: AI suggestions never silently modify data; every change requires human review action.

### Prompt 4: Cryptographic Record Hashing, Verified Records & Export
- **Goal**: Implement golden record creation, quality scoring, SHA-256 record hashing, and CSV/JSON export.
- **Prompt**:
  > *"Build Verified Records and Data Consumer Dashboard. Compute SHA-256 hashes of canonical verified loan records. Calculate portfolio data quality scores. Provide CSV and JSON streaming exports of verified records. Create an immutable Audit Trail tracking the complete lifecycle of every entity."*
- **Result**: `verified.py`, `audit.py`, `VerifiedLoans.jsx`, `AuditTrail.jsx`, and `ConsumerDashboard.jsx`.
- **Human Review**: Validated that `record_hash` uses deterministic sorted JSON serialization so hashes remain reproducible across platforms.

### Prompt 5: Automated Testing Suite
- **Goal**: Comprehensive test coverage across all pipeline components using in-memory SQLite.
- **Prompt**:
  > *"Write pytest suites for validation rules, reviewer decision workflows, verified loan queries, quality score calculations, CSV/JSON exports, and audit trail retrieval. Ensure tests run without a live PostgreSQL instance."*
- **Result**: `test_auth.py`, `test_upload.py`, `test_normalization.py`, `test_validation.py`, `test_reviews.py`, `test_verified.py`, and `test_audit.py`.
- **Human Review**: Confirmed dependency overrides and SQLite rollback fixtures properly isolate test state.

---

## 4. Human Review & Verification Process

Throughout development, human engineering oversight focused on:
1. **Financial Domain Heuristics**:
   - Interest rate parsing: Distinguishing decimal fractions (e.g. `0.085` $\to$ `8.5%`) from whole percentages (`8.5%` $\to$ `8.5`).
   - Payment status consistency: Reconciling ambiguous status strings (e.g., "30-59 Days Past Due") with numeric `days_past_due`.
2. **Auditability & Integrity**:
   - Ensuring `raw_records` remain immutable read-only records.
   - Enforcing SHA-256 hash generation upon verification.
   - Validating that AI recommendations and reviewer comments are permanently logged in `audit_events`.
3. **Security & Role Boundaries**:
   - Verifying that only `DATA_OPERATOR` can upload datasets.
   - Verifying that only `REVIEWER` can submit exception decisions.
   - Verifying that `DATA_CONSUMER` can browse verified golden records and export.

---

## 5. Rejected AI Output & Corrections

### Example 1: Silent Auto-Correction in Normalization
- **AI Suggestion**: The AI initially generated normalization logic that automatically capped `current_balance` to `original_principal` during initial CSV parsing.
- **Why Rejected**: Normalization must only standardize data formats, not alter business values or make underwriting assumptions. Capping the balance silently would destroy the evidence of a source data anomaly.
- **Human Correction**: Preserved the original balance during normalization and created the `BALANCE_EXCEEDS_PRINCIPAL` rule in validation so the anomaly is visibly flagged in the Exception Queue for reviewer judgment.

### Example 2: External LLM Dependency for Core Features
- **AI Suggestion**: The AI suggested integrating the OpenAI API (`gpt-4o`) for generating fix suggestions.
- **Why Rejected**: Relying on external API keys introduces network latency, rate limits, non-deterministic outputs, and failure modes during hackathon judging if an API key expires or is unavailable.
- **Human Correction**: Replaced external API calls with an internal, deterministic rule-based heuristic copilot (`ai_suggestion_service.py`) that reliably delivers instant, contextual explanations and recommendations without external credentials.

### Example 3: Non-Deterministic Record Hashing
- **AI Suggestion**: The AI initially proposed hashing the loan model dictionary directly using Python's `hash()` function.
- **Why Rejected**: Python's `hash()` uses randomized per-process salt, meaning hashes change across server restarts. Additionally, raw dictionaries with non-sorted keys produce unstable hashes.
- **Human Correction**: Implemented `compute_record_hash()` using standard `hashlib.sha256()` over a strictly ordered, canonical JSON string representation of verified fields.

---

## 6. AI-Assisted Code Contribution Breakdown

| Layer | AI Contribution | Human Engineering & Review |
|---|---|---|
| Backend Models & Schemas | 90% | 10% (schema validation, foreign keys, enums) |
| Ingestion & Normalization Logic | 85% | 15% (edge case heuristics, currency parentheses) |
| Validation & Deduplication Engine | 85% | 15% (financial rule calibration, duplicate logic) |
| AI Review & Decision Workflow | 90% | 10% (audit logging & state transition guards) |
| Verified Records & Hashing | 90% | 10% (canonical JSON serialization, hashing format) |
| Frontend React Components & UX | 90% | 10% (responsive layouts, dark mode styling, modals) |
| Test Suites & Documentation | 90% | 10% (test scenarios, edge cases, verification) |
| **Overall Project Estimate** | **~88%** | **~12%** |

---

## 7. Lessons Learned

- **Agentic Coding Power**: AI agents excel at generating consistent boilerplate, boilerplate-heavy CRUD routes, complex React UI components, and exhaustive test suites in minutes.
- **Critical Need for Domain Review**: In financial applications, the boundary between *format normalization* (syntactic) and *data validation / exception review* (semantic) requires strict human judgment.
- **Deterministic AI in Production**: For compliance and regulatory auditing, pairing deterministic heuristic AI with human sign-off provides explainable, reproducible, and safe automation.
