from fastapi.testclient import TestClient

from app.main import app
from app.services import feedback_service


def new_client() -> TestClient:
    return TestClient(app)


def test_submit_feedback_anonymous() -> None:
    resp = new_client().post(
        "/api/feedback",
        json={"content": "匿名反馈：这个工具很好用", "feedbackType": "praise", "toolSlug": "json-format"},
    )
    assert resp.status_code == 200
    assert resp.json()["code"] == 0
    assert resp.json()["data"]["id"]


def test_submit_feedback_rejects_empty_content() -> None:
    resp = new_client().post("/api/feedback", json={"content": "   ", "feedbackType": "bug"})
    assert resp.status_code == 400
    assert resp.json()["code"] == 4001


def test_submit_feedback_attaches_account_when_logged_in() -> None:
    account = "13800002001"
    client = new_client()
    client.post("/api/auth/register", json={"account": account, "password": "abc12345"})

    resp = client.post("/api/feedback", json={"content": "登录用户的反馈", "feedbackType": "content"})
    assert resp.status_code == 200

    latest = feedback_service.recent(limit=10)[0]
    assert latest["content"] == "登录用户的反馈"
    assert latest["account"] == account


def test_submit_feedback_keeps_account_blank_when_not_logged_in() -> None:
    client = new_client()
    resp = client.post("/api/feedback", json={"content": "未登录用户反馈", "feedbackType": "bug"})
    assert resp.status_code == 200

    latest = feedback_service.recent(limit=10)[0]
    assert latest["content"] == "未登录用户反馈"
    assert latest["account"] == ""


def test_long_fields_are_truncated_not_rejected() -> None:
    resp = new_client().post(
        "/api/feedback",
        json={"content": "x" * 100, "toolName": "名" * 999, "userAgent": "UA" * 999},
    )
    assert resp.status_code == 200
