from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship
import re


class ONWiEScraper(BaseScraper):
    URL = "https://www.onwie.ca/resource-tools/scholarships-and-opportunities/"

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        try:
            page.goto(self.URL, wait_until="networkidle", timeout=30000)
            page.wait_for_timeout(2000)

            html = page.content()
            soup = BeautifulSoup(html, "lxml")

            # ONWiE is a WordPress site — entries are in the content area
            content = soup.select_one(".entry-content, .page-content, main")
            if not content:
                content = soup

            links = content.select("a[href]")
            seen = set()
            for link in links:
                name = link.get_text(strip=True)
                url = link["href"]

                if not name or len(name) < 10 or url in seen:
                    continue
                if not url.startswith("http"):
                    continue
                # Skip nav/footer links
                if any(skip in url for skip in ["onwie.ca/about", "onwie.ca/programs", "onwie.ca/contact"]):
                    continue

                seen.add(url)
                parent_text = link.parent.get_text(" ", strip=True) if link.parent else ""
                text = parent_text[:300]

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
                    source="ONWiE",
                    amount_text=amount_text,
                    deadline_text=deadline_text,
                    description=text,
                    eligibility_tags=["female", "engineering", "ontario", "canadian"],
                    effort="medium",
                ))

        except Exception as e:
            print(f"[ONWiE] Scrape failed: {e}")

        return scholarships
