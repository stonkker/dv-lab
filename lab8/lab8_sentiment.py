"""
TFB3133/TEB3133 Data Visualization - Lab 8
Qualitative Data and Sentiment Analysis

Run with:   streamlit run lab8_sentiment.py
Install:    python -m pip install streamlit pandas matplotlib wordcloud vaderSentiment

Lesson 1  - synthetic comments + VADER sentiment labels
Lesson 2  - sentiment count chart, word cloud, original comments table
Lesson 3  - assignment edits (marked "ASSIGNMENT" below):
            2. stop-word changes + word-size caption
            3. audit of six labels + negation test
            4. a main topic per comment, sentiment by topic, summary for the product team
"""

import altair as alt
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS

# ==========================================================================
# Lesson 1: Creating the sample and classifying comments
# ==========================================================================
reviews = [
    "The bottle keeps my water cold all day.",
    "Great size and easy to carry to class.",
    "I love the simple design and sturdy lid.",
    "It leaks in my bag. Very disappointing.",
    "The cap is hard to open and the bottle feels heavy.",
    "Good value, but cleaning the narrow opening is difficult.",
    "Keeps drinks cold, though the paint scratches easily.",
    "The bottle is fine. Nothing special either way.",
    "I expected better insulation for this price.",
    "Lightweight, useful, and easy to wash.",
    "Not bad, but I would prefer a larger capacity.",
    "Excellent bottle. I use it every day.",
    "The lid broke after one week. Poor quality.",
    "It works as described and arrived on time.",
    "Nice color, but it does not keep drinks cold.",
    "Affordable and practical for carrying water.",
    "The bottle is okay; the handle is uncomfortable.",
    "Very happy with the purchase and the quality.",
]

# ASSIGNMENT 4: the main topic of each comment (assigned by hand, one per comment)
topics = [
    "Insulation",            # R01 keeps water cold
    "Size & portability",    # R02 size, easy to carry
    "Design",                # R03 simple design, sturdy lid
    "Durability & leaks",    # R04 leaks
    "Lid & cap",             # R05 cap hard to open
    "Cleaning",              # R06 narrow opening hard to clean
    "Insulation",            # R07 keeps cold (paint scratches is a second topic)
    "General",               # R08 fine, nothing special
    "Insulation",            # R09 expected better insulation
    "Cleaning",              # R10 easy to wash
    "Size & portability",    # R11 wants larger capacity
    "General",               # R12 excellent, use it every day
    "Durability & leaks",    # R13 lid broke after one week
    "General",               # R14 works as described, arrived on time
    "Insulation",            # R15 does not keep drinks cold
    "Price & value",         # R16 affordable and practical
    "Design",                # R17 handle uncomfortable
    "General",               # R18 happy with purchase and quality
]

df = pd.DataFrame({"id": [f"R{i:02}" for i in range(1, 19)],
                   "text": reviews,
                   "topic": topics})

analyzer = SentimentIntensityAnalyzer()


def label_sentiment(text):
    score = analyzer.polarity_scores(text)["compound"]
    if score >= 0.05:
        return "Positive", score
    if score <= -0.05:
        return "Negative", score
    return "Neutral", score


df[["sentiment", "compound"]] = df["text"].apply(
    lambda text: pd.Series(label_sentiment(text)))
df["compound"] = df["compound"].astype(float)

ORDER = ["Positive", "Neutral", "Negative"]
COLOURS = ["#1baf7a", "#9aa0a6", "#e34948"]   # green / grey / red, same in every chart


# ==========================================================================
# Lesson 2: The Streamlit dashboard
# ==========================================================================
st.set_page_config(page_title="Lab 8 | Feedback", layout="wide")
st.title("Product Feedback: A Text Summary")
st.caption("Practice data only. Automated labels need human review.")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Comments", len(df))
for col, s in zip([c2, c3, c4], ORDER):
    col.metric(s, int((df["sentiment"] == s).sum()))

