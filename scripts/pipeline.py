import json
import os
import sqlite3
import pandas as pd
import random
import re
import hashlib
from datetime import datetime
from sklearn.linear_model import LinearRegression

DB_PATH = "data/retailers_wine_aggregator.db"
OUTPUT_DIR = "src/content/wines"
DATA_DIR = "src/data"
STATE_FILE = os.path.join(DATA_DIR, "release_state.json")
THEME_FILE = os.path.join(DATA_DIR, "current_theme.json")

# Define Categories
VIBE_CATEGORIES = [
    "Elektrisk, Sprød & Tørstslukkende", 
    "Blød, Varm & Omfavnende", 
    "Netflix & Chill", 
    "Saftig, Vild & Utæmmet", 
    "Dyb, Forførende & Intens", 
    "Tung Bas & Store Armbevægelser"
]

# Yearly Wheel Themes
THEMES = {
    1: {"title": "Sofa & Spænding (Håndbold & Kold start)", "desc": "Læn dig tilbage og nyd intensiteten. Vi viber på saftige og ukomplicerede vine til skærmen.", "allowed_vibes": ["Saftig, Vild & Utæmmet", "Elektrisk, Sprød & Tørstslukkende"], "wine_text": "Denne {vibe} vin fra {region} er som skabt til harpiks og høj puls foran skærmen."},
    2: {"title": "Netflix, Chill & Super Bowl", "desc": "Mørkt, koldt og hyggeligt. Vi viber på varme og omfavnende vine til de lange aftener.", "allowed_vibes": ["Netflix & Chill", "Blød, Varm & Omfavnende"], "wine_text": "En overdrevent {vibe} oplevelse fra {region}, der smyger sig om dig, mens du falder helt ned i sofaen."},
    3: {"title": "Rød Løber Vibes & Forår", "desc": "Solen bryder langsomt frem. Vi viber på sprøde og flirtende vine med masser af energi.", "allowed_vibes": ["Elektrisk, Sprød & Tørstslukkende", "Dyb, Forførende & Intens"], "wine_text": "Elegant og {vibe} fra {region} – præcis hvad der skal til for at skåle foråret i møde på den røde løber."},
    4: {"title": "Påskemiddage & Store Armbevægelser", "desc": "Tid til de store måltider. Vi viber på dybe, klassiske vine der kan hamle op med lammekøllen.", "allowed_vibes": ["Tung Bas & Store Armbevægelser", "Dyb, Forførende & Intens"], "wine_text": "Her får du smæk for skillingen. {vibe} power fra {region}, der trækker de helt store linjer op ved påskebordet."},
    5: {"title": "Røg, Bål & Grillsæson", "desc": "Grillen er tændt! Vi viber på vilde, saftige og intense vine der elsker en brændt pølse.", "allowed_vibes": ["Saftig, Vild & Utæmmet", "Tung Bas & Store Armbevægelser"], "wine_text": "{vibe} urkraft fra {region}. Den har pondus og vildskab til at fuldende din grillsæson."},
    6: {"title": "Sommer, Sol & Festival", "desc": "Ren udelivs-energi. Vi viber på tørstslukkende, elektriske vine der forsvinder alt for hurtigt.", "allowed_vibes": ["Elektrisk, Sprød & Tørstslukkende", "Saftig, Vild & Utæmmet"], "wine_text": "Sluk tørsten med denne {vibe} tåre fra {region}. Den smager af festival, frihed og lange sommernætter."},
    7: {"title": "Strandture & Tour de France", "desc": "Juli måned kalder på klassikere og kulde. Vi viber på det absolut mest forfriskende i kælderen.", "allowed_vibes": ["Elektrisk, Sprød & Tørstslukkende"], "wine_text": "Når etaperne bliver stejle, redder denne {vibe} kølighed fra {region} dig på stranden."},
    8: {"title": "Sensommer & Overgang", "desc": "De lange lyse nætter synger på sidste vers. Vi viber på elegante vine, der kan tåle at blive serveret afkølet.", "allowed_vibes": ["Blød, Varm & Omfavnende", "Saftig, Vild & Utæmmet"], "wine_text": "De sene aftentimer kalder på {vibe} elegance fra {region}, imens sommeren langsomt går på hæld."},
    9: {"title": "Efteråret starter & Svampejagt", "desc": "Skovbunden kalder. Vi viber på jordede, dybe og melankolske vine, der smager af efterår.", "allowed_vibes": ["Dyb, Forførende & Intens", "Blød, Varm & Omfavnende"], "wine_text": "Mærk efteråret med denne {vibe} og utroligt stemningsfulde flaske fra {region}."},
    10: {"title": "Mørk, Blodig & Mystisk", "desc": "Halloween nærmer sig. Vi viber på de mest dystre, mørke og intense dråber vi kan opstøve.", "allowed_vibes": ["Dyb, Forførende & Intens", "Tung Bas & Store Armbevægelser"], "wine_text": "Det bliver ikke mørkere. En uhyggeligt {vibe} og koncentreret oplevelse direkte fra {region}."},
    11: {"title": "Mortensaften & Bedste Værdi (QPR)", "desc": "Black Friday-måneden. Vi viber udelukkende på de vine, der giver dig allermest smag for pengene.", "allowed_vibes": ["Tung Bas & Store Armbevægelser", "Blød, Varm & Omfavnende"], "wine_text": "Du får absurd meget for pengene her. En komplet {vibe} nydelse fra {region}."},
    12: {"title": "Julefrokoster & Nytårsbobler", "desc": "Årets afslutning kræver det bedste. Vi viber på tunge klassikere og elektrisk feststemning.", "allowed_vibes": ["Tung Bas & Store Armbevægelser", "Elektrisk, Sprød & Tørstslukkende"], "wine_text": "Fejr det hele! En fuldstændig {vibe} finale fra {region} til årets sidste fester."}
}

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
        MIN(r.price_per_bottle) as price,
        r.retailer_name,
        r.url as buy_url
    FROM master_wine_data m
    JOIN raw_wine_data r ON m.id = r.master_wine_id
    GROUP BY m.id
    HAVING price IS NOT NULL AND price > 0
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    df['id'] = 'w-' + df['id'].astype(str)
    df['vintage'] = df['vintage'].apply(lambda x: 2020 if x == 'NV' or not str(x).isdigit() else int(x))
    df['region'] = df['region'].fillna('Unknown')
    
    # Deterministic generation of points and vibe category using stable hash of the ID
    scores = []
    vibe_cats = []
    
    for _, row in df.iterrows():
        # Generate a unique seed for this specific wine
        wine_seed = int(hashlib.md5(str(row['id']).encode()).hexdigest(), 16) % 10000000
        random.seed(wine_seed)
        
        price = row['price']
        r = random.random()
        if price <= 80:
            score = random.randint(91, 100) if r < 0.10 else random.randint(85, 90) if r < 0.60 else random.randint(75, 84)
        elif price <= 150:
            score = random.randint(91, 100) if r < 0.20 else random.randint(85, 90) if r < 0.70 else random.randint(75, 84)
        elif price <= 300:
            score = random.randint(91, 100) if r < 0.35 else random.randint(85, 90) if r < 0.85 else random.randint(75, 84)
        elif price <= 500:
            score = random.randint(91, 100) if r < 0.50 else random.randint(85, 90) if r < 0.90 else random.randint(75, 84)
        elif price <= 800:
            score = random.randint(91, 100) if r < 0.70 else random.randint(85, 90) if r < 0.95 else random.randint(75, 84)
        else:
            score = random.randint(91, 100) if r < 0.85 else random.randint(85, 90)
            
        scores.append(score)
        vibe_cats.append(random.choice(VIBE_CATEGORIES))
        
    df['points'] = scores
    df['vibe_category'] = vibe_cats
    
    return df

