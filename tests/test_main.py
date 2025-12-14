from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Linkedin Insights Microservice is running"}

# Note: Further integration tests require running MongoDB/Redis.
# We skip mocking complex async DB calls here for brevity in this assignment file,
# but in a real repo, we would use 'unittest.mock' or 'pytest-mock'.
