from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any

from fastapi import HTTPException


def slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    lowered = ascii_only.lower()
    return re.sub(r"[^a-z0-9]+", "-", lowered).strip("-")


@dataclass(slots=True)
class FestivalStore:
    path: Path
    _lock: Lock = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._lock = Lock()

    def load(self) -> dict[str, Any]:
        with self._lock:
            if not self.path.exists():
                raise HTTPException(status_code=404, detail="Festival data file not found.")
            return json.loads(self.path.read_text(encoding="utf-8"))

    def save(self, data: dict[str, Any]) -> None:
        with self._lock:
            text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            self.path.write_text(text, encoding="utf-8")


def festival_days(first_day: str, last_day: str) -> list[str]:
    start = date.fromisoformat(first_day)
    end = date.fromisoformat(last_day)
    if end < start:
        raise HTTPException(status_code=500, detail="Festival date range is invalid.")
    days: list[str] = []
    cursor = start
    while cursor <= end:
        days.append(cursor.isoformat())
        cursor += timedelta(days=1)
    return days


def venue_views(raw: dict[str, Any]) -> list[dict[str, Any]]:
    views: list[dict[str, Any]] = []
    for venue in raw.get("venues", []):
        views.append(
            {
                "slug": slugify(venue["name"]),
                "name": venue["name"],
                "capacity": venue["capacity"],
                "address": venue["address"],
            }
        )
    return views


def artist_views(raw: dict[str, Any]) -> list[dict[str, Any]]:
    artists = [
        {
            "slug": slugify(artist["name"]),
            "name": artist["name"],
            "bio": artist.get("bio", ""),
            "photo_url": artist.get("photo_url", ""),
        }
        for artist in raw.get("artists", [])
    ]
    return sorted(artists, key=lambda artist: artist["slug"])


def programme_views(raw: dict[str, Any]) -> list[dict[str, Any]]:
    venues = {venue["slug"]: venue for venue in venue_views(raw)}
    artists = {artist["slug"]: artist for artist in artist_views(raw)}

    views = [
        _performance_view(index, performance, venues, artists)
        for index, performance in enumerate(raw.get("performances", []))
    ]
    return sorted(views, key=lambda item: item["start"])


def performance_view_at(raw: dict[str, Any], index: int) -> dict[str, Any]:
    venues = {venue["slug"]: venue for venue in venue_views(raw)}
    artists = {artist["slug"]: artist for artist in artist_views(raw)}
    performances = raw.get("performances", [])
    return _performance_view(index, performances[index], venues, artists)


def _performance_view(
    index: int,
    performance: dict[str, Any],
    venues: dict[str, dict[str, Any]],
    artists: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    start = datetime.fromisoformat(performance["start"])
    item: dict[str, Any] = {
        "id": index,
        "kind": performance["kind"],
        "title": performance["title"],
        "start": performance["start"],
        "day": start.date().isoformat(),
        "time": start.strftime("%H:%M"),
        "duration_minutes": performance["duration_minutes"],
        "description": performance.get("description", ""),
        "venue_slug": performance["venue"],
        "venue_name": venues.get(performance["venue"], {}).get("name", performance["venue"]),
    }

    if performance["kind"] == "solo":
        artist_slug = performance["artist"]
        item["artist_slug"] = artist_slug
        item["artist_name"] = artists.get(artist_slug, {}).get("name", artist_slug)
        item["min_age"] = performance.get("min_age", 0)
    elif performance["kind"] == "lineup":
        host_slug = performance["host"]
        acts = performance.get("acts", [])
        item["host_slug"] = host_slug
        item["host_name"] = artists.get(host_slug, {}).get("name", host_slug)
        item["acts"] = [
            {
                "slug": act_slug,
                "name": artists.get(act_slug, {}).get("name", act_slug),
            }
            for act_slug in acts
        ]
    elif performance["kind"] == "workshop":
        teacher_slug = performance["teacher"]
        item["teacher_slug"] = teacher_slug
        item["teacher_name"] = artists.get(teacher_slug, {}).get("name", teacher_slug)
        item["max_participants"] = performance.get("max_participants", 0)
        item["participants"] = performance.get("participants", [])
    else:
        raise HTTPException(status_code=500, detail=f"Unknown performance kind: {performance['kind']}")

    return item
