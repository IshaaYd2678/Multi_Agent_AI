from agents.email_agent import process_email


def test_missing_from_header_returns_unknown_sender():
    """6.2 — no From: header → sender == 'Unknown', no 'error' key"""
    result = process_email("Subject: Hello\n\nThis is the body.")
    assert "error" not in result
    assert result["sender"] == "Unknown"


def test_valid_from_header_returns_correct_sender():
    """6.3 — valid From: header → correct sender preserved"""
    result = process_email("From: alice@example.com\nSubject: Test\n\nBody text.")
    assert "error" not in result
    assert result["sender"] == "alice@example.com"
