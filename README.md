# Manga Release Date Fixer

A Komf-style dashboard for fixing manga release dates in ComicInfo.xml, with Docker support for Unraid.

## Features

- HTML dashboard (Bootstrap + JS)
- Series cover, alt titles, and links from MangaUpdates
- CBZ/CBR/ZIP/RAR support
- Extracts and fixes ComicInfo.xml dates with advanced filename parsing
- Fallbacks to file mod date if missing
- Official date fetch from MangaUpdates
- Status color coding, Fix/Batch Fix buttons
- Docker-ready, mount `/comics`, port 1996

## Usage

```bash
docker build -t manga-release-date-fixer .
docker run -it --rm -p 1996:1996 -v /your/manga:/comics manga-release-date-fixer
```

Open [http://localhost:1996](http://localhost:1996) in your browser.

---