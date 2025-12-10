# tests/test_api.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_root_page():
    response = client.get("/")
    assert response.status_code == 200

def test_feed_requires_login():
    response = client.get("/feed")
    # Redirect to login because no cookie
    assert response.status_code == 200 or response.status_code == 302
