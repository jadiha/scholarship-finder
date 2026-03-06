import os
import json
import requests
from datetime import date, datetime
from scrapers.base import Scholarship


EFFORT_LABELS = {"low": "Easy apply", "medium": "Some effort", "high": "High effort"}
URGENCY_COLORS = {
    "critical": 0xE74C3C,   # red   — <7 days
    "high":     0xE67E22,   # orange — <14 days
    "medium":   0xF1C40F,   # yellow — <30 days
    "low":      0x2ECC71,   # green  — 30+ days
    "unknown":  0x95A5A6,   # grey
}


def _urgency(deadline_iso: str | None) -> str:
    if not deadline_iso:
        return "unknown"
    try:
        days = (datetime.fromisoformat(deadline_iso).date() - date.today()).days
        if days <= 7:
            return "critical"
        if days <= 14:
            return "high"
        if days <= 30:
            return "medium"
        return "low"
    except Exception:
        return "unknown"


def _days_label(deadline_iso: str | None, deadline_text: str) -> str:
    if not deadline_iso:
        return deadline_text
    try:
        days = (datetime.fromisoformat(deadline_iso).date() - date.today()).days
        if days < 0:
            return f"{deadline_text} (closed)"
        if days == 0:
            return f"{deadline_text} (TODAY)"
        return f"{deadline_text} ({days} days left)"
    except Exception:
        return deadline_text


def post_to_discord(scholarships: list[Scholarship], webhook_url: str):
    if not scholarships:
        return

    for s in scholarships:
        urgency = _urgency(s.deadline_iso)
        color = URGENCY_COLORS[urgency]
        days_label = _days_label(s.deadline_iso, s.deadline_text)
        tags = " ".join(f"`{t}`" for t in s.eligibility_tags[:5])

        embed = {
            "title": s.name,
            "url": s.url,
            "color": color,
            "fields": [
                {"name": "Amount", "value": s.amount_text, "inline": True},
                {"name": "Deadline", "value": days_label, "inline": True},
                {"name": "Effort", "value": EFFORT_LABELS.get(s.effort, s.effort), "inline": True},
                {"name": "Match Score", "value": f"{s.score}/100", "inline": True},
                {"name": "Source", "value": s.source, "inline": True},
                {"name": "Eligibility", "value": tags or "—", "inline": False},
            ],
            "footer": {"text": "scholarship-finder • github.com/jadiha/-scholarship-finder"},
        }

        if s.description:
            embed["description"] = s.description[:200] + ("..." if len(s.description) > 200 else "")

        payload = {
            "username": "Scholarship Finder",
            "embeds": [embed],
        }

        try:
            r = requests.post(webhook_url, json=payload, timeout=10)
            r.raise_for_status()
        except Exception as e:
            print(f"[Discord] Failed to post '{s.name}': {e}")

    # Summary message at the end
    try:
        requests.post(webhook_url, json={
            "username": "Scholarship Finder",
            "content": (
                f"**{len(scholarships)} new scholarship(s) found** — "
                f"sorted by match score. Check the dashboard for the full list."
            ),
        }, timeout=10)
    except Exception:
        pass


def generate_dashboard(all_scholarships: list[Scholarship], output_path: str = "docs/index.html"):
    os.makedirs("docs", exist_ok=True)

    today = date.today().strftime("%B %d, %Y")

    rows = ""
    for s in all_scholarships:
        urgency = _urgency(s.deadline_iso)
        urgency_colors = {
            "critical": "#e74c3c", "high": "#e67e22",
            "medium": "#f39c12", "low": "#27ae60", "unknown": "#95a5a6"
        }
        badge_color = urgency_colors[urgency]
        days_label = _days_label(s.deadline_iso, s.deadline_text)

        rows += f"""
        <tr>
            <td><a href="{s.url}" target="_blank">{s.name}</a></td>
            <td>{s.amount_text}</td>
            <td style="color:{badge_color};font-weight:600">{days_label}</td>
            <td><span class="score">{s.score}</span></td>
            <td>{s.source}</td>
            <td>{EFFORT_LABELS.get(s.effort, s.effort)}</td>
            <td>{" ".join(f'<span class="tag">{t}</span>' for t in s.eligibility_tags[:4])}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Scholarship Finder</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; background: #f5f5f5; color: #222; }}
  header {{ background: #1a1a2e; color: white; padding: 2rem; }}
  header h1 {{ font-size: 1.6rem; }}
  header p {{ opacity: 0.7; font-size: 0.9rem; margin-top: 0.3rem; }}
  .container {{ max-width: 1200px; margin: 2rem auto; padding: 0 1rem; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }}
  th {{ background: #1a1a2e; color: white; padding: 0.8rem 1rem; text-align: left; font-size: 0.85rem; }}
  td {{ padding: 0.75rem 1rem; border-bottom: 1px solid #eee; font-size: 0.9rem; vertical-align: top; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #fafafa; }}
  a {{ color: #2980b9; text-decoration: none; font-weight: 500; }}
  a:hover {{ text-decoration: underline; }}
  .score {{ background: #1a1a2e; color: white; border-radius: 4px; padding: 2px 8px; font-size: 0.8rem; font-weight: 700; }}
  .tag {{ background: #eef; color: #336; border-radius: 3px; padding: 1px 6px; font-size: 0.75rem; margin-right: 3px; display: inline-block; }}
  .updated {{ color: #888; font-size: 0.8rem; margin-top: 1rem; }}
</style>
</head>
<body>
<header>
  <h1>Scholarship Finder</h1>
  <p>Personalized for: 3rd year Systems Design Engineering · UWaterloo · Female · Canadian</p>
</header>
<div class="container">
  <table>
    <thead>
      <tr>
        <th>Scholarship</th>
        <th>Amount</th>
        <th>Deadline</th>
        <th>Score</th>
        <th>Source</th>
        <th>Effort</th>
        <th>Tags</th>
      </tr>
    </thead>
    <tbody>
      {rows}
    </tbody>
  </table>
  <p class="updated">Last updated: {today}</p>
</div>
</body>
</html>"""

    with open(output_path, "w") as f:
        f.write(html)

    print(f"[Dashboard] Generated {output_path} with {len(all_scholarships)} scholarships")
