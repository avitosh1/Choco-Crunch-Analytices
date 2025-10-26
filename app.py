import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

st.set_page_config(page_title="ChocoCrunch Analytics", page_icon="🍫", layout="wide")
st.title("🍫 ChocoCrunch Analytics Dashboard")
st.markdown("### Sweet Stats & Sour Truths")

conn = sqlite3.connect("chococrunch.db")
st.sidebar.header("Select Analysis Type")
option = st.sidebar.selectbox(
    "Choose a view",
    [
        "Top 5 Brands by Product Count",
        "Calorie Category Distribution",
        "Sugar Category Distribution",
        "NOVA Group Distribution",
        "Top 10 Highest Calorie Products",
        "Sugar vs Calorie Scatter",
        "Sugar to Carb Ratio by Brand (Boxplot)",
        "Ultra-Processed Distribution",
        "Average Sugar per NOVA Group",
        "Fruit-Veg-Nut Products by Calorie Cat",
        "High Calorie & High Sugar Products",
        "Correlation Heatmap",
        "Treemap: Brand & Calorie Category",
        "KPI Cards (Calories, Sugar, Ultra-Processed)",
        "Brand: Ultra-processed Stacked",
    ]
)

if option == "Top 5 Brands by Product Count":
    q = "SELECT brand, COUNT(*) as count FROM product_info GROUP BY brand ORDER BY count DESC LIMIT 5;"
    df = pd.read_sql_query(q, conn)
    st.bar_chart(df.set_index("brand"))
    st.dataframe(df)

elif option == "Calorie Category Distribution":
    q = "SELECT calorie_category, COUNT(*) as count FROM derived_metrics GROUP BY calorie_category;"
    df = pd.read_sql_query(q, conn)
    fig = px.pie(df, names="calorie_category", values="count", title="Calorie Category Distribution")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

elif option == "Sugar Category Distribution":
    q = "SELECT sugar_category, COUNT(*) as count FROM derived_metrics GROUP BY sugar_category;"
    df = pd.read_sql_query(q, conn)
    fig = px.pie(df, names="sugar_category", values="count", title="Sugar Category Distribution")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

elif option == "NOVA Group Distribution":
    q = "SELECT `nova-group`, COUNT(*) as count FROM nutrient_info GROUP BY `nova-group`;"
    df = pd.read_sql_query(q, conn)
    fig = px.bar(df, x='nova-group', y='count', text='count', title="NOVA Group Distribution")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

elif option == "Top 10 Highest Calorie Products":
    q = "SELECT product_code, energy-kcal_value FROM nutrient_info ORDER BY energy-kcal_value DESC LIMIT 10;"
    df = pd.read_sql_query(q, conn)
    st.dataframe(df)

elif option == "Sugar vs Calorie Scatter":
    q = "SELECT n.sugars_value, n.`energy-kcal_value`, p.brand FROM nutrient_info n JOIN product_info p ON n.product_code = p.product_code"
    df = pd.read_sql_query(q, conn)
    fig = px.scatter(df, x="sugars_value", y="energy-kcal_value", color="brand", title="Calories vs Sugar Content")
    st.plotly_chart(fig, use_container_width=True)

elif option == "Sugar to Carb Ratio by Brand (Boxplot)":
    q = ("SELECT d.sugar_to_carb_ratio, p.brand FROM derived_metrics d "
         "JOIN product_info p ON d.product_code = p.product_code")
    df = pd.read_sql_query(q, conn)
    fig = px.box(df, x='brand', y='sugar_to_carb_ratio', points='all', title="Sugar/Carb Ratio by Brand")
    st.plotly_chart(fig, use_container_width=True)

elif option == "Ultra-Processed Distribution":
    q = "SELECT is_ultra_processed, COUNT(*) as count FROM derived_metrics GROUP BY is_ultra_processed;"
    df = pd.read_sql_query(q, conn)
    fig = px.pie(df, names="is_ultra_processed", values="count", title="Ultra-Processed vs Non-Processed")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

elif option == "Average Sugar per NOVA Group":
    q = "SELECT `nova-group`, AVG(sugars_value) as avg_sugar FROM nutrient_info GROUP BY `nova-group`;"
    df = pd.read_sql_query(q, conn)
    fig = px.bar(df, x='nova-group', y='avg_sugar', text='avg_sugar', title="Avg Sugar by NOVA Group")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

elif option == "Fruit-Veg-Nut Products by Calorie Cat":
    q = ("SELECT d.calorie_category, COUNT(*) as count FROM derived_metrics d "
         "JOIN nutrient_info n ON d.product_code = n.product_code "
         "WHERE n.`fruits-vegetables-nuts-estimate-from-ingredients_100g` > 0 GROUP BY calorie_category;")
    df = pd.read_sql_query(q, conn)
    fig = px.bar(df, x='calorie_category', y='count', text='count', title="Fruit/Veg/Nut Products by Calorie Category")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

elif option == "High Calorie & High Sugar Products":
    q = ("SELECT d.product_code, p.brand, d.sugar_to_carb_ratio FROM derived_metrics d "
         "JOIN product_info p ON d.product_code = p.product_code "
         "WHERE d.calorie_category = 'High' AND d.sugar_category = 'High Sugar'")
    df = pd.read_sql_query(q, conn)
    st.dataframe(df)

elif option == "Correlation Heatmap":
    df = pd.read_sql_query(
        "SELECT energy-kcal_value, sugars_value, fat_value, carbohydrates_value FROM nutrient_info", conn
    )
    corr = df.corr()
    st.write("Correlation Matrix")
    st.dataframe(corr)
    fig = px.imshow(corr, text_auto=True, title="Nutrient Correlation Heatmap")
    st.plotly_chart(fig, use_container_width=True)

elif option == "Treemap: Brand & Calorie Category":
    q = ("SELECT p.brand, d.calorie_category, COUNT(*) as count FROM product_info p "
         "JOIN derived_metrics d ON p.product_code=d.product_code GROUP BY p.brand, d.calorie_category")
    df = pd.read_sql_query(q, conn)
    fig = px.treemap(df, path=['brand','calorie_category'], values='count', title="Treemap of Brand & Calorie Category")
    st.plotly_chart(fig, use_container_width=True)

elif option == "KPI Cards (Calories, Sugar, Ultra-Processed)":
    q1 = "SELECT AVG(energy-kcal_value) as avg_cal FROM nutrient_info"
    q2 = "SELECT AVG(sugars_value) as avg_sugar FROM nutrient_info"
    q3 = "SELECT COUNT(*) as ultra_cnt FROM derived_metrics WHERE is_ultra_processed = 'Yes'"
    st.metric("Avg Calories", round(pd.read_sql_query(q1,conn).at[0,'avg_cal'],2))
    st.metric("Avg Sugar", round(pd.read_sql_query(q2,conn).at[0,'avg_sugar'],2))
    st.metric("Ultra-Processed Count", int(pd.read_sql_query(q3,conn).at[0,'ultra_cnt']))

elif option == "Brand: Ultra-processed Stacked":
    q = ("SELECT p.brand, d.is_ultra_processed, COUNT(*) as count FROM product_info p "
         "JOIN derived_metrics d ON p.product_code = d.product_code GROUP BY p.brand, d.is_ultra_processed")
    df = pd.read_sql_query(q, conn)
    fig = px.bar(df, x='brand', y='count', color='is_ultra_processed', barmode='stack', title="Ultra-Processed by Brand")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df)

conn.close()
st.markdown("---")
st.caption("© 2025 Avitosh Sood x Data Analytics Series")
