from decimal import Decimal
from app.utils.normalization import (
    normalize_currency,
    normalize_interest_rate,
    normalize_date,
    normalize_text,
    normalize_column_name,
)


def test_currency_dollar_sign():
    assert normalize_currency("$500,000") == Decimal("500000")


def test_currency_rupee_symbol():
    assert normalize_currency("₹5,00,000") == Decimal("500000")
    assert normalize_currency("₹ 10,00,000.50") == Decimal("1000000.50")


def test_currency_rs_prefix():
    assert normalize_currency("Rs. 25,00,000") == Decimal("2500000")
    assert normalize_currency("Rs 150000") == Decimal("150000")
    assert normalize_currency("INR 50,00,000") == Decimal("5000000")


def test_currency_with_commas():
    assert normalize_currency("500,000.00") == Decimal("500000.00")


def test_currency_plain():
    assert normalize_currency("500000") == Decimal("500000")


def test_currency_none():
    assert normalize_currency(None) is None
    assert normalize_currency("") is None
    assert normalize_currency("N/A") is None


def test_interest_rate_percent():
    assert normalize_interest_rate("8.5%") == Decimal("8.5")


def test_interest_rate_plain():
    assert normalize_interest_rate("8.5") == Decimal("8.5")


def test_interest_rate_decimal_fraction():
    result = normalize_interest_rate("0.085")
    assert result is not None
    assert abs(result - Decimal("8.5")) < Decimal("0.001")


def test_date_iso():
    from datetime import date
    assert normalize_date("2025-01-15") == date(2025, 1, 15)


def test_date_us_format():
    from datetime import date
    assert normalize_date("01/15/2025") == date(2025, 1, 15)


def test_date_textual():
    from datetime import date
    assert normalize_date("15-Jan-2025") == date(2025, 1, 15)


def test_date_none():
    assert normalize_date(None) is None
    assert normalize_date("") is None


def test_text_strips_whitespace():
    assert normalize_text("  hello  ") == "hello"


def test_text_empty_to_none():
    assert normalize_text("") is None
    assert normalize_text("N/A") is None
    assert normalize_text("null") is None


def test_column_name_mapping():
    assert normalize_column_name("Loan ID") == "loan_id"
    assert normalize_column_name("INTEREST RATE") == "interest_rate"  # Function lowercases before lookup
    assert normalize_column_name("interest rate") == "interest_rate"
    assert normalize_column_name("loan_id") == "loan_id"
    assert normalize_column_name("unknown_column_xyz") is None
