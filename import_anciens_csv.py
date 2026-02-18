"""
import_anciens_csv.py
Convertit les anciens CSV Spotify + Deezer vers le format artist_urls.csv
"""

import pandas as pd
import os

# ─── CHEMINS ──────────────────────────────────────────────
SPOTIFY_CSV  = 'data/spotify_ancien.csv'
DEEZER_CSV   = 'data/deezer_ancien.csv'
OUTPUT_CSV   = 'artist_urls.csv'

# ─── MAPPING GENRES ───────────────────────────────────────
def mapper_genre(genre_raw):
    """Mappe un genre vers les catégories standardisées"""
    if not genre_raw or pd.isna(genre_raw) or genre_raw == 'Non spécifié':
        return 'Rap-HipHop-RnB'
    
    genre_lower = str(genre_raw).lower()
    
    # Rap / Hip-Hop / RnB
    if any(x in genre_lower for x in ['rap', 'hip hop', 'hip-hop', 'rnb', 'r&b', 'trap', 'drill']):
        return 'Rap-HipHop-RnB'
    
    # Pop / Variété
    elif any(x in genre_lower for x in ['pop', 'variété', 'chanson', 'french pop']):
        return 'Pop'
    
    # Rock / Metal
    elif any(x in genre_lower for x in ['rock', 'metal', 'punk']):
        return 'Rock-Metal'
    
    # Jazz / Soul / Blues
    elif any(x in genre_lower for x in ['jazz', 'soul', 'blues']):
        return 'Jazz-Soul'
    
    # Afro
    elif any(x in genre_lower for x in ['afro', 'amapiano']):
        return 'Afrobeat-Amapiano'
    
    # Indie / Alternative
    elif any(x in genre_lower for x in ['indie', 'alternatif', 'alternative']):
        return 'Indie-Alternative'
    
    # Electro / EDM
    elif any(x in genre_lower for x in ['electro', 'house', 'techno', 'edm', 'dance']):
        return 'Electro'
    
    # Country / Folk
    elif any(x in genre_lower for x in ['country', 'folk']):
        return 'Country-Folk'
    
    # Reggae / Latin
    elif any(x in genre_lower for x in ['reggae', 'latin', 'reggaeton']):
        return 'Reggaeton-Latin'
    
    # Fallback
    else:
        return 'Rap-HipHop-RnB'

# ─── NORMALISER NOM ───────────────────────────────────────
def normaliser_nom(nom):
    """Normalise un nom d'artiste pour la fusion"""
    import unicodedata
    nom = str(nom).strip().lower()
    nom = unicodedata.normalize('NFKD', nom)
    nom = nom.encode('ASCII', 'ignore').decode('ASCII')
    nom = ''.join(c for c in nom if c.isalnum() or c.isspace())
    return nom.strip()

# ═══════════════════════════════════════════════════════════
# TRAITEMENT SPOTIFY
# ═══════════════════════════════════════════════════════════

print(" CONVERSION ANCIENS CSV → artist_urls.csv\n")
print("=" * 60)

spotify_data = {}

if os.path.exists(SPOTIFY_CSV):
    print(f"\n Lecture {SPOTIFY_CSV}...")
    df_spotify = pd.read_csv(SPOTIFY_CSV)
    print(f"    {len(df_spotify)} artistes Spotify")
    
    for _, row in df_spotify.iterrows():
        nom = row['nom']
        nom_norm = normaliser_nom(nom)
        
        genre = mapper_genre(row.get('genres', ''))
        
        spotify_data[nom_norm] = {
            'nom': nom,
            'url_spotify': row['url_spotify'],
            'url_deezer': '',
            'categorie': genre,
            'genre': genre,
            'source': 'import_spotify'
        }
    
    print(f"    {len(spotify_data)} artistes Spotify traités")
else:
    print(f"    {SPOTIFY_CSV} non trouvé, ignoré")

# ═══════════════════════════════════════════════════════════
# TRAITEMENT DEEZER
# ═══════════════════════════════════════════════════════════

deezer_data = {}

