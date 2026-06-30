"""文件说明：测试 test backoffice 相关后端接口或服务逻辑。"""

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services import backoffice_service


BACKOFFICE_ADMIN_ACCOUNT = "admin"
BACKOFFICE_ADMIN_PASSWORD = "deng1201"
BACKOFFICE_VIEWER_ACCOUNT = "view"
BACKOFFICE_VIEWER_PASSWORD = "viewroot"
BACKOFFICE_ANSWER = "我的爱"


def new_client() -> TestClient:
    return TestClient(app)


def configure_backoffice() -> None:
    settings = get_settings()
    settings.backoffice_accounts = (
        f"{BACKOFFICE_ADMIN_ACCOUNT}:{BACKOFFICE_ADMIN_PASSWORD}:admin,"
        f"{BACKOFFICE_VIEWER_ACCOUNT}:{BACKOFFICE_VIEWER_PASSWORD}:viewer"
    )
    settings.backoffice_account = ""
    settings.backoffice_password = ""
    settings.backoffice_entry_answer = BACKOFFICE_ANSWER
    settings.backoffice_entry_question = "如果时间忘记了名字，它会把前三个音节藏在哪里？"
    backoffice_service.reset_for_tests()


def test_old_ai_admin_endpoints_are_removed() -> None:
    configure_backoffice()
    client = new_client()
    client.post("/api/auth/register", json={"account": "13900000000", "password": "admin12345"})
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert "is_admin" not in me.json()["data"]["user"]
    assert client.get("/api/admin/feedback").status_code == 404
    assert client.get("/api/admin/logs").status_code == 404


def test_backoffice_entry_login_and_readonly_data() -> None:
    configure_backoffice()
    client = new_client()

    assert client.get("/api/backoffice/feedback").status_code == 401
    challenge = client.get("/api/backoffice/challenge")
    assert challenge.status_code == 200
    assert challenge.json()["data"]["question"] == "如果时间忘记了名字，它会把前三个音节藏在哪里？"

    wrong_entry = client.post("/api/backoffice/entry", json={"answer": "wrong"})
    assert wrong_entry.status_code == 401

    entry = client.post("/api/backoffice/entry", json={"answer": BACKOFFICE_ANSWER})
    assert entry.status_code == 200
    path = entry.json()["data"]["path"]
    assert path.startswith("/qx-backoffice/")
    ticket = path.rsplit("/", 1)[-1]

    consume = client.post("/api/backoffice/entry/consume", json={"ticket": ticket})
    assert consume.status_code == 200
    assert client.post("/api/backoffice/entry/consume", json={"ticket": ticket}).status_code == 401

    assert client.post("/api/backoffice/login", json={"account": BACKOFFICE_ADMIN_ACCOUNT, "password": "wrong"}).status_code == 401
    login = client.post(
        "/api/backoffice/login",
        json={"account": BACKOFFICE_ADMIN_ACCOUNT, "password": BACKOFFICE_ADMIN_PASSWORD},
    )
    assert login.status_code == 200
    assert login.json()["data"]["user"]["account"] == BACKOFFICE_ADMIN_ACCOUNT
    assert login.json()["data"]["user"]["role"] == "admin"

    # 后台只读页复用现有反馈与账号活动数据，但鉴权使用后台专用 Cookie。
    client.post("/api/feedback", json={"content": "后台可见的反馈", "feedbackType": "bug"})
    feedback = client.get("/api/backoffice/feedback")
    assert feedback.status_code == 200
    assert any(item["content"] == "后台可见的反馈" for item in feedback.json()["data"]["items"])

    logs = client.get("/api/backoffice/logs")
    assert logs.status_code == 200
    assert "items" in logs.json()["data"]

    logout = client.post("/api/backoffice/logout")
    assert logout.status_code == 200
    assert client.get("/api/backoffice/me").status_code == 401


def test_backoffice_viewer_can_only_read_feedback() -> None:
    configure_backoffice()
    client = new_client()

    login = client.post(
        "/api/backoffice/login",
        json={"account": BACKOFFICE_VIEWER_ACCOUNT, "password": BACKOFFICE_VIEWER_PASSWORD},
    )
    assert login.status_code == 200
    assert login.json()["data"]["user"]["role"] == "viewer"
    assert client.get("/api/backoffice/feedback").status_code == 200
    logs = client.get("/api/backoffice/logs")
    assert logs.status_code == 403
    assert logs.json()["message"] == "当前后台账号无权查看该内容"
