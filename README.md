https://m5od4kzzqbouucnjkkweqy.streamlit.app/
# AI Sales Strategy Bot

Quick start
- Install dependencies: `pip install -r sales_ai_bot/requirements.txt`
- Run: `streamlit run sales_ai_bot/app.py --server.port 8501`
- Upload CSV/XLSX and generate stakeholder PDF from the Export section

Key features
- Executive KPIs with data-quality safeguards
- Forecast methodology disclosure (MAPE, baseline, RMSE)
- Churn risk (logistic, recency-based) with precision/recall
- Product zone classification (BCG-style)
- PDF export with KPI cards and chart insights
- Multi-pattern → multi-segment → multi-stakeholder analysis

Repo hygiene
- Artifacts ignored via `.gitignore` (charts, PDFs, caches)
- No secrets tracked; configure credentials locally for Git
