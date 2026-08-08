"""
app.py — Data Analyst Agent
============================
An interactive Streamlit agent that performs:
  1. Data loading & quality scanning
  2. Data cleaning (with audit trail)
  3. Automated EDA with charts
  4. Interactive dashboards (Plotly)
  5. SQL querying (DuckDB) + plain-English query explanation
  6. Reusable Python code generation

Run with:  streamlit run app.py
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from streamlit_helpers import (
    load_file, detect_problems, clean_data, run_eda,
    auto_dashboard, df_to_sql, run_sql, get_schema,
    explain_query, natural_language_to_sql,
    generate_cleaning_code, generate_eda_code,
    generate_sql_examples, explain_code_block,
)

# ─────────────────────────── PAGE CONFIG ────────────────────────────
st.set_page_config(
    page_title="Data Analyst Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-header {font-size:2.2rem; font-weight:800; color:#1e3a8a;}
    .subheader {font-size:1.1rem; color:#475569; margin-bottom:1rem;}
    .stAlert {border-radius:10px;}
    .step-badge {
        display:inline-block; background:#1e3a8a; color:white;
        padding:2px 10px; border-radius:12px; font-size:0.85rem;
        font-weight:600; margin-right:8px;
    }
    .explanation-box {
        background:#f0f9ff; border-left:4px solid #0284c7;
        padding:12px 16px; border-radius:6px; margin:8px 0;
        font-size:0.95rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🤖 Data Analyst Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="subheader">Your AI partner for data cleaning, EDA, dashboards, SQL & Python — explained every step of the way.</div>', unsafe_allow_html=True)

# ─────────────────────────── SIDEBAR ────────────────────────────────
with st.sidebar:
    st.header("📁 Data Source")
    uploaded = st.file_uploader(
        "Upload CSV, Excel, Parquet, or JSON",
        type=["csv", "xlsx", "xls", "parquet", "json"],
    )
    use_sample = st.checkbox("Use sample sales dataset", value=False)

    st.divider()
    st.markdown("### 🧭 Agent Steps")
    st.markdown("""
    1. **Load & Inspect** data
    2. **Scan for problems**
    3. **Clean** the data
    4. **Explore** (EDA)
    5. **Dashboard**
    6. **SQL queries**
    7. **Python code export**
    """)

# ─────────────────────────── LOAD DATA ──────────────────────────────
def get_sample_data() -> pd.DataFrame:
    """Generate a realistic sample sales dataset with intentional messiness."""
    np.random.seed(42)
    n = 1000
    dates = pd.date_range("2023-01-01", "2024-12-31", periods=n)
    regions = ["North", "South", "East", "West"]
    products = ["Laptop", "Phone", "Tablet", "Monitor", "Keyboard"]
    channels = ["Online", "Retail", "Partner"]

    df = pd.DataFrame({
        "Order Date": dates,
        "Region": np.random.choice(regions, n),
        "Product": np.random.choice(products, n),
        "Sales Channel": np.random.choice(channels, n),
        "Units Sold": np.random.randint(1, 50, n).astype(float),
        "Unit Price": np.round(np.random.uniform(50, 2000, n), 2),
        "Customer Age": np.random.randint(18, 75, n).astype(float),
        "Customer Rating": np.round(np.random.uniform(1, 5, n), 1),
    })
    df["Revenue"] = df["Units Sold"] * df["Unit Price"]

    # inject problems
    df.loc[df.sample(50).index, "Customer Age"] = np.nan
    df.loc[df.sample(30).index, "Revenue"] = np.nan
    df.loc[df.sample(20).index, "Region"] = np.nan
    dup_rows = df.sample(15)
    df = pd.concat([df, dup_rows], ignore_index=True)
    df["Region"] = df["Region"].astype(object)
    for i in df[df["Region"].notna()].sample(20).index:
        df.at[i, "Region"] = str(df.at[i, "Region"]) + " "
    return df


# Session state
if "df_raw" not in st.session_state:
    st.session_state.df_raw = None
if "df_clean" not in st.session_state:
    st.session_state.df_clean = None
if "sql_con" not in st.session_state:
    st.session_state.sql_con = None
if "clean_report" not in st.session_state:
    st.session_state.clean_report = None

# Load file
if uploaded is not None:
    with st.spinner("Loading file..."):
        import tempfile, os
        suffix = os.path.splitext(uploaded.name)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = tmp.name
        df_raw, load_note = load_file(tmp_path)
        st.session_state.df_raw = df_raw
        st.session_state.df_clean = None
    st.success(load_note)
elif use_sample:
    with st.spinner("Generating sample dataset..."):
        df_raw = get_sample_data()
        st.session_state.df_raw = df_raw
        st.session_state.df_clean = None
    n, c = df_raw.shape
    st.success(f"✅ Loaded sample sales dataset — {n:,} rows × {c} columns (with intentional missing values, duplicates, and whitespace for demonstration).")

# ─────────────────────────── TABS ───────────────────────────────────
if st.session_state.df_raw is not None:
    df_raw = st.session_state.df_raw

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔍 1. Inspect", "🧹 2. Clean", "📊 3. EDA",
        "📈 4. Dashboard", "🗄️ 5. SQL", "💻 6. Python Code"
    ])

    # ───────────────── TAB 1: INSPECT ─────────────────
    with tab1:
        st.markdown('<span class="step-badge">Step 1</span> **Data Inspection & Quality Scan**', unsafe_allow_html=True)

        st.subheader("📋 First 20 rows")
        st.dataframe(df_raw.head(20), use_container_width=True)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Rows", f"{len(df_raw):,}")
        c2.metric("Columns", df_raw.shape[1])
        c3.metric("Missing cells", f"{df_raw.isna().sum().sum():,}")
        c4.metric("Duplicates", f"{df_raw.duplicated().sum():,}")

        st.subheader("📐 Data types")
        dtype_df = pd.DataFrame({
            "Column": df_raw.columns,
            "Type": df_raw.dtypes.astype(str).values,
            "Non-null count": df_raw.notna().sum().values,
            "Missing": df_raw.isna().sum().values,
            "% Missing": (df_raw.isna().sum().values / len(df_raw) * 100).round(1),
            "Unique values": [df_raw[c].nunique() for c in df_raw.columns],
        })
        st.dataframe(dtype_df, use_container_width=True, hide_index=True)

        if st.button("🔬 Run full quality scan", type="primary"):
            with st.spinner("Scanning for data quality issues..."):
                problems, problem_note = detect_problems(df_raw)
            st.markdown(f'<div class="explanation-box">{problem_note.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
            st.session_state["problems"] = problems

    # ───────────────── TAB 2: CLEAN ─────────────────
    with tab2:
        st.markdown('<span class="step-badge">Step 2</span> **Data Cleaning**', unsafe_allow_html=True)
        st.markdown("Configure cleaning options. The agent will log **every change** it makes.")

        with st.form("cleaning_form"):
            col_a, col_b = st.columns(2)
            with col_a:
                opt_dup = st.checkbox("Remove duplicate rows", value=True)
                opt_names = st.checkbox("Standardize column names", value=True)
                opt_dates = st.checkbox("Auto-parse date columns", value=True)
                opt_strip = st.checkbox("Trim whitespace in text", value=True)
            with col_b:
                opt_missing = st.selectbox(
                    "Missing-value strategy",
                    ["smart (median/mode)", "mean", "zero", "drop rows", "keep as-is"],
                    index=0,
                )
                opt_outliers = st.checkbox("Remove statistical outliers (⚠️ use carefully)")
                opt_highcard = st.checkbox("Drop high-cardinality text columns")

            submitted = st.form_submit_button("🧹 Clean my data", type="primary")

        strategy_map = {
            "smart (median/mode)": "smart",
            "mean": "mean", "zero": "zero",
            "drop rows": "drop", "keep as-is": "keep",
        }

        if submitted:
            with st.spinner("Cleaning data..."):
                df_clean, report = clean_data(
                    df_raw,
                    drop_duplicates=opt_dup,
                    fix_column_names=opt_names,
                    parse_dates=opt_dates,
                    strip_strings=opt_strip,
                    missing_strategy=strategy_map[opt_missing],
                    remove_outliers=opt_outliers,
                    drop_high_cardinality=opt_highcard,
                )
            st.session_state.df_clean = df_clean
            st.session_state.clean_report = report

            st.success(f"✅ Cleaning complete! {len(df_clean):,} rows × {df_clean.shape[1]} columns.")

            st.subheader("📝 Cleaning audit log — what I did and why")
            for entry in report:
                with st.expander(f"✦ {entry['step']}"):
                    st.markdown(entry["detail"])
                    if "before" in entry:
                        st.caption(f"Before: {entry['before']}  →  After: {entry['after']}")

            st.subheader("🔍 Cleaned data preview")
            st.dataframe(df_clean.head(20), use_container_width=True)

            csv = df_clean.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Download cleaned CSV", csv, "cleaned_data.csv", "text/csv")

    # ───────────────── TAB 3: EDA ─────────────────
    with tab3:
        st.markdown('<span class="step-badge">Step 3</span> **Automated Exploratory Data Analysis (EDA)**', unsafe_allow_html=True)
        st.markdown("The agent computes statistics, identifies patterns, and generates visualizations automatically.")

        eda_source = st.session_state.df_clean if st.session_state.df_clean is not None else df_raw
        src_label = "cleaned data" if st.session_state.df_clean is not None else "raw data"
        st.info(f"Running EDA on **{src_label}** ({len(eda_source):,} rows). Clean the data first for better results.")

        if st.button("🚀 Run full EDA", type="primary"):
            with st.spinner("Analyzing data and generating charts..."):
                results, explanation = run_eda(eda_source)

            st.markdown(f'<div class="explanation-box">{explanation.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

            st.subheader("📈 Numeric statistics")
            st.dataframe(results["numeric_stats"], use_container_width=True)

            if results["categorical_stats"]:
                st.subheader("🔤 Top categories")
                for col_name, vc in results["categorical_stats"].items():
                    with st.expander(f"**{col_name}** — {len(vc)} top values"):
                        st.dataframe(vc.rename("count"), use_container_width=True)

            if not results["correlation"].empty:
                st.subheader("🔗 Correlation matrix")
                st.dataframe(results["correlation"].round(2), use_container_width=True)

            st.subheader("🖼️ Visualizations")
            for pname, b64 in results["plots"].items():
                st.image(f"data:image/png;base64,{b64}", caption=pname.replace("_", " ").title(),
                         use_container_width=True)

    # ───────────────── TAB 4: DASHBOARD ─────────────────
    with tab4:
        st.markdown('<span class="step-badge">Step 4</span> **Interactive Dashboard**', unsafe_allow_html=True)

        dash_source = st.session_state.df_clean if st.session_state.df_clean is not None else df_raw

        if st.button("🎨 Generate dashboard", type="primary"):
            with st.spinner("Building interactive dashboard..."):
                figures, kpis, dash_expl = auto_dashboard(dash_source)

            st.markdown(f'<div class="explanation-box">{dash_expl.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

            st.subheader("🎯 Key metrics")
            kpi_cols = st.columns(min(len(kpis), 4))
            for i, (k, v) in enumerate(kpis.items()):
                kpi_cols[i % len(kpi_cols)].metric(k, f"{v:,}" if isinstance(v, int) else v)

            st.divider()
            st.subheader("📊 Charts")
            for chart_type, title, fig in figures:
                st.markdown(f"**{chart_type.title()} — {title}**")
                st.plotly_chart(fig, use_container_width=True)
                st.caption(
                    {
                        "bar": "A bar chart compares counts or values across categories.",
                        "histogram": "A histogram shows the frequency distribution of a numeric variable.",
                        "timeseries": "A line chart tracks how a value changes over time.",
                        "heatmap": "A heatmap shows correlation strength — blue = positive, red = negative.",
                        "box": "A box plot shows median, quartiles, and outliers for each group.",
                        "scatter": "A scatter plot reveals the relationship between two numeric variables.",
                        "pie": "A pie chart shows parts of a whole (proportions).",
                    }.get(chart_type, "")
                )

    # ───────────────── TAB 5: SQL ─────────────────
    with tab5:
        st.markdown('<span class="step-badge">Step 5</span> **SQL Query Engine (DuckDB)**', unsafe_allow_html=True)
        st.markdown("Your data is loaded into an in-memory SQL database. Ask questions in plain English or write raw SQL.")

        sql_source = st.session_state.df_clean if st.session_state.df_clean is not None else df_raw
        table_name = "dataset"

        if st.button("🔌 Connect to SQL engine", type="primary"):
            con, sql_note = df_to_sql(sql_source, table_name)
            st.session_state.sql_con = con
            st.markdown(f'<div class="explanation-box">{sql_note.replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)

            schema_df, schema_note = get_schema(con, table_name)
            st.markdown(f"**{schema_note}**")
            st.dataframe(schema_df, use_container_width=True, hide_index=True)

        if st.session_state.sql_con is not None:
            con = st.session_state.sql_con

            st.subheader("💬 Ask in plain English")
            nl_query = st.text_input(
                "What do you want to know?",
                placeholder="e.g. top 5 regions by revenue, average revenue by product, monthly trend..."
            )
            if nl_query:
                generated_sql = natural_language_to_sql(nl_query, table_name, sql_source)
                st.code(generated_sql, language="sql")
                st.markdown(f'<div class="explanation-box">{explain_query(generated_sql).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                if st.button("▶️ Run this query", key="run_nl"):
                    result, result_note = run_sql(con, generated_sql)
                    st.info(result_note)
                    st.dataframe(result, use_container_width=True, hide_index=True)
                    csv_res = result.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download results", csv_res, "query_results.csv", "text/csv")

            st.subheader("✍️ Write your own SQL")
            custom_sql = st.text_area(
                "SQL query",
                height=160,
                value=f"SELECT * FROM {table_name} LIMIT 10;",
            )
            if st.button("▶️ Run SQL", key="run_custom"):
                result, result_note = run_sql(con, custom_sql)
                st.info(result_note)
                if not result.empty:
                    st.dataframe(result, use_container_width=True, hide_index=True)
                    st.markdown(f'<div class="explanation-box">{explain_query(custom_sql).replace(chr(10), "<br>")}</div>', unsafe_allow_html=True)
                    csv_res = result.to_csv(index=False).encode("utf-8")
                    st.download_button("⬇️ Download results", csv_res, "query_results.csv", "text/csv")

            with st.expander("📚 Advanced SQL examples (click to expand)"):
                examples = generate_sql_examples()
                for name, sql in examples.items():
                    st.markdown(f"**{name}**")
                    st.code(sql, language="sql")
                    st.caption(explain_query(sql).replace("\n", " "))

    # ───────────────── TAB 6: PYTHON CODE ─────────────────
    with tab6:
        st.markdown('<span class="step-badge">Step 6</span> **Reusable Python Code**', unsafe_allow_html=True)
        st.markdown("Copy these snippets to run analysis in your own notebook. Each block is explained.")

        st.subheader("🧹 Data-cleaning script")
        clean_code = generate_cleaning_code()
        st.code(clean_code, language="python")
        with st.expander("💡 What this code does"):
            st.markdown(explain_code_block(clean_code).replace("\n", "\n\n"))
        st.download_button("⬇️ Download cleaning script", clean_code.encode(), "clean_data.py", "text/x-python")

        st.subheader("📊 EDA script")
        eda_code = generate_eda_code()
        st.code(eda_code, language="python")
        with st.expander("💡 What this code does"):
            st.markdown(explain_code_block(eda_code).replace("\n", "\n\n"))
        st.download_button("⬇️ Download EDA script", eda_code.encode(), "eda.py", "text/x-python")

        st.subheader("🗄️ SQL examples")
        for name, sql in generate_sql_examples().items():
            with st.expander(f"📌 {name}"):
                st.code(sql, language="sql")
                st.markdown(explain_query(sql))

else:
    st.info("👈 Upload a file or check 'Use sample sales dataset' in the sidebar to get started.")

    st.markdown("""
    ### 🚀 What this agent can do for you

    | Step | Capability | What you get |
    |------|-----------|--------------|
    | 1 | **Load & inspect** | Shape, data types, missing/duplicate counts |
    | 2 | **Clean data** | Duplicate removal, name fixing, date parsing, missing-value imputation, outlier handling — with a full audit log |
    | 3 | **EDA** | Statistics, distributions, correlations, 5+ auto-generated chart types |
    | 4 | **Dashboard** | Interactive Plotly KPI cards + charts (bar, line, scatter, pie, heatmap, box) |
    | 5 | **SQL** | Query your data with DuckDB; ask in plain English; every query explained line-by-line |
    | 6 | **Python code** | Export reusable, commented scripts for cleaning & EDA |

    ### 🎓 The agent *explains* everything
    Every action comes with a plain-English explanation:
    - What was changed and **why**
    - What a chart shows and how to read it
    - What a SQL query does, clause by clause
    - What each Python line does
    """)
