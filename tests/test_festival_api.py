import json
import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from api import create_app


def make_client(tmp_path: Path) -> TestClient:
    original = Path("data/festival.json")
    target = tmp_path / "festival.json"
    target.write_text(original.read_text(encoding="utf-8"), encoding="utf-8")
    app = create_app(target)
    return TestClient(app)


def test_festival_basics(tmp_path: Path):
    client = make_client(tmp_path)
    festival = client.get("/api/festival")
    assert festival.status_code == 200
    payload = festival.json()
    assert payload["name"] == "Deauville Festival du Rire 2027"
    assert payload["days"] == [
        "2027-06-10",
        "2027-06-11",
        "2027-06-12",
        "2027-06-13",
    ]


def test_programme_filter_by_day(tmp_path: Path):
    client = make_client(tmp_path)
    response = client.get("/api/programme", params={"day": "2027-06-12"})
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert all(item["day"] == "2027-06-12" for item in response.json())


def test_programme_write_persists_json(tmp_path: Path):
    client = make_client(tmp_path)
    body = {
        "kind": "solo",
        "title": "Sunset Laughs",
        "venue": "le-kiosque",
        "start": "2027-06-13T16:00",
        "duration_minutes": 60,
        "description": "Warm and funny stories before dinner.",
        "artist": "maya-choukri",
        "min_age": 0,
    }
    created = client.post("/api/programme", json=body)
    assert created.status_code == 201
    assert created.json()["title"] == "Sunset Laughs"

    stored = json.loads((tmp_path / "festival.json").read_text(encoding="utf-8"))
    assert stored["performances"][-1]["title"] == "Sunset Laughs"
