"""Validation adapted from the supplied Research Opportunity Portal; see README."""
from datetime import datetime, date
import re

TEXT_FIELDS = [
    "research_title",
    "research_description",
    "research_area",
    "faculty_name",
    "department",
    "required_skills",
]
ALL_FIELDS = TEXT_FIELDS + ["available_positions", "application_deadline", "status"]
TEXT_LIMITS = {"research_title": 200, "research_area": 100, "faculty_name": 100,
               "department": 100, "required_skills": 255}
VALID_STATUSES = ["Open", "Closed"]


# ---------------------------------------------------------------- helpers

def to_json(row):
    """Convert a database row (dict) into JSON-friendly values."""
    if row and isinstance(row.get("application_deadline"), date):
        row["application_deadline"] = row["application_deadline"].isoformat()
    return row


def validate(data):
    """
    Check one opportunity's data.
    Returns (clean_data, errors). If errors is empty, the data is valid.
    """
    errors = []
    clean = {}

    # Text fields must be non-empty strings
    for field in TEXT_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or value.strip() == "":
            errors.append(f"{field} is required")
        else:
            clean[field] = value.strip()
            if len(clean[field]) > TEXT_LIMITS.get(field, 65535) or (field == "research_description" and len(clean[field].encode("utf-8")) > 65535):
                errors.append(f"{field} exceeds its database length limit")

    # Available positions must be a positive whole number
    positions = data.get("available_positions")
    try:
        if isinstance(positions, bool):
            raise ValueError
        positions = int(str(positions))
        if positions <= 0 or positions > 2147483647:
            raise ValueError
        clean["available_positions"] = positions
    except (ValueError, TypeError):
        errors.append("available_positions must be a positive whole number")

    # Deadline must be a real date in YYYY-MM-DD format
    deadline = data.get("application_deadline")
    try:
        if not isinstance(deadline, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", deadline):
            raise ValueError
        clean["application_deadline"] = datetime.strptime(str(deadline), "%Y-%m-%d").date()
        if clean["application_deadline"].year < 1000:
            raise ValueError
    except (ValueError, TypeError):
        errors.append("application_deadline must be a valid date (YYYY-MM-DD)")

    # Status must be Open or Closed (defaults to Open when creating)
    status = data.get("status", "Open")
    if status not in VALID_STATUSES:
        errors.append("status must be either 'Open' or 'Closed'")
    else:
        clean["status"] = status

    return clean, errors


