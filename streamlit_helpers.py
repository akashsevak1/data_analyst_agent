"""
streamlit_helpers.py — Re-export everything from the core package so
app.py stays tidy.
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from core.utils import load_file, detect_problems
from core.cleaning import clean_data
from core.eda import run_eda
from core.dashboard import auto_dashboard
from core.sql_agent import (
    df_to_sql, run_sql, get_schema, explain_query, natural_language_to_sql
)
from core.code_gen import (
    generate_cleaning_code, generate_eda_code,
    generate_sql_examples, explain_code_block,
)
