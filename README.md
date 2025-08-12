# Chapter Release Date Updater

A minimal CLI tool inspired by `komf` that updates chapter (book) release dates in Komga, using MangaDex as the source. Designed to be extensible for Kavita and more sources later.

## Features
- Fetch chapter release dates from MangaDex.
- Match chapters by chapter number.
- Update Komga book `releaseDate` via API.
- Dry-run mode to preview updates.

## Requirements
- Python 3.10+

## Setup
```bash
cd /workspace
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration
Copy the example config:
```bash
cp config.example.yaml config.yaml
```
Edit `config.yaml` and fill in your Komga base URL and API key.

## Usage
- Update a single Komga series using a known MangaDex ID:
```bash
python -m chapter_release_updater.cli update komga --series-id <KOMGA_SERIES_ID> \
  --mangadex-id <MANGADEX_MANGA_ID> --language en --dry-run
```
Remove `--dry-run` to apply changes. Add `--lock` to lock `releaseDate` after setting.

- Bootstrap a config file:
```bash
python -m chapter_release_updater.cli init-config --path config.yaml
```

## Notes
- For Komga, the tool calls `PATCH /api/books/{bookId}/metadata` with `{"releaseDate": "YYYY-MM-DD", "lockReleaseDate": true|false}` when applying updates.
- For MangaDex, the tool uses chapter `publishAt` as the source date, falling back to `readableAt` if missing.

## Roadmap
- Add Kavita client (write support pending in API).
- Additional sources and smarter title-based matching.