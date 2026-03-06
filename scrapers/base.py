from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import hashlib
import requests


@dataclass
class Scholarship:
    name: str
    url: str
    source: str
    amount_text: str = "Unknown"
    amount_min: int = 0
    deadline_text: str = "Unknown"
    deadline_iso: Optional[str] = None  # YYYY-MM-DD
    description: str = ""
    eligibility_tags: list = field(default_factory=list)
    notes: str = ""
    renewable: bool = False
    effort: str = "medium"  # low / medium / high
    score: int = 0

    @property
    def id(self) -> str:
        return hashlib.md5(f"{self.name}{self.url}".encode()).hexdigest()[:12]


class BaseScraper(ABC):
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def scrape(self) -> list[Scholarship]:
        pass

    def get(self, url: str, **kwargs) -> requests.Response:
        resp = requests.get(url, headers=self.HEADERS, timeout=15, **kwargs)
        resp.raise_for_status()
        return resp
