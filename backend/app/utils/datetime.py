from datetime import datetime, timedelta, timezone


CHINA_TZ = timezone(timedelta(hours=8))


def now_cn() -> datetime:
    """Return naive datetime in China Standard Time (UTC+8) for MySQL DATETIME fields."""
    return datetime.now(CHINA_TZ).replace(tzinfo=None)
