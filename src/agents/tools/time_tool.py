# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""Time tool for date resolution."""

from datetime import datetime

from strands.tools import tool


@tool
def get_current_time() -> str:
    """Get current date and time in Mauritius timezone (Indian/Mauritius, UTC+4).

    Use this tool when user mentions relative dates like 'today', 'tomorrow', 'next week'.

    Returns:
        Current datetime in ISO 8601 format with timezone: YYYY-MM-DDTHH:MM:SS+04:00
    """
    # Mauritius is UTC+4 (no DST)
    now = datetime.utcnow()
    mauritius_time = now.replace(microsecond=0)
    # Add 4 hours for Mauritius timezone
    from datetime import timedelta

    mauritius_time = mauritius_time + timedelta(hours=4)
    return mauritius_time.strftime("%Y-%m-%dT%H:%M:%S+04:00")
