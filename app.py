"""
app.py  –  Main Streamlit Dashboard: Coffee Quality Analysis
Course : Exploratory Data Analysis  |  Instructor: Ali Hassan Sherazi
Dataset: arabica_data_cleaned.csv   |  1,311 samples graded by Q-graders
"""

import streamlit as st
import pandas as pd
import numpy as np

from filters import load_data, apply_filters
from charts  import (pie_chart, histogram, line_chart, bar_chart,
                     scatter_plot, box_plot, heatmap, area_chart,
                     count_plot, violin_plot, pair_plot)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="☕ Coffee Quality Dashboard",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Lato:wght@300;400;700&display=swap');

html, body, [class*="css"] {
    background-color: #1C1008;
    color: #F5E6D0;
    font-family: 'Lato', sans-serif;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #2A1A0E;
    border-right: 1px solid #3D2B1F;
}
section[data-testid="stSidebar"] * { color: #F5E6D0 !important; }

/* Header banner */
.banner {
    background: linear-gradient(135deg, #3D2B1F 0%, #6F4E37 60%, #C8A97E 100%);
    border-radius: 12px;
    padding: 28px 36px;
    margin-bottom: 20px;
    border: 1px solid #C8A97E33;
}
.banner h1 {
    font-family: 'Playfair Display', serif;
    font-size: 2.4rem;
    color: #F5E6D0;
    margin: 0;
    letter-spacing: 1px;
}
.banner p { color: #C8A97E; margin: 6px 0 0; font-size: 0.95rem; }

/* KPI cards */
.kpi-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
.kpi {
    background: #2A1A0E;
    border: 1px solid #3D2B1F;
    border-top: 3px solid #C8A97E;
    border-radius: 10px;
    padding: 18px 22px;
    flex: 1;
    min-width: 140px;
    transition: transform .2s;
}
.kpi:hover { transform: translateY(-3px); border-top-color: #D2691E; }
.kpi .val {
    font-family: 'Playfair Display', serif;
    font-size: 1.9rem;
    color: #C8A97E;
    display: block;
}
.kpi .lbl { font-size: 0.75rem; color: #A0907A; text-transform: uppercase; letter-spacing: 1px; }

/* Section headers */
.sec-head {
    font-family: 'Playfair Display', serif;
    color: #C8A97E;
    font-size: 1.2rem;
    border-left: 4px solid #C8A97E;
    padding-left: 12px;
    margin: 28px 0 14px;
}

/* Chart containers */
.chart-wrap {
    background: #2A1A0E;
    border: 1px solid #3D2B1F;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
    transition: box-shadow .2s;
}
.chart-wrap:hover { box-shadow: 0 0 0 1px #C8A97E55; }

/* Buttons */
div.stButton > button {
    background: linear-gradient(135deg, #6F4E37, #C8A97E);
    color: #1C1008;
    font-weight: 700;
    border: none;
    border-radius: 8px;
    padding: 8px 20px;
    transition: opacity .2s;
    width: 100%;
}
div.stButton > button:hover { opacity: 0.85; }

/* Streamlit widget labels */
label { color: #C8A97E !important; font-size: 0.82rem !important; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
@st.cache_data
def get_data():
    return load_data()

df = get_data()

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ☕ Filters")
    st.markdown("---")

    # Reset button
    if st.button("🔄 Reset All Filters"):
        st.session_state["reset"] = True
        st.rerun()

    reset = st.session_state.get("reset", False)

    # 1. Date/Time Range Filter
    yr_min = int(df["Grading.Year"].min())
    yr_max = int(df["Grading.Year"].max())
    year_range = st.slider("📅 Grading Year Range", yr_min, yr_max,
                           (yr_min, yr_max) if reset else (yr_min, yr_max))

    # 2. Category Filter – Country
    all_countries = sorted(df["Country.of.Origin"].unique())
    countries = st.multiselect("🌍 Country of Origin",
                               all_countries,
                               default=[] if reset else [])

    # 3. Category Filter – Processing Method
    all_methods = sorted(df["Processing.Method"].unique())
    proc = st.multiselect("⚙️ Processing Method",
                          all_methods,
                          default=[] if reset else [])

    # 4. Multi-Select Filter – Variety
    top_varieties = df["Variety"].value_counts().head(20).index.tolist()
    varieties = st.multiselect("🌱 Variety (Top 20)",
                               top_varieties,
                               default=[] if reset else [])

    # 5. Multi-Select Filter – Color
    all_colors = sorted(df["Color"].unique())
    colors = st.multiselect("🎨 Bean Color",
                             all_colors,
                             default=[] if reset else [])

    # 6. Numerical Range Slider – Cup Points
    sc_min = float(df["Total.Cup.Points"].min())
    sc_max = float(df["Total.Cup.Points"].max())
    score_range = st.slider("🏆 Total Cup Points",
                             sc_min, sc_max, (sc_min, sc_max))

    # 7. Numerical Range Slider – Altitude
    alt_min = float(df["altitude_mean_meters"].min())
    alt_max = float(df["altitude_mean_meters"].max())
    alt_range = st.slider("⛰️ Altitude (m)",
                           alt_min, alt_max, (alt_min, alt_max))

    # 8. Search / Text Filter
    search = st.text_input("🔍 Search (Country / Variety / Owner)",
                            value="" if reset else "")

    st.session_state["reset"] = False
    st.markdown("---")
    st.caption("All charts update simultaneously when filters change.")

# ── APPLY FILTERS ─────────────────────────────────────────────────────────────
fdf = apply_filters(df, countries, proc, varieties, colors,
                    score_range, alt_range, year_range, search)

# ── BANNER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="banner">
  <div style="text-align:center; margin-bottom:16px;">
    <div style="font-size:0.68rem; letter-spacing:4px; text-transform:uppercase; color:#F5E6D0; opacity:0.75;">Created By</div>
    <div style="font-family:'Playfair Display',serif; font-size:1.9rem; color:#F5E6D0; font-weight:700; letter-spacing:2px;">Faiqa Eman</div>
    <div style="width:60px; height:2px; background:linear-gradient(90deg,transparent,#F5E6D0,transparent); margin:6px auto 0;"></div>
  </div>
  <h1 style="text-align:center;">☕ Coffee Quality Dashboard</h1>
  <p style="text-align:center;">1,311 Arabica samples graded by Q-graders on Aroma, Flavor, Body, Acidity & Balance
  &nbsp;·&nbsp; Exploratory Data Analysis &nbsp;·&nbsp; Instructor: Ali Hassan Sherazi</p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ────────────────────────────────────────────────────────────────
total   = len(fdf)
avg_sc  = fdf["Total.Cup.Points"].mean() if total else 0
high_sc = fdf["Total.Cup.Points"].max()  if total else 0
low_sc  = fdf["Total.Cup.Points"].min()  if total else 0
avg_ar  = fdf["Aroma"].mean()            if total else 0
countries_n = fdf["Country.of.Origin"].nunique() if total else 0

st.markdown(f"""
<div class="kpi-row">
  <div class="kpi"><span class="val">{total:,}</span><span class="lbl">Total Records</span></div>
  <div class="kpi"><span class="val">{avg_sc:.2f}</span><span class="lbl">Avg Cup Score</span></div>
  <div class="kpi"><span class="val">{high_sc:.2f}</span><span class="lbl">Highest Score</span></div>
  <div class="kpi"><span class="val">{low_sc:.2f}</span><span class="lbl">Lowest Score</span></div>
  <div class="kpi"><span class="val">{avg_ar:.2f}</span><span class="lbl">Avg Aroma</span></div>
  <div class="kpi"><span class="val">{countries_n}</span><span class="lbl">Countries</span></div>
</div>
""", unsafe_allow_html=True)

if total == 0:
    st.warning("No records match the current filters. Please adjust the sidebar filters.")
    st.stop()

# ── SECTION 1: Distribution Charts ───────────────────────────────────────────
st.markdown('<div class="sec-head">📊 Distribution Analysis</div>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(histogram(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(pie_chart(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 2: Categorical Analysis ──────────────────────────────────────────
st.markdown('<div class="sec-head">🌍 Categorical Analysis</div>', unsafe_allow_html=True)
c3, c4 = st.columns(2)
with c3:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(bar_chart(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c4:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(count_plot(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 3: Time Series ────────────────────────────────────────────────────
st.markdown('<div class="sec-head">📈 Trends Over Time</div>', unsafe_allow_html=True)
c5, c6 = st.columns(2)
with c5:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(line_chart(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c6:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(area_chart(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 4: Relationship & Spread ─────────────────────────────────────────
st.markdown('<div class="sec-head">🔬 Relationship & Spread Analysis</div>', unsafe_allow_html=True)
c7, c8 = st.columns(2)
with c7:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(scatter_plot(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c8:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(box_plot(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 5: Advanced ───────────────────────────────────────────────────────
st.markdown('<div class="sec-head">🎻 Advanced Visualisations</div>', unsafe_allow_html=True)
c9, c10 = st.columns(2)
with c9:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(violin_plot(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
with c10:
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(heatmap(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── SECTION 6: BONUS Pair Plot (full width) ───────────────────────────────────
st.markdown('<div class="sec-head">✨ Bonus: Pair Plot</div>', unsafe_allow_html=True)
with st.expander("Show Pair Plot (may take a moment to render)", expanded=False):
    st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
    st.pyplot(pair_plot(fdf), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── RAW DATA PREVIEW ─────────────────────────────────────────────────────────
st.markdown('<div class="sec-head">🗃️ Filtered Data Preview</div>', unsafe_allow_html=True)
with st.expander("Show filtered data table"):
    st.dataframe(fdf.head(200), use_container_width=True)

st.caption("Dashboard by Faiqa Eman  ·  Course: Exploratory Data Analysis  ·  Instructor: Ali Hassan Sherazi")