import requests
import pandas as pd
import numpy as np
import sqlite3
import time
import certifi
import warnings

warnings.filterwarnings("ignore")

# -------- STEP 1: API Extraction --------
data_list = []
base_url = "https://world.openfoodfacts.org/api/v2/search"
for page in range(1, 121):
    try:
        params = {
            "categories": "chocolates",
            "fields": "code,product_name,brands,nutriments",
            "page_size": 100, "page": page
        }
        r = requests.get(base_url, params=params, verify=certifi.where(), timeout=10)
        if r.status_code != 200:
            continue
        for p in r.json().get('products', []):
            row = {
                'product_code': p.get('code'),
                'product_name': p.get('product_name'),
                'brand': p.get('brands'),
            }
            n = p.get('nutriments', {})
            # Required columns based on spec
            for nf in [
                'energy-kcal_value','energy-kj_value','carbohydrates_value','sugars_value',
                'fat_value','saturated-fat_value','proteins_value','fiber_value','salt_value',
                'sodium_value','nutrition-score-fr','nova-group','fruits-vegetables-nuts-estimate-from-ingredients_100g']:
                row[nf] = n.get(nf)
            data_list.append(row)
        time.sleep(0.5)
    except Exception as ex:
        print("API Error:", ex)
        break

df = pd.DataFrame(data_list)
print("Downloaded columns:", df.columns.tolist())
df.to_csv('raw_choco_data.csv', index=False)

# -------- STEP 2: Data Cleaning --------
required_cols = [
    'product_code', 'product_name', 'brand',
    'energy-kcal_value', 'energy-kj_value', 'carbohydrates_value', 'sugars_value',
    'fat_value', 'saturated-fat_value', 'proteins_value', 'fiber_value', 'salt_value',
    'sodium_value', 'fruits-vegetables-nuts-estimate-from-ingredients_100g',
    'nova-group', 'nutrition-score-fr'
]

existing_cols = [col for col in required_cols if col in df.columns]
df = df[existing_cols]
df = df.dropna(subset=[col for col in ['product_code', 'product_name', 'brand'] if col in df.columns])
num_cols = df.select_dtypes(include=[np.number]).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].mean())

# -------- STEP 3: Feature Engineering --------

if 'carbohydrates_value' in df.columns and 'sugars_value' in df.columns:
    df['sugar_to_carb_ratio'] = df['sugars_value'] / df['carbohydrates_value']
else:
    df['sugar_to_carb_ratio'] = np.nan

if 'energy-kcal_value' in df.columns:
    df['calorie_category'] = pd.cut(df['energy-kcal_value'], [-np.inf, 299, 499, np.inf],
                                    labels=['Low', 'Moderate', 'High'])
else:
    df['calorie_category'] = 'Unknown'

if 'sugars_value' in df.columns:
    df['sugar_category'] = pd.cut(df['sugars_value'], [-np.inf, 19, 39, np.inf],
                                  labels=['Low Sugar', 'Moderate Sugar', 'High Sugar'])
else:
    df['sugar_category'] = 'Unknown'

df['is_ultra_processed'] = df['nova-group'].apply(lambda x: 'Yes' if x == 4 else 'No') if 'nova-group' in df.columns else 'Unknown'

df.to_csv('cleaned_choco_data.csv', index=False)

# -------- STEP 4: SQL Table Design and Insertion --------
conn = sqlite3.connect('chococrunch.db')

product_info = df[['product_code', 'product_name', 'brand']].drop_duplicates()
nutrient_info = df[['product_code', 'energy-kcal_value', 'energy-kj_value', 'carbohydrates_value', 'sugars_value',
                    'fat_value', 'saturated-fat_value', 'proteins_value', 'fiber_value', 'salt_value', 'sodium_value',
                    'fruits-vegetables-nuts-estimate-from-ingredients_100g', 'nutrition-score-fr', 'nova-group']]
derived_metrics = df[['product_code', 'sugar_to_carb_ratio', 'calorie_category',
                      'sugar_category', 'is_ultra_processed']]

product_info.to_sql('product_info', conn, if_exists='replace', index=False)
nutrient_info.to_sql('nutrient_info', conn, if_exists='replace', index=False)
derived_metrics.to_sql('derived_metrics', conn, if_exists='replace', index=False)

conn.close()
print("ETL pipeline complete. Database created.")
