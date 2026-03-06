from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class UWaterlooEngineeringScraper(BaseScraper):
    """
    Scrapes the UWaterloo Engineering faculty scholarships page — separate from
    the general awards database and often has faculty-specific awards.
    """
    URLS = [
        "https://uwaterloo.ca/engineering/undergraduate-students/scholarships-and-awards",
        "https://uwaterloo.ca/student-awards-financial-aid/awards/database"
        "?field_award_level=undergraduate&field_award_faculty=engineering",
    ]

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        seen_names = set()

        for url in self.URLS:
            try:
                resp = self.get(url)
                soup = BeautifulSoup(resp.text, "lxml")

                # Try multiple selector patterns UW Drupal sites use
                sections = soup.select(
                    ".field-items li, .award-item, .views-row, "
                    "article, .uw-contained-width li"
                )

                for section in sections:
                    text = section.get_text(strip=True)
                    if len(text) < 30:
                        continue

                    link_el = section.select_one("a[href]")
                    title_el = section.select_one("h2, h3, h4, strong, b")

                    name = None
                    if title_el:
                        name = title_el.get_text(strip=True)
                    elif link_el:
                        name = link_el.get_text(strip=True)

                    if not name or name in seen_names or len(name) < 5:
                        continue
                    seen_names.add(name)

                    href = link_el["href"] if link_el else url
                    if href.startswith("/"):
                        href = "https://uwaterloo.ca" + href

                    amount_match = re.search(r"\$[\d,]+", text)
                    amount_text = amount_match.group(0) if amount_match else "See details"

                    deadline_match = re.search(
                        r"(January|February|March|April|May|June|July|August|"
                        r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                        text, re.IGNORECASE
                    )
                    deadline_text = deadline_match.group(0) if deadline_match else "Check portal"

                    # Tag female-specific if mentioned
                    tags = ["engineering", "uwaterloo", "undergraduate"]
                    text_lower = text.lower()
                    if any(w in text_lower for w in ["female", "woman", "women", "girl"]):
                        tags.append("female")

                    scholarships.append(Scholarship(
                        name=name,
                        url=href,
                        source="UWaterloo Engineering",
                        amount_text=amount_text,
                        deadline_text=deadline_text,
                        description=text[:250],
                        eligibility_tags=tags,
                        effort="low",
                    ))

            except Exception as e:
                print(f"[UWaterloo Engineering] Scrape failed for {url}: {e}")

        return scholarships
