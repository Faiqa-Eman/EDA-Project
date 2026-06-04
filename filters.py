"""
filters.py - Data loading, cleaning, and filtering functions
WHY: Separating filter logic keeps app.py clean and makes each function testable.
"""

import pandas as pd
import numpy as np

# ── 1. LOAD & CLEAN ──────────────────────────────────────────────────────────

def load_data(path: str = "data/arabica_data_cleaned.csv") -> pd.DataFrame:
    """
    Load the dataset from disk.
    WHY: Centralised load means one place to fix path issues.
    """
    df = pd.read_csv(path)

    # Drop unnamed index column inserted by original CSV
    df.drop(columns=["Unnamed: 0"], errors="ignore", inplace=True)

    # ── Grading.Date → datetime (used for time-range filter) ──
    # WHY: Grading.Date is stored as string; converting lets us slice by year.
    df["Grading.Date"] = pd.to_datetime(df["Grading.Date"], errors="coerce")
    df["Grading.Year"] = df["Grading.Date"].dt.year

    # ── Harvest.Year: extract 4-digit year ──
    df["Harvest.Year.Clean"] = (
        df["Harvest.Year"]
        .astype(str)
        .str.extract(r"(\d{4})")
        .squeeze()
        .astype(float)
    )

    # ── Numerical: fill NaN with median to keep rows usable ──
    num_cols = [
        "Aroma","Flavor","Aftertaste","Acidity","Body","Balance",
        "Uniformity","Clean.Cup","Sweetness","Cupper.Points",
        "Total.Cup.Points","Moisture","altitude_mean_meters",
    ]
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    # ── Categorical: fill NaN with 'Unknown' ──
    cat_cols = ["Country.of.Origin","Variety","Processing.Method","Color"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").str.strip()

    # ── Remove obvious outlier rows (Total.Cup.Points == 0) ──
    df = df[df["Total.Cup.Points"] > 0].reset_index(drop=True)

    return df


# ── 2. FILTER ────────────────────────────────────────────────────────────────

def apply_filters(
    df: pd.DataFrame,
    countries: list,
    process_methods: list,
    varieties: list,
    colors: list,
    score_range: tuple,
    altitude_range: tuple,
    year_range: tuple,
    search_text: str,
) -> pd.DataFrame:
    """
    Apply all sidebar filters and return filtered DataFrame.
    WHY: One function → all charts call this → filters linked to ALL charts.
    """
    fdf = df.copy()

    # Category filters (dropdown / multi-select)
    if countries:
        fdf = fdf[fdf["Country.of.Origin"].isin(countries)]
    if process_methods:
        fdf = fdf[fdf["Processing.Method"].isin(process_methods)]
    if varieties:
        fdf = fdf[fdf["Variety"].isin(varieties)]
    if colors:
        fdf = fdf[fdf["Color"].isin(colors)]

    # Numerical range sliders
    fdf = fdf[
        (fdf["Total.Cup.Points"] >= score_range[0]) &
        (fdf["Total.Cup.Points"] <= score_range[1])
    ]
    fdf = fdf[
        (fdf["altitude_mean_meters"] >= altitude_range[0]) &
        (fdf["altitude_mean_meters"] <= altitude_range[1])
    ]

    # Date / time range filter
    fdf = fdf[
        (fdf["Grading.Year"] >= year_range[0]) &
        (fdf["Grading.Year"] <= year_range[1])
    ]

    # Search / text filter (searches Country, Variety, Owner)
    if search_text.strip():
        mask = (
            fdf["Country.of.Origin"].str.contains(search_text, case=False, na=False) |
            fdf["Variety"].str.contains(search_text, case=False, na=False) |
            fdf["Owner"].str.contains(search_text, case=False, na=False)
        )
        fdf = fdf[mask]

    return fdf.reset_index(drop=True)
