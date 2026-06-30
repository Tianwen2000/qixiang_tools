"""文件说明：测试 test time 相关后端接口或服务逻辑。"""

from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient

from app.main import app
from app.services.time_service import build_beijing_time_snapshot


client = TestClient(app)


def test_build_beijing_time_snapshot_for_fixed_datetime() -> None:
    snapshot = build_beijing_time_snapshot(datetime(2026, 4, 8, 12, 0, 0, tzinfo=ZoneInfo("Asia/Shanghai")))

    assert snapshot.timezone == "Asia/Shanghai"
    assert snapshot.now_iso == "2026-04-08T12:00:00+08:00"
    assert snapshot.date_text == "今天是2026年4月8日 星期三"
    assert snapshot.time_text == "12:00:00"
    assert snapshot.weekday_cn == "星期三"
    assert snapshot.lunar_text == "二月廿一"
    assert snapshot.lunar_full_text == "农历二月廿一"


def test_beijing_time_endpoint() -> None:
    response = client.get("/api/time/beijing")

    assert response.status_code == 200
    data = response.json()["data"]
    assert data["timezone"] == "Asia/Shanghai"
    assert data["now_iso"].endswith("+08:00")
    assert isinstance(data["unix_ms"], int)
    assert data["date_text"].startswith("今天是")
    assert data["time_text"].count(":") == 2
    assert data["weekday_cn"].startswith("星期")
    assert data["lunar_full_text"].startswith("农历")
