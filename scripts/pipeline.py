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
    1: {"title": "Sofa & Spænding (Håndbold & Kold start)", "desc": "Læn dig tilbage og nyd intensiteten. Vi viber på saftige og ukomplicerede vine til skærmen.", "allowed_vibes": ["Saftig, Vild & Utæmmet", "Elektrisk, Sprød & Tørstslukkende"], "wine_text": "Denne vin med {vibe} vibe fra {region} er som skabt til harpiks og høj puls foran skærmen."},
    2: {"title": "Netflix, Chill & Super Bowl", "desc": "Mørkt, koldt og hyggeligt. Vi viber på varme og omfavnende vine til de lange aftener.", "allowed_vibes": ["Netflix & Chill", "Blød, Varm & Omfavnende"], "wine_text": "En overdrevent lækker oplevelse med {vibe} vibe fra {region}, der smyger sig om dig, mens du falder helt ned i sofaen."},
    3: {"title": "Rød Løber Vibes & Forår", "desc": "Solen bryder langsomt frem. Vi viber på sprøde og flirtende vine med masser af energi.", "allowed_vibes": ["Elektrisk, Sprød & Tørstslukkende", "Dyb, Forførende & Intens"], "wine_text": "En flaske med {vibe} vibe fra {region} – præcis hvad der skal til for at skåle foråret i møde på den røde løber."},
    4: {"title": "Påskemiddage & Store Armbevægelser", "desc": "Tid til de store måltider. Vi viber på dybe, klassiske vine der kan hamle op med lammekøllen.", "allowed_vibes": ["Tung Bas & Store Armbevægelser", "Dyb, Forførende & Intens"], "wine_text": "Her får du smæk for skillingen. En flaske med {vibe} power fra {region}, der trækker de helt store linjer op ved påskebordet."},
    5: {"title": "Røg, Bål & Grillsæson", "desc": "Grillen er tændt! Vi viber på vilde, saftige og intense vine der elsker en brændt pølse.", "allowed_vibes": ["Saftig, Vild & Utæmmet", "Tung Bas & Store Armbevægelser"], "wine_text": "En flaske med {vibe} urkraft fra {region}. Den har pondus og vildskab til at fuldende din grillsæson."},
    6: {"title": "Sommer, Sol & Festival", "desc": "Ren udelivs-energi. Vi viber på tørstslukkende, elektriske vine der forsvinder alt for hurtigt.", "allowed_vibes": ["Elektrisk, Sprød & Tørstslukkende", "Saftig, Vild & Utæmmet"], "wine_text": "Sluk tørsten med denne forfriskende dråbe med {vibe} vibe fra {region}. Den smager af festival, frihed og lange sommernætter."},
    7: {"title": "Strandture & Tour de France", "desc": "Juli måned kalder på klassikere og kulde. Vi viber på det absolut mest forfriskende i kælderen.", "allowed_vibes": ["Elektrisk, Sprød & Tørstslukkende"], "wine_text": "Når etaperne bliver stejle, redder denne kølige flaske med {vibe} vibe fra {region} dig på stranden."},
    8: {"title": "Sensommer & Overgang", "desc": "De lange lyse nætter synger på sidste vers. Vi viber på elegante vine, der kan tåle at blive serveret afkølet.", "allowed_vibes": ["Blød, Varm & Omfavnende", "Saftig, Vild & Utæmmet"], "wine_text": "De sene aftentimer kalder på en flaske med {vibe} vibe fra {region}, imens sommeren langsomt går på hæld."},
    9: {"title": "Efteråret starter & Svampejagt", "desc": "Skovbunden kalder. Vi viber på jordede, dybe og melankolske vine, der smager af efterår.", "allowed_vibes": ["Dyb, Forførende & Intens", "Blød, Varm & Omfavnende"], "wine_text": "Mærk efteråret med denne stemningsfulde flaske med {vibe} vibe fra {region}."},
    10: {"title": "Mørk, Blodig & Mystisk", "desc": "Halloween nærmer sig. Vi viber på de mest dystre, mørke og intense dråber vi kan opstøve.", "allowed_vibes": ["Dyb, Forførende & Intens", "Tung Bas & Store Armbevægelser"], "wine_text": "Det bliver ikke mørkere. En koncentreret oplevelse med {vibe} vibe direkte fra {region}."},
    11: {"title": "Mortensaften & Bedste Værdi (QPR)", "desc": "Black Friday-måneden. Vi viber udelukkende på de vine, der giver dig allermest smag for pengene.", "allowed_vibes": ["Tung Bas & Store Armbevægelser", "Blød, Varm & Omfavnende"], "wine_text": "Du får absurd meget for pengene her. En komplet nydelse med {vibe} vibe fra {region}."},
    12: {"title": "Julefrokoster & Nytårsbobler", "desc": "Årets afslutning kræver det bedste. Vi viber på tunge klassikere og elektrisk feststemning.", "allowed_vibes": ["Tung Bas & Store Armbevægelser", "Elektrisk, Sprød & Tørstslukkende"], "wine_text": "Fejr det hele! En fuldstændig festlig finale med {vibe} vibe fra {region} til årets sidste fester."}
}

