import json
import os
import yaml
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from scrapers.uwaterloo import UWaterlooScraper
from scrapers.uwaterloo_engineering import UWaterlooEngineeringScraper
from scrapers.onwie import ONWiEScraper
from scrapers.engineers_canada import EngineersCanadaScraper
from scrapers.womeninengtech import WomenInEngTechScraper
from scrapers.scholars_canada import ScholarshipsCanadaScraper
from scrapers.student_awards import StudentAwardsScraper
from scrapers.corporate import CorporateScraper
from scrapers.bold import BoldScraper
from filters import filter_and_score
from notifier import post_to_discord, generate_dashboard

load_dotenv()

SEEN_PATH = "seen.json"


def load_config() -> dict:
    with open("config.yaml") as f:
        return yaml.safe_load(f)


def load_seen() -> set:
    if not os.path.exists(SEEN_PATH):
        return set()
    with open(SEEN_PATH) as f:
        return set(json.load(f))


def save_seen(seen: set):
    with open(SEEN_PATH, "w") as f:
        json.dump(sorted(seen), f, indent=2)


def main():
    config = load_config()
    seen = load_seen()

    scrapers = [
        UWaterlooScraper(config),
        UWaterlooEngineeringScraper(config),
        ONWiEScraper(config),
        EngineersCanadaScraper(config),
        WomenInEngTechScraper(config),
        ScholarshipsCanadaScraper(config),
        StudentAwardsScraper(config),
        CorporateScraper(config),
        BoldScraper(config),
    ]

    all_raw = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        for scraper in scrapers:
            name = scraper.__class__.__name__
            # CorporateScraper doesn't need a browser page
            if isinstance(scraper, CorporateScraper):
                results = scraper.scrape(page=None)
            else:
                results = scraper.scrape(page)
            print(f"  [{name}] found {len(results)}")
            all_raw.extend(results)

        browser.close()

    print(f"Total raw: {len(all_raw)}")

    eligible = filter_and_score(all_raw, config)
    print(f"Eligible after filtering: {len(eligible)}")

    new = [s for s in eligible if s.id not in seen]
    print(f"New (not yet notified): {len(new)}")

    if new and config.get("notifications", {}).get("discord"):
        webhook = os.environ.get("DISCORD_WEBHOOK_URL")
        if webhook:
            post_to_discord(new, webhook)
            print(f"[Discord] Posted {len(new)} scholarships")
        else:
            print("[Discord] DISCORD_WEBHOOK_URL not set — skipping")

    if config.get("notifications", {}).get("github_pages"):
        generate_dashboard(eligible)

    for s in new:
        seen.add(s.id)
    save_seen(seen)

    print("Done.")


if __name__ == "__main__":
    main()