left, right = st.columns(2)
with left:
    st.subheader("Comment counts by sentiment")
    counts = df["sentiment"].value_counts().reindex(ORDER, fill_value=0)
    count_df = pd.DataFrame({"Sentiment": ORDER, "Number of comments": counts.values})
    count_chart = alt.Chart(count_df).mark_bar(cornerRadiusEnd=4, height=34).encode(
        x=alt.X("Number of comments:Q", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("Sentiment:N", sort=ORDER, title=None),
        color=alt.Color("Sentiment:N", scale=alt.Scale(domain=ORDER, range=COLOURS), legend=None),
        tooltip=["Sentiment", "Number of comments"],
    )
    count_labels = count_chart.mark_text(align="left", dx=6, color="#333").encode(
        text="Number of comments:Q")
    st.altair_chart((count_chart + count_labels).properties(height=200), width="stretch")
    st.caption("Each comment gets exactly one label, so a comment that both praises and "
               "criticises the bottle is counted in only one bar.")

with right:
    st.subheader("Words used in the comments")
    # ASSIGNMENT 2: stop-word changes
    #  - ADDED "day": it is frequent ("all day", "every day") but says nothing about the product.
    #  - KEPT "not": the default list removes it, which hides complaints such as
    #    "does not keep drinks cold". Keeping it shows readers that negation appears in the feedback.
    stop_words = (set(STOPWORDS) | {"bottle", "drinks", "drink", "day"}) - {"not"}
    cloud = WordCloud(width=900, height=500, background_color="white",
                      colormap="viridis", stopwords=stop_words,
                      collocations=False, random_state=1).generate(" ".join(df["text"]))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.imshow(cloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig, clear_figure=True)
    st.caption("Bigger word = used more often (after filler words are removed). Position and "
               "colour mean nothing, and size ignores context: \"cold\" is large, but one of its "
               "uses is a complaint (\"does not keep drinks cold\"). With only 18 comments, a word "
               "used 3 times looks big.")

st.subheader("Review the original comments")
st.dataframe(df[["id", "text", "topic", "sentiment", "compound"]],
             width="stretch", hide_index=True,
             column_config={"id": "ID", "text": "Comment", "topic": "Main topic",
                            "sentiment": "Sentiment", "compound": st.column_config.NumberColumn(
                                "Compound score", format="%.3f")})
st.caption("A compound score is a model output, not a confidence rating.")


# ==========================================================================
# ASSIGNMENT 3: Audit sentiment labels
# ==========================================================================
st.header("Audit of the automated labels")
st.write("Six comments reviewed by hand - two of each label VADER gave.")

audit = pd.DataFrame([
    ("R12", "Positive", "Positive", "Reasonable",
     "Clear praise (\"Excellent\")."),
    ("R09", "Positive", "Negative", "Incorrect",
     "A complaint - insulation was worse than expected. VADER reacts to the word \"better\"."),
    ("R14", "Neutral", "Neutral / slightly positive", "Reasonable",
     "Factual; meeting expectations is mildly positive."),
    ("R01", "Neutral", "Positive", "Borderline",
     "Keeping water cold all day is praise, but none of the words are in VADER's emotion list."),
    ("R13", "Negative", "Negative", "Reasonable",
     "Product broke - clearly negative."),
    ("R08", "Negative", "Neutral", "Incorrect",
     "\"Fine... nothing special\" is neutral; \"nothing\" pulls the score below -0.05."),
], columns=["ID", "VADER label", "My judgement", "Verdict", "Why"])
audit.insert(1, "Comment", audit["ID"].map(df.set_index("id")["text"]))
audit.insert(3, "Score", audit["ID"].map(df.set_index("id")["compound"]).round(3))
st.table(audit.set_index("ID").style.format({"Score": "{:+.3f}"}))
st.caption("Other questionable labels: R15 (\"does not keep drinks cold\") is labelled Positive "
           "because of \"Nice\", and R16 (\"Affordable and practical\") is Neutral although it is praise. "
           "That is 5 of 18 labels (28%) worth questioning.")

st.subheader("Negation test")
original = "The bottle is easy to clean."
test = st.text_input("Type a comment to score", "The bottle is not easy to clean.")
t1, t2 = st.columns(2)
for col, text, name in [(t1, original, "Without negation"), (t2, test, "Your comment")]:
    lab, sc = label_sentiment(text)
    col.metric(f"{name}: \"{text}\"", lab, f"{sc:+.3f}")
st.caption("VADER handles a simple \"not\" correctly: the label flips from Positive to Negative. "
           "It is weaker with sarcasm, expectations (\"expected better\") and mixed sentences.")


# ==========================================================================
# ASSIGNMENT 4: Compare by topic and communicate
# ==========================================================================
st.header("Sentiment by topic")
by_topic = (pd.crosstab(df["topic"], df["sentiment"])
            .reindex(columns=ORDER, fill_value=0))
by_topic["Total"] = by_topic.sum(axis=1)
by_topic = by_topic.sort_values("Total", ascending=False)

tl, tr = st.columns([1.4, 1])
with tl:
    long = by_topic[ORDER].reset_index().melt(id_vars="topic", var_name="Sentiment",
                                               value_name="Comments")
    topic_chart = alt.Chart(long[long["Comments"] > 0]).mark_bar(
        stroke="white", strokeWidth=2).encode(
        x=alt.X("sum(Comments):Q", title="Number of comments", axis=alt.Axis(tickMinStep=1)),
        y=alt.Y("topic:N", sort=list(by_topic.index), title="Main topic"),
        color=alt.Color("Sentiment:N", scale=alt.Scale(domain=ORDER, range=COLOURS),
                        legend=alt.Legend(orient="bottom")),
        order=alt.Order("sort_key:Q"),
        tooltip=[alt.Tooltip("topic:N", title="Topic"), "Sentiment:N", "Comments:Q"],
    ).transform_calculate(
        sort_key="indexof(['Positive','Neutral','Negative'], datum.Sentiment)")
    st.altair_chart(topic_chart.properties(height=320), width="stretch")
with tr:
    st.dataframe(by_topic.rename_axis("Main topic"), width="stretch")
st.warning("**Too small for a fair comparison.** Most topics have only 1-2 comments, and the largest "
           "(Insulation) has 4. One extra comment could flip any topic's result. VADER also calls "
           "Insulation 3 positive / 1 neutral, but a human reads 2 of those 4 as complaints "
           "(R09, R15) - so the topic chart inherits the labelling errors.")

with st.expander("Summary for the product team", expanded=True):
    st.markdown(
        "**Finding.** Of 18 practice comments, the automated tool labels 9 positive, 3 neutral and "
        "6 negative. Praise centres on portability and ease of use (\"easy to carry\", \"easy to "
        "wash\", \"lightweight\"). Complaints concentrate on physical quality: a leak, a lid that "
        "broke within a week, a hard-to-open cap, an uncomfortable handle and scratched paint.\n\n"
        "**Limitation.** The labels are not reliable enough to report on their own. A manual check "
        "found about 5 of 18 labels questionable. Two insulation complaints (\"expected better "
        "insulation\", \"does not keep drinks cold\") were labelled positive, so the tool makes "
        "insulation look better than customers describe it. Several comments are mixed and fit no "
        "single label, and 18 synthetic comments cannot represent real customers.\n\n"
        "**Recommendation.** Collect a larger set of real reviews, and ask customers to rate "
        "specific features (lid, insulation, cleaning, price) on a short scale alongside a free-text "
        "comment. Have a person label a random sample to measure how often the tool is wrong before "
        "trusting its counts."
    )


# ==========================================================================
# ASSIGNMENT 1: Run and describe
# ==========================================================================
with st.expander("Assignment notes - run and describe"):
    st.markdown(
        "- **Check:** the app shows **18 comments**, each with a sentiment label and score.\n"
        "- **Largest group:** Positive, with 9 of 18 comments (Negative has 6, Neutral 3).\n"
        "- **Recurring theme:** \"cold\" is the biggest word, so keeping drinks cold (insulation) "
        "is the most discussed topic - but it appears in both praise and complaints.\n"
        "- **Mixed-tone comment:** R07 \"Keeps drinks cold, though the paint scratches easily\" is "
        "labelled Positive. The single label hides the complaint about the paint, so a team reading "
        "only the counts would miss a durability problem. R06 and R15 are also mixed."
    )
