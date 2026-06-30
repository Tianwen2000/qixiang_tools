"""文件说明：定义 time 相关接口的数据结构。"""

from pydantic import BaseModel


class BeijingTimeOut(BaseModel):
    timezone: str
    now_iso: str
    unix_ms: int
    date_text: str
    time_text: str
    weekday_cn: str
    lunar_text: str
    lunar_full_text: str
