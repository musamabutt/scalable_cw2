from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_homepage():
    response = client.get("/")
    assert response.status_code == 200

def test_video_upload_page():
    response = client.get("/upload")
    assert response.status_code == 200

def test_api_healthcheck():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
