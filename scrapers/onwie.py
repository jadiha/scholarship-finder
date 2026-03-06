from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class ONWiEScraper(BaseScraper):
    """
    Scrapes the Ontario Network of Women in Engineering scholarship listings.
    https://www.onwie.ca/resource-tools/scholarships-and-opportunities/
    """
    URL = "https://www.onwie.ca/resource-tools/scholarships-and-opportunities/"

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        try:
            resp = self.get(self.URL)
            soup = BeautifulSoup(resp.text, "lxml")

            entries = soup.select(".entry-content li, .scholarship-item, article, .wp-block-group")
            if not entries:
                entries = soup.select("li")

            for entry in entries:
                text = entry.get_text(strip=True)
                if len(text) < 20:
                    continue

                link_el = entry.select_one("a[href]")
                if not link_el:
                    continue

                name = link_el.get_text(strip=True)
                url = link_el["href"]

                # Try to extract amount from text
                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                # Try to extract deadline
                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                    text, re.IGNORECASE
                )
                deadline_text = deadline_match.group(0) if deadline_match else "Check site"

                scholarships.append(Scholarship(
                    name=name,
                    url=url,
                    source="ONWiE",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=["female", "engineering", "ontario", "canadian"],
                    effort="medium",
                ))

        except Exception as e:
            print(f"[ONWiE] Scrape failed: {e}")

        return scholarships
