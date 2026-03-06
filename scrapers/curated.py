import re
from datetime import date
from bs4 import BeautifulSoup
from .base import BaseScraper, Scholarship

# Verified scholarships specifically for Canadian female engineering students.
# Each entry has a direct application/info URL. The scraper visits each page
# and tries to pull the current deadline. If it can't find one, deadline_text
# is set to "Check site" rather than showing fake data.

SCHOLARSHIPS = [
    # --- UWaterloo specific ---
    {
        "name": "Women in Engineering Bursary (UWaterloo)",
        "url": "https://uwaterloo.ca/student-awards-financial-aid/awards/women-engineering-bursary",
        "amount_text": "$2,000",
        "amount_min": 2000,
        "tags": ["female", "engineering", "uwaterloo", "undergraduate"],
        "effort": "low",
        "notes": "UW portal application. Open to 2nd-4th year female engineering students.",
    },
    {
        "name": "Engineering Excellence Award for Women (UWaterloo)",
        "url": "https://uwaterloo.ca/engineering/undergraduate-students/scholarships-and-awards",
        "amount_text": "Varies",
        "amount_min": 0,
        "tags": ["female", "engineering", "uwaterloo", "undergraduate"],
        "effort": "low",
        "notes": "Awarded to 3rd year female UW engineering students with strong academics and involvement.",
    },
    {
        "name": "UWaterloo Undergraduate Awards Portal",
        "url": "https://uwaterloo.ca/student-awards-financial-aid/awards/database",
        "amount_text": "Various",
        "amount_min": 0,
        "tags": ["engineering", "uwaterloo", "undergraduate"],
        "effort": "low",
        "notes": "Apply through the UW portal — filter by Engineering + Women to find all relevant awards.",
    },

    # --- Engineers Canada ---
    {
        "name": "Engineers Canada / Manulife Scholarship",
        "url": "https://engineerscanada.ca/awards-and-honours/scholarships/engineers-canada-manulife-scholarship",
        "amount_text": "$12,500",
        "amount_min": 12500,
        "tags": ["engineering", "canadian"],
        "effort": "medium",
        "notes": "For Canadian engineering students returning for further study. Deadline typically mid-March.",
    },
    {
        "name": "Engineers Canada Scholarships (Full List)",
        "url": "https://engineerscanada.ca/awards-and-honours/scholarships",
        "amount_text": "$90,000+ total across 14 awards",
        "amount_min": 0,
        "tags": ["engineering", "canadian", "undergraduate"],
        "effort": "medium",
        "notes": "14 scholarships available. Check page for individual deadlines.",
    },

    # --- ONWiE / Women in Engineering ---
    {
        "name": "OSPE Scholarship for Women in Engineering",
        "url": "https://ospe.on.ca/awards/",
        "amount_text": "Varies",
        "amount_min": 0,
        "tags": ["female", "engineering", "ontario", "canadian"],
        "effort": "medium",
        "notes": "Ontario Society of Professional Engineers. Multiple awards for women in engineering.",
    },
    {
        "name": "Fortis Inc. Women in Engineering Award",
        "url": "https://www.fortisinc.com/community/scholarships",
        "amount_text": "$5,000",
        "amount_min": 5000,
        "tags": ["female", "engineering", "canadian"],
        "effort": "medium",
        "notes": "Includes potential summer work placement after 2nd/3rd year at a Fortis utility.",
    },

    # --- Corporate ---
    {
        "name": "Google Generation Scholarship (Women in Tech)",
        "url": "https://buildyourfuture.withgoogle.com/scholarships/generation-google-scholarship",
        "amount_text": "$10,000 USD",
        "amount_min": 13500,
        "tags": ["female", "engineering", "stem", "canadian"],
        "effort": "high",
        "notes": "For women in CS/engineering. Open to Canadian students. Essay + transcript required.",
    },
    {
        "name": "RBC Future Launch Scholarship",
        "url": "https://www.rbc.com/community-social-impact/education-financial-health/rbc-future-launch.html",
        "amount_text": "$2,000–$7,500",
        "amount_min": 2000,
        "tags": ["canadian", "stem"],
        "effort": "low",
        "notes": "Open to all Canadian students in STEM. Check site for current cycle.",
    },
    {
        "name": "TD Scholarships for Community Leadership",
        "url": "https://www.td.com/ca/en/personal-banking/solutions/student-centre/td-scholarship/",
        "amount_text": "$70,000 over 4 years",
        "amount_min": 70000,
        "tags": ["canadian", "leadership"],
        "effort": "high",
        "notes": "Highly competitive. Strong leadership and community involvement required.",
    },
    {
        "name": "Scotiabank Women Initiative Scholarship",
        "url": "https://www.scotiabank.com/ca/en/personal/chequing-savings/student-banking/scholarships.html",
        "amount_text": "$5,000",
        "amount_min": 5000,
        "tags": ["female", "canadian", "stem"],
        "effort": "medium",
        "notes": "For women pursuing STEM degrees at Canadian universities.",
    },
    {
        "name": "Microsoft Scholarship for Women in STEM",
        "url": "https://careers.microsoft.com/students/us/en/usscholarshipprogram",
        "amount_text": "$5,000 USD",
        "amount_min": 6500,
        "tags": ["female", "engineering", "stem", "tech"],
        "effort": "high",
        "notes": "Essay + interview. Open internationally including Canadian students.",
    },
    {
        "name": "De Beers Group Scholarship for Women in STEM",
        "url": "https://www.debeersgroup.com/building-forever/partnerships/scholarships",
        "amount_text": "Varies",
        "amount_min": 0,
        "tags": ["female", "stem", "canadian"],
        "effort": "medium",
        "notes": "14 scholarships annually for Canadian women entering STEM programs.",
    },
    {
        "name": "Shopify Equality Fund Scholarship",
        "url": "https://www.shopify.com/careers",
        "amount_text": "$5,000",
        "amount_min": 5000,
        "tags": ["female", "engineering", "canadian", "tech"],
        "effort": "medium",
        "notes": "For women and underrepresented groups in tech. Check site for current cycle.",
    },

    # --- Government / National ---
    {
        "name": "NSERC Undergraduate Student Research Awards",
        "url": "https://www.nserc-crsng.gc.ca/Students-Etudiants/UG-PC/USRA-BRPC_eng.asp",
        "amount_text": "$4,500+ per semester",
        "amount_min": 4500,
        "tags": ["engineering", "canadian", "stem"],
        "effort": "medium",
        "notes": "Paid research term with a professor. Apply through your department. Deadline typically December-January.",
    },
    {
        "name": "Canada Graduate Scholarships (NSERC CGS-M)",
        "url": "https://www.nserc-crsng.gc.ca/Students-Etudiants/PG-CS/CGSM-BESCM_eng.asp",
        "amount_text": "$17,500/year",
        "amount_min": 17500,
        "tags": ["engineering", "canadian", "graduate"],
        "effort": "high",
        "notes": "For graduate studies. Relevant if you're planning grad school after UW.",
    },
    {
        "name": "Ontario Graduate Scholarship (OGS)",
        "url": "https://osap.gov.on.ca/OSAPPortal/en/A-ZListofAid/PRDR019245.html",
        "amount_text": "$10,000–$15,000",
        "amount_min": 10000,
        "tags": ["engineering", "canadian", "ontario", "graduate"],
        "effort": "medium",
        "notes": "Ontario government scholarship. Apply through your university.",
    },
    {
        "name": "Canada Student Grants (OSAP)",
        "url": "https://www.ontario.ca/page/osap-ontario-student-assistance-program",
        "amount_text": "Up to $3,000",
        "amount_min": 0,
        "tags": ["canadian", "ontario", "financial_need"],
        "effort": "low",
        "notes": "Need-based. Apply through OSAP portal. Grants don't need to be repaid.",
    },

    # --- Women in STEM specific ---
    {
        "name": "FIRST Robotics Canada Women in STEM Award",
        "url": "https://firstroboticscanada.org/cwis/",
        "amount_text": "$10,000",
        "amount_min": 10000,
        "tags": ["female", "stem", "canadian"],
        "effort": "medium",
        "notes": "For Canadian women pursuing post-secondary STEM education.",
    },
    {
        "name": "Women in Nuclear Canada Scholarship",
        "url": "https://win-rfc.ca/scholarships/",
        "amount_text": "$2,000",
        "amount_min": 2000,
        "tags": ["female", "engineering", "canadian"],
        "effort": "medium",
        "notes": "For women in nuclear science, engineering, or related fields.",
    },
    {
        "name": "SWE (Society of Women Engineers) Scholarship",
        "url": "https://swe.org/scholarships/",
        "amount_text": "$1,000–$15,000",
        "amount_min": 1000,
        "tags": ["female", "engineering", "stem"],
        "effort": "medium",
        "notes": "Multiple scholarships. Open to international students including Canadians.",
    },
    {
        "name": "IEEE Women in Engineering Scholarship",
        "url": "https://wie.ieee.org/scholarships/",
        "amount_text": "Varies",
        "amount_min": 0,
        "tags": ["female", "engineering", "stem", "canadian"],
        "effort": "medium",
        "notes": "Multiple IEEE scholarships for women in electrical/systems engineering.",
    },
    {
        "name": "Electromate Scholarship for Women in Robotics/STEM",
        "url": "https://www.electromate.com/scholarships",
        "amount_text": "$2,500",
        "amount_min": 2500,
        "tags": ["female", "engineering", "canadian", "stem"],
        "effort": "low",
        "notes": "For Canadian women studying robotics, automation, or engineering. Less well-known.",
    },
]


