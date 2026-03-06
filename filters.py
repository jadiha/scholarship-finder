from scrapers.base import Scholarship
from datetime import date, datetime
from dateutil import parser as dateparser


def is_eligible(s: Scholarship, profile: dict, filters: dict) -> bool:
    tags = [t.lower() for t in s.eligibility_tags]

    # Gender gate
    if "male_only" in tags:
        return False
    if "female" in tags and profile.get("gender") != "female":
        return False

    # Citizenship gate
    if "canadian" in tags and profile.get("citizenship") not in ("canadian", "permanent_resident"):
        return False

    # Year gate
    year = profile.get("year", 3)
    if "final_year_only" in tags and year < 4:
        return False
    if "no_final_year" in tags and year == 4:
        return False

    # Amount gate
    min_amount = filters.get("min_amount", 0)
    if s.amount_min > 0 and s.amount_min < min_amount:
        return False
    if s.amount_min == 0 and not filters.get("include_no_amount", True):
        return False

    return True


def score(s: Scholarship, profile: dict) -> int:
    tags = [t.lower() for t in s.eligibility_tags]
    total = 0

    # --- Specificity (35 pts) ---
    # The more the scholarship targets YOUR exact profile, the less competition
    if "female" in tags:
        total += 10
    if "uwaterloo" in tags:
        total += 15  # very few people qualify
    if "systems_design" in tags or "syde" in tags:
        total += 10  # rarest filter

    # --- Amount (25 pts) ---
    if s.amount_min >= 10000:
        total += 25
    elif s.amount_min >= 5000:
        total += 20
    elif s.amount_min >= 2000:
        total += 15
    elif s.amount_min >= 500:
        total += 8
    else:
        total += 5  # unknown amount — still worth checking

    # --- Deadline urgency (20 pts) ---
    if s.deadline_iso:
        try:
            deadline = datetime.fromisoformat(s.deadline_iso).date()
            days_left = (deadline - date.today()).days
            if 0 <= days_left <= 7:
                total += 20   # closing this week
            elif days_left <= 14:
                total += 16
            elif days_left <= 30:
                total += 12
            elif days_left <= 60:
                total += 6
            else:
                total += 2
        except Exception:
            total += 5
    else:
        total += 5  # unknown deadline

    # --- Effort (20 pts) ---
    effort_scores = {"low": 20, "medium": 12, "high": 5}
    total += effort_scores.get(s.effort, 12)

    return min(total, 100)


def filter_and_score(scholarships: list[Scholarship], config: dict) -> list[Scholarship]:
    profile = config.get("profile", {})
    filters = config.get("filters", {})

    eligible = [s for s in scholarships if is_eligible(s, profile, filters)]

    for s in eligible:
        s.score = score(s, profile)

    return sorted(eligible, key=lambda s: s.score, reverse=True)
