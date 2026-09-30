import pytest

from app.pii import scrub_text, summarize_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out, f"Phone {phone_number} should be scrubbed"
        assert "REDACTED_PHONE_VN" in out


def test_scrub_email_in_sentence() -> None:
    out = scrub_text("Contact me at test.user@example.com for details")
    assert "test.user@example.com" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_multiple_phone_formats() -> None:
    text = "First: 0901234567, second: 090 123 4567, third: 090.123.4567, fourth: 090-123-4567, fifth: +84 90 123 4567"
    out = scrub_text(text)
    assert "0901234567" not in out
    assert "090 123 4567" not in out
    assert "090.123.4567" not in out
    assert "090-123-4567" not in out
    assert "+84 90 123 4567" not in out
    assert out.count("REDACTED_PHONE_VN") == 5


def test_scrub_cccd() -> None:
    out = scrub_text("My CCCD is 012345678901")
    assert "012345678901" not in out
    assert "REDACTED_CCCD" in out


def test_scrub_credit_card() -> None:
    out = scrub_text("Card 4111 1111 1111 1111")
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_credit_card_no_spaces() -> None:
    out = scrub_text("Card: 4111-1111-1111-1111")
    assert "4111-1111-1111-1111" not in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_mixed_pii() -> None:
    text = "Email test@example.com, phone 0901234567, CCCD 012345678901, card 4111 1111 1111 1111"
    out = scrub_text(text)
    assert "test@example.com" not in out
    assert "0901234567" not in out
    assert "012345678901" not in out
    assert "4111 1111 1111 1111" not in out
    assert "REDACTED_EMAIL" in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_CCCD" in out
    assert "REDACTED_CREDIT_CARD" in out


def test_scrub_bytes_input() -> None:
    out = scrub_text(b"Email me at test@example.com")
    assert isinstance(out, str)
    assert "test@example.com" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_non_string_input() -> None:
    out = scrub_text(12345)
    assert isinstance(out, str)
    # Integer should not match any pattern
    assert "REDACTED" not in out


def test_summarize_text() -> None:
    out = summarize_text("This is a very long message with email test@example.com in it")
    assert "test@example.com" not in out
    assert "REDACTED_EMAIL" in out
    assert len(out) <= 83  # max_len=80 + "..."


def test_summarize_text_short() -> None:
    out = summarize_text("Short message")
    assert "REDACTED" not in out
    assert out == "Short message"


def test_scrub_no_false_positives_for_normal_numbers() -> None:
    # Regular 10-digit numbers that are not Vietnamese phone format should NOT be scrubbed
    out = scrub_text("Order number 1234567890 and quantity 50")
    assert "1234567890" in out  # no Vietnamese carrier prefix
    assert "50" in out
    assert "REDACTED" not in out
