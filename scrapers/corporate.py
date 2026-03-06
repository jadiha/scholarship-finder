from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


# Corporate scholarships that post annually for women in engineering/tech.
# These are scraped directly from their program pages.

CORPORATE_SOURCES = [
    {
        "name": "Google Generation Scholarship",
        "url": "https://buildyourfuture.withgoogle.com/scholarships/generation-google-scholarship-emea",
        "amount_text": "$10,000 USD",
        "amount_min": 13000,
        "tags": ["female", "engineering", "stem", "canadian"],
        "effort": "high",
        "notes": "Essay + academic transcript required",
    },
    {
        "name": "Shopify Women in Tech Scholarship",
        "url": "https://www.shopify.com/careers/scholarships",
        "amount_text": "$5,000",
        "amount_min": 5000,
        "tags": ["female", "engineering", "canadian", "tech"],
        "effort": "medium",
        "notes": "Essay on impact in tech",
    },
    {
        "name": "RBC Future Launch STEM Scholarship",
        "url": "https://www.rbcroyalbank.com/dms/business/student/rbc-future-launch/index.html",
        "amount_text": "$2,500",
        "amount_min": 2500,
        "tags": ["engineering", "canadian", "stem"],
        "effort": "low",
        "notes": "Open to all Canadian STEM students",
    },
    {
        "name": "TD Scholarships for Community Leadership",
        "url": "https://www.td.com/ca/en/personal-banking/solutions/student-centre/td-scholarship/",
        "amount_text": "$70,000 (over 4 years)",
        "amount_min": 70000,
        "tags": ["canadian", "leadership"],
        "effort": "high",
        "notes": "Leadership focus, renewable, highly competitive",
    },
    {
        "name": "Scotiabank Women Initiative Scholarship",
        "url": "https://www.scotiabank.com/ca/en/personal/chequing-savings/student-banking/scholarships.html",
        "amount_text": "$5,000",
        "amount_min": 5000,
        "tags": ["female", "canadian", "stem"],
        "effort": "medium",
        "notes": "Women in STEM, check deadline annually",
    },
    {
        "name": "Microsoft Scholarship Program",
        "url": "https://careers.microsoft.com/students/us/en/usscholarshipprogram",
        "amount_text": "$5,000 USD",
        "amount_min": 6500,
        "tags": ["female", "engineering", "stem", "tech"],
        "effort": "high",
        "notes": "Essay + interview process",
    },
    {
        "name": "Fortis Inc. Women in Engineering Award",
        "url": "https://www.fortisinc.com/community/scholarships",
        "amount_text": "$5,000",
        "amount_min": 5000,
        "tags": ["female", "engineering", "canadian"],
        "effort": "medium",
        "notes": "Includes potential summer work placement after 2nd/3rd year",
    },
    {
        "name": "De Beers Group Scholarship for Women in STEM",
        "url": "https://www.debeersgroup.com/building-forever/partnerships/scholarships",
        "amount_text": "Varies",
        "amount_min": 0,
        "tags": ["female", "stem", "canadian"],
        "effort": "medium",
        "notes": "14 new scholarships awarded annually to Canadian women in STEM",
    },
]


class CorporateScraper(BaseScraper):
    """
    Returns a curated list of corporate scholarships for women in engineering.
    These are static entries (no scraping needed — pages rarely change structure).
    Live deadline info is checked via a lightweight page fetch where possible.
    """

    def scrape(self, page=None) -> list[Scholarship]:
        scholarships = []

        for entry in CORPORATE_SOURCES:
            deadline_text, deadline_iso = self._try_fetch_deadline(entry["url"])

            scholarships.append(Scholarship(
                name=entry["name"],
                url=entry["url"],
                source="Corporate",
                amount_text=entry["amount_text"],
                amount_min=entry["amount_min"],
                deadline_text=deadline_text,
                deadline_iso=deadline_iso,
                eligibility_tags=entry["tags"],
                effort=entry["effort"],
                notes=entry.get("notes", ""),
            ))

        return scholarships

    def _try_fetch_deadline(self, url: str) -> tuple:
        """Best-effort: fetch the page and look for a deadline date."""
        try:
            resp = self.get(url)
            soup = BeautifulSoup(resp.text, "lxml")
            text = soup.get_text(" ", strip=True)

            match = re.search(
                r"(January|February|March|April|May|June|July|August|September|October|November|December)"
                r"\s+\d{1,2},?\s*\d{4}",
                text, re.IGNORECASE
            )
            if match:
                from dateutil import parser as dp
                dt = dp.parse(match.group(0))
                return match.group(0), dt.strftime("%Y-%m-%d")
        except Exception:
            pass

        return "Check site annually", None
