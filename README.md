# ✈️ India Civil Aviation Analytics — End-to-End ETL & Executive Power BI Suite

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Cleaning-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-Dashboard%20%26%20DAX-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)
![Data Modeling](https://img.shields.io/badge/Architecture-Star%20Schema-0F294A?style=for-the-badge)

An end-to-end data analytics and business intelligence project analyzing **India's Civil Aviation sector (2015–2026)** using official operational filings from the **Directorate General of Civil Aviation (DGCA)** and daily airport telemetry from the **Ministry of Civil Aviation (MoCA)**.

---

## 📊 Executive Summary & Key Insights

| Metric | Value | Key Takeaway |
| :--- | :--- | :--- |
| **Total Domestic Passengers** | **1,422.60M** | Sustained structural growth (`7.43%` YoY), rebounding from the `125M` trough in 2020 to `334M` in 2025 |
| **Weighted Passenger Load Factor** | **83.9%** | High fleet utilization across scheduled carriers despite rapid capacity expansion |
| **Market Leader Share** | **52.8%** | **IndiGo** dominates domestic volume, followed by Air India (`12.0%`) and SpiceJet (`8.9%`) |
| **Busiest Domestic Trunk** | **62M Pax** | **Delhi – Mumbai** leads both passenger traffic (`62M`) and belly-hold air freight (`0.53M MT`) |
| **International Bilateral Traffic** | **621.75M** | Near-symmetric flow (`49.2%` inbound) anchored by Gulf hubs—**5 of the top 7** international routes connect to **Dubai** |
| **Air Cargo Resilience** | **18.29M MT** | International air freight rebounded sharply in Q2–Q3 2020 even while passenger borders remained closed |

---

## 🖥️ Dashboard Architecture (3-Page Executive Suite)

### 1️⃣ Page 1: `India Civil Aviation - Executive Overview`
* **KPI Strip:** Domestic Passengers (`1422.60M`), Pax YoY Growth (`7.43%`), Weighted PLF (`83.9%`), Domestic Cargo (`8.07M`), Avg Daily Domestic Pax (`423.69K`).
* **Visuals:**
  * Monthly Domestic Passenger Trend & Weighted PLF % (Combo Line & Column Chart)
  * Domestic Passenger Market Share % — Top Carriers (Clustered Bar Chart)
  * Annual Domestic Traffic by Operation Type (`Scheduled` vs. `Non-Scheduled`)
  * Daily Airport Telemetry: Departing vs. Arriving Pax (Continuous Line Chart)

### 2️⃣ Page 2: `Domestic Route & Cargo Network`
* **KPI Strip:** City-Pair Passengers (`1392.63M`), Active Corridors (`1,887`), Avg Pax / Corridor (`738.01K`), Route Freight (`5.76M MT`), Route Mail (`293.47K MT`).
* **Visuals:**
  * Top 7 Busiest Domestic Air Corridors (`DEL-BOM`, `BLR-DEL`, `BLR-BOM`, `DEL-CCU`, `DEL-HYD`, `DEL-PNQ`, `MAA-DEL`)
  * Top 7 Domestic Air Freight Corridors (MT)
  * Monthly Domestic Freight & Mail Tonnage Trend vs. Active Network Corridors
  * **Corridor Efficiency Scatter Matrix:** Plots passenger volume against freight tonnage to isolate dual mega-trunks (`DEL-BOM`, `BLR-DEL`) from pure passenger corridors (`DEL-PNQ`).

### 3️⃣ Page 3: `International Traffic & Global Corridors`
* **KPI Strip:** International Passengers (`621.75M`), Inbound Share (`49.2%`), Global City Pairs (`1,163`), Intl Route Cargo (`5.76M MT`), Intl Carrier Cargo (`18.29M MT`).
* **Visuals:**
  * Top 7 International City Corridors (`Dubai-Mumbai 23M`, `Delhi-Dubai 20M`, `Delhi-London 11M`)
  * Top 7 International Carriers by Passenger Volume (`IndiGo 77.5M`, `Air India 74.6M`, `Emirates 54.5M`)
  * Quarterly International Passenger (Inbound vs. Outbound) & Air Cargo Trend
  * **Partner Country Matrix:** Scatter analysis contrasting bilateral passenger volume against air freight tonnage (highlighting cargo-heavy hubs like Hong Kong & Germany vs. mega-hub UAE).

---

## 🛠️ Data Engineering & Star-Schema Modeling

### Python ETL Pipeline (`clean_aviation_data.py`)
Raw DGCA & MoCA multi-grain datasets contained mixed date formats, footnote asterisks (`UNITED ARAB EMIRATES*`), text-encoded numeric strings, and duplicate monthly/quarterly filings. The Python pipeline automates:
* **Schema Standardization:** Normalizes dates into ISO `YYYY-MM-DD` keys (`Date`), strips footnote characters, and coerces numeric metrics to `float64`.
* **Granularity Aggregation:** Groups city-pair and carrier tables cleanly (`groupby(["Year", "Month", "Date", ...])`) to eliminate duplicate sub-entries prior to BI ingestion.
* **Modular Fact Exports:** Outputs 6 clean, analysis-ready fact tables (`fact_dom_carrier.csv`, `fact_dom_city.csv`, `fact_intl_carrier.csv`, `fact_intl_city.csv`, `fact_intl_country.csv`, `fact_daily_moca.csv`).

### Power BI Star Schema & DAX Highlights
* **Eliminated Many-to-Many Double Counting:** Built centralized **`Dim_Date`** and **`Dim_Airline`** dimension tables connected via `1:*` (one-to-many) single-direction relationships, preventing `2x` metric inflation across multi-grain fact tables.
* **Custom DAX Measures:** Implemented dynamic YoY growth (`SAMEPERIODLASTYEAR`), capacity-weighted Passenger Load Factor (`DIVIDE(SUM(Pax), SUM(AvailableSeats))`), bilateral directional symmetry ratios, and cross-filtered country/corridor cargo metrics.

---

## 📁 Repository Structure

```text
india-aviation-analytics/
│
├── data/
│   ├── raw/                        # Original DGCA & MoCA CSV datasets
│   └── cleaned/                    # ETL-processed fact tables ready for Power BI
│       ├── fact_dom_carrier.csv
│       ├── fact_dom_city.csv
│       ├── fact_intl_carrier.csv
│       ├── fact_intl_city.csv
│       ├── fact_intl_country.csv
│       └── fact_daily_moca.csv
│
├── scripts/
│   └── clean_aviation_data.py      # Python Pandas ETL & data hygiene pipeline
│
├── powerbi/
│   └── India_Aviation_Suite.pbix   # 3-page interactive Power BI report
│
├── exports/
│   └── Indian Aviation.pdf         # Exported 3-page executive dashboard PDF
│
└── README.md
