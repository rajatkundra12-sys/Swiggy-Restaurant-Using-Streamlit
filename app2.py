import streamlit as st
import pandas as pd
from textwrap import dedent

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="Restaurant Recommendation System",
    page_icon="🍽️",
    layout="wide"
)

# ================= CSS (FIXED) =================
st.markdown("""
<style>

/* MAIN BACKGROUND */
.stApp {
    background: linear-gradient(135deg,#fff7ed,#fffbeb,#f0f9ff);
}

/* SIDEBAR ONLY (STRICT SCOPE) */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#1f2937,#111827);
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: white !important;
}

/* SELECTED CARD */
.selected {
    background: linear-gradient(135deg,#fde68a,#fef3c7);
    padding:28px;
    border-radius:18px;
    margin-bottom:30px;
    box-shadow:0 15px 35px rgba(0,0,0,0.12);
}

/* RECOMMENDATION CARD */
.card {
    background:white;
    padding:22px;
    border-radius:16px;
    margin-bottom:18px;
    box-shadow:0 10px 25px rgba(0,0,0,0.08);
}
.card h3 {
    color:#111827 !important;
    font-weight:800;
}
.card p {
    color:#374151 !important;
    line-height:1.7;
}

</style>
""", unsafe_allow_html=True)

# ================= LOAD DATA =================
@st.cache_data
def load_data():
    return pd.read_csv("cleaned_data_with_clusters.csv")

df = load_data()

# ================= HEADER =================
st.markdown("<h1 style='text-align:center;color:#111827;'>🍽️ Restaurant Recommendation System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#6b7280;'>Smart Swiggy-style recommendations</p><hr>", unsafe_allow_html=True)

# ================= SIDEBAR =================
st.sidebar.header("🔍 Filter Your Choice")

city = st.sidebar.selectbox(
    "Select City",
    ["All Cities"] + sorted(df["city"].unique())
)

# Cuisine
all_cuisines = sorted(set(",".join(df["cuisine"]).split(",")))
cuisine = st.sidebar.selectbox(
    "Select Cuisine / Category",
    ["All"] + all_cuisines
)

# Filtered DF
filtered = df.copy()
if city != "All Cities":
    filtered = filtered[filtered["city"] == city]
if cuisine != "All":
    filtered = filtered[filtered["cuisine"].str.contains(cuisine, case=False, na=False)]

restaurant = st.sidebar.selectbox(
    "Select Restaurant",
    sorted(filtered["name"].unique())
)

top_n = st.sidebar.slider("Number of Recommendations", 5, 15, 10)

# ================= LOGIC =================
# ====== SAFETY CHECK ======
if filtered.empty:
    st.markdown("""
    <div style="
        background:#fff1f2;
        padding:25px;
        border-radius:16px;
        border-left:6px solid #ef4444;
        color:#7f1d1d;
        font-size:16px;
    ">
        😔 <b>No restaurants found</b><br><br>
        There are no <b>Arabian</b> restaurants available in <b>Abohar</b> right now.<br>
        Try changing the city or cuisine.
    </div>
    """, unsafe_allow_html=True)
    st.stop()
selected_row = filtered[filtered["name"] == restaurant].iloc[0]
cluster = selected_row["cluster"]

# Primary recommendations (city + cuisine)
recs = filtered[
    (filtered["cluster"] == cluster) &
    (filtered["name"] != restaurant)
]

# 🔥 FALLBACK: agar kam pad gaye
if len(recs) < top_n:
    fallback = df[
        (df["cluster"] == cluster) &
        (df["name"] != restaurant)
    ]
    recs = pd.concat([recs, fallback]).drop_duplicates()

recs = recs.sort_values(
    ["rating","rating_count"],
    ascending=False
).head(top_n)

# ================= SELECTED RESTAURANT =================
st.markdown(dedent(f"""
<div class="selected">
  <h2 style="color:#92400e;">⭐ Your Selected Restaurant</h2>
  <h3 style="color:#78350f;">🍴 {selected_row['name']}</h3>
  <p style="color:#78350f;font-size:16px;">
    📍 <b>{selected_row['city']}</b><br>
    🍽️ {selected_row['cuisine']}<br>
    ⭐ <b>{selected_row['rating']:.1f}</b> ({selected_row['rating_count']} reviews)<br>
    💰 Cost for two: <b>₹{selected_row['cost']}</b>
  </p>
</div>
"""), unsafe_allow_html=True)

# ================= RECOMMENDATIONS =================
st.markdown("<h2 style='color:#111827;'>🔥 Recommended for You</h2>", unsafe_allow_html=True)

for _, r in recs.iterrows():
    st.markdown(dedent(f"""
    <div class="card">
      <h3>🍴 {r['name']}</h3>
      <p>
        📍 <b>{r['city']}</b><br>
        🍽️ {r['cuisine']}<br>
        ⭐ <b>{r['rating']}</b> ({r['rating_count']} reviews)<br>
        💰 Cost for two: <b>₹{r['cost']}</b>
      </p>
    </div>
    """), unsafe_allow_html=True)

st.markdown("<hr><p style='text-align:center;color:#6b7280;'>Built with ❤️ using ML & Streamlit</p>", unsafe_allow_html=True)