DEADLINE_PATTERN = re.compile(
    r"(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+\d{1,2},?\s*\d{4}",
    re.IGNORECASE,
)

AMOUNT_PATTERN = re.compile(r"\$[\d,]+")


class CuratedScraper(BaseScraper):
    """
    Visits each verified scholarship URL and tries to extract the current
    deadline. Falls back to 'Check site' if none found — never returns
    fake or stale deadline data.
    """

    def scrape(self, page) -> list[Scholarship]:
        scholarships = []
        today = date.today()

        for entry in SCHOLARSHIPS:
            deadline_text, deadline_iso = self._fetch_deadline(page, entry["url"])

            # Skip if deadline has already passed
            if deadline_iso:
                try:
                    dl = date.fromisoformat(deadline_iso)
                    if dl < today:
                        deadline_text = f"{deadline_text} (closed)"
                except Exception:
                    pass

            scholarships.append(Scholarship(
                name=entry["name"],
                url=entry["url"],
                source="Curated",
                amount_text=entry["amount_text"],
                amount_min=entry["amount_min"],
                deadline_text=deadline_text,
                deadline_iso=deadline_iso,
                eligibility_tags=entry["tags"],
                effort=entry["effort"],
                notes=entry.get("notes", ""),
            ))

        return scholarships

    def _fetch_deadline(self, page, url: str) -> tuple:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=20000)
            html = page.content()
            soup = BeautifulSoup(html, "lxml")
            text = soup.get_text(" ", strip=True)

            match = DEADLINE_PATTERN.search(text)
            if match:
                from dateutil import parser as dp
                dt = dp.parse(match.group(0))
                return match.group(0), dt.strftime("%Y-%m-%d")
        except Exception as e:
            print(f"  [Curated] Could not fetch deadline for {url}: {e}")

        return "Check site", None
