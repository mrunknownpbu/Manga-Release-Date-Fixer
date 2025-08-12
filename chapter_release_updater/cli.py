from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint

from .config import load_config, write_default_config
from .clients.komga import KomgaClient
from .sources.mangadex import MangaDex
from .matching import build_chapter_number_index, match_books_to_chapters
from .utils import parse_mangadex_datetime_to_date, ensure_date_str

app = typer.Typer(add_completion=False)


@app.command()
def init_config(path: str = typer.Option("config.yaml", help="Path to write config to")):
    cfg_path = Path(path)
    if cfg_path.exists():
        rprint(f"[yellow]Config already exists at {cfg_path}. Overwriting.[/yellow]")
    write_default_config(cfg_path)
    rprint(f"[green]Wrote example config to {cfg_path}[/green]")


@app.command()
def update(
    target: str = typer.Argument(..., help="Target server: 'komga'"),
    series_id: str = typer.Option(..., "--series-id", help="Komga series ID"),
    mangadex_id: Optional[str] = typer.Option(None, "--mangadex-id", help="MangaDex manga ID"),
    language: Optional[str] = typer.Option(None, "--language", help="MangaDex language, e.g., en, ja, es"),
    config: str = typer.Option("config.yaml", "--config", help="Path to config.yaml"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Do not perform writes"),
    lock: bool = typer.Option(False, "--lock", help="Lock releaseDate after setting"),
):
    if target.lower() != "komga":
        rprint("[red]Only 'komga' target is currently implemented.[/red]")
        raise typer.Exit(code=2)

    cfg = load_config(Path(config))
    md_lang = language or cfg.mangadex.language

    # Resolve MangaDex ID
    if not mangadex_id:
        # try from series_mapping
        mangadex_id = cfg.series_mapping.get(series_id)
        if not mangadex_id:
            rprint("[red]MangaDex ID is required (via --mangadex-id or config series_mapping).[/red]")
            raise typer.Exit(code=2)

    komga = KomgaClient(
        base_url=cfg.komga.base_url,
        api_key=cfg.komga.api_key,
        username=cfg.komga.username,
        password=cfg.komga.password,
        page_size=cfg.komga.page_size,
    )
    mangadex = MangaDex(language=md_lang, delay_seconds=cfg.mangadex.delay_seconds)

    rprint(f"[bold]Fetching Komga books for series[/bold] {series_id} ...")
    books = komga.get_series_books(series_id)

    rprint(f"[bold]Fetching MangaDex chapters[/bold] for manga {mangadex_id} ...")
    chapters = mangadex.get_manga_chapters(mangadex_id)

    index = build_chapter_number_index(chapters)
    mapping = match_books_to_chapters(books, index)

    updated = 0
    skipped = 0

    for book in books:
        ch = mapping.get(book.id)
        if not ch:
            skipped += 1
            continue
        source_date = parse_mangadex_datetime_to_date(ch.publish_at) or parse_mangadex_datetime_to_date(ch.readable_at)
        if not source_date:
            skipped += 1
            continue
        source_date_str = ensure_date_str(source_date)
        current_date = (book.metadata or {}).get("releaseDate")
        if current_date == source_date_str:
            skipped += 1
            continue
        rprint(f"Will set book {book.id} number={book.metadata.get('number')} date {current_date} -> {source_date_str}")
        if not dry_run:
            komga.update_book_release_date(book.id, source_date_str, lock=lock)
            updated += 1

    rprint(f"[green]Done. Updated: {updated}, Skipped: {skipped}, Total books: {len(books)}[/green]")


if __name__ == "__main__":
    app()