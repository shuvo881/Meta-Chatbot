from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_facebook_login_url_endpoint():
    response = client.get("/auth/facebook/login-url")
    assert response.status_code == 200
    payload = response.json()
    assert "login_url" in payload
    assert "facebook.com" in payload["login_url"]


def test_facebook_callback_requires_code():
    response = client.get("/auth/facebook/callback")
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing Facebook authorization code"


def test_facebook_login_url_uses_pages_messaging_scope_by_default():
    response = client.get("/auth/facebook/login-url")
    assert response.status_code == 200

    query = parse_qs(urlparse(response.json()["login_url"]).query)
    assert query["scope"][0] == "pages_messaging"
    assert "email" not in query["scope"][0]


def test_messenger_webhook_verifies_subscription():
    response = client.get("/webhooks/messenger?hub.mode=subscribe&hub.challenge=test-challenge&hub.verify_token=demo-token")
    assert response.status_code == 200
    assert response.text == "test-challenge"


def test_root_webhook_verifies_subscription():
    response = client.get("/?hub.mode=subscribe&hub.challenge=test-challenge&hub.verify_token=demo-token")
    assert response.status_code == 200
    assert response.text == "test-challenge"


def test_messenger_webhook_rejects_invalid_token():
    response = client.get("/webhooks/messenger?hub.mode=subscribe&hub.challenge=test-challenge&hub.verify_token=wrong-token")
    assert response.status_code == 403
