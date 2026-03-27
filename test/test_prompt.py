import pytest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


def test_valid_prompt():
    response = client.post(
        url= '/v1/safeagent/prompt',
        json={
            "prompt": "hello"
        }
    )
    assert response.status_code == 200
    assert response.json() == "success"

def test_invalid_prompt():
    prompt = "hello"*500
    response = client.post(
        url= '/v1/safeagent/prompt',
        json= {
            "prompt": prompt
        }
    )
    assert response.status_code == 422