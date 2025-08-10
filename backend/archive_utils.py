import os
from datetime import datetime
from comicinfo import get_comicinfo_date, set_comicinfo_date
from filename_utils import parse_filename
from mangaupdates import get_manga_info

def scan_manga_archives(directory):
    result = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(('.cbz', '.cbr', '.zip', '.rar')):
                path = os.path.join(root, file)
                year, month, day = get_comicinfo_date(path)
                mod_time = int(os.path.getmtime(path))
                info = parse_filename(file)
                title_guess = os.path.basename(root)
                mu = get_manga_info(title_guess)
                result.append({
                    "path": path,
                    "filename": file,
                    "comicinfo_date": f"{year or ''}-{month or ''}-{day or ''}" if year else None,
                    "file_mod_date": datetime.utcfromtimestamp(mod_time).isoformat()[:10],
                    "parsed_volume": info.get("volume"),
                    "parsed_chapter": info.get("chapter"),
                    "parsed_date": info.get("date"),
                    "title": mu.get("title", title_guess),
                    "alt_titles": mu.get("alt_titles", []),
                    "cover_url": mu.get("cover_url"),
                    "series_url": mu.get("series_url"),
                    "status": status_code(year, info.get("date")),
                    "official_date": info.get("date"),
                })
    return result

def status_code(comicinfo_year, parsed_date):
    if comicinfo_year and parsed_date and str(comicinfo_year) in parsed_date:
        return "ok"
    if not comicinfo_year:
        return "missing"
    return "wrong"

def update_archive_date(archive_path, new_date):
    y, m, d = None, None, None
    if new_date:
        parts = new_date.split("-")
        if len(parts) == 3:
            y, m, d = parts
        elif len(parts) == 2:
            y, m = parts
            d = "01"
        elif len(parts) == 1:
            y = parts[0]
            m = d = "01"
    ok = set_comicinfo_date(archive_path, y, m, d)
    return {"ok": ok}

def batch_fix(directory):
    chapters = scan_manga_archives(directory)
    results = []
    for chap in chapters:
        if chap["status"] != "ok":
            date = chap["parsed_date"] or chap["file_mod_date"]
            ok = set_comicinfo_date(chap["path"], *(date.split("-")))
            results.append({"file": chap["filename"], "result": ok})
    return results