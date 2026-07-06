from datetime import date, datetime, time, timezone
from zoneinfo import ZoneInfo

THAI_MONTHS = [
    "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค.",
]

BANGKOK_TZ = ZoneInfo("Asia/Bangkok")


def thai_date_str(d: date | datetime) -> str:
    if isinstance(d, datetime):
        d = d.astimezone(BANGKOK_TZ).date()
    be_year = d.year + 543
    return f"{d.day:02d}-{THAI_MONTHS[d.month - 1]}-{be_year}"


def thai_datetime_str(dt: datetime) -> str:
    bk = dt.astimezone(BANGKOK_TZ)
    be_year = bk.year + 543
    return f"{bk.day:02d}-{THAI_MONTHS[bk.month - 1]}-{be_year} {bk.hour:02d}:{bk.minute:02d}"


def bangkok_today() -> date:
    return datetime.now(BANGKOK_TZ).date()


def bangkok_now() -> datetime:
    return datetime.now(BANGKOK_TZ)


def bangkok_closes_at_utc(d: date) -> datetime:
    """Return 23:59:59 Bangkok time for the given date, converted to UTC."""
    bkk_dt = datetime.combine(d, time(23, 59, 59), tzinfo=BANGKOK_TZ)
    return bkk_dt.astimezone(timezone.utc)


def parse_as_bangkok(dt_str: str, fmt: str = "%Y-%m-%d %H:%M") -> datetime:
    naive = datetime.strptime(dt_str, fmt)
    return naive.replace(tzinfo=BANGKOK_TZ)
