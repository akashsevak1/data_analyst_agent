# 🤖 Data Analyst Agent

An interactive AI agent that handles your **entire data analysis workflow** — from raw file to dashboard — and explains every single step in plain English.

Built with **Streamlit + Pandas + DuckDB + Plotly + Seaborn**.

---

## 🚀 Quick Start

The app is already running. If you need to restart it:

```bash
cd /home/user/data_analyst_agent
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

Then open the live preview URL in your browser.

---

## 📦 What's Inside

```
data_analyst_agent/
├── app.py                    # Main Streamlit UI (6 tabs)
├── streamlit_helpers.py      # Import bridge
├── core/
│   ├── utils.py              # File loading + problem detection
│   ├── cleaning.py           # Data-cleaning pipeline with audit log
│   ├── eda.py                # Automated EDA + chart generation
│   ├── dashboard.py          # Auto Plotly dashboard builder
│   ├── sql_agent.py          # DuckDB engine + NL→SQL + query explainer
│   └── code_gen.py           # Reusable Python/SQL code snippets
└── data/                     # Put your files here (optional)
```

---

## 🧭 The 6 Steps

### 1. 🔍 Inspect
- Upload **CSV, Excel, Parquet, or JSON** (or use the sample sales dataset)
- See shape, data types, missing values, duplicates, unique counts
- Run a full quality scan that flags:
  - Missing values per column
  - Duplicate rows
  - Text columns that look like dates
  - High-cardinality columns (likely IDs)
  - Constant columns (no variation)
  - Numeric outliers (IQR rule)

### 2. 🧹 Clean
Configure and run a full cleaning pipeline:
- Standardize column names (`Customer Name` → `customer_name`)
- Remove exact duplicate rows
- Trim whitespace in text
- Auto-convert date-like text to datetime
- Fill missing values (median / mean / zero / drop / keep)
- Optionally remove outliers or high-cardinality columns

**Every change is logged** — the agent shows you what was changed, the before/after counts, and *why*.

### 3. 📊 EDA (Exploratory Data Analysis)
One-click automated analysis:
- Descriptive statistics for all numeric columns
- Skewness / distribution shape explanation
- Top categories for categorical columns
- Correlation matrix with strongest pairs highlighted
- Auto-generated charts:
  - Histograms + KDE curves
  - Bar charts
  - Correlation heatmap
  - Box plots
  - Scatter matrix

### 4. 📈 Interactive Dashboard
The agent auto-detects column types and builds a full Plotly dashboard:
- KPI metric cards (rows, cols, averages, missing, duplicates)
- Bar, histogram, line/area, scatter, pie, box, heatmap charts
- All charts are zoomable, hoverable, downloadable as PNG

### 5. 🗄️ SQL Query Engine
Your data is loaded into an in-memory **DuckDB** database:
- **Ask in plain English** — e.g. *"top 5 region by sales"*, *"average revenue by product"*, *"monthly trend"*
- The agent writes the SQL for you
- **Every query is explained clause-by-clause** in plain English
- Or write your own advanced SQL (window functions, CTEs, joins)
- Includes 7 ready-made advanced SQL examples:
  - Top-N per group (ROW_NUMBER)
  - Running totals (SUM OVER)
  - Month-over-month growth (LAG)
  - 7-day moving average
  - Pivot / cross-tab (CASE WHEN)
  - Duplicate detection
  - Basic aggregation

### 6. 💻 Python Code Export
Download production-ready, well-commented Python scripts:
- `clean_data.py` — full cleaning pipeline
- `eda.py` — EDA with matplotlib/seaborn
- All code is explained line by line

---

## 🎓 The Agent Explains Everything

Unlike black-box tools, every output includes a **plain-English explanation**:

| Action | What you learn |
|--------|---------------|
| Clean data | What was changed, before/after counts, and why |
| Histogram | Whether distribution is symmetric/skewed |
| Correlation | Strength & direction (strong positive, weak negative, etc.) |
| Dashboard chart | What the chart type shows and how to read it |
| SQL query | Line-by-line breakdown (SELECT, FROM, JOIN, WHERE, GROUP BY, window functions…) |
| Python code | What each important line does |

---

## 🧪 Try It With the Sample Data

1. Check **"Use sample sales dataset"** in the sidebar
2. Go through tabs 1–6 in order
3. In the SQL tab, type: `top 5 region by revenue` or `average revenue by product`
4. Watch the agent generate, run, and explain the query!

The sample dataset intentionally includes:
- Missing values (customer_age, revenue, region)
- Duplicate rows
- Hidden whitespace in region names
- Messy column names with spaces & capitalization

…so you can see the cleaning agent do real work.

---

## 🛠️ Tech Stack

- **pandas** — data manipulation
- **numpy** — numerical computing
- **matplotlib + seaborn** — static EDA charts
- **plotly** — interactive dashboard
- **duckdb** — in-process SQL engine
- **streamlit** — web UI
- **scikit-learn** — available for future ML extensions

---

## 💡 Ideas for Extension

- Add a machine-learning tab (regression/classification with sklearn)
- Add PDF report generation
- Add multi-file joins in the SQL tab
- Add natural-language chart generation
- Connect to PostgreSQL / BigQuery / Snowflake
