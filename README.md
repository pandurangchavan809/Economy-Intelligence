# Global Economic Intelligence Platform
Global Economic Intelligence Platform with real-time GDP and defense spending counters, continent and country-level analytics, and ML-based economic health scoring using World Bank, IMF, and CountryLayer APIs.

__init__.py :- These files can be empty — they just tell Python:

“This folder is a package”

Run the script as a MODULE (important)

Instead of this ❌:

python etl/countrylayer.py


Run this ✅ from project root:

python -m etl.countrylayer


📌 This tells Python:

“Treat the project root as the package root”

PHASE 2.3 — IMF ETL (Global Intelligence Layer)

This phase feeds:

🌍 World page

📈 Global GDP growth

🔮 Forecast context

⚙️ Live counter baselines

⚠️ Important reality check (professional honesty):
IMF does NOT have a simple, stable REST API like World Bank.
In real projects, engineers use:

IMF SDMX API (complex)

IMF WEO CSV datasets (most common)

IMF manual refresh pipeline

👉 For a student + resume-grade project, the correct professional choice is:

Use IMF WEO (World Economic Outlook) CSV datasets

This is what analysts and researchers actually do.




