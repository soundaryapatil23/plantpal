from app import create_app


def client():
    return create_app().test_client()


def test_health():
    r = client().get("/health")
    assert r.status_code == 200
    assert r.get_json() == {"status": "UP"}


def test_list_plants_returns_seed_data():
    r = client().get("/plants")
    assert r.status_code == 200
    assert len(r.get_json()) == 2


def test_add_plant():
    c = client()
    r = c.post("/plants", json={"name": "Money Plant", "water_every_days": 4})
    assert r.status_code == 201
    assert r.get_json()["days_since_watered"] == 0
    assert len(c.get("/plants").get_json()) == 3


def test_add_plant_validates_input():
    c = client()
    assert c.post("/plants", json={"water_every_days": 3}).status_code == 400
    assert c.post("/plants", json={"name": "Fern", "water_every_days": 0}).status_code == 400


def test_due_then_water():
    c = client()
    assert [p["name"] for p in c.get("/plants/due").get_json()] == ["Tulsi"]
    assert c.post("/plants/1/water").status_code == 200
    assert c.get("/plants/due").get_json() == []
    assert c.post("/plants/99/water").status_code == 404