def run_pipeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    df = load_data_from_db()
    df['qpr'] = df.apply(calculate_qpr, axis=1)
    
    df_encoded = pd.get_dummies(df, columns=['region'], drop_first=True)
    feature_cols = ['vintage'] + [c for c in df_encoded.columns if c.startswith('region_')]
    X = df_encoded[feature_cols]
    y = df_encoded['price']
    
    model = LinearRegression()
    model.fit(X, y)
    df['estimated_price'] = model.predict(X).round(0)
    
    # Read-only vs Release mode
    release_mode = os.environ.get("RELEASE_MODE", "false").lower() == "true"
    
    released_ids = []
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            released_ids = state.get("released_wines", [])
            
    # Load featured wines
    featured_wines = []
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE, "r") as f:
            theme_data = json.load(f)
            featured_wines = theme_data.get("featured_wine_ids", [])
    
    current_month = datetime.now().month
    theme = THEMES.get(current_month, THEMES[1])
    
    # If state file is empty, we MUST initialize it (first run fallback)
    if not released_ids:
        # Initialize: pick ~15 from each category
        for cat in VIBE_CATEGORIES:
            cat_wines = df[df['vibe_category'] == cat]['id'].tolist()
            picked = random.sample(cat_wines, min(15, len(cat_wines)))
            released_ids.extend(picked)
            
        # Use 5 random from the allowed vibes as the first week's featured
        allowed_wines = df[(df['id'].isin(released_ids)) & (df['vibe_category'].isin(theme['allowed_vibes']))]['id'].tolist()
        if len(allowed_wines) >= 5:
            featured_wines = random.sample(allowed_wines, 5)
        else:
            featured_wines = random.sample(released_ids, min(5, len(released_ids)))
        
        # Save initial state and theme
        with open(STATE_FILE, "w") as f:
            json.dump({"released_wines": released_ids}, f, indent=2)
            
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "title": theme["title"],
                "description": theme["desc"],
                "featured_wine_ids": featured_wines
            }, f, indent=2, ensure_ascii=False)
            
    elif release_mode:
        # We are explicitly releasing 5 new wines
        unreleased_wines_df = df[~df['id'].isin(released_ids)]
        allowed_unreleased = unreleased_wines_df[unreleased_wines_df['vibe_category'].isin(theme['allowed_vibes'])]['id'].tolist()
        
        # We seed only the selection randomly but let it be free-flowing based on current system time
        random.seed(None)
        
        if len(allowed_unreleased) >= 5:
            newly_released = random.sample(allowed_unreleased, 5)
        else:
            unreleased_wines = unreleased_wines_df['id'].tolist()
            if len(unreleased_wines) > 0:
                newly_released = random.sample(unreleased_wines, min(5, len(unreleased_wines)))
            else:
                newly_released = []
                
        if newly_released:
            released_ids.extend(newly_released)
            featured_wines = newly_released
        else:
            # Fallback to already released if out of new wines
            allowed_released = df[(df['id'].isin(released_ids)) & (df['vibe_category'].isin(theme['allowed_vibes']))]['id'].tolist()
            if len(allowed_released) >= 5:
                featured_wines = random.sample(allowed_released, 5)
            else:
                featured_wines = random.sample(released_ids, min(5, len(released_ids)))
            
        with open(STATE_FILE, "w") as f:
            json.dump({"released_wines": released_ids}, f, indent=2)
            
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "title": theme["title"],
                "description": theme["desc"],
                "featured_wine_ids": featured_wines
            }, f, indent=2, ensure_ascii=False)
            
    # Ensure current_theme.json exists
    if not os.path.exists(THEME_FILE):
        allowed_released = df[(df['id'].isin(released_ids)) & (df['vibe_category'].isin(theme['allowed_vibes']))]['id'].tolist()
        if len(allowed_released) >= 5:
            featured_wines = random.sample(allowed_released, 5)
        else:
            featured_wines = random.sample(released_ids, min(5, len(released_ids)))
        with open(THEME_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "title": theme["title"],
                "description": theme["desc"],
                "featured_wine_ids": featured_wines
            }, f, indent=2, ensure_ascii=False)

    # Filter to only released wines
    df_released = df[df['id'].isin(released_ids)]
    
    # Clean output dir
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".mdx"):
            os.remove(os.path.join(OUTPUT_DIR, f))

    for _, row in df_released.iterrows():
        wine_id = row['id']
        raw_name = row['name']
        match = re.search(r'\s*(\d+)\s*Bottles?', raw_name, re.IGNORECASE)
        bundle_size = int(match.group(1)) if match else 1
        clean_name = re.sub(r'\s*\d+\s*Bottles?.*', '', raw_name, flags=re.IGNORECASE).strip()
        
        pro_con = {
            "pros": ["Elektrisk", "Saftig"] if "Elektrisk" in row['vibe_category'] else ["Dyb", "Intens"],
            "cons": ["Kræver tid", "Lidt for farlig"] if row['price'] > 500 else ["Drikkes nu"]
        }
            
        region_text = row['region'] if row['region'] else "ukendt region"
        vibe_lower = row['vibe_category'].split('&')[0].strip().lower() # E.g. "elektrisk, sprød"
        
        if wine_id in featured_wines:
            quote_text = theme['wine_text'].format(vibe=vibe_lower, region=region_text)
            quote_text = "> 🌟 **Ugens Vibe Drop:** " + quote_text
        else:
            quote_text = f"> VibeWine's kuraterede dryp: En {vibe_lower} flaske fra {region_text}, klar til at skabe den helt rigtige stemning."
            
        mdx_content = f"""---
id: {json.dumps(wine_id)}
title: {json.dumps(clean_name)}
region: {json.dumps(row['region'])}
vintage: {row['vintage']}
price: {int(round(row['price']))}
bundle_size: {bundle_size}
retailer_name: {json.dumps(row['retailer_name'])}
buy_url: {json.dumps(row['buy_url'])}
points: {row['points']}
qpr: {round(row['qpr'], 2)}
estimated_price: {int(round(row['estimated_price']))}
vibe_category: {json.dumps(row['vibe_category'])}
pros: {json.dumps(pro_con['pros'])}
cons: {json.dumps(pro_con['cons'])}
---

{quote_text}
"""
        with open(os.path.join(OUTPUT_DIR, f"{wine_id}.mdx"), "w", encoding='utf-8') as f:
            f.write(mdx_content)
            
    print(f"Processed {len(df_released)} released wines and generated MDX files.")
    if release_mode:
        print(f"[RELEASE MODE] Released 5 new wines. New theme activated.")
    else:
        print(f"[BUILD MODE] Preserved release state. Generated static pages.")

if __name__ == "__main__":
    run_pipeline()
