from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class EngineersCanadaScraper(BaseScraper):
    """
    Scrapes Engineers Canada scholarship listings.
    https://engineerscanada.ca/awards-and-honours/scholarships
    """
    URL = "https://engineerscanada.ca/awards-and-honours/scholarships"

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        try:
            resp = self.get(self.URL)
            soup = BeautifulSoup(resp.text, "lxml")

            # Engineers Canada renders awards as cards or list items
            cards = soup.select(".award-card, .scholarship-item, .views-row, article")
            if not cards:
                cards = soup.select("li")

            for card in cards:
                link_el = card.select_one("a[href]")
                if not link_el:
                    continue

                name = link_el.get_text(strip=True)
                if not name or len(name) < 5:
                    continue

                url = link_el["href"]
                if url.startswith("/"):
                    url = "https://engineerscanada.ca" + url

                text = card.get_text(strip=True)

                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                    text, re.IGNORECASE
                )
                deadline_text = deadline_match.group(0) if deadline_match else "Check site"

                scholarships.append(Scholarship(
                    name=name,
                    url=url,
                    source="Engineers Canada",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=["engineering", "canadian", "undergraduate"],
                    effort="medium",
                ))

        except Exception as e:
            print(f"[EngineersCanada] Scrape failed: {e}")

        return scholarships
