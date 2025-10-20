# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""Tests for response cleaning functionality."""

import re


def clean_response(text: str) -> str:
    """Remove <think> and <thinking> tags and internal reasoning from response."""
    # Remove <think>...</think> and <thinking>...</thinking> blocks (including multiline)
    cleaned = re.sub(
        r"<think(?:ing)?>.*?</think(?:ing)?>", "", text, flags=re.DOTALL | re.IGNORECASE
    )
    # Remove extra whitespace/newlines left behind
    cleaned = re.sub(r"\n\s*\n\s*\n", "\n\n", cleaned)
    return cleaned.strip()


def test_clean_response_removes_think_tags():
    """Test that <think> tags are removed from responses."""
    # Test single-line think tag
    text = "Hello! <think>I need to check availability</think> How can I help?"
    expected = "Hello!  How can I help?"
    assert clean_response(text) == expected

    # Test multi-line think tag
    text = """Hello!
<think>
Let me reason about this:
1. Check calendar
2. Verify time slot
</think>
I can help you book a table."""
    expected = "Hello!\n\nI can help you book a table."
    assert clean_response(text) == expected

    # Test multiple think tags
    text = "<think>First thought</think>Response<think>Second thought</think>"
    expected = "Response"
    assert clean_response(text) == expected

    # Test case insensitive
    text = "Hello <THINK>reasoning</THINK> there"
    expected = "Hello  there"
    assert clean_response(text) == expected

    # Test no think tags
    text = "Hello! How can I help you today?"
    assert clean_response(text) == text


def test_clean_response_handles_empty():
    """Test that empty strings are handled correctly."""
    assert clean_response("") == ""
    assert clean_response("<think>only thinking</think>") == ""


def test_clean_response_real_world_examples():
    """Test with realistic agent responses."""
    # Example with think tag at start
    text = """<think>User wants to book a table. I need to collect: name, date, time, party size.</think>

I'd be happy to help you book a table at La Bella Vita! To proceed, I'll need a few details:
- Your name
- Preferred date and time
- Number of guests"""

    result = clean_response(text)
    assert "<think>" not in result
    assert "</think>" not in result
    assert "I'd be happy to help" in result

    # Example with think tag in middle
    text = """Sure! Let me check our menu. <think>I should use the search_restaurant_info tool</think>

Here are our vegetarian options:
- Margherita Pizza
- Pasta Primavera"""

    result = clean_response(text)
    assert "<think>" not in result
    assert "Here are our vegetarian options" in result

    # Example with <thinking> tag (actual model output)
    text = """<thinking> The current time is 2025-10-09T20:18:08.914074+04:00. Therefore, tomorrow is 2025-10-10. I need to collect the customer's name, party size, and phone number to create the booking. </thinking>

Hello! I can help you with that. Could you please provide me with your name, the number of guests, and your phone number?"""

    result = clean_response(text)
    assert "<thinking>" not in result
    assert "</thinking>" not in result
    assert "Hello! I can help you with that" in result
    assert "Could you please provide" in result
