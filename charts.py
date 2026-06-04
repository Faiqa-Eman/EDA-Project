"""
charts.py  –  All 10 required chart types + bonus pair-plot
WHY each chart is chosen for coffee data is documented inside each function.
Matplotlib + Seaborn are MANDATORY per rubric; we use them exclusively here.
"""

import matplotlib
matplotlib.use("Agg")          # non-interactive backend (required for Streamlit)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import pandas as pd
import numpy as np

# ── Colour palette: warm espresso tones ──────────────────────────────────────
PALETTE   = ["#6F4E37","#C8A97E","#3D2B1F","#A0522D","#D2691E",
             "#8B4513","#F5DEB3","#DEB887","#BC8A5F","#7B3F00"]
BG        = "#1C1008"          # dark roast background
CARD_BG   = "#2A1A0E"
TEXT      = "#F5E6D0"
ACCENT    = "#C8A97E"

def _style(fig, ax_list=None):
    """Apply consistent dark-roast theme to any figure."""
    fig.patch.set_facecolor(BG)
    if ax_list is None:
        ax_list = fig.get_axes()
    for ax in ax_list:
        ax.set_facecolor(CARD_BG)
        ax.tick_params(colors=TEXT, labelsize=9)
        ax.xaxis.label.set_color(TEXT)
        ax.yaxis.label.set_color(TEXT)
        ax.title.set_color(ACCENT)
        for spine in ax.spines.values():
            spine.set_edgecolor("#3D2B1F")


# ── 1. PIE CHART ─────────────────────────────────────────────────────────────
def pie_chart(df: pd.DataFrame) -> plt.Figure:
    """
    WHY PIE: Shows proportional split of coffee samples by Processing Method.
    Categorical distribution is immediately readable in pie form.
    """
    counts = df["Processing.Method"].value_counts().head(6)
    fig, ax = plt.subplots(figsize=(6, 5))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct="%1.1f%%",
        colors=PALETTE[:len(counts)],
        startangle=140,
        wedgeprops=dict(edgecolor=BG, linewidth=1.5),
    )
    for t in texts + autotexts:
        t.set_color(TEXT)
        t.set_fontsize(9)
    ax.set_title("Processing Method Distribution", fontsize=13, pad=12)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 2. HISTOGRAM ─────────────────────────────────────────────────────────────
def histogram(df: pd.DataFrame) -> plt.Figure:
    """
    WHY HISTOGRAM: Total Cup Points is the primary grading score.
    Histogram reveals whether scores are normally distributed, skewed, or bimodal.
    """
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.histplot(df["Total.Cup.Points"], bins=30, kde=True,
                 color=PALETTE[0], edgecolor=BG, ax=ax)
    ax.lines[0].set_color(ACCENT)
    ax.set_xlabel("Total Cup Points")
    ax.set_ylabel("Count")
    ax.set_title("Distribution of Total Cup Points", fontsize=13)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 3. LINE CHART ─────────────────────────────────────────────────────────────
def line_chart(df: pd.DataFrame) -> plt.Figure:
    """
    WHY LINE: Tracks average Total Cup Points per Grading Year.
    Time-series line reveals quality trends over years.
    """
    yearly = (
        df.groupby("Grading.Year")["Total.Cup.Points"]
        .mean()
        .reset_index()
        .dropna()
        .sort_values("Grading.Year")
    )
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(yearly["Grading.Year"], yearly["Total.Cup.Points"],
            color=ACCENT, linewidth=2.5, marker="o", markersize=5,
            markerfacecolor=PALETTE[0])
    ax.fill_between(yearly["Grading.Year"], yearly["Total.Cup.Points"],
                    alpha=0.15, color=ACCENT)
    ax.set_xlabel("Grading Year")
    ax.set_ylabel("Avg Total Cup Points")
    ax.set_title("Average Cup Score Trend by Year", fontsize=13)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 4. BAR CHART ─────────────────────────────────────────────────────────────
