from fastapi.testclient import TestClient

from app.main import app


ADMIN = "13900000000"  # 与 conftest 的 ADMIN_ACCOUNTS 一致
PASSWORD = "admin12345"


def new_client() -> TestClient:
    return TestClient(app)


def test_admin_endpoints_require_login() -> None:
    assert new_client().get("/api/admin/feedback").status_code == 401
    assert new_client().get("/api/admin/logs").status_code == 401


def test_non_admin_is_forbidden() -> None:
    client = new_client()
    client.post("/api/auth/register", json={"account": "13700000001", "password": "user12345"})
    me = client.get("/api/auth/me")
    assert me.json()["data"]["user"]["is_admin"] is False
    assert client.get("/api/admin/feedback").status_code == 403


def test_admin_can_view_feedback_and_logs() -> None:
    client = new_client()
    client.post("/api/auth/register", json={"account": ADMIN, "password": PASSWORD})

    me = client.get("/api/auth/me")
    assert me.json()["data"]["user"]["is_admin"] is True

    # 先提交一条反馈
    client.post("/api/feedback", json={"content": "管理员可见的反馈", "feedbackType": "bug"})

    feedback = client.get("/api/admin/feedback")
    assert feedback.status_code == 200
    assert any(item["content"] == "管理员可见的反馈" for item in feedback.json()["data"]["items"])

    logs = client.get("/api/admin/logs")
    assert logs.status_code == 200
    events = [(item["event"], item["account"]) for item in logs.json()["data"]["items"]]
    # 注册管理员账号应留下一条 register 活动日志
    assert ("register", ADMIN) in events
