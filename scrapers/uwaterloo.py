from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship


class UWaterlooScraper(BaseScraper):
    """
    Scrapes the UWaterloo undergraduate awards database filtered by
    Engineering faculty and Women affiliation.
    """
    BASE_URL = (
        "https://uwaterloo.ca/student-awards-financial-aid/awards/database"
        "?field_award_level=undergraduate"
        "&field_award_faculty=engineering"
        "&field_award_affiliation=women"
    )

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        try:
            resp = self.get(self.BASE_URL)
            soup = BeautifulSoup(resp.text, "lxml")

            # UW awards database renders each award as a row/block
            rows = soup.select(".views-row, .award-item, article.award")
            if not rows:
                # Fallback: try generic list items
                rows = soup.select("li.views-row")

            for row in rows:
                name_el = row.select_one("h3, h2, .field-content a, .views-field-title a")
                if not name_el:
                    continue

                name = name_el.get_text(strip=True)
                link_el = row.select_one("a[href]")
                url = link_el["href"] if link_el else self.BASE_URL
                if url.startswith("/"):
                    url = "https://uwaterloo.ca" + url

                amount_el = row.select_one(".field-award-value, .views-field-field-award-value")
                amount_text = amount_el.get_text(strip=True) if amount_el else "See details"

                deadline_el = row.select_one(".field-award-deadline, .views-field-field-award-deadline")
                deadline_text = deadline_el.get_text(strip=True) if deadline_el else "Check portal"

                desc_el = row.select_one(".field-body, .views-field-body")
                description = desc_el.get_text(strip=True)[:300] if desc_el else ""

                scholarships.append(Scholarship(
                    name=name,
                    url=url,
                    source="UWaterloo",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=description,
                    eligibility_tags=["female", "engineering", "uwaterloo", "undergraduate"],
                    effort="low",
                ))

        except Exception as e:
            print(f"[UWaterloo] Scrape failed: {e}")

        return scholarships
