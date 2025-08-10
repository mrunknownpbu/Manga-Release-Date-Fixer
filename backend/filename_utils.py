import re
from datetime import datetime

FILENAME_PATTERNS = [
    r'v(?P<volume>\d+)[\s_]*c(?P<chapter>\d+)',       
    r'v(?P<volume>\d+)',                              
    r'c(?P<chapter>\d+)',                             
    r'(?P<date>\d{4}[-.]\d{2}[-.]\d{2})',             
    r'(?P<date>\d{4}[-.]\d{2})',                      
    r'(?P<date>\d{4})',                               
]

def parse_filename(filename):
    info = {"volume": None, "chapter": None, "date": None}
    for pat in FILENAME_PATTERNS:
        m = re.search(pat, filename, re.IGNORECASE)
        if m:
            d = m.groupdict()
            info.update({k: v for k, v in d.items() if v is not None})
    if info["date"]:
        for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y-%m", "%Y.%m", "%Y"):
            try:
                info["date"] = datetime.strptime(info["date"], fmt).date().isoformat()
                break
            except Exception:
                continue
    return info