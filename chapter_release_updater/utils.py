from __future__ import annotations

from datetime import datetime, timezone, date
from typing import Optional
from dateutil import parser as date_parser


def parse_mangadex_datetime_to_date(value: Optional[str]) -> Optional[date]:
    if not value:
        return None
    dt = date_parser.isoparse(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.date()


def ensure_date_str(d: date) -> str:
    return d.isoformat()