from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class BoldScraper(BaseScraper):
    URL = "https://bold.org/scholarships/by-demographics/women/women-stem-scholarships/"

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        try:
            page.goto(self.URL, wait_until="networkidle", timeout=30000)
            # Scroll to load more results
            for _ in range(3):
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            cards = soup.select("[class*='ScholarshipCard'], [class*='scholarship-card'], article")
            for card in cards:
                title_el = card.select_one("h2, h3, h4, [class*='title'], [class*='name']")
                link_el = card.select_one("a[href]")
                if not title_el or not link_el:
                    continue

                name = title_el.get_text(strip=True)
                url = link_el["href"]
                if url.startswith("/"):
                    url = "https://bold.org" + url

                text = card.get_text(" ", strip=True)
                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|"
                    r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                    text, re.IGNORECASE
                )
                deadline_text = deadline_match.group(0) if deadline_match else "Check site"

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
