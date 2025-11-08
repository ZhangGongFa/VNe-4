
# AI-Driven Corporate Default Risk App

End-to-end Streamlit application scaffold for **AI-DRIVEN CORPORATE DEFAULT RISK PREDICTION THROUGH THE INTEGRATION OF FINANCIAL AND SENTIMENT DATA WITH TREE-BASED MODELS**.

This drop contains the **Financial** module completed:
- **Income Statement**, **Balance Sheet**, **Cashflow Statement**, **Financial Indicator**: tables + CSV export
- **Report**: summary charts and analyst notes

User flow: input a **Ticker** and number of **Years** (default 10) in the sidebar, click **Fetch**. No uploads required.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project Layout
```
ai-default-risk-app/
├─ README.md
├─ requirements.txt
├─ .streamlit/config.toml
├─ app.py
└─ src/
   ├─ core/
   ├─ data/
   └─ ui/
       ├─ components/
       └─ tabs/
           └─ financial/
```
You can later add Sentiment and Summary modules under `src/ui/tabs/`.

## Notes
- Matplotlib is used for charts. No specific colors/styles are enforced.
- The demo backend generates deterministic data so the app runs immediately.
- All tables have one-click CSV export.
