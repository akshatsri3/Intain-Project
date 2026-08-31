from datetime import datetime, timezone
from typing import Optional

from app.models.validation_exception import ValidationException
from app.models.loan import Loan


def generate_suggestion(exception: ValidationException, loan: Optional[Loan] = None) -> dict:
    rule = exception.rule_code
    suggestion = _SUGGESTION_GENERATORS.get(rule, _default_suggestion)(exception, loan)
    suggestion["model"] = "rule-engine-v1"
    suggestion["generated_at"] = datetime.now(timezone.utc).isoformat()
    suggestion["rule_code"] = rule
    return suggestion

def _suggest_balance_exceeds_principal(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": f"Cap current_balance at original_principal value ({exc.expected_range})",
        "explanation": (
            f"The current balance ({exc.current_value}) exceeds the original principal "
            f"({exc.expected_range}). This typically indicates a data entry error where the "
            "balance was not properly updated after payments, or a system that includes "
            "accrued interest in the balance field. "
            "Recommendation: set current_balance = original_principal unless the loan terms "
            "allow negative amortization."
        ),
        "confidence": "HIGH",
    }


def _suggest_negative_balance(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": f"Convert {exc.field_name} to absolute value or set to 0",
        "explanation": (
            f"A negative value ({exc.current_value}) was detected in {exc.field_name}. "
            "This is most commonly caused by parenthetical notation in the source file "
            "(e.g., '(1000)' representing negative ₹1,000) that was not fully cleaned "
            "during normalization, or a refund/overpayment that should be handled separately. "
            "Recommendation: convert to absolute value if this represents a valid principal."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_rate_out_of_range(exc: ValidationException, loan: Optional[Loan]) -> dict:
    rate_val = exc.current_value
    try:
        rate_float = float(rate_val)
        if 0 < rate_float <= 1:
            suggested = round(rate_float * 100, 4)
            return {
                "suggested_action": f"Multiply rate by 100: {rate_val} → {suggested}%",
                "explanation": (
                    f"The interest rate ({rate_val}) appears to be stored as a decimal fraction "
                    f"rather than a percentage. A value of {rate_val} likely represents "
                    f"{suggested}%. This is a common format discrepancy between systems."
                ),
                "confidence": "HIGH",
            }
    except (ValueError, TypeError):
        pass

    return {
        "suggested_action": "Review and correct the interest rate value manually",
        "explanation": (
            f"The interest rate ({rate_val}) is outside the expected range of 0% to 50%. "
            "This may indicate a data entry error or unit conversion issue. "
            "Verify against the source document."
        ),
        "confidence": "LOW",
    }


def _suggest_maturity_before_origination(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Swap origination_date and maturity_date",
        "explanation": (
            f"The maturity date is before the origination date. "
            "This is almost certainly a data entry error where the two date fields were "
            "reversed. Recommendation: swap the values so origination comes first."
        ),
        "confidence": "HIGH",
    }


def _suggest_duplicate_loan_id(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Use the most recent record (by last_updated_at or upload date)",
        "explanation": (
            f"Loan ID '{exc.current_value}' appears in multiple datasets. "
            "This often happens when servicer updates are uploaded alongside the original "
            "loan tape. The most recent record typically contains the latest payment and "
            "balance information. Recommendation: retain the most recently uploaded or "
            "updated record and mark older duplicates as superseded."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_suspicious_duplicate(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Review for potential duplicate loan origination",
        "explanation": (
            f"Borrower '{exc.current_value}' has multiple loans with the same principal "
            "and origination date. While a borrower can have multiple loans, identical "
            "amounts on the same date suggest a possible duplicate entry. "
            "Recommendation: verify with source system whether these are distinct loans."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_payment_status_mismatch(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Align payment_status with days_past_due value",
        "explanation": (
            f"Inconsistency detected: {exc.message} "
            "The payment status and days-past-due fields should be consistent. "
            "If DPD > 0, status should reflect delinquency. If DPD = 0, status should be Current. "
            "Recommendation: update the payment_status to match the DPD value, "
            "or correct the DPD if the status is authoritative."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_missing_loan_id(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Generate a system-assigned loan ID or flag for manual entry",
        "explanation": (
            "The loan ID is missing, which makes this record difficult to track, "
            "reconcile, or deduplicate. Recommendation: assign a system-generated "
            "identifier (e.g., based on dataset + row number) or request the loan ID "
            "from the data source."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_missing_principal(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Request principal balance from source system",
        "explanation": (
            "Original principal is a critical loan attribute required for balance validation, "
            "LTV calculations, and portfolio analytics. Without it, many downstream "
            "validations cannot be performed. Recommendation: retrieve from the source "
            "system or flag for manual data entry."
        ),
        "confidence": "LOW",
    }


def _suggest_missing_document_status(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Cross-reference with document_manifest data source",
        "explanation": (
            "Document status is missing. In a complete loan verification workflow, "
            "document availability (e.g., note, deed, title) must be confirmed. "
            "Recommendation: check the document manifest file or request a status "
            "update from the document custodian."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_negative_term(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Correct term_months to a positive value",
        "explanation": (
            f"Loan term is {exc.current_value} months, which is invalid. "
            "This may be a sign error or a parsing issue. "
            "Recommendation: review the source data and correct to the actual loan term."
        ),
        "confidence": "HIGH",
    }


def _suggest_excessive_dpd(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Verify if loan should be marked as charged-off or closed",
        "explanation": (
            f"Days past due is {exc.current_value}, which exceeds 360 days. "
            "Loans delinquent for over a year are typically charged off. "
            "Recommendation: verify the loan's current status with the servicer "
            "and update payment_status accordingly."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_invalid_state(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Correct to a valid Indian state/UT abbreviation",
        "explanation": (
            f"'{exc.current_value}' is not a recognized Indian state or union territory code. "
            "This may be a typo or full state name that was not abbreviated. "
            "Recommendation: map to the correct two-letter state/UT code (e.g. MH, DL, KA, TN)."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_stale_record(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Request updated data from the servicer",
        "explanation": (
            f"This record was last updated on {exc.current_value}, which is over a year ago. "
            "Stale records may not reflect current payment status, balance, or delinquency. "
            "Recommendation: request a fresh data extract from the servicer."
        ),
        "confidence": "MEDIUM",
    }


def _suggest_closed_with_balance(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Set current_balance to 0 or update payment_status",
        "explanation": (
            f"Loan is marked as closed/paid but has a remaining balance of {exc.current_value}. "
            "Either the balance was not zeroed out when the loan was closed, or the "
            "payment status is incorrect. Recommendation: if truly closed, set balance to 0."
        ),
        "confidence": "HIGH",
    }


def _default_suggestion(exc: ValidationException, loan: Optional[Loan]) -> dict:
    return {
        "suggested_action": "Review this exception manually",
        "explanation": f"Validation rule '{exc.rule_code}' was triggered: {exc.message}",
        "confidence": "LOW",
    }


def generate_batch_summary(exceptions: list) -> dict:
    if not exceptions:
        return {"summary": "No exceptions to summarize.", "recommendations": []}

    rule_counts = {}
    severity_counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    for exc in exceptions:
        rule_counts[exc.rule_code] = rule_counts.get(exc.rule_code, 0) + 1
        severity_counts[exc.severity.value if hasattr(exc.severity, 'value') else exc.severity] += 1

    top_rule = max(rule_counts, key=rule_counts.get)
    top_count = rule_counts[top_rule]

    recommendations = []
    if severity_counts["ERROR"] > 0:
        recommendations.append(
            f"Prioritize resolving {severity_counts['ERROR']} ERROR-level exceptions first."
        )
    if "DUPLICATE_LOAN_ID" in rule_counts:
        recommendations.append(
            f"Found {rule_counts['DUPLICATE_LOAN_ID']} duplicate loan IDs. Consider deduplication."
        )
    if "BALANCE_EXCEEDS_PRINCIPAL" in rule_counts:
        recommendations.append(
            f"{rule_counts['BALANCE_EXCEEDS_PRINCIPAL']} loans have balance > principal."
        )

    return {
        "total_exceptions": len(exceptions),
        "severity_breakdown": severity_counts,
        "rule_breakdown": rule_counts,
        "top_issue": f"{top_rule} ({top_count} occurrences)",
        "summary": (
            f"Found {len(exceptions)} validation exceptions across this dataset. "
            f"The most common issue is {top_rule} ({top_count} occurrences). "
            f"There are {severity_counts['ERROR']} errors and "
            f"{severity_counts['WARNING']} warnings requiring attention."
        ),
        "recommendations": recommendations,
        "model": "rule-engine-v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


# Mapping from rule codes to suggestion generators
_SUGGESTION_GENERATORS = {
    "BALANCE_EXCEEDS_PRINCIPAL": _suggest_balance_exceeds_principal,
    "NEGATIVE_BALANCE": _suggest_negative_balance,
    "RATE_OUT_OF_RANGE": _suggest_rate_out_of_range,
    "MATURITY_BEFORE_ORIGINATION": _suggest_maturity_before_origination,
    "DUPLICATE_LOAN_ID": _suggest_duplicate_loan_id,
    "SUSPICIOUS_DUPLICATE": _suggest_suspicious_duplicate,
    "PAYMENT_STATUS_DPD_MISMATCH": _suggest_payment_status_mismatch,
    "MISSING_LOAN_ID": _suggest_missing_loan_id,
    "MISSING_PRINCIPAL": _suggest_missing_principal,
    "MISSING_DOCUMENT_STATUS": _suggest_missing_document_status,
    "NEGATIVE_TERM": _suggest_negative_term,
    "EXCESSIVE_DPD": _suggest_excessive_dpd,
    "INVALID_STATE_CODE": _suggest_invalid_state,
    "STALE_RECORD": _suggest_stale_record,
    "CLOSED_WITH_BALANCE": _suggest_closed_with_balance,
}