if os.path.exists(DEEZER_CSV):
    print(f"\n Lecture {DEEZER_CSV}...")
    df_deezer = pd.read_csv(DEEZER_CSV)
    print(f"    {len(df_deezer)} artistes Deezer")
    
    for _, row in df_deezer.iterrows():
        nom = row['nom']
        nom_norm = normaliser_nom(nom)
        
        # Genre par défaut pour Deezer
        genre = 'Rap-HipHop-RnB'
        
        deezer_data[nom_norm] = {
            'nom': nom,
            'url_spotify': '',
            'url_deezer': row['url_deezer'],
            'categorie': genre,
            'genre': genre,
            'source': 'import_deezer'
        }
    
    print(f"    {len(deezer_data)} artistes Deezer traités")
else:
    print(f"    {DEEZER_CSV} non trouvé, ignoré")

# ═══════════════════════════════════════════════════════════
# FUSION SPOTIFY + DEEZER
# ═══════════════════════════════════════════════════════════

print(f"\n Fusion des données...")

artistes_finaux = {}

# Ajouter tous les Spotify
for nom_norm, data in spotify_data.items():
    artistes_finaux[nom_norm] = data.copy()

# Fusionner avec Deezer
for nom_norm, data_deezer in deezer_data.items():
    if nom_norm in artistes_finaux:
        # Artiste existe dans Spotify → ajouter URL Deezer
        artistes_finaux[nom_norm]['url_deezer'] = data_deezer['url_deezer']
        artistes_finaux[nom_norm]['source'] = 'import_spotify_deezer'
        print(f"    Match : {artistes_finaux[nom_norm]['nom']} (Spotify + Deezer)")
    else:
        # Artiste uniquement sur Deezer
        artistes_finaux[nom_norm] = data_deezer.copy()

print(f"    {len(artistes_finaux)} artistes uniques après fusion")

# Compter les sources
sources = {}
for data in artistes_finaux.values():
    src = data['source']
    sources[src] = sources.get(src, 0) + 1

print(f"\n Répartition :")
print(f"   • Spotify uniquement : {sources.get('import_spotify', 0)}")
print(f"   • Deezer uniquement  : {sources.get('import_deezer', 0)}")
print(f"   • Spotify + Deezer   : {sources.get('import_spotify_deezer', 0)}")

# ═══════════════════════════════════════════════════════════
# FUSION AVEC ARTIST_URLS.CSV EXISTANT (SI EXISTE)
# ═══════════════════════════════════════════════════════════

if os.path.exists(OUTPUT_CSV):
    print(f"\n Lecture {OUTPUT_CSV} existant...")
    df_existant = pd.read_csv(OUTPUT_CSV)
    print(f"    {len(df_existant)} artistes déjà présents")
    
    # Normaliser les noms existants
    noms_existants = set()
    for _, row in df_existant.iterrows():
        nom_norm = normaliser_nom(row['nom'])
        noms_existants.add(nom_norm)
    
    # Compter les nouveaux
    nouveaux = 0
    for nom_norm in artistes_finaux.keys():
        if nom_norm not in noms_existants:
            nouveaux += 1
    
    print(f"    {nouveaux} nouveaux artistes à ajouter")
    print(f"    {len(artistes_finaux) - nouveaux} artistes déjà présents (ignorés)")
    
    # Ajouter uniquement les nouveaux
    for nom_norm, data in artistes_finaux.items():
        if nom_norm not in noms_existants:
            df_existant = pd.concat([
                df_existant,
                pd.DataFrame([data])
            ], ignore_index=True)
    
    df_final = df_existant
    
else:
    print(f"\n Création de {OUTPUT_CSV} (nouveau fichier)")
    df_final = pd.DataFrame(list(artistes_finaux.values()))

# ═══════════════════════════════════════════════════════════
# SAUVEGARDE
# ═══════════════════════════════════════════════════════════

# Assurer l'ordre des colonnes
colonnes = ['nom', 'url_spotify', 'url_deezer', 'categorie', 'genre']
df_final = df_final[colonnes]

df_final.to_csv(OUTPUT_CSV, index=False)

print(f"\n" + "=" * 60)
print(f" TERMINÉ !")

print(f" Fichier créé : {OUTPUT_CSV}")
print(f" Total artistes : {len(df_final)}")
print(f"\n Prochaine étape :")
print(f"   python music_talent_radar.py --all")
