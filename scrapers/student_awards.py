from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class StudentAwardsScraper(BaseScraper):
    """
    Scrapes studentawards.com for women + engineering scholarships in Canada.
    """
    URLS = [
        "https://studentawards.com/scholarships/engineering/",
        "https://studentawards.com/scholarships/women/",
    ]

    def scrape(self) -> list[Scholarship]:
        scholarships = []
        seen_names = set()

        for url in self.URLS:
            try:
                resp = self.get(url)
                soup = BeautifulSoup(resp.text, "lxml")

                cards = soup.select("article, .scholarship-card, .award-item, .listing")
                if not cards:
                    cards = soup.select("div[class*='award'], div[class*='scholarship']")

                for card in cards:
                    title_el = card.select_one("h2, h3, h4, .entry-title, .card-title")
                    link_el = card.select_one("a[href]")
                    if not title_el or not link_el:
                        continue

                    name = title_el.get_text(strip=True)
                    if name in seen_names:
                        continue
                    seen_names.add(name)

                    href = link_el["href"]
                    if href.startswith("/"):
                        href = "https://studentawards.com" + href

                    text = card.get_text(strip=True)
                    amount_match = re.search(r"\$[\d,]+", text)
                    amount_text = amount_match.group(0) if amount_match else "See details"

                    deadline_match = re.search(
                        r"(January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s*\d{4}",
                        text, re.IGNORECASE
                    )
                    deadline_text = deadline_match.group(0) if deadline_match else "Check site"

                    tags = ["engineering", "canadian"]
                    if "women" in url or "female" in text.lower() or "woman" in text.lower():
                        tags.append("female")

                    scholarships.append(Scholarship(
                        name=name,
                        url=href,
                        source="StudentAwards",
                        amount_text=amount_text,
                        deadline_text=deadline_text,
                        description=text[:250],
                        eligibility_tags=tags,
                        effort="medium",
                    ))

            except Exception as e:
                print(f"[StudentAwards] Scrape failed for {url}: {e}")

        return scholarships
