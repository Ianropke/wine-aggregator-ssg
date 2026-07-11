import json
import os
import sqlite3
import pandas as pd
import random
from sklearn.linear_model import LinearRegression

DB_PATH = "data/retailers_wine_aggregator.db"
OUTPUT_DIR = "src/content/wines"

def calculate_qpr(row):
    bonus = 2.0 if row['points'] >= 93 else 1.0
    return round((row['points'] / row['price']) * bonus, 4)

def load_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        m.id, 
        m.normalized_name as name, 
        m.vintage, 
        m.region, 
        MIN(r.price_per_bottle) as price
    FROM master_wine_data m
    JOIN raw_wine_data r ON m.id = r.master_wine_id
    GROUP BY m.id
    HAVING price IS NOT NULL AND price > 0
    LIMIT 100
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Clean up and mock missing data
    df['id'] = 'w-' + df['id'].astype(str)
    df['vintage'] = df['vintage'].apply(lambda x: 2020 if x == 'NV' or not str(x).isdigit() else int(x))
    df['region'] = df['region'].fillna('Unknown')
    
    # Mocking Points (85 - 100)
    df['points'] = [random.randint(85, 100) for _ in range(len(df))] # nosec B311
    
    # Mocking Vibe Notes
    vibe_options = [
        (["Elektrisk", "Farlig", "Intens"], "Kendrick Lamar, A$AP Rocky, Travis Scott", "Elektrisk, farlig og klar til at vælte din aften. Det her er flydende selvtillid hældt på flaske."),
        (["Let", "Flirtende", "Sommerlig"], "Peggy Gou, Charli XCX, Fred again..", "Let, flirtende og farligt letdrikkelig. Den forsvinder fra glasset før du overhovedet har sat dig ned."),
        (["Mørk", "Melankolsk", "Dyb"], "The Weeknd, Daft Punk, Justice", "Mørk, melankolsk og dyb som en sen natte-samtale. Den kræver din fulde opmærksomhed og kvitterer med ren poesi."),
        (["Varm", "Imødekommende", "Frugtig"], "Sade, Miles Davis, Erykah Badu", "Varm, imødekommende og blød som et uventet kram. Den svøber dig ind i komfort og nægter at give slip.")
    ]
    notes = []
    seeds = []
    descriptions = []
    for _ in range(len(df)):
        opt = random.choice(vibe_options) # nosec B311
        notes.append(opt[0])
        seeds.append(opt[1])
        descriptions.append(opt[2])
        
    df['tasting_notes'] = notes
    df['spotify_seed'] = seeds
    df['vibe_description'] = descriptions
    
    return df

def run_pipeline():
    # Load Data from SQLite DB
    df = load_data_from_db()
    
    # Calculate QPR
    df['qpr'] = df.apply(calculate_qpr, axis=1)
    
    # Calculate Hedonic Pricing
    # Need to dummy encode the regions
    df_encoded = pd.get_dummies(df, columns=['region'], drop_first=True)
    # Features: vintage and regions
    feature_cols = ['vintage'] + [c for c in df_encoded.columns if c.startswith('region_')]
    
    X = df_encoded[feature_cols]
    y = df_encoded['price']
    
    # Fit the Hedonic model
    model = LinearRegression()
    model.fit(X, y)
    
    df['estimated_price'] = model.predict(X).round(0)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Generate MDX
    for _, row in df.iterrows():
        wine_id = row['id']
        diff_pct = round(((row['estimated_price'] - row['price']) / row['price'] * 100), 0)
        
        # Mock LLM generation
        letterboxd = f"En {row['name']} der rammer dig som et godstog. {row['tasting_notes'][0]} og ufiltreret attitude."
        
        pro_con = {
            "pros": row['tasting_notes'][:2],
            "cons": ["Kræver tid", "Lidt for farlig"] if row['price'] > 500 else ["Drikkes nu"]
        }
        
        mdx_content = f"""---
id: "{wine_id}"
title: "{row['name']}"
region: "{row['region']}"
vintage: {row['vintage']}
price: {int(round(row['price']))}
points: {row['points']}
qpr: {round(row['qpr'], 2)}
estimated_price: {int(round(row['estimated_price']))}
spotify_seed: "{row['spotify_seed']}"
pros: {json.dumps(pro_con['pros'])}
cons: {json.dumps(pro_con['cons'])}
---

> {row['vibe_description']}

{letterboxd}
"""
        with open(os.path.join(OUTPUT_DIR, f"{wine_id}.mdx"), "w", encoding='utf-8') as f:
            f.write(mdx_content)
            
    print(f"Processed {len(df)} wines and generated MDX files in {OUTPUT_DIR}.")

if __name__ == "__main__":
    run_pipeline()
