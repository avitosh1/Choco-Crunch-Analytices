# 🍫 ChocoCrunch Analytics: Sweet Stats & Sour Truths

## 📌 Project Overview

This project analyzes global chocolate products using data from the OpenFoodFacts API.
The goal is to identify nutritional risks, processing levels, and brand-level health patterns.

---

## 🎯 Objectives

* Extract chocolate product data using API
* Clean and preprocess nutritional data
* Perform feature engineering to derive health metrics
* Store structured data in SQL database
* Run analytical SQL queries (27 queries)
* Perform Exploratory Data Analysis (EDA)
* Build an interactive dashboard using Streamlit

---

## 🛠 Tech Stack

* Python (Pandas, NumPy, Requests)
* SQL (SQLite)
* Data Visualization (Matplotlib, Seaborn)
* Streamlit (Dashboard)

---

## 🔄 Project Workflow

### 1. Data Extraction

* Extracted ~12,000 chocolate products using OpenFoodFacts API
* Implemented pagination and structured JSON parsing

### 2. Data Cleaning

* Removed duplicates
* Handled missing values using median imputation
* Standardized brand names

### 3. Feature Engineering

Created new metrics:

* `sugar_to_carb_ratio`
* `calorie_category` (Low / Moderate / High)
* `sugar_category` (Low / Moderate / High)
* `is_ultra_processed` (based on NOVA classification)

### 4. SQL Database

Designed 3 tables:

* `product_info`
* `nutrient_info`
* `derived_metrics`

### 5. SQL Analysis

* Executed 27 SQL queries
* Performed brand, nutrition, and category analysis

### 6. EDA

* Distribution analysis (calories, sugar, carbs)
* Correlation heatmaps
* Category comparisons
* Brand-level insights

### 7. Dashboard

* Built interactive Streamlit dashboard
* Included filters and multiple visualizations

---

## 📊 Key Insights

* 🍬 Majority of chocolate products are **high in sugar**
* ⚠️ Ultra-processed chocolates have **higher average calories**
* 🏭 Certain brands consistently produce **high-calorie products**
* 🔬 Many products have **high sugar-to-carb ratios (>70%)**

---

## 💡 Business Recommendations

* Consumers should avoid **high sugar + high calorie chocolates**
* Prefer **low sugar and minimally processed products**
* Brands should focus on improving **nutritional profiles**

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## 📁 Output

* Cleaned dataset
* SQL database
* 27 SQL query outputs
* EDA visualizations
* Interactive dashboard


---

## Avitosh Sood

Your Name
