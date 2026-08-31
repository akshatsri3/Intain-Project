import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Optional, Any

COLUMN_NAME_MAP: dict[str, str] = {
    # Loan identifiers
    "loan id": "loan_id",
    "loan_id": "loan_id",
    "loanid": "loan_id",
    "loan number": "loan_id",
    "loan_number": "loan_id",

    # Borrower
    "borrower id": "borrower_id",
    "borrower_id": "borrower_id",
    "borrowerid": "borrower_id",
    "borrower": "borrower_id",

    # Loan type
    "loan type": "loan_type",
    "loan_type": "loan_type",
    "loantype": "loan_type",
    "type": "loan_type",

    # Dates
    "origination date": "origination_date",
    "origination_date": "origination_date",
    "originationdate": "origination_date",
    "orig date": "origination_date",
    "orig_date": "origination_date",
    "issue date": "origination_date",
    "issue_date": "origination_date",

    "maturity date": "maturity_date",
    "maturity_date": "maturity_date",
    "maturitydate": "maturity_date",
    "due date": "maturity_date",
    "due_date": "maturity_date",

    "last payment date": "last_payment_date",
    "last_payment_date": "last_payment_date",
    "lastpaymentdate": "last_payment_date",
    "last payment": "last_payment_date",
    "last_payment": "last_payment_date",

    "last updated": "last_updated_at",
    "last_updated": "last_updated_at",
    "last_updated_at": "last_updated_at",
    "lastupdated": "last_updated_at",

    # Monetary
    "original principal": "original_principal",
    "original_principal": "original_principal",
    "original principal balance": "original_principal",
    "original_principal_balance": "original_principal",
    "orig principal": "original_principal",
    "orig_principal": "original_principal",
    "loan amount": "original_principal",
    "loan_amount": "original_principal",
    "principal": "original_principal",

    "current balance": "current_balance",
    "current_balance": "current_balance",
    "currentbalance": "current_balance",
    "balance": "current_balance",
    "outstanding balance": "current_balance",
    "outstanding_balance": "current_balance",

    # Interest rate
    "interest rate": "interest_rate",
    "interest_rate": "interest_rate",
    "interestrate": "interest_rate",
    "rate": "interest_rate",
    "coupon": "interest_rate",
    "coupon rate": "interest_rate",
    "coupon_rate": "interest_rate",

    # Term
    "term months": "term_months",
    "term_months": "term_months",
    "term": "term_months",
    "loan term": "term_months",
    "loan_term": "term_months",

    # Borrower details
    "borrower state": "borrower_state",
    "borrower_state": "borrower_state",
    "state": "borrower_state",

    "loan purpose": "loan_purpose",
    "loan_purpose": "loan_purpose",
    "purpose": "loan_purpose",

    "credit grade": "credit_grade",
    "credit_grade": "credit_grade",
    "grade": "credit_grade",
    "rating": "credit_grade",

    "employment length": "employment_length",
    "employment_length": "employment_length",
    "emp length": "employment_length",
    "emp_length": "employment_length",

    "income band": "income_band",
    "income_band": "income_band",
    "income": "income_band",

    # Payment / servicing
    "payment status": "payment_status",
    "payment_status": "payment_status",
    "status": "payment_status",
    "loan status": "payment_status",
    "loan_status": "payment_status",

    "days past due": "days_past_due",
    "days_past_due": "days_past_due",
    "dpd": "days_past_due",
    "days delinquent": "days_past_due",

    "servicer name": "servicer_name",
    "servicer_name": "servicer_name",
    "servicer": "servicer_name",

    # Document
    "document status": "document_status",
    "document_status": "document_status",
    "doc status": "document_status",
    "doc_status": "document_status",

    # Source
    "source system": "source_system",
    "source_system": "source_system",
    "source": "source_system",
}


def normalize_column_name(raw_name: str) -> Optional[str]:
    """Map a raw CSV column name to the internal field name, or None if unknown."""
def normalize_column_name(raw_name: str) -> Optional[str]:
    return COLUMN_NAME_MAP.get(raw_name.strip().lower())


def normalize_text(value: Any) -> Optional[str]:
    if value is None:
        return None
    s = str(value).strip()
    if s in ("", "nan", "NaN", "N/A", "n/a", "NA", "na", "NULL", "null", "None", "none"):
        return None
    return s


