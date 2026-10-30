from fastapi.testclient import TestClient

def test_admin_login_failure(client: TestClient):
    response = client.post("/api/v1/admin/auth/login", json={
        "email": "wrong@brainmint.com",
        "password": "wrongpassword"
    })
    # Expecting an unauthorized or bad request status code on invalid login
    assert response.status_code in [400, 401, 422]

def test_refresh_token_invalid(client: TestClient):
    response = client.post("/api/v1/admin/auth/refresh", json={
        "refresh_token": "invalid_token_string"
    })
    assert response.status_code in [400, 401, 422]

def test_forgot_password_no_token_leak(client: TestClient):
    """
    Ensure the forgot-password endpoint returns a secure message 
    and does not leak the debug_reset_token in the response.
    """
    response = client.post("/api/v1/admin/auth/forgot-password", json={
        "email": "admin@brainmint.com"
    })
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "debug_reset_token" not in data