def calculate_qpr(row):
    bonus = 2.0 if row['points'] >= 93 else 1.0
    return round((row['points'] / row['price']) * bonus, 4)

def sample_diverse_wines(candidates_df, count):
    if len(candidates_df) <= count:
        return candidates_df['id'].tolist()
        
    picked = []
    retailer_groups = {}
    for ret, group in candidates_df.groupby('retailer_name'):
        items = group['id'].tolist()
        random.shuffle(items)
        retailer_groups[ret] = items
        
    retailers = list(retailer_groups.keys())
    random.shuffle(retailers)
    
    while len(picked) < count and any(retailer_groups.values()):
        for ret in list(retailers):
            if len(picked) >= count:
                break
            if retailer_groups[ret]:
                picked.append(retailer_groups[ret].pop(0))
                
    return picked

def is_quality_wine(row):
    # Frasorter vine der er for billige (bulk) eller over 550 kr.
    if row['price'] < 45 or row['price'] > 550:
        return False
        
    name_str = str(row['name'])
    
    # Hårdt længde-filter: Ægte kvalitetsvine har sjældent navne over 80 tegn
    if len(name_str) > 80:
        return False
        
    # Frasorter vine der er fyldt med mærkelige navne/tilbuds-ord
    name_lower = name_str.lower()
    bad_keywords = [
        # Danske bulk- & tilbudsord
        "eller rosé", "eller rødvin", "eller hvidvin", "rød hvid",
        "forskellige slags", "bag in box", "bib", "pr liter", 
        "literpris", "vol alk", "partivare", "begrænset parti", 
        "stykpris", "flasker à", "flere varianter", "frit valg",
        "el rosé", "el hvidvin", "el rødvin", "% alc", "% vol",
        "pris", "kasse", "pr flaske", "pr box",
        "tilbud", "udsalg", "kampagne", "spotvare", "spar ", 
        "gælder kun med", "ugens kup", "inkl. pant", "ex pant", 
        "ekskl. pant", " pant", "x 6", "6 stk", "x6",
        
        # Supermarkeder
        "føtex", "netto", "bilka", "meny", "lidl", "coop",
        
        # Tyske / Engelske / Franske bulk-ord
        "oder weiss", "oder rot", "oder rose", "pro flasche", 
        "pro liter", "verschiedene sorten", "kiste", "angebot",
        "or white", "or red", "mixed case", "clearance", "per bottle",
        "ou rouge", "par litre", "caisse",
        
        # Ikke-vin / Alkoholfri
        "mousserende drik", "alkoholfri", "alcohol-free", "0.0%", 
        "sparkletini", "breezer", "cider", "gløgg", "sangria"
    ]
    
    for kw in bad_keywords:
        if kw in name_lower:
            return False
            
    return True

