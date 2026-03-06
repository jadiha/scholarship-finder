from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class BoldScraper(BaseScraper):
    """
    Scrapes Bold.org for women in STEM scholarships open to Canadians.
    https://bold.org/scholarships/by-demographics/women/women-stem-scholarships/
    """
    URL = "https://bold.org/scholarships/by-demographics/women/women-stem-scholarships/"

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        try:
            resp = self.get(self.URL)
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select(
                ".scholarship-card, .ScholarshipCard, article, "
                "[class*='ScholarshipCard'], [class*='scholarship-card']"
            )

            for card in cards:
                title_el = card.select_one("h2, h3, h4, [class*='title'], [class*='name']")
                link_el = card.select_one("a[href]")
                if not title_el or not link_el:
                    continue

                name = title_el.get_text(strip=True)
                url = link_el["href"]
                if url.startswith("/"):
                    url = "https://bold.org" + url

                text = card.get_text(strip=True)

                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                    text, re.IGNORECASE
                )
                deadline_text = deadline_match.group(0) if deadline_match else "Check site"

                # Bold has many US-only scholarships — flag for filter
                is_canada_ok = any(w in text.lower() for w in ["canada", "international", "worldwide", "any country"])
                tags = ["female", "stem"]
                if is_canada_ok:
                    tags.append("canadian")

                scholarships.append(Scholarship(
                    name=name,
                    url=url,
                    source="Bold.org",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=tags,
                    effort="low",
                ))

        except Exception as e:
            print(f"[Bold.org] Scrape failed: {e}")

        return scholarships
