from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional
import time
import requests


@dataclass
class KomgaBook:
    id: str
    series_id: str
    number: Optional[str]
    number_sort: Optional[float]
    metadata: Dict


class KomgaClient:
    def __init__(self, base_url: str, api_key: Optional[str] = None,
                 username: Optional[str] = None, password: Optional[str] = None,
                 page_size: int = 100):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.page_size = page_size
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})
        elif username and password:
            self.session.auth = (username, password)
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, path: str) -> str:
        if not path.startswith('/'):
            path = '/' + path
        return f"{self.base_url}{path}"

    def get_series_books(self, series_id: str) -> List[KomgaBook]:
        # Komga pagination: /api/series/{seriesId}/books?page=0&size=N
        books: List[KomgaBook] = []
        page = 0
        while True:
            resp = self.session.get(
                self._url(f"/api/series/{series_id}/books"),
                params={"page": page, "size": self.page_size},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", [])
            for b in content:
                books.append(
                    KomgaBook(
                        id=b["id"],
                        series_id=series_id,
                        number=b.get("metadata", {}).get("number"),
                        number_sort=b.get("metadata", {}).get("numberSort"),
                        metadata=b.get("metadata", {}),
                    )
                )
            if data.get("last", True):
                break
            page += 1
        return books

    def update_book_release_date(self, book_id: str, release_date: str, lock: bool = False) -> None:
        # PATCH /api/books/{bookId}/metadata
        payload = {
            "releaseDate": release_date,
            "lockReleaseDate": bool(lock),
        }
        resp = self.session.patch(self._url(f"/api/books/{book_id}/metadata"), json=payload, timeout=30)
        if resp.status_code >= 400:
            raise requests.HTTPError(f"Komga update failed: {resp.status_code} {resp.text}")

    def get_series(self, series_id: str) -> Dict:
        resp = self.session.get(self._url(f"/api/series/{series_id}"), timeout=30)
        resp.raise_for_status()
        return resp.json()