def normalize_currency(value: Any) -> Optional[Decimal]:
    text = normalize_text(value)
    if text is None:
        return None
    cleaned = re.sub(r"\binr\b|rs\.?|[₹$€£,\s]", "", text, flags=re.IGNORECASE)
    if cleaned.startswith("(") and cleaned.endswith(")"):
        cleaned = "-" + cleaned[1:-1]
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def normalize_interest_rate(value: Any) -> Optional[Decimal]:
    text = normalize_text(value)
    if text is None:
        return None

    try:
        if text.endswith("%"):
            return Decimal(text[:-1].strip())
        val = Decimal(text)
        if Decimal("0") < val <= Decimal("1"):
            return (val * Decimal("100")).quantize(Decimal("0.0001"))
        return val
    except InvalidOperation:
        return None


DATE_FORMATS = [
    "%Y-%m-%d",
    "%m/%d/%Y",
    "%d/%m/%Y",
    "%m-%d-%Y",
    "%d-%m-%Y",
    "%d-%b-%Y",
    "%b %d %Y",
    "%B %d, %Y",
    "%d %b %Y",
    "%Y/%m/%d",
    "%m/%d/%y",
    "%d-%b-%y",
]


def normalize_date(value: Any) -> Optional[date]:
    text = normalize_text(value)
    if text is None:
        return None

    from datetime import datetime as dt
    for fmt in DATE_FORMATS:
        try:
            return dt.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def normalize_integer(value: Any) -> Optional[int]:
    text = normalize_text(value)
    if text is None:
        return None
    cleaned = re.sub(r"[,$\s]", "", text)
    try:
        return int(float(cleaned))
    except (ValueError, TypeError):
        return None


def normalize_state(value: Any) -> Optional[str]:
    text = normalize_text(value)
    if text is None:
        return None
    return text.upper()


class NormalizationCounters:
    def __init__(self):
        self.dates_normalized = 0
        self.currency_values_normalized = 0
        self.interest_rates_normalized = 0
        self.missing_values_converted_to_null = 0

    def to_dict(self) -> dict:
        return {
            "dates_normalized": self.dates_normalized,
            "currency_values_normalized": self.currency_values_normalized,
            "interest_rates_normalized": self.interest_rates_normalized,
            "missing_values_converted_to_null": self.missing_values_converted_to_null,
        }


def normalize_row(raw_row: dict, counters: NormalizationCounters) -> dict:
    mapped: dict[str, Any] = {}

    for raw_col, raw_val in raw_row.items():
        internal_field = normalize_column_name(raw_col)
        if internal_field is None:
            continue
        mapped[internal_field] = raw_val

    text_fields = [
        "loan_id", "borrower_id", "loan_type", "loan_purpose",
        "credit_grade", "employment_length", "income_band",
        "payment_status", "servicer_name", "document_status", "source_system",
    ]

    result: dict[str, Any] = {}

    for field in text_fields:
        raw = mapped.get(field)
        normalized = normalize_text(raw)
        result[field] = normalized
        if raw is not None and str(raw).strip() != "" and normalized is None:
            counters.missing_values_converted_to_null += 1

    raw_state = mapped.get("borrower_state")
    result["borrower_state"] = normalize_state(raw_state)
    if raw_state is not None and str(raw_state).strip() != "" and result["borrower_state"] is None:
        counters.missing_values_converted_to_null += 1

    date_fields = ["origination_date", "maturity_date", "last_payment_date", "last_updated_at"]
    for field in date_fields:
        raw = mapped.get(field)
        if raw is not None and str(raw).strip() not in ("", "nan", "N/A", "NA", "NULL", "null", "None"):
            result[field] = normalize_date(raw)
            counters.dates_normalized += 1
        else:
            result[field] = None

    currency_fields = ["original_principal", "current_balance"]
    for field in currency_fields:
        raw = mapped.get(field)
        if raw is not None and str(raw).strip() not in ("", "nan", "N/A", "NA"):
            result[field] = normalize_currency(raw)
            counters.currency_values_normalized += 1
        else:
            result[field] = None

    raw_rate = mapped.get("interest_rate")
    if raw_rate is not None and str(raw_rate).strip() not in ("", "nan", "N/A", "NA"):
        result["interest_rate"] = normalize_interest_rate(raw_rate)
        counters.interest_rates_normalized += 1
    else:
        result["interest_rate"] = None

    result["term_months"] = normalize_integer(mapped.get("term_months"))
    result["days_past_due"] = normalize_integer(mapped.get("days_past_due"))

    return result
