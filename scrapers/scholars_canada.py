from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class ScholarshipsCanadaScraper(BaseScraper):
    """
    Scrapes scholarshipscanada.com — largest Canadian scholarship aggregator.
    Filters by engineering + female.
    """
    URL = "https://www.scholarshipscanada.com/Scholarships/ScholarshipSearch.aspx?field=engineering&gender=female&citizenship=canadian"

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        try:
            resp = self.get(self.URL)
            soup = BeautifulSoup(resp.text, "lxml")

            cards = soup.select(".scholarship-listing, .search-result-item, .scholarship-item, .listing-item")
            if not cards:
                cards = soup.select("div[class*='scholarship']")

            for card in cards:
                title_el = card.select_one("h2, h3, h4, .title, a.scholarship-title")
                link_el = card.select_one("a[href]")
                if not title_el or not link_el:
                    continue

                name = title_el.get_text(strip=True)
                url = link_el["href"]
                if url.startswith("/"):
                    url = "https://www.scholarshipscanada.com" + url

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
                    source="ScholarshipsCanada",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=["engineering", "canadian"],
                    effort="medium",
                ))

        except Exception as e:
            print(f"[ScholarshipsCanada] Scrape failed: {e}")

        return scholarships
