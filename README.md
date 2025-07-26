
# CARE + DAC ZIP Overlay Module

This sub‑module generates **CARE‑dense ZIP codes overlaid with CalEnviroScreen
SB 535 Disadvantaged Community tracts** so you can target SGIP Equity prospects.

## How to run locally

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
wget -O High_CARE_ZIPs_CA.csv <YOUR-PREVIOUS-CSV-URL>
python src/scripts/build_care_dac_zip_list.py
```

Output: `CARE_DAC_ZIPs_Enriched.csv`.

## GitHub Action

A manual workflow **Refresh CARE DAC ZIP list** is included at
`.github/workflows/update_care_dac.yml`.  
Trigger it in the Actions tab anytime new CPUC CARE filings are released.
