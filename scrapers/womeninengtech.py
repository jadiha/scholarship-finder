from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class WomenInEngTechScraper(BaseScraper):
    """
    Scrapes Women in Engineering and Technology scholarship listings.
    https://womeninengtech.ca/timeline-category/stem-scholarships-and-bursaries/
    """
    URL = "https://womeninengtech.ca/timeline-category/stem-scholarships-and-bursaries/"

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        try:
            resp = self.get(self.URL)
            soup = BeautifulSoup(resp.text, "lxml")

            entries = soup.select("article, .entry, .timeline-item, .post")
            if not entries:
                entries = soup.select(".jet-listing-grid__item")

            for entry in entries:
                title_el = entry.select_one("h1, h2, h3, h4, .entry-title")
                link_el = entry.select_one("a[href]")
                if not title_el or not link_el:
                    continue

                name = title_el.get_text(strip=True)
                url = link_el["href"]
                text = entry.get_text(strip=True)

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
                    source="WomenInEngTech",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=["female", "engineering", "stem", "canadian"],
                    effort="medium",
                ))

        except Exception as e:
            print(f"[WomenInEngTech] Scrape failed: {e}")

        return scholarships