def load_data_from_db():
    conn = sqlite3.connect(DB_PATH)
    query = """
    SELECT 
        'm-' || m.id as id, 
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

    UNION ALL

    SELECT 
        'r-' || r.id as id, 
        r.raw_name as name, 
        COALESCE(r.raw_vintage, 2020) as vintage, 
        'Unknown' as region, 
        r.price_per_bottle as price,
        r.retailer_name,
        r.url as buy_url
    FROM raw_wine_data r
    WHERE r.master_wine_id IS NULL AND r.price_per_bottle IS NOT NULL AND r.price_per_bottle > 0
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
    
    # Kvalitetssikring: Filtrer de værste bulk-vine fra
    df['is_valid'] = df.apply(is_quality_wine, axis=1)
    df = df[df['is_valid'] == True].copy()
    
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
        # Initialize with ~100 wines adhering to 60/30/10 distribution with maximum retailer diversity
        b1_df = df[df['price'] <= 150]
        b2_df = df[(df['price'] > 150) & (df['price'] <= 350)]
        b3_df = df[df['price'] > 350]
        
        b1_picked = sample_diverse_wines(b1_df, 60)
        b2_picked = sample_diverse_wines(b2_df, 30)
        b3_picked = sample_diverse_wines(b3_df, 10)
        
        released_ids.extend(b1_picked + b2_picked + b3_picked)
            
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
        allowed_unreleased = unreleased_wines_df[unreleased_wines_df['vibe_category'].isin(theme['allowed_vibes'])]
        
        current_b1 = len(df[(df['id'].isin(released_ids)) & (df['price'] <= 150)])
        current_b2 = len(df[(df['id'].isin(released_ids)) & (df['price'] > 150) & (df['price'] <= 350)])
        current_b3 = len(df[(df['id'].isin(released_ids)) & (df['price'] > 350)])
        total = current_b1 + current_b2 + current_b3
        
        random.seed(None)
        
        newly_released = []
        for _ in range(5):
            t_total = total + len(newly_released) + 1
            t_b1 = t_total * 0.60
            t_b2 = t_total * 0.30
            t_b3 = t_total * 0.10
            
            c_b1 = current_b1 + sum(1 for wid in newly_released if df[df['id']==wid]['price'].iloc[0] <= 150)
            c_b2 = current_b2 + sum(1 for wid in newly_released if 150 < df[df['id']==wid]['price'].iloc[0] <= 350)
            c_b3 = current_b3 + sum(1 for wid in newly_released if df[df['id']==wid]['price'].iloc[0] > 350)
            
            diffs = {
                1: t_b1 - c_b1,
                2: t_b2 - c_b2,
                3: t_b3 - c_b3
            }
            
            sorted_brackets = sorted(diffs.items(), key=lambda x: x[1], reverse=True)
            picked_wine = None
            
            # Current retailer counts to prioritize underrepresented retailers
            current_released_df = df[df['id'].isin(released_ids + newly_released)]
            ret_counts = current_released_df['retailer_name'].value_counts().to_dict()
            
            for bracket, deficit in sorted_brackets:
                if bracket == 1:
                    candidates = allowed_unreleased[allowed_unreleased['price'] <= 150]
                elif bracket == 2:
                    candidates = allowed_unreleased[(allowed_unreleased['price'] > 150) & (allowed_unreleased['price'] <= 350)]
                else:
                    candidates = allowed_unreleased[allowed_unreleased['price'] > 350]
                    
                candidates = candidates[~candidates['id'].isin(newly_released)]
                if len(candidates) > 0:
                    # Sort candidates by retailer count (ascending) to pick underrepresented retailers
                    c_copy = candidates.copy()
                    c_copy['ret_count'] = c_copy['retailer_name'].map(lambda r: ret_counts.get(r, 0))
                    min_count = c_copy['ret_count'].min()
                    best_candidates = c_copy[c_copy['ret_count'] == min_count]['id'].tolist()
                    picked_wine = random.choice(best_candidates)
                    break
                    
            if not picked_wine:
                rem = allowed_unreleased[~allowed_unreleased['id'].isin(newly_released)]
                if len(rem) > 0:
                    picked_wine = random.choice(rem['id'].tolist())
                    
            if picked_wine:
                newly_released.append(picked_wine)
                
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
        vibe_category_lower = row['vibe_category'].lower()
        
        if wine_id in featured_wines:
            quote_text = theme['wine_text'].format(vibe=vibe_category_lower, region=region_text)
            quote_text = "> 🌟 **Ugens Vibe Drop:** " + quote_text
        else:
            quote_text = f"> VibeWine's kuraterede dryp: En flaske med {vibe_category_lower} vibe fra {region_text}, klar til at skabe den helt rigtige stemning."
            
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