def bar_chart(df: pd.DataFrame) -> plt.Figure:
    """
    WHY BAR: Compares average Total Cup Points across top 10 countries.
    Bar chart is the clearest way to rank discrete categories.
    """
    top = (
        df.groupby("Country.of.Origin")["Total.Cup.Points"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(top["Country.of.Origin"], top["Total.Cup.Points"],
                   color=PALETTE[:10], edgecolor=BG)
    ax.set_xlabel("Avg Total Cup Points")
    ax.set_title("Top 10 Countries by Avg Cup Score", fontsize=13)
    ax.invert_yaxis()
    for bar, val in zip(bars, top["Total.Cup.Points"]):
        ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
                f"{val:.2f}", va="center", color=TEXT, fontsize=8)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 5. SCATTER PLOT ───────────────────────────────────────────────────────────
def scatter_plot(df: pd.DataFrame) -> plt.Figure:
    """
    WHY SCATTER: Plots Aroma vs Flavor (two key Q-grader scores).
    Reveals correlation strength; colored by Processing Method for extra insight.
    """
    methods = df["Processing.Method"].unique()[:5]
    color_map = dict(zip(methods, PALETTE))
    fig, ax = plt.subplots(figsize=(7, 5))
    for method in methods:
        sub = df[df["Processing.Method"] == method]
        ax.scatter(sub["Aroma"], sub["Flavor"], label=method,
                   color=color_map[method], alpha=0.6, s=30, edgecolors="none")
    ax.set_xlabel("Aroma Score")
    ax.set_ylabel("Flavor Score")
    ax.set_title("Aroma vs Flavor by Processing Method", fontsize=13)
    legend = ax.legend(fontsize=8, facecolor=CARD_BG, labelcolor=TEXT,
                       edgecolor="#3D2B1F")
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 6. BOX PLOT ───────────────────────────────────────────────────────────────
def box_plot(df: pd.DataFrame) -> plt.Figure:
    """
    WHY BOX PLOT: Shows spread, median, and outliers for the 6 primary Q-grader
    sensory scores. Lets viewer compare variability across attributes at a glance.
    """
    cols = ["Aroma","Flavor","Aftertaste","Acidity","Body","Balance"]
    melted = df[cols].melt(var_name="Attribute", value_name="Score")
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.boxplot(data=melted, x="Attribute", y="Score", hue="Attribute",
                palette=PALETTE[:6], ax=ax, legend=False,
                flierprops=dict(marker="o", color=ACCENT, markersize=3))
    ax.set_xlabel("Sensory Attribute")
    ax.set_ylabel("Score")
    ax.set_title("Score Distribution Across Sensory Attributes", fontsize=13)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 7. HEATMAP ────────────────────────────────────────────────────────────────
def heatmap(df: pd.DataFrame) -> plt.Figure:
    """
    WHY HEATMAP: Correlation matrix of all numeric sensory scores.
    Reveals which attributes co-vary – critical for understanding Q-grader behavior.
    """
    num_cols = ["Aroma","Flavor","Aftertaste","Acidity","Body","Balance",
                "Uniformity","Clean.Cup","Sweetness","Total.Cup.Points"]
    corr = df[num_cols].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="YlOrBr",
                linewidths=0.5, linecolor=BG,
                annot_kws={"size": 7, "color": "#1C1008"},
                ax=ax)
    ax.set_title("Feature Correlation Heatmap", fontsize=13)
    ax.tick_params(axis="x", rotation=45)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 8. AREA CHART ─────────────────────────────────────────────────────────────
def area_chart(df: pd.DataFrame) -> plt.Figure:
    """
    WHY AREA: Cumulative number of coffee samples graded per year.
    Area fill emphasises volume growth of the dataset / industry over time.
    """
    yearly = (
        df.groupby("Grading.Year").size()
        .reset_index(name="Count")
        .sort_values("Grading.Year")
        .dropna()
    )
    yearly["Cumulative"] = yearly["Count"].cumsum()
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.fill_between(yearly["Grading.Year"], yearly["Cumulative"],
                    color=PALETTE[0], alpha=0.7)
    ax.plot(yearly["Grading.Year"], yearly["Cumulative"],
            color=ACCENT, linewidth=2)
    ax.set_xlabel("Year")
    ax.set_ylabel("Cumulative Samples")
    ax.set_title("Cumulative Coffee Samples Graded Over Time", fontsize=13)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 9. COUNT PLOT ─────────────────────────────────────────────────────────────
def count_plot(df: pd.DataFrame) -> plt.Figure:
    """
    WHY COUNT PLOT: Frequency of coffee bean Color categories.
    Categorical count plot immediately shows data imbalance.
    """
    order = df["Color"].value_counts().index
    fig, ax = plt.subplots(figsize=(7, 4))
    sns.countplot(data=df, x="Color", hue="Color", order=order, legend=False,
                  palette=PALETTE[:len(order)], ax=ax,
                  edgecolor=BG)
    ax.set_xlabel("Bean Color")
    ax.set_ylabel("Count")
    ax.set_title("Frequency of Bean Color Categories", fontsize=13)
    ax.tick_params(axis="x", rotation=15)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── 10. VIOLIN PLOT ───────────────────────────────────────────────────────────
def violin_plot(df: pd.DataFrame) -> plt.Figure:
    """
    WHY VIOLIN: Shows full probability density of Flavor scores by Color.
    Violin is richer than box plot – shows bimodality if it exists.
    """
    top_colors = df["Color"].value_counts().head(4).index
    sub = df[df["Color"].isin(top_colors)]
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.violinplot(data=sub, x="Color", y="Flavor", hue="Color", legend=False,
                   palette=PALETTE[:4], inner="quartile", ax=ax)
    ax.set_xlabel("Bean Color")
    ax.set_ylabel("Flavor Score")
    ax.set_title("Flavor Score Distribution by Bean Color", fontsize=13)
    _style(fig, [ax])
    fig.tight_layout()
    return fig


# ── BONUS: PAIR PLOT ──────────────────────────────────────────────────────────
def pair_plot(df: pd.DataFrame) -> plt.Figure:
    """
    WHY PAIR PLOT (BONUS): Multi-dimensional view of Aroma, Flavor, Acidity, Body.
    Reveals pairwise relationships and class separation by Processing Method.
    """
    cols = ["Aroma","Flavor","Acidity","Body","Processing.Method"]
    sub  = df[cols].dropna()
    top_methods = sub["Processing.Method"].value_counts().head(4).index
    sub = sub[sub["Processing.Method"].isin(top_methods)]
    g = sns.pairplot(sub, hue="Processing.Method",
                     palette=dict(zip(top_methods, PALETTE)),
                     plot_kws=dict(alpha=0.5, s=15),
                     diag_kind="kde")
    g.figure.patch.set_facecolor(BG)
    g.figure.suptitle("Pair Plot: Key Sensory Attributes", y=1.01,
                       color=ACCENT, fontsize=12)
    for ax in g.axes.flatten():
        if ax:
            ax.set_facecolor(CARD_BG)
            ax.tick_params(colors=TEXT)
            ax.xaxis.label.set_color(TEXT)
            ax.yaxis.label.set_color(TEXT)
    return g.figure
