from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class ScholarshipsCanadaScraper(BaseScraper):
    URL = "https://www.scholarshipscanada.com/Scholarships/FeaturedScholarships.aspx"

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        try:
            page.goto(self.URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            cards = soup.select(".scholarship-listing, .search-result, .featured-scholarship, tr")
            for card in cards:
                link_el = card.select_one("a[href]")
                if not link_el:
                    continue

                name = link_el.get_text(strip=True)
                if not name or len(name) < 5:
                    continue

                url = link_el["href"]
                if url.startswith("/"):
                    url = "https://www.scholarshipscanada.com" + url

                text = card.get_text(" ", strip=True)
                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|"
                    r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
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
