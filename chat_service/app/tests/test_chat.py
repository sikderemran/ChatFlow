import pytest
from fastapi.testclient import TestClient
# from chat_service.main import app
from app.main import app

client = TestClient(app)

def test_send_and_get_messages():
    # Send
    res = client.post("/send", json={"sender_id": 1, "receiver_id": 2, "content": "Hello"})
    assert res.status_code == 200
    msg = res.json()
    assert msg["content"] == "Hello"

    # Get messages
    res = client.get("/messages/2")
    assert res.status_code == 200
    history = res.json()
    assert any(m["content"] == "Hello" for m in history)
