# Scholarship Finder

A free, self-hosted tool that finds scholarships for you and delivers them to Discord daily. No server, no account, no cost — runs entirely on GitHub Actions.

Built specifically for **female-identifying engineering students at Canadian universities** but configurable for any profile.

---

## What it does

- Runs every morning at 8am EST
- Pulls from a verified list of scholarships + Engineers Canada live listings
- Filters by your profile (year, program, gender, citizenship, GPA, etc.)
- Scores each scholarship by how well it fits you
- Posts **only new** ones to your Discord — no repeat spam
- Generates a full dashboard on GitHub Pages sorted by deadline

---

## Setup (10 minutes, no coding required)

### 1. Fork this repo

Click **Fork** at the top right. Your copy runs independently on your own GitHub account for free.

---

### 2. Create a Discord webhook

1. Open Discord → create a server or use an existing one
2. Create a channel (e.g. `#scholarships`)
3. Click the gear icon → **Integrations** → **Webhooks** → **New Webhook**
4. Name it anything → click **Copy Webhook URL**

**Keep this URL private — treat it like a password.**

---

### 3. Add GitHub secrets

Go to your forked repo → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add this secret:

| Name | Value |
|---|---|
| `DISCORD_WEBHOOK_URL` | your webhook URL from step 2 |

Optionally add these for more precise filtering (all default to safe values if not set):

| Name | Example value | Default |
|---|---|---|
| `GPA` | `3.7` | `3.5` |
| `FINANCIAL_NEED` | `true` or `false` | `false` |
| `FIRST_GEN` | `true` or `false` | `false` |
| `VISIBLE_MINORITY` | `true` or `false` | `false` |

---

### 4. Customize your profile

The non-sensitive parts of your profile (year, program, school, gender) are in `.github/workflows/scrape.yml`. Edit them directly in GitHub:

1. Open `.github/workflows/scrape.yml`
2. Click the pencil icon
3. Find the **Write config** step and update the values
4. Commit changes

---

### 5. Enable GitHub Pages (optional dashboard)

1. **Settings** → **Pages**
2. Source: **Deploy from a branch** → `main` → `/docs`
3. Save

Your dashboard will be at `https://yourusername.github.io/scholarship-finder/`

---

### 6. Run it

1. Go to the **Actions** tab
2. Click **Daily Scholarship Scrape**
3. Click **Run workflow** → **Run workflow**

Takes about 2 minutes. Check your Discord channel when it's done.

After the first run, it runs automatically every day at 8am EST.

---

## Run locally

```bash
git clone https://github.com/yourusername/scholarship-finder.git
cd scholarship-finder
pip install -r requirements.txt
playwright install --with-deps chromium
cp .env.example .env
# paste your Discord webhook URL in .env
python main.py
```

---

## How scholarships are scored

Each scholarship is scored 0–100:

| Factor | Weight | Logic |
|---|---|---|
| Specificity | 35% | More targeted to your profile = less competition |
| Amount | 25% | Higher dollar value ranks higher |
| Deadline urgency | 20% | Closing soon gets boosted |
| Effort | 20% | Easier applications rank higher |

---

## Adding a scholarship

Found one we're missing? Add it to `scrapers/curated.py`:

```python
{
    "name": "Scholarship Name",
    "url": "https://direct-application-link.com",
    "amount_text": "$5,000",
    "amount_min": 5000,
    "deadline_text": "April 30, 2026",
    "deadline_iso": "2026-04-30",
    "tags": ["female", "engineering", "canadian"],
    "effort": "medium",
    "notes": "Any requirements or tips.",
},
```

Or open an issue and describe it — it'll get added.

---

## Current scholarship sources

- Manually curated verified list (18 scholarships)
- Engineers Canada live listings (scraped daily)

---

Built by [@jadiha](https://github.com/jadiha)
