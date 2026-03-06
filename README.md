# Scholarship Finder

A free, self-hosted scholarship scraper that runs daily and delivers personalized results to your Discord. No accounts, no servers, no cost. Mainly targeted for Female Identifying Waterloo Engineering Students.

Scrapes 9 sources, filters by your profile, scores by fit, and posts new scholarships directly to you.

**Sources:** UWaterloo Awards DB, UWaterloo Engineering, ONWiE, Engineers Canada, Women in Eng & Tech, ScholarshipsCanada, StudentAwards, Bold.org, Corporate (Google, Shopify, RBC, TD, Scotiabank, Microsoft, Fortis, De Beers)

---

## How it works

1. GitHub Actions runs daily at 8am EST — free, no server needed
2. Scrapes all sources and filters by your `config.yaml` profile
3. Scores each scholarship by how well it fits you (specificity, amount, deadline, effort)
4. Posts **only new** scholarships to Discord — no spam
5. Updates a full dashboard on GitHub Pages

---

## Setup (10 minutes)

### Step 1 — Fork this repo

Click **Fork** at the top right of this page. This creates your own copy that runs independently.

---

### Step 2 — Edit your profile

Open `config.yaml` in your forked repo and update it with your details:

```yaml
profile:
  year: 3                          # your current year (1–4)
  program: systems_design_engineering
  school: university_of_waterloo
  gender: female                   # female / male / any
  citizenship: canadian            # canadian / permanent_resident / international
  gpa: 3.7                         # used to filter GPA-gated scholarships
  financial_need: false            # true = include need-based awards
  first_gen: false                 # true = include first-gen awards
  visible_minority: false          # true = include equity-focused awards
  leadership: true
  stem_volunteering: true
  target_industry: software        # software / hardware / sustainability / finance / etc.

filters:
  min_amount: 500                  # ignore scholarships under this amount
  include_no_amount: true          # include scholarships where amount isn't listed

notifications:
  discord: true
  github_pages: true
```

To edit: click the file → pencil icon → make changes → click "Commit changes".

---

### Step 3 — Create a Discord webhook

1. Open Discord → go to any server you own (or create a new one)
2. Create a channel called `#scholarships`
3. Click the gear icon on the channel → **Integrations** → **Webhooks**
4. Click **New Webhook** → give it a name (e.g. "Scholarship Bot") → click **Copy Webhook URL**

Keep this URL — you need it for the next step.

---

### Step 4 — Add the webhook as a GitHub secret

1. Go to your forked repo on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Name: `DISCORD_WEBHOOK_URL`
5. Value: paste your webhook URL
6. Click **Add secret**

---

### Step 5 — Enable GitHub Pages

1. Go to **Settings** → **Pages** (left sidebar)
2. Under **Source**, select **Deploy from a branch**
3. Branch: `main` | Folder: `/docs`
4. Click **Save**

Your dashboard will be live at: `https://yourusername.github.io/scholarship-finder/`

---

### Step 6 — Run it for the first time

1. Go to the **Actions** tab in your repo
2. Click **Daily Scholarship Scrape** on the left
3. Click **Run workflow** → **Run workflow**

Wait about 2 minutes. You should see new scholarships posted in your Discord channel and your dashboard updated.

After this it runs every day at 8am EST automatically.

---

## Run locally (optional)

```bash
git clone https://github.com/yourusername/-scholarship-finder.git
cd -scholarship-finder
pip install -r requirements.txt
cp .env.example .env
# open .env and paste your Discord webhook URL
python main.py
```

---

## Adding more scrapers

Each scraper is a single file in `scrapers/`. To add a new source:

1. Create `scrapers/mysource.py`:

```python
from .base import BaseScraper, Scholarship

class MySourceScraper(BaseScraper):
    def scrape(self) -> list[Scholarship]:
        # fetch + parse the page
        # return list of Scholarship objects
        return []
```

2. Add it to `main.py`:

```python
from scrapers.mysource import MySourceScraper
# ...
scrapers = [
    ...,
    MySourceScraper(config),
]
```

---

## Scholarship scoring

Each scholarship is scored 0–100 based on:

| Factor | Weight | Logic |
|---|---|---|
| Specificity | 35% | Scholarships targeted to your exact profile = less competition |
| Amount | 25% | Higher dollar value ranks higher |
| Deadline urgency | 20% | Closing soon gets boosted |
| Effort required | 20% | Easy applications rank higher |

Discord posts are sorted by score — highest match first.

---

## Support

If something isn't working, open an issue on this repo.
