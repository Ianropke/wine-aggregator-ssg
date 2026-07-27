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
    """Værdi-Index skaleret til 1-100.
    Baseret udelukkende på score (points) og pris.
    Lineær normalisering af points/price ratioen mod
    teoretisk min (82 pts / 550 kr) og max (98 pts / 45 kr).
    """
    ratio = row['points'] / row['price']
    QPR_MIN = 82.0 / 550.0   # ~0.149  → maps to 1
    QPR_MAX = 98.0 / 45.0    # ~2.178  → maps to 100
    scaled = ((ratio - QPR_MIN) / (QPR_MAX - QPR_MIN)) * 99.0 + 1.0
    return int(max(1, min(100, round(scaled))))

def clean_wine_title(raw_name):
    if not raw_name:
        return "Kvalitetsvin"
    name = str(raw_name)
    # Strip flag emojis and other non-Latin emoji characters
    name = re.sub(r'[\U0001F1E0-\U0001F1FF]+', '', name)
    name = re.sub(r'[\U0001F300-\U0001F9FF]+', '', name)
    # Remove alcohol percentage patterns (e.g. "11,5 %", "18%", "12%")
    name = re.sub(r'\s*\d+[.,]?\d*\s*%\s*', ' ', name)
    # Remove ml/stk volume patterns (e.g. "750 ml", "1000 ml", "1 stk")
    name = re.sub(r'\s*\d+\s*(ml|stk)\b.*', '', name, flags=re.IGNORECASE)
    # Remove "eller" multi-product alternatives
    name = re.sub(r'\s+eller\s+.*', '', name, flags=re.IGNORECASE)
    # Existing cleanup rules
    name = re.sub(r'\s*\d+\s*Bottles?.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Pr\.\s*liter.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Liter\s*=.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*1\s*l\s*=.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Pr\.\s*kr\..*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\/\s*\d+([.,]\d+)?\s*€.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Flaske\s*à\s*\d+([.,]\d+)?\s*(liter|l|cl).*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*\d+([.,]\d+)?\s*(cl|liter|l)\b.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Jyllands-Posten.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*Tør/Sød.*', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s*-\s*$', '', name).strip()
    name = re.sub(r'\s*\.$', '', name).strip()
    # Collapse multiple spaces
    name = re.sub(r'\s{2,}', ' ', name).strip()
    return name if name else str(raw_name)

FOOD_PAIRINGS = {
    "Elektrisk, Sprød & Tørstslukkende": ["🍣 Sushi & Fisk", "☀️ Terrasseliv"],
    "Blød, Varm & Omfavnende": ["🍝 Pasta & Pizza", "🛋️ Sofahygge"],
    "Netflix & Chill": ["🍿 Snacking", "🍕 Fredagstaco"],
    "Saftig, Vild & Utæmmet": ["🥩 Grillbøf", "🧀 Ostebord"],
    "Dyb, Forførende & Intens": ["🍷 Datenight", "🥩 Vildt & Bøf"],
    "Tung Bas & Store Armbevægelser": ["🔥 Fest & Middag", "🥩 Heavy Meat"]
}

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
    # Block wines with flag emojis (Wolt Market junk data)
    if re.search(r'[\U0001F1E0-\U0001F1FF]', name_str):
        return False
    
    # Block wines with ml/stk volume in name
    if re.search(r'\d+\s*(ml|stk)\b', name_str, re.IGNORECASE):
        return False
    
    # Block wines with naked alcohol % in name (e.g. "12%", "11,5 %")
    if re.search(r'\d+[.,]?\d*\s*%', name_str):
        return False
    
    # Block multi-product "eller" alternatives
    if ' eller ' in name_lower:
        return False
    
    bad_keywords = [
        # Danske bulk- & tilbudsord
        "forskellige slags", "bag in box", "bib", "pr liter", 
        "literpris", "vol alk", "partivare", "begrænset parti", 
        "stykpris", "flasker à", "flere varianter", "frit valg",
        "% alc", "% vol",
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
        # Strict Point Distribution:
        # Only ~3% of wines get 95-98 points. Most quality wines get 86-94 points.
        if r < 0.03:
            score = random.randint(95, 98)
        elif r < 0.20:
            score = random.randint(92, 94)
        elif r < 0.70:
            score = random.randint(87, 91)
        else:
            score = random.randint(82, 86)
            
        scores.append(score)
        vibe_cats.append(random.choice(VIBE_CATEGORIES))
        
    df['points'] = scores
    df['vibe_category'] = vibe_cats
    
    return df

def run_pipeline(release_mode=False):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    df = load_data_from_db()
    
    # Rens titler FØR kvalitetsvurdering
    df['name'] = df['name'].apply(clean_wine_title)
    
    # Kvalitetssikring: Filtrer de værste bulk-vine fra
    df['is_valid'] = df.apply(is_quality_wine, axis=1)
    df = df[df['is_valid'] == True].copy()
    
    # Dedupliker: Behold den billigste (bedste QPR) ved duplikat-titler
    df = df.sort_values('price').drop_duplicates(subset='name', keep='first').copy()
    
    df['qpr'] = df.apply(calculate_qpr, axis=1)
    
    df_encoded = pd.get_dummies(df, columns=['region'], drop_first=True)
    feature_cols = ['vintage'] + [c for c in df_encoded.columns if c.startswith('region_')]
    X = df_encoded[feature_cols]
    y = df['price']
    
    model = LinearRegression()
    model.fit(X, y)
    df['estimated_price'] = model.predict(X).round(0)
    
    release_mode = release_mode or (os.environ.get("RELEASE_MODE", "false").lower() == "true")
    
    released_ids = []
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            released_ids = state.get("released_wines", [])
            
    featured_wines = []
    
    current_month = datetime.now().month
    theme = THEMES.get(current_month, THEMES[1])
    
    if os.path.exists(THEME_FILE):
        with open(THEME_FILE, "r") as f:
            theme_data = json.load(f)
            featured_wines = theme_data.get("featured_wine_ids", [])
    
    if not released_ids:
        b1_df = df[df['price'] <= 150]
        b2_df = df[(df['price'] > 150) & (df['price'] <= 350)]
        b3_df = df[df['price'] > 350]
        
        b1_picked = sample_diverse_wines(b1_df, 60)
        b2_picked = sample_diverse_wines(b2_df, 30)
        b3_picked = sample_diverse_wines(b3_df, 10)
        
        released_ids.extend(b1_picked + b2_picked + b3_picked)
            
        allowed_wines = df[(df['id'].isin(released_ids)) & (df['vibe_category'].isin(theme['allowed_vibes']))]['id'].tolist()
        if len(allowed_wines) >= 5:
            featured_wines = random.sample(allowed_wines, 5)
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
            
    elif release_mode:
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

    df_released = df[df['id'].isin(released_ids)]
    
    for f in os.listdir(OUTPUT_DIR):
        if f.endswith(".mdx"):
            os.remove(os.path.join(OUTPUT_DIR, f))

    for _, row in df_released.iterrows():
        wine_id = row['id']
        raw_name = row['name']
        match = re.search(r'\s*(\d+)\s*Bottles?', raw_name, re.IGNORECASE)
        bundle_size = int(match.group(1)) if match else 1
        clean_name = clean_wine_title(raw_name)
        
        pro_con = {
            "pros": ["Elektrisk", "Saftig"] if "Elektrisk" in row['vibe_category'] else ["Dyb", "Intens"],
            "cons": ["Kræver tid", "Lidt for farlig"] if row['price'] > 500 else ["Drikkes nu"]
        }
            
        raw_region = row['region']
        if not raw_region or str(raw_region).strip().lower() in ['unknown', 'unknown region', 'ukendt region', 'none', '']:
            region_text = "Kvalitetsområde"
        else:
            region_text = raw_region
            
        vibe_category_lower = row['vibe_category'].lower()
        food_pairing = FOOD_PAIRINGS.get(row['vibe_category'], ["🍷 Nydelse", "🧀 Snacks"])
        
        if wine_id in featured_wines:
            quote_text = theme['wine_text'].format(vibe=vibe_category_lower, region=region_text)
            quote_text = "> 🌟 **Ugens Vibe Drop:** " + quote_text
        else:
            quote_text = f"> VibeWine's kuraterede dryp: En flaske med {vibe_category_lower} vibe fra {region_text}, klar til at skabe den helt rigtige stemning."
            
        mdx_content = f"""---
id: {json.dumps(wine_id)}
title: {json.dumps(clean_name)}
region: {json.dumps(region_text)}
vintage: {row['vintage']}
price: {int(round(row['price']))}
bundle_size: {bundle_size}
retailer_name: {json.dumps(row['retailer_name'])}
buy_url: {json.dumps(row['buy_url'])}
points: {row['points']}
qpr: {row['qpr']}
estimated_price: {int(round(row['estimated_price']))}
vibe_category: {json.dumps(row['vibe_category'])}
food_pairing: {json.dumps(food_pairing)}
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
