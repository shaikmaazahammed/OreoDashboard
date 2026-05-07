# 🍪 The Great Oreo Takeover — Content Dashboard

Interactive Streamlit dashboard for tracking the Oreo Hungary brand awareness campaign.

## What's included

```
oreo_dashboard/
├── app.py                        # Main Streamlit app
├── requirements.txt              # Python dependencies
├── data/
│   └── oreo_content_calendar.xlsx   # Source data (Content Calendar, KPI Tracker, Budget)
└── README.md
```

## Setup & Run

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run locally

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## Deploy to Streamlit Community Cloud (free)

1. Push this folder to a **GitHub repo** (make sure `data/` is included)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"** → select your repo → set **Main file path** to `app.py`
4. Click **Deploy** — live in ~2 minutes ✅

> ⚠️ Make sure the `data/oreo_content_calendar.xlsx` file is committed to the repo.

---

## Dashboard Sections

| Tab | Description |
|-----|-------------|
| 📅 Content Calendar | Timeline scatter + posts-per-day bar + phase/week table |
| 📊 Platform Analysis | Platform pie, format breakdown, phase heatmap, KPI focus bar |
| 💰 Budget | Platform allocation donut, funnel split, organic vs paid mix |
| 🎯 KPI Tracker | Editable weekly actuals table + primary KPI target cards |
| 🗂 Raw Data | Searchable full data table with CSV export |

## Sidebar Filters (apply across all tabs)

- **Phase** — filter by Phase 1 / 2 / 3
- **Platform** — TikTok, Instagram, YouTube, Facebook, UGC/Creator, Boost
- **Status** — Planned / Analysis
- **Budget Type** — Organic / Paid

---

## Campaign Summary

| Field | Value |
|-------|-------|
| Product | Oreo Original Sandwich Cookie |
| Goal | Brand Awareness |
| Market | Hungary |
| Target | 14–34 year olds |
| Budget | 20,000,000 HUF |
| Duration | 5 Weeks |
| Lead Platform | TikTok + Instagram |
| Hashtag | #OreoMoment |
