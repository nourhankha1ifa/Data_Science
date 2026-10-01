from datetime import datetime


def _parse(value, fmt, message):
    try:
        return datetime.strptime(value.strip(), fmt).strftime(fmt)
    except (ValueError, AttributeError):
        raise ValueError(message)


def validate_date(value, field_name="Date"):
    """Returns the date normalised as YYYY-MM-DD."""
    return _parse(value, "%Y-%m-%d", f"{field_name} must be in YYYY-MM-DD format")


def validate_month(value, field_name="Month"):
    """Returns the month normalised as YYYY-MM."""
    return _parse(value, "%Y-%m", f"{field_name} must be in YYYY-MM format")


def validate_time(value, field_name="Time"):
    """Empty time is allowed (e.g. absent). Otherwise HH:MM."""
    value = value.strip()
    if not value:
        return ""
    return _parse(value, "%H:%M", f"{field_name} must be in HH:MM format")
