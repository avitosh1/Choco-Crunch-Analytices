import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------- CONFIG ----------------
st.set_page_config(page_title="ChocoCrunch Analytics", layout="wide")

st.title("🍫 ChocoCrunch Analytics Dashboard")

# ---------------- DB ----------------
conn = sqlite3.connect("chococrunch.db")

# ---------------- LOAD DATA ----------------
query = """
SELECT p.product_name, p.brand,
       n.energy_kcal_value, n.sugars_value, n.fat_value,
       d.calorie_category, d.sugar_category, d.is_ultra_processed
FROM product_info p
JOIN nutrient_info n ON p.product_code = n.product_code
JOIN derived_metrics d ON p.product_code = d.product_code
"""
full_df = pd.read_sql(query, conn)

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

full_df['brand'] = full_df['brand'].str.lower()
full_df['calorie_category'] = full_df['calorie_category'].astype(str)
full_df['sugar_category'] = full_df['sugar_category'].astype(str)

st.sidebar.header("🔍 Filters")

brand_filter = st.sidebar.selectbox(
    "Brand",
    ["All"] + sorted(full_df['brand'].dropna().unique().tolist())
)

calorie_filter = st.sidebar.selectbox(
    "Calorie Category",
    ["All"] + sorted(full_df['calorie_category'].dropna().unique().tolist())
)

sugar_filter = st.sidebar.selectbox(
    "Sugar Category",
    ["All"] + sorted(full_df['sugar_category'].dropna().unique().tolist())
)

# Apply filters
df = full_df.copy()

if brand_filter != "All":
    df = df[df['brand'] == brand_filter]

if calorie_filter != "All":
    df = df[df['calorie_category'] == calorie_filter]

if sugar_filter != "All":
    df = df[df['sugar_category'] == sugar_filter]

if df.empty:
    st.warning("⚠️ No data found for selected filters. Try different options.")
    st.stop()

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 EDA", "🧾 SQL Queries", "🧠 Insights"])

# ================= TAB 1: OVERVIEW =================
with tab1:
    st.subheader("📊 Key Metrics")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Products", len(df))
    col2.metric("Avg Calories", round(df['energy_kcal_value'].mean(),2))
    col3.metric("Avg Sugar", round(df['sugars_value'].mean(),2))
    col4.metric("Ultra Processed %", f"{round((df['is_ultra_processed']=='Yes').mean()*100,2)}%")

# ================= TAB 2: EDA =================
with tab2:
    st.subheader("📈 Data Visualizations")

    col1, col2 = st.columns(2)

    with col1:
        fig, ax = plt.subplots()
        df['calorie_category'].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Calorie Category Distribution")
        st.pyplot(fig)

    with col2:
        fig, ax = plt.subplots()
        df['sugar_category'].value_counts().plot(kind='bar', ax=ax)
        ax.set_title("Sugar Category Distribution")
        st.pyplot(fig)

    col3, col4 = st.columns(2)

    with col3:
        fig, ax = plt.subplots()
        sns.scatterplot(x='energy_kcal_value', y='sugars_value', data=df, ax=ax)
        ax.set_title("Calories vs Sugar")
        st.pyplot(fig)

    with col4:
        fig, ax = plt.subplots()
        pd.crosstab(df['calorie_category'], df['is_ultra_processed']).plot(kind='bar', stacked=True, ax=ax)
        ax.set_title("Ultra Processed vs Calorie Category")
        st.pyplot(fig)

