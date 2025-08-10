import requests

SEARCH_URL = 'https://api.mangaupdates.com/v1/series/search'
SERIES_URL = 'https://api.mangaupdates.com/v1/series/'

def get_manga_info(title):
    resp = requests.post(SEARCH_URL, json={"search": title})
    if resp.status_code != 200:
        return {}
    results = resp.json().get("results", [])
    if not results:
        return {}
    s = results[0]
    series_id = s.get("series_id")
    url = SERIES_URL + str(series_id)
    meta = requests.get(url).json()
    return {
        "series_id": series_id,
        "title": meta.get("title"),
        "alt_titles": meta.get("aka", []),
        "cover_url": meta.get("cover"),
        "series_url": f"https://www.mangaupdates.com/series.html?id={series_id}"
    }