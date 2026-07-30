#!/usr/bin/env python3
"""Comprehensive data quality audit for all wine MDX files."""
import os, re, yaml, json

wines_dir = 'src/content/wines'
issues = []
all_titles = {}
all_data = []

for f in sorted(os.listdir(wines_dir)):
    if not f.endswith('.mdx'):
        continue
    path = os.path.join(wines_dir, f)
    with open(path, 'r', encoding='utf-8') as fh:
        content = fh.read()
    
    parts = content.split('---', 2)
    if len(parts) < 3:
        issues.append({"file": f, "sev": "CRITICAL", "msg": "Manglende frontmatter"})
        continue
    
    try:
        data = yaml.safe_load(parts[1])
    except Exception as e:
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Ugyldig YAML: {e}"})
        continue
    
    all_data.append({"file": f, "data": data})
    
    title = str(data.get('title', ''))
    region = str(data.get('region', ''))
    price = data.get('price', 0) or 0
    points = data.get('points', 0) or 0
    qpr = data.get('qpr', 0) or 0
    vintage = data.get('vintage', 0) or 0
    retailer = str(data.get('retailer_name', ''))
    buy_url = str(data.get('buy_url', ''))
    vibe = str(data.get('vibe_category', ''))
    bundle = data.get('bundle_size', 1) or 1
    food = data.get('food_pairing', []) or []
    
    # === TITLE CHECKS ===
    if not title or title == 'Kvalitetsvin':
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Tom/generisk titel"})
    
    if len(title) > 70:
        issues.append({"file": f, "sev": "WARNING", "msg": f"Lang titel ({len(title)} tegn): {title[:60]}..."})
    
    title_lower = title.lower()
    bad_words = ['liter', ' l ', 'flasker', 'bottles', 'stk', 'pr.', 'jyllands', 'politiken', 
                 'berlingske', 'ekstra bladet', 'netto', 'bilka', 'coop', 'rema',
                 '0,75', '0.75', '1,5', 'alkoholfri']
    for bad in bad_words:
        if bad in title_lower:
            issues.append({"file": f, "sev": "CRITICAL", "msg": f"Stoej i titel ({bad}): {title}"})
            break
            
    if re.search(r'\b\d+\s*(cl|ml)\b', title, re.IGNORECASE):
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Volumen i titel: {title}"})
    
    # Check for price/currency in title
    if re.search(r'\d+[.,]\d+\s*(eur|dkk|kr)', title, re.I):
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Valuta i titel: {title}"})
    
    # Check for weird characters
    if re.search(r'[<>{}|\\]', title):
        issues.append({"file": f, "sev": "WARNING", "msg": f"Maerkelige tegn i titel: {title}"})
    
    # === REGION CHECKS ===
    if not region or region.lower() in ['unknown', 'unknown region', 'none', '']:
        issues.append({"file": f, "sev": "WARNING", "msg": f"Region=Unknown/tom: '{region}'"})
    elif region == 'Kvalitetsomraade' or region == 'Kvalitetsområde':
        pass  # Acceptabel fallback
    
    # === PRICE CHECKS ===
    if price <= 0:
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Ugyldig pris: {price}"})
    elif price < 45:
        issues.append({"file": f, "sev": "WARNING", "msg": f"For billig (<45kr): {price} kr."})
    elif price > 550:
        issues.append({"file": f, "sev": "WARNING", "msg": f"For dyr (>550kr): {price} kr."})
    
    # === POINTS CHECKS ===
    if points < 80 or points > 100:
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Points udenfor 80-100: {points}"})
    
    # === QPR CHECKS ===
    if qpr < 1 or qpr > 100:
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"QPR udenfor 1-100: {qpr}"})
    
    # === VINTAGE CHECKS ===
    if vintage < 1990 or vintage > 2026:
        issues.append({"file": f, "sev": "WARNING", "msg": f"Maerkelig aargang: {vintage}"})
    
    # === URL CHECKS ===
    if not buy_url or not buy_url.startswith('http'):
        issues.append({"file": f, "sev": "CRITICAL", "msg": f"Ugyldig buy_url"})
    
    # === RETAILER CHECKS ===
    if not retailer:
        issues.append({"file": f, "sev": "WARNING", "msg": "Mangler retailer_name"})
    
    # === VIBE CATEGORY CHECKS ===
    valid_vibes = [
        'Elektrisk, Spr\u00f8d & T\u00f8rstslukkende',
        'Bl\u00f8d, Varm & Omfavnende',
        'Netflix & Chill',
        'Saftig, Vild & Ut\u00e6mmet',
        'Dyb, Forf\u00f8rende & Intens',
        'Tung Bas & Store Armbev\u00e6gelser'
    ]
    if vibe not in valid_vibes:
        issues.append({"file": f, "sev": "WARNING", "msg": f"Ugyldig vibe: '{vibe}'"})
    
    # === FOOD PAIRING CHECKS ===
    if not food or len(food) == 0:
        issues.append({"file": f, "sev": "INFO", "msg": "Mangler food_pairing"})
    
    # === BODY/CONTENT CHECK ===
    body = parts[2].strip() if len(parts) > 2 else ''
    if not body:
        issues.append({"file": f, "sev": "WARNING", "msg": "Tom anmeldelsestekst"})
    
    # === DUPLICATE TITLE CHECK ===
    if title in all_titles:
        issues.append({"file": f, "sev": "WARNING", "msg": f"DUPLIKAT titel: '{title}' (ogsaa: {all_titles[title]})"})
    else:
        all_titles[title] = f

# === CROSS-WINE CHECKS ===
# Check retailer distribution
from collections import Counter
retailer_counts = Counter(d['data'].get('retailer_name', '') for d in all_data)
for ret, count in retailer_counts.most_common():
    pct = count / len(all_data) * 100
    if pct > 40:
        issues.append({"file": "GLOBAL", "sev": "WARNING", "msg": f"Retailer-dominans: {ret} har {count}/{len(all_data)} vine ({pct:.0f}%)"})

# Write results as JSON for safe output
results = {
    "total_wines": len(all_data),
    "critical": [i for i in issues if i["sev"] == "CRITICAL"],
    "warning": [i for i in issues if i["sev"] == "WARNING"],
    "info": [i for i in issues if i["sev"] == "INFO"],
}
results["summary"] = {
    "critical_count": len(results["critical"]),
    "warning_count": len(results["warning"]),
    "info_count": len(results["info"]),
}

with open('data_audit_results.json', 'w', encoding='utf-8') as out:
    json.dump(results, out, indent=2, ensure_ascii=False)

print(f"Audit complete. {results['summary']['critical_count']} critical, {results['summary']['warning_count']} warnings, {results['summary']['info_count']} info.")
print("Full results: data_audit_results.json")
