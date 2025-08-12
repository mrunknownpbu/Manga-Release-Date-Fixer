from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict
import yaml


@dataclass
class KomgaConfig:
    base_url: str
    api_key: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    page_size: int = 100


@dataclass
class MangaDexConfig:
    language: str = "en"
    delay_seconds: float = 0.5


@dataclass
class AppConfig:
    komga: KomgaConfig
    mangadex: MangaDexConfig
    series_mapping: Dict[str, str]


def load_config(path: Path) -> AppConfig:
    with open(path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    komga_raw = raw.get("komga", {})
    mangadex_raw = raw.get("mangadex", {})

    komga_cfg = KomgaConfig(
        base_url=str(komga_raw.get("base_url", "")).rstrip("/"),
        api_key=komga_raw.get("api_key"),
        username=komga_raw.get("username"),
        password=komga_raw.get("password"),
        page_size=int(komga_raw.get("page_size", 100)),
    )

    mangadex_cfg = MangaDexConfig(
        language=str(mangadex_raw.get("language", "en")),
        delay_seconds=float(mangadex_raw.get("delay_seconds", 0.5)),
    )

    series_map = raw.get("series_mapping", {}) or {}

    return AppConfig(komga=komga_cfg, mangadex=mangadex_cfg, series_mapping=series_map)


def write_default_config(path: Path) -> None:
    example = Path(__file__).resolve().parent.parent / "config.example.yaml"
    content = example.read_text(encoding="utf-8")
    path.write_text(content, encoding="utf-8")