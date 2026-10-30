from __future__ import annotations

from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from festival_site import (
    FestivalStore,
    artist_views,
    festival_days,
    performance_view_at,
    programme_views,
    venue_views,
)


class PerformanceIn(BaseModel):
    kind: Literal["solo", "lineup", "workshop"]
    title: str = Field(min_length=2, max_length=120)
    venue: str = Field(min_length=2, max_length=120)
    start: str = Field(min_length=16, max_length=32, description="ISO date time (YYYY-MM-DDTHH:MM)")
    duration_minutes: int = Field(ge=15, le=360)
    description: str = Field(default="", max_length=500)
    artist: str | None = None
    host: str | None = None
    acts: list[str] | None = None
    teacher: str | None = None
    max_participants: int | None = Field(default=None, ge=1, le=200)
    participants: list[str] | None = None
    min_age: int | None = Field(default=None, ge=0, le=21)


def create_app(data_path: Path, static_path: Path | None = None) -> FastAPI:
    app = FastAPI(title="Festival Website API", version="1.0.0")
    store = FestivalStore(data_path)

    def ensure_performance_shape(body: PerformanceIn) -> dict:
        payload = body.model_dump(exclude_none=True)

        if body.kind == "solo":
            if not body.artist:
                raise HTTPException(
                    status_code=422, detail="A solo performance requires 'artist'."
                )
            payload.setdefault("min_age", 0)
            payload.pop("host", None)
            payload.pop("acts", None)
            payload.pop("teacher", None)
            payload.pop("max_participants", None)
            payload.pop("participants", None)
        elif body.kind == "lineup":
            if not body.host:
                raise HTTPException(
                    status_code=422, detail="A lineup requires 'host'."
                )
            if not body.acts:
                raise HTTPException(
                    status_code=422, detail="A lineup requires at least one act."
                )
            payload.pop("artist", None)
            payload.pop("teacher", None)
            payload.pop("max_participants", None)
            payload.pop("participants", None)
            payload.pop("min_age", None)
        elif body.kind == "workshop":
            if not body.teacher:
                raise HTTPException(
                    status_code=422, detail="A workshop requires 'teacher'."
                )
            if body.max_participants is None:
                raise HTTPException(
                    status_code=422,
                    detail="A workshop requires 'max_participants'.",
                )
            payload.setdefault("participants", [])
            payload.pop("artist", None)
            payload.pop("host", None)
            payload.pop("acts", None)
            payload.pop("min_age", None)

        return payload

    @app.get("/api/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/api/festival")
    def get_festival() -> dict:
        raw = store.load()
        return {
            "name": raw["name"],
            "first_day": raw["first_day"],
            "last_day": raw["last_day"],
            "days": festival_days(raw["first_day"], raw["last_day"]),
        }

    @app.get("/api/venues")
    def get_venues() -> list[dict]:
        return venue_views(store.load())

    @app.get("/api/artists")
    def get_artists() -> list[dict]:
        return artist_views(store.load())

    @app.get("/api/programme")
    def get_programme(
        day: str | None = Query(default=None, description="YYYY-MM-DD"),
        venue: str | None = Query(default=None, description="Venue slug"),
    ) -> list[dict]:
        items = programme_views(store.load())
        if day:
            items = [item for item in items if item["day"] == day]
        if venue:
            items = [item for item in items if item["venue_slug"] == venue]
        return items

    @app.post("/api/programme", status_code=201)
    def add_programme(body: PerformanceIn) -> dict:
        raw = store.load()
        payload = ensure_performance_shape(body)
        raw["performances"].append(payload)
        store.save(raw)
        return performance_view_at(raw, len(raw["performances"]) - 1)

    if static_path is not None:
        app.mount("/", StaticFiles(directory=static_path, html=True), name="web")

    return app


app = create_app(Path("data/festival.json"), Path("web/public"))
