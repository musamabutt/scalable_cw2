from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200

def test_videos_endpoint():
    response = client.get("/videos")
    # Check that the endpoint responds (even if empty)
    assert response.status_code == 200
    # Optionally, check that response is a list
    assert isinstance(response.json(), list)
