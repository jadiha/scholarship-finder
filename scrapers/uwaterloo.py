from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class UWaterlooScraper(BaseScraper):
    URL = (
        "https://uwaterloo.ca/student-awards-financial-aid/awards/database"
        "?field_award_level=undergraduate&field_award_faculty=engineering"
    )

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        try:
            page.goto(self.URL, wait_until="networkidle", timeout=30000)
            page.wait_for_selector(".views-row, article, .award", timeout=10000)
            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            rows = soup.select(".views-row, article.node, .award-item")
            for row in rows:
                title_el = row.select_one("h2, h3, .field-content a, a")
                if not title_el:
                    continue

                name = title_el.get_text(strip=True)
                if not name or len(name) < 5:
                    continue

                link_el = row.select_one("a[href]")
                url = link_el["href"] if link_el else self.URL
                if url.startswith("/"):
                    url = "https://uwaterloo.ca" + url

                text = row.get_text(" ", strip=True)
                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|"
                    r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                    text, re.IGNORECASE
                )
                deadline_text = deadline_match.group(0) if deadline_match else "Check portal"

                tags = ["engineering", "uwaterloo", "undergraduate"]
                text_lower = text.lower()
                if any(w in text_lower for w in ["female", "woman", "women"]):
                    tags.append("female")

                scholarships.append(Scholarship(
                    name=name,
                    url=url,
                    source="UWaterloo",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=tags,
                    effort="low",
                ))

        except Exception as e:
            print(f"[UWaterloo] Scrape failed: {e}")

        return scholarships
