# qatar-dashboard
Qatar Foundation job market analysis
# Qatar 2030 Labor Market Intelligence Dashboard

Evidence-based workforce gap analysis for the Qatar Foundation Manara Programme & QNV 2030.

**Live dashboard:** https://apptar-dashboard-hck3shi5tcffxmt9cjdsvy.streamlit.app/

---

## What This Is

An interactive Streamlit dashboard that visualizes strategic skill gaps across 5 economic 
scenarios and 8 industry sectors in Qatar's labor market. Built as part of the CMU Tepper 
MSBA Capstone 2025 for Qatar Foundation's Higher Education Division.

It compares skill demand signals extracted from 41 authoritative published sources (IMF, 
World Bank, QNV 2030, McKinsey, QatarEnergy, and others) against 5,067 Qatar job postings 
to identify where strategic ambitions and actual hiring diverge.

---

## Repository Structure
```
qatar-dashboard/
│
├── app.py                              # Dashboard application — all logic in one file
├── requirements.txt                    # Python dependencies
├── .streamlit/
│   └── config.toml                     # Visual theme — colors, background, font
│
└── data/
    ├── scenario_gap_analysis.csv       # Primary input — 224 skill gaps
    ├── scenario_skill_matrix.csv       # Scenario x sector x skill demand matrix
    ├── scenario_calibration.csv        # Calibration lookup table
    ├── scenario_sources_raw.csv        # Full signal audit trail — 321 signals, 41 sources
    ├── scenario_coefficients.csv       # Source contributions per scenario
    ├── scenario_skill_weights.csv      # Normalized skill weights per scenario
    ├── sector_function_distribution.csv  # Sector to job function mapping reference
    └── historical_skillasign_0406_2.zip  # U.S. historical benchmark dataset
```

## Updating the Data

No code changes or server access needed. To refresh the dashboard with new pipeline outputs:

1. Go to this repository on GitHub
2. Open the `data/` folder
3. Click **Add file** > **Upload files**
4. Upload the new CSV file(s)
5. Click **Commit changes**

Streamlit Cloud detects the commit and redeploys automatically within approximately 
60 seconds.

---

## Running Locally

Requires Python 3.10+.

```bash
git clone https://github.com/dpolukhin23081979/qatar-dashboard
cd qatar-dashboard
pip install -r requirements.txt
streamlit run app.py
```

---

## Modifying the Dashboard

All dashboard logic lives in `app.py`. To edit:

**In the browser:** Open `app.py` on GitHub, click the pencil icon, edit, and commit.

**Locally:** Clone the repository, open `app.py` in any editor, make changes, commit and push.

Streamlit Cloud redeploys automatically after any commit. The visual theme is configured 
separately in `.streamlit/config.toml`.

---

## Re-running the Scenario Pipeline

To incorporate new published sources or updated job postings, open 
`Qatar_Scenario_Pipeline_v15.ipynb` in Google Colab. Full instructions are in 
`Data_Documentation.docx` in the `Data & Model: Code and Files` folder.

---

## Dashboard Tabs

| Tab | What it shows |
|-----|---------------|
| Executive Summary | Auto-generated headline findings based on active filters |
| Guide & Definitions | How to use the dashboard and definitions of all key terms |
| Skill Gap Analysis | Ranked gaps and cross-scenario heatmap |
| Industry Matrix | Average gap score by sector and scenario |
| Strategic Demand | Pure strategy-side demand from 41 sources |
| Scenario Coefficients | Model transparency — source contributions and weights |
| Skill Weights | Normalized skill weights per scenario |
| Source Evidence | Full citation trail — every signal traced to its publication |
| Data Explorer | Search, filter, and download any underlying dataset |
| Skill Shift 2019-2024 | U.S. historical benchmark for directional context |

---

## Built By

CMU Tepper MSBA Capstone 2025 — Qatar Foundation Manara Programme

Aiko Kikuchi · Akhmed Sungurov · Arshia Sabdar · Dima Polukhin · Malak Alseaf

Advised by Professor Ganesh Mani, PhD in Artificial Intelligence

---

## Documentation

Full documentation is available in the project Google Drive folder:

- `Dashboard_Documentation.docx` — deployment, data updates, and GitHub guide
- `Data_Documentation.docx` — data collection, skill extraction, and pipeline guide

