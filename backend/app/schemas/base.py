from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

# Resolve Phoenix timezone with graceful fallbacks if tzdata is missing
try:
    PHOENIX_TZ = ZoneInfo("America/Phoenix")
except ZoneInfoNotFoundError:
    try:
        PHOENIX_TZ = ZoneInfo("US/Arizona")
    except ZoneInfoNotFoundError:
        # Final fallback: use UTC to avoid crashes; outputs will be UTC
        PHOENIX_TZ = timezone.utc


def _dt_to_phoenix(v: datetime | None):
    if v is None:
        return None
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.astimezone(PHOENIX_TZ).isoformat()


class PhoenixBaseModel(BaseModel):
    """Base Pydantic model that serializes all datetime fields to America/Phoenix.
    Storage remains UTC; this only affects JSON serialization.
    """
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: _dt_to_phoenix},
    )
