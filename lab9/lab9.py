"""Lab 9: Design Principles and Chartjunk.

The app shows the same branch sales as a cluttered chart and as an improved
chart. Changes from the lab's starter code are marked with "CHANGE".
"""
import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

AUTHOR = "[Your Name]"  # CHANGE: put your name here before you submit
SOURCE_NOTE = f"Data: fictional practice values (2026) | Chart: {AUTHOR}"

NEUTRAL = "#4C78A8"  # blue for the other bars
ACCENT = "#E07A3F"   # orange for the top branch (readable with blue for colour-blind viewers)

st.set_page_config(page_title="Lab 9 | Chart Design", layout="wide")

# CHANGE: added two branches (Central and Coastal). The values are still fictional
# and close together, so a truncated axis would still exaggerate the gaps.
all_data = pd.DataFrame({
    "Branch": ["North", "South", "East", "West", "Central", "Coastal"],
    "Sales": [96, 99, 98, 100, 95, 97],
})

st.title("Designing a Clearer Bar Chart")
version = st.radio("Choose a chart", ["Cluttered", "Improved"], horizontal=True)
# CHANGE: switch between the original four branches and all six
show_all = st.checkbox("Show all six branches (adds Central and Coastal)", value=True)
data = all_data if show_all else all_data.iloc[:4]

fig, ax = plt.subplots(figsize=(8, 4.5))

if version == "Cluttered":
    # Kept as-is on purpose so the two versions can be compared
    bars = ax.bar(data["Branch"], data["Sales"],
                  color=["#8FB9A8", "#D8B365", "#B2ABD2", "#5E3C99",
                         "#A6D96A", "#F4A582"][:len(data)])
    # Truncated axis starts just below the smallest value (the misleading choice)
    ax.set_ylim(data["Sales"].min() - 1, 101)
    ax.set_facecolor("#E8E8E8")
    ax.grid(True, which="both", color="white", linewidth=2)
    ax.set_title("SALES PERFORMANCE!!!")
    ax.set_ylabel("Sales (units)")
else:
    # CHANGE: sort from highest to lowest so the ranking is easy to read
    data = data.sort_values("Sales", ascending=False)
    top = data.loc[data["Sales"].idxmax(), "Branch"]
    colors = [ACCENT if b == top else NEUTRAL for b in data["Branch"]]
    bars = ax.bar(data["Branch"], data["Sales"], color=colors, width=0.6)

    # Zero baseline and natural increments keep bar length proportional to value
    ax.set_ylim(0, 110)
    ax.set_yticks(range(0, 101, 20))
    labels = ax.bar_label(bars, fmt="%.0f", padding=3, fontsize=10)
    # CHANGE: the top value is also bold, so the highlight doesn't rely on colour alone
    for branch, label in zip(data["Branch"], labels):
        if branch == top:
            label.set_fontweight("bold")

    # CHANGE: the title states the message, including how small the differences are
    spread = data["Sales"].max() - data["Sales"].min()
    ax.set_title(f"{top} branch sold the most, but all {len(data)} branches "
                 f"were within {spread} units of each other",
                 loc="left", fontsize=12)
    ax.set_ylabel("Sales (units)")

    # CHANGE: removed the horizontal gridlines. Every bar has its own value label,
    # so the gridlines added nothing. The left axis stays because it shows the
    # scale starts at zero.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(axis="both", labelsize=10)

# CHANGE: source and author note on the chart itself, so it stays with any copy
fig.text(0.01, 0.01, SOURCE_NOTE, fontsize=8, color="#555555", ha="left")
fig.tight_layout(rect=(0, 0.04, 1, 1))
st.pyplot(fig, clear_figure=True)
st.caption("Fictional practice data. The improved bar chart starts at zero.")