# ================= TAB 3: SQL QUERIES =================
with tab3:
    st.subheader("🧾 SQL Queries (All 27)")

    queries = {
        "Q1 Count products per brand": "SELECT brand, COUNT(*) FROM product_info GROUP BY brand",
        "Q2 Unique products per brand": "SELECT brand, COUNT(DISTINCT product_code) FROM product_info GROUP BY brand",
        "Q3 Top 5 brands": "SELECT brand, COUNT(*) as count FROM product_info GROUP BY brand ORDER BY count DESC LIMIT 5",
        "Q4 Missing product names": "SELECT * FROM product_info WHERE product_name IS NULL OR TRIM(product_name)=''",
        "Q5 Unique brands": "SELECT COUNT(DISTINCT brand) FROM product_info",
        "Q6 Codes starting with 3": "SELECT * FROM product_info WHERE product_code LIKE '3%'",

        "Q7 Top calories": "SELECT * FROM nutrient_info ORDER BY energy_kcal_value DESC LIMIT 10",
        "Q8 Avg sugar per nova": "SELECT nova_group, AVG(sugars_value) FROM nutrient_info GROUP BY nova_group",
        "Q9 Fat >20": "SELECT COUNT(*) FROM nutrient_info WHERE fat_value > 20",
        "Q10 Avg carbs": "SELECT product_code, AVG(carbohydrates_value) FROM nutrient_info GROUP BY product_code",
        "Q11 Sodium >1": "SELECT * FROM nutrient_info WHERE sodium_value > 1",
        "Q12 Fruits/veg >0": "SELECT COUNT(*) FROM nutrient_info WHERE fruits_veg_nuts > 0",
        "Q13 Calories >500": "SELECT * FROM nutrient_info WHERE energy_kcal_value > 500",

        "Q14 Count calorie category": "SELECT calorie_category, COUNT(*) FROM derived_metrics GROUP BY calorie_category",
        "Q15 High sugar count": "SELECT COUNT(*) FROM derived_metrics WHERE sugar_category='High Sugar'",
        "Q16 Avg ratio high calorie": "SELECT AVG(sugar_to_carb_ratio) FROM derived_metrics WHERE calorie_category='High'",
        "Q17 High cal & sugar": "SELECT * FROM derived_metrics WHERE calorie_category='High' AND sugar_category='High Sugar'",
        "Q18 Ultra processed count": "SELECT COUNT(*) FROM derived_metrics WHERE is_ultra_processed='Yes'",
        "Q19 Ratio >0.7": "SELECT * FROM derived_metrics WHERE sugar_to_carb_ratio > 0.7",
        "Q20 Avg ratio by category": "SELECT calorie_category, AVG(sugar_to_carb_ratio) FROM derived_metrics GROUP BY calorie_category",

        "Q21 Top brands high cal": "SELECT p.brand, COUNT(*) FROM product_info p JOIN derived_metrics d ON p.product_code=d.product_code WHERE d.calorie_category='High' GROUP BY p.brand ORDER BY COUNT(*) DESC LIMIT 5",
        "Q22 Avg calories category": "SELECT d.calorie_category, AVG(n.energy_kcal_value) FROM derived_metrics d JOIN nutrient_info n ON d.product_code=n.product_code GROUP BY d.calorie_category",
        "Q23 Ultra per brand": "SELECT p.brand, COUNT(*) FROM product_info p JOIN derived_metrics d ON p.product_code=d.product_code WHERE d.is_ultra_processed='Yes' GROUP BY p.brand",
        "Q24 High sugar & cal": "SELECT p.brand, d.product_code FROM derived_metrics d JOIN product_info p ON d.product_code=p.product_code WHERE d.calorie_category='High' AND d.sugar_category='High Sugar'",
        "Q25 Avg sugar ultra": "SELECT p.brand, AVG(n.sugars_value) FROM product_info p JOIN nutrient_info n ON p.product_code=n.product_code JOIN derived_metrics d ON p.product_code=d.product_code WHERE d.is_ultra_processed='Yes' GROUP BY p.brand",
        "Q26 Fruits by category": "SELECT d.calorie_category, COUNT(*) FROM derived_metrics d JOIN nutrient_info n ON d.product_code=n.product_code WHERE n.fruits_veg_nuts > 0 GROUP BY d.calorie_category",
        "Q27 Top ratio": "SELECT * FROM derived_metrics ORDER BY sugar_to_carb_ratio DESC LIMIT 5"
    }

    selected_query = st.selectbox("Select Query", list(queries.keys()))
    result = pd.read_sql(queries[selected_query], conn)

    st.dataframe(result)

# ================= TAB 4: INSIGHTS =================
with tab4:
    st.subheader("🧠 Key Insights")

    st.markdown("""
    - 🍬 High sugar products dominate the dataset  
    - ⚠️ Ultra-processed chocolates have higher calorie averages  
    - 🏭 Certain brands consistently produce high-calorie products  
    - 🔬 Many products have high sugar-to-carb ratios (>70%)  

    ### 💡 Recommendation:
    Consumers should prefer low sugar and minimally processed chocolates for better health.
    """)

st.markdown("---")
st.caption("© 2025 Avitosh Sood x Data Analytics Series")
