from app import create_app


def test_live_health_endpoint():
    client = create_app().test_client()

    response = client.get("/api/health/live")

    assert response.status_code == 200
    assert response.json == {"status": "ok"}
