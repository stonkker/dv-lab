"""Lab 10: Framing the Data Story.

The same skill ratings are told for three audiences. Changes from the lab's
starter code are marked with "CHANGE".
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

AUTHOR = "[Your Name]"  # CHANGE: put your name here
HIGHLIGHT = "#E07A3F"   # orange: the one point to notice
NEUTRAL = "#4C78A8"     # blue: everything else
MUTED = "#B8C4D6"       # light blue-grey, used for the annotation style

st.set_page_config(page_title="Lab 10 | Data Story", layout="wide")

skills = ["Data storytelling", "Python", "Chart selection",
          "Color and labels", "Data cleaning"]
original = [2.4, 3.0, 3.2, 3.7, 4.1]
# CHANGE: one rating changed. Python drops from 3.0 to 2.2, so the lowest skill
# (and therefore the takeaway) moves from data storytelling to Python.
updated = [2.4, 2.2, 3.2, 3.7, 4.1]

# ---- Controls -------------------------------------------------------------
c1, c2, c3 = st.columns(3)
audience = c1.selectbox("Audience", ["Students", "Workshop instructor",
                                     "Department manager"])
use_updated = c2.toggle("Use changed rating (Python 3.0 → 2.2)", value=False)
style = c3.radio("Highlight style", ["Colour", "Position + annotation"])

ratings = updated if use_updated else original
# CHANGE: sort lowest first so the skill needing support is always at the top
df = (pd.DataFrame({"Skill": skills, "Average rating": ratings})
      .sort_values("Average rating").reset_index(drop=True))
low = df.iloc[0]
low_skill, low_value = low["Skill"], low["Average rating"]
# Lower-case a skill mid-sentence, but keep proper nouns like Python
low_name = low_skill if low_skill == "Python" else low_skill.lower()

# CHANGE: the title is written for each audience and is built
# from the data, so it stays correct when a rating changes.
stories = {
    "Students": {
        "question": "Which skill should our next workshop cover?",
        "title": f"{low_skill} is our weakest skill — make it the next workshop",
    },
    "Workshop instructor": {
        "question": "What should I teach first, and at what level?",
        "title": f"Start with {low_name}: students rate it {low_value:.1f} / 5",
    },
    "Department manager": {
        "question": "Where should workshop time and budget go?",
        "title": f"Fund {low_name} training first — it is the largest skill gap",
    },
}
story = stories[audience]

# ---- Page -----------------------------------------------------------------
st.title("Plan a Workshop Around Students' Needs")
st.write(f"**Audience:** {audience}  ·  **Their question:** {story['question']}")

fig, ax = plt.subplots(figsize=(8, 4.5))
if style == "Colour":
    colors = [HIGHLIGHT if s == low_skill else NEUTRAL for s in df["Skill"]]
else:
    # CHANGE: alternative highlight. The lowest bar keeps full colour and sits
    # at the top; the others are muted, and a text note explains the point.
    colors = [NEUTRAL if s == low_skill else MUTED for s in df["Skill"]]
bars = ax.barh(df["Skill"], df["Average rating"], color=colors, height=0.6)

ax.set_xlim(0, 5)
ax.set_xticks(range(0, 6))
# CHANGE: revised label — says the values are class averages, not one student
ax.set_xlabel("Class average self-rating  (1 = beginner, 5 = confident)")
ax.set_title(story["title"], loc="left", fontsize=11.5)
ax.invert_yaxis()
# CHANGE: removed the vertical gridlines. Every bar is labelled with its value,
# so the gridlines only added clutter.
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.tick_params(axis="y", length=0)

for bar, (skill, value) in zip(bars, zip(df["Skill"], df["Average rating"])):
    ax.text(value + 0.05, bar.get_y() + bar.get_height() / 2, f"{value:.1f}",
            va="center", fontweight="bold" if skill == low_skill else "normal")

if style == "Position + annotation":
    ax.annotate("Lowest rating → focus of the next workshop",
                xy=(low_value + 0.35, 0), xytext=(low_value + 0.9, 0),
                va="center", fontsize=10, color="#333333",
                arrowprops=dict(arrowstyle="->", color="#333333"))

fig.text(0.01, 0.01,
         f"Data: fictional practice values (2026), class averages on a 1–5 scale "
         f"| Chart: {AUTHOR}", fontsize=8, color="#555555")
fig.tight_layout(rect=(0, 0.04, 1, 1))
st.pyplot(fig, clear_figure=True)

st.caption("Fictional practice values. Ratings are averages on a 1-5 scale.")
