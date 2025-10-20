# Copyright (C) 2025 Teamwork Mauritius
# AGPL-3.0 License

"""Business hours configuration for La Bella Vita restaurant."""

from datetime import time

# Restaurant operating hours (Mauritius timezone: UTC+4)
BUSINESS_HOURS = {
    "monday": {"start": time(11, 0), "end": time(22, 0)},  # 11am - 10pm
    "tuesday": {"start": time(11, 0), "end": time(22, 0)},
    "wednesday": {"start": time(11, 0), "end": time(22, 0)},
    "thursday": {"start": time(11, 0), "end": time(22, 0)},
    "friday": {"start": time(11, 0), "end": time(23, 0)},  # 11am - 11pm
    "saturday": {"start": time(11, 0), "end": time(23, 0)},
    "sunday": {"start": time(11, 0), "end": time(22, 0)},
}

# Closed days (if any)
CLOSED_DAYS = []  # e.g., ["monday"] if closed on Mondays

# Default booking duration in hours
DEFAULT_BOOKING_DURATION = 2
