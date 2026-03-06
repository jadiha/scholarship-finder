from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
from dateutil import parser as dp
import re

DEADLINE_PATTERN = re.compile(
    r"(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
    re.IGNORECASE,
)


class EngineersCanadaScraper(BaseScraper):
    """
    Scrapes Engineers Canada scholarship listing.
    Each card links to a detail page — we follow those links to get real deadlines.
    """
    LIST_URL = "https://engineerscanada.ca/awards-and-honours/scholarships"
    BASE = "https://engineerscanada.ca"

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        try:
            page.goto(self.LIST_URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)
            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            # Engineers Canada uses a main content area — grab links only from there
            content = soup.select_one("main, .main-content, #main, article, .content")
            if not content:
                content = soup

            # Find links that look like individual scholarship pages
            seen_urls = set()
            candidate_links = content.select("a[href*='scholarship'], a[href*='award'], a[href*='bursary']")

            for link in candidate_links:
                name = link.get_text(strip=True)
                href = link.get("href", "")

                if not name or len(name) < 10:
                    continue
                if href.startswith("/"):
                    href = self.BASE + href
                if not href.startswith("http"):
                    continue
                if href in seen_urls:
                    continue
                # Skip external links and nav links
                if "engineerscanada.ca" not in href:
                    continue
                seen_urls.add(href)

                # Visit the scholarship detail page for real deadline
                deadline_text, deadline_iso, amount_text, description = self._fetch_detail(page, href)

                scholarships.append(Scholarship(
                    name=name,
                    url=href,
                    source="Engineers Canada",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    deadline_iso=deadline_iso,
                    description=description,
                    eligibility_tags=["engineering", "canadian", "undergraduate"],
                    effort="medium",
                ))

        except Exception as e:
            print(f"[EngineersCanada] Scrape failed: {e}")

        return scholarships

    def _fetch_detail(self, page, url: str) -> tuple:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(" ", strip=True)

            deadline_match = DEADLINE_PATTERN.search(text)
            deadline_text = deadline_match.group(0) if deadline_match else "Check site"
            deadline_iso = None
            if deadline_match:
                try:
                    deadline_iso = dp.parse(deadline_match.group(0)).strftime("%Y-%m-%d")
                except Exception:
                    pass

            amount_match = re.search(r"\$[\d,]+", text)
            amount_text = amount_match.group(0) if amount_match else "See details"

            # Grab first meaningful paragraph as description
            desc_el = soup.select_one("main p, article p, .content p")
            description = desc_el.get_text(strip=True)[:250] if desc_el else ""

            return deadline_text, deadline_iso, amount_text, description

        except Exception:
            return "Check site", None, "See details", ""
