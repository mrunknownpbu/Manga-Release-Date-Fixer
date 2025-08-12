from __future__ import annotations

from typing import Dict, Iterable, Optional

from .clients.komga import KomgaBook
from .sources.mangadex import MangaDexChapter


def build_chapter_number_index(chapters: Iterable[MangaDexChapter]) -> Dict[str, MangaDexChapter]:
    index: Dict[str, MangaDexChapter] = {}
    for ch in chapters:
        num = (ch.chapter_number or "").strip()
        if not num:
            continue
        # Prefer first occurrence; MangaDex may have duplicates across groups
        index.setdefault(num, ch)
    return index


def match_books_to_chapters(books: Iterable[KomgaBook], chapter_index: Dict[str, MangaDexChapter]) -> Dict[str, MangaDexChapter]:
    mapping: Dict[str, MangaDexChapter] = {}
    for book in books:
        num = (book.metadata.get("number") or book.number or "").strip()
        if not num:
            continue
        if num in chapter_index:
            mapping[book.id] = chapter_index[num]
    return mapping