from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import hashlib


@dataclass
class Scholarship:
    name: str
    url: str
    source: str
    amount_text: str = "Unknown"
    amount_min: int = 0
    deadline_text: str = "Unknown"
    deadline_iso: Optional[str] = None
    description: str = ""
    eligibility_tags: list = field(default_factory=list)
    notes: str = ""
    renewable: bool = False
    effort: str = "medium"
    score: int = 0

    @property
    def id(self) -> str:
        return hashlib.md5(f"{self.name}{self.url}".encode()).hexdigest()[:12]


class BaseScraper(ABC):
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def scrape(self, page) -> list[Scholarship]:
        """page is a Playwright page object"""
        pass
