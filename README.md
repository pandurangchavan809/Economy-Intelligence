# AI Economics Dashboard: Global Intelligence Platform

An advanced analytical suite for real-time economic synthesis, defense spending surveillance, and ML-driven market health scoring. This platform bridges the gap between raw macroeconomic data and actionable financial intelligence.

---

## 🚀 Core Features

### 1. High-Fidelity Data Engine
* **Multisource Ingestion:** Seamlessly aggregates data from the **World Bank Open Data API**, **CountryLayer**, and curated **IMF World Economic Outlook (WEO)** datasets.
* **10-Year Temporal Analysis:** Provides a longitudinal view (2015–2025) of national performance, moving beyond static snapshots to identify decade-long growth trajectories.
* **Precision Scaling:** Automated normalization of GDP figures into Nominal USD Billions, ensuring accurate cross-border comparisons for economies of all scales (from Emerging Markets to the G7).

### 2. Live Intelligence Dashboards
* **Macro-Financial KPIs:** Real-time tracking of GDP Growth, Consumer Price Index (CPI) Inflation, and Unemployment trends.
* **Defense & Fiscal Surveillance:** Integrated monitoring of government expenditure, specifically isolating defense spending baselines against total fiscal capacity.
* **Dynamic Visualizations:** High-contrast, interactive charting using **Plotly Spline-Line** and **Minimalist Bar** architectures for reduced cognitive load and immediate trend recognition.

### 3. ML-Driven Economic Health Scoring
* **Predictive Health Index:** A proprietary scoring algorithm that weights Debt-to-GDP, FDI inflows, and Inflation volatility to provide a 1-100 "Market Stability" score.
* **Anomaly Detection:** Identifies fiscal outliers and sudden shifts in economic policy using pattern recognition across 48+ World Bank indicators.

---

## 🛠 Strategic Engineering Decisions

### The IMF Data Challenge (Professional Honesty)
Standard REST APIs for the IMF (like SDMX) are notoriously unstable for production-grade real-time systems. 
* **The Solution:** This project utilizes an automated **IMF WEO CSV Pipeline**. 
* **The Benefit:** By processing raw World Economic Outlook datasets, the platform ensures 100% data reliability and allows for the inclusion of forecasted "Estimate" data for 2025, which is often missing from standard APIs.

### Performance & Rate Management
* **Intelligent Caching:** Implements a TTL (Time-To-Live) caching layer to minimize API overhead and prevent `429: Quota Exceeded` errors during high-intensity usage.
* **Recursive Retry Logic:** Built-in auto-recovery for network-level interruptions, ensuring the dashboard remains operational during server-side AI latency.

---

## 🧠 AI Integration (Gemini 2.5 Flash)
The platform leverages the **Gemini 2.5 Flash** large language model as a "Virtual Economic Consultant." 
* **Context-Aware Analysis:** The AI doesn't just answer questions; it ingests the current dashboard's data state to provide deep-dive insights into regional fiscal risks and trade policy impacts.
* **Zero-Markdown Parsing:** A custom sanitization layer ensures AI-generated data is converted into pure JSON, preventing UI crashes and ensuring data integrity.

---

## 📈 Planned Roadmap
- [ ] **Sentinel Alerts:** Automated email/SMS triggers for when a country's inflation crosses a custom threshold.
- [ ] **Geopolitical Sentiment Analysis:** Integrating news-feed NLP to correlate economic shifts with political events.
- [ ] **Export Engine:** One-click PDF/Excel generation for executive-level reporting.


