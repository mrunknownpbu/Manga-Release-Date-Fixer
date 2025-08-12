from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional
import time
import requests


API_BASE = "https://api.mangadex.org"


@dataclass
class MangaDexChapter:
    id: str
    chapter_number: Optional[str]
    title: Optional[str]
    publish_at: Optional[str]
    readable_at: Optional[str]


class MangaDex:
    def __init__(self, language: str = "en", delay_seconds: float = 0.5):
        self.language = language
        self.delay_seconds = delay_seconds
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def get_manga_chapters(self, manga_id: str) -> List[MangaDexChapter]:
        # GET /chapter?manga=<id>&translatedLanguage[]=en&order[chapter]=asc&limit=100&includes[]=scanlation_group
        chapters: List[MangaDexChapter] = []
        offset = 0
        limit = 100
        while True:
            params = {
                "manga": manga_id,
                "translatedLanguage[]": self.language,
                "order[chapter]": "asc",
                "limit": limit,
                "offset": offset,
            }
            resp = self.session.get(f"{API_BASE}/chapter", params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            for itm in data.get("data", []):
                attr = itm.get("attributes", {})
                chapters.append(MangaDexChapter(
                    id=itm.get("id"),
                    chapter_number=attr.get("chapter"),
                    title=attr.get("title"),
                    publish_at=attr.get("publishAt"),
                    readable_at=attr.get("readableAt"),
                ))
            total = data.get("total", 0)
            offset += limit
            if offset >= total:
                break
            if self.delay_seconds:
                time.sleep(self.delay_seconds)
        return chapters