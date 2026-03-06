from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class UWaterlooEngineeringScraper(BaseScraper):
    URL = "https://uwaterloo.ca/engineering/undergraduate-students/scholarships-and-awards"

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        seen_names = set()
        try:
            page.goto(self.URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            content = soup.select_one(".field-items, .layout-container, main, article")
            items = (content or soup).select("li, .views-row, .award-item, p")

            for item in items:
                link_el = item.select_one("a[href]")
                if not link_el:
                    continue

                name = link_el.get_text(strip=True)
                if not name or len(name) < 5 or name in seen_names:
                    continue
                seen_names.add(name)

                url = link_el["href"]
                if url.startswith("/"):
                    url = "https://uwaterloo.ca" + url

                text = item.get_text(" ", strip=True)
                amount_match = re.search(r"\$[\d,]+", text)
                amount_text = amount_match.group(0) if amount_match else "See details"

                deadline_match = re.search(
                    r"(January|February|March|April|May|June|July|August|"
                    r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                    text, re.IGNORECASE
                )
                deadline_text = deadline_match.group(0) if deadline_match else "Check portal"

                tags = ["engineering", "uwaterloo", "undergraduate"]
                if any(w in text.lower() for w in ["female", "woman", "women"]):
                    tags.append("female")

                scholarships.append(Scholarship(
                    name=name,
                    url=url,
                    source="UWaterloo Engineering",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text[:250],
                    eligibility_tags=tags,
                    effort="low",
                ))

        except Exception as e:
            print(f"[UWaterloo Engineering] Scrape failed: {e}")

        return scholarships
