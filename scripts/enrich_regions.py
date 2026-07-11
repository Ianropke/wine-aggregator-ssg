import sqlite3

DB_PATH = "data/retailers_wine_aggregator.db"

def get_region_for_wine(name):
    name_lower = name.lower()
    
    # Mapping based on common wine names and appellations
    if 'pomerol' in name_lower or 'l\'evangile' in name_lower or 'conseillante' in name_lower or 'beauregard' in name_lower or 'feytit' in name_lower or 'eglise clinet' in name_lower or 'violette' in name_lower:
        return 'Bordeaux (Pomerol)'
    elif 'pauillac' in name_lower or 'haut bages liberal' in name_lower or 'lafite' in name_lower or 'pichon baron' in name_lower:
        return 'Bordeaux (Pauillac)'
    elif 'margaux' in name_lower or 'prieuré lichine' in name_lower or 'brane cantenac' in name_lower or 'rauzan ségla' in name_lower or 'palmer' in name_lower:
        return 'Bordeaux (Margaux)'
    elif 'saint-julien' in name_lower or 'las cases' in name_lower or 'clos du marquis' in name_lower or 'ducru beaucaillou' in name_lower or 'poyferre' in name_lower or 'beychevelle' in name_lower:
        return 'Bordeaux (Saint-Julien)'
    elif 'saint-estephe' in name_lower or 'montrose' in name_lower or 'calon ségur' in name_lower or 'capbern' in name_lower:
        return 'Bordeaux (Saint-Estèphe)'
    elif 'pessac' in name_lower or 'graves' in name_lower or 'smith haut lafitte' in name_lower or 'haut brion' in name_lower or 'pavillon blanc' in name_lower:
        return 'Bordeaux (Pessac-Léognan)'
    elif 'saint-emilion' in name_lower or 'ausone' in name_lower or 'figeac' in name_lower or 'mondotte' in name_lower or 'bécot' in name_lower or 'troplong' in name_lower or 'pavie macquin' in name_lower or 'canon' in name_lower:
        return 'Bordeaux (Saint-Émilion)'
    elif 'sauternes' in name_lower or 'rieussec' in name_lower or 'yquem' in name_lower:
        return 'Bordeaux (Sauternes)'
    elif 'château' in name_lower or 'bordeaux' in name_lower:
        return 'Bordeaux'
        
    elif 'andremily' in name_lower or 'dumol' in name_lower or 'dominus' in name_lower or 'napanook' in name_lower:
        return 'California, USA'
    elif 'gantenbein' in name_lower:
        return 'Graubünden, Switzerland'
    elif 'mogador' in name_lower or 'barbier' in name_lower:
        return 'Priorat, Spain'
        
    elif 'conterno' in name_lower or 'vietti' in name_lower or 'barolo' in name_lower or 'barbaresco' in name_lower or 'barbera' in name_lower:
        return 'Piedmont, Italy'
    elif 'sassicaia' in name_lower or 'san giusto' in name_lower or 'tignanello' in name_lower:
        return 'Tuscany, Italy'
    elif 'doi mats' in name_lower or 'friuli' in name_lower:
        return 'Friuli, Italy'
        
    elif 'grange des peres' in name_lower:
        return 'Languedoc, France'
    elif 'chave' in name_lower or 'hermitage' in name_lower or 'guigal' in name_lower or 'côte rôtie' in name_lower or 'saint joseph' in name_lower or 'parisy' in name_lower:
        return 'Rhône, France'
        
    elif 'ganevat' in name_lower:
        return 'Jura, France'
        
    elif 'colin' in name_lower or 'montrachet' in name_lower or 'remilly' in name_lower or 'noëllat' in name_lower or 'vosne' in name_lower or 'bourgogne' in name_lower:
        return 'Burgundy, France'
        
    elif 'roederer' in name_lower or 'heidsieck' in name_lower or 'agrapart' in name_lower or 'champagne' in name_lower:
        return 'Champagne, France'
        
    elif 'suntory' in name_lower or 'chita' in name_lower:
        return 'Japan (Whisky)'
    elif 'macallan' in name_lower:
        return 'Speyside, Scotland (Whisky)'
    elif 'hennessy' in name_lower:
        return 'Cognac, France'
        
    return 'Unknown Region'

def update_regions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Fetch all wines that need a region update
    cursor.execute("SELECT id, normalized_name, region FROM master_wine_data")
    rows = cursor.fetchall()
    
    updated_count = 0
    for row in rows:
        wine_id, name, current_region = row
        if current_region is None or current_region == 'Unknown' or current_region == 'Unknown Region':
            new_region = get_region_for_wine(name)
            if new_region != 'Unknown Region':
                cursor.execute("UPDATE master_wine_data SET region = ? WHERE id = ?", (new_region, wine_id))
                updated_count += 1
                
    conn.commit()
    conn.close()
    print(f"Opdaterede {updated_count} vine med nye regioner baseret på semantisk navne-søgning.")

if __name__ == "__main__":
    update_regions()
