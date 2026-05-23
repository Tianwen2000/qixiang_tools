from datetime import datetime
from zoneinfo import ZoneInfo

from lunar_python import Solar

from app.schemas.time import BeijingTimeOut


BEIJING_TIMEZONE = ZoneInfo("Asia/Shanghai")
WEEKDAY_LABELS = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]


def build_beijing_time_snapshot(current_time: datetime | None = None) -> BeijingTimeOut:
    now = (current_time or datetime.now(BEIJING_TIMEZONE)).astimezone(BEIJING_TIMEZONE).replace(microsecond=0)
    solar = Solar.fromDate(now)
    lunar = solar.getLunar()
    is_leap_month = lunar.getMonth() < 0
    lunar_text = f"{'闰' if is_leap_month else ''}{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}"

    return BeijingTimeOut(
        timezone="Asia/Shanghai",
        now_iso=now.isoformat(),
        unix_ms=int(now.timestamp() * 1000),
        date_text=f"今天是{now.year}年{now.month}月{now.day}日 {WEEKDAY_LABELS[now.weekday()]}",
        time_text=now.strftime("%H:%M:%S"),
        weekday_cn=WEEKDAY_LABELS[now.weekday()],
        lunar_text=lunar_text,
        lunar_full_text=f"农历{lunar_text}",
    )
