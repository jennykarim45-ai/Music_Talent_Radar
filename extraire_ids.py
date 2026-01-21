
"""
Script pour extraire les IDs Spotify/Deezer depuis ta base existante
Cela va te permettre de récupérer les vrais IDs au lieu de "id1", "id2", "id3"
"""

import sqlite3
import pandas as pd
import re

DB_PATH = 'data/music_talent_radar_v2.db'
OUTPUT_FILE = 'artist_ids_extracted.csv'

print("EXTRACTION DES IDs SPOTIFY/DEEZER")
print("=" * 60)

# Connexion à la base
conn = sqlite3.connect(DB_PATH)

# Charger artistes
print("\n Chargement des artistes...")
artistes_df = pd.read_sql_query("""
    SELECT 
        nom,
        url_spotify,
        url_deezer,
        source,
        followers,
        fans,
        score
    FROM artistes
    ORDER BY score DESC
""", conn)

print(f" {len(artistes_df)} artistes chargés")

# Fonction extraction ID Spotify
def extract_spotify_id(url):
    """Extrait l'ID depuis une URL Spotify"""
    if pd.isna(url) or not url:
        return None
    
    # Format: https://open.spotify.com/artist/4dpARuHxo51G3z768sgnrY
    match = re.search(r'artist/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

# Fonction extraction ID Deezer
def extract_deezer_id(url):
    """Extrait l'ID depuis une URL Deezer"""
    if pd.isna(url) or not url:
        return None
    
    # Format: https://www.deezer.com/artist/123456
    match = re.search(r'artist/(\d+)', url)
    return match.group(1) if match else None

# Extraire les IDs
print("\n Extraction des IDs...")

artistes_df['spotify_id'] = artistes_df['url_spotify'].apply(extract_spotify_id)
artistes_df['deezer_id'] = artistes_df['url_deezer'].apply(extract_deezer_id)

# Statistiques
spotify_count = artistes_df['spotify_id'].notna().sum()
deezer_count = artistes_df['deezer_id'].notna().sum()

print(f" IDs Spotify extraits : {spotify_count}")
print(f" IDs Deezer extraits : {deezer_count}")

# Créer listes pour le script de collecte
print("\n Génération des listes d'IDs...")

# Top 50 Spotify (par score)
spotify_ids = artistes_df[artistes_df['spotify_id'].notna()].sort_values('score', ascending=False).head(50)['spotify_id'].tolist()

# Top 50 Deezer (par score)
deezer_ids = artistes_df[artistes_df['deezer_id'].notna()].sort_values('score', ascending=False).head(50)['deezer_id'].tolist()

# Sauvegarder CSV complet
output_df = artistes_df[['nom', 'source', 'score', 'followers', 'fans', 'spotify_id', 'deezer_id']].copy()
output_df.to_csv(OUTPUT_FILE, index=False)

print(f"\n CSV sauvegardé : {OUTPUT_FILE}")
print(f"   - {len(output_df)} artistes")
print(f"   - Colonnes : nom, source, score, followers, fans, spotify_id, deezer_id")

# Générer code Python pour collecter_donnees_v2.py
print("\n" + "=" * 60)
print(" CODE À COPIER DANS collecter_donnees_v2.py")
print("=" * 60)

print("\n# ==================== IDs SPOTIFY ====================")
print("SPOTIFY_IDS = [")
for idx, spotify_id in enumerate(spotify_ids[:20], 1):  # Afficher 20 premiers
    artist_name = artistes_df[artistes_df['spotify_id'] == spotify_id]['nom'].values[0]
    print(f"    '{spotify_id}',  # {artist_name}")
print("    # ... ajoute le reste depuis artist_ids_extracted.csv")
print("]")

print("\n# ==================== IDs DEEZER ====================")
print("DEEZER_IDS = [")
for idx, deezer_id in enumerate(deezer_ids[:20], 1):  # Afficher 20 premiers
    artist_name = artistes_df[artistes_df['deezer_id'] == deezer_id]['nom'].values[0]
    print(f"    '{deezer_id}',  # {artist_name}")
print("    # ... ajoute le reste depuis artist_ids_extracted.csv")
print("]")

print("\n" + "=" * 60)
print(" EXTRACTION TERMINÉE")
print("=" * 60)

print("\n PROCHAINES ÉTAPES :")
print("1. Ouvre collecter_donnees_v2.py")
print("2. Copie/colle les listes SPOTIFY_IDS et DEEZER_IDS ci-dessus")
print("3. Configure SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET")
print("4. Lance : python collecter_donnees_v2.py")

conn.close()
