
"""
Script pour filtrer les CSV et garder seulement les artistes VRAIMENT émergents
"""

import pandas as pd

SEUIL_FOLLOWERS = 60000  

print(f" Filtrage des CSV pour garder seulement les artistes < {SEUIL_FOLLOWERS:,} followers/fans\n")

# 1. Filtrer Spotify
print(" SPOTIFY")
spotify_df = pd.read_csv('data/spotify_artists_20260112.csv')
print(f"  Avant : {len(spotify_df)} artistes")

if 'followers' in spotify_df.columns:
    spotify_filtered = spotify_df[spotify_df['followers'] < SEUIL_FOLLOWERS]
    print(f"  Après : {len(spotify_filtered)} artistes (< {SEUIL_FOLLOWERS:,})")
    
    # Sauvegarder
    spotify_filtered.to_csv('data/spotify_artists_filtered.csv', index=False)
    print(f"  Sauvegardé : data/spotify_artists_filtered.csv\n")
else:
    print("   Colonne 'followers' manquante\n")

# 2. Filtrer Deezer
print("DEEZER")
deezer_df = pd.read_csv('data/deezer_artists_20260112.csv')
print(f"  Avant : {len(deezer_df)} artistes")

if 'fans' in deezer_df.columns:
    deezer_filtered = deezer_df[deezer_df['fans'] < SEUIL_FOLLOWERS]
    print(f"  Après : {len(deezer_filtered)} artistes (< {SEUIL_FOLLOWERS:,})")
    
    # Sauvegarder
    deezer_filtered.to_csv('data/deezer_artists_filtered.csv', index=False)
    print(f"  Sauvegardé : data/deezer_artists_filtered.csv\n")
else:
    print("  Colonne 'fans' manquante\n")

print("=" * 60)
print("1. Importer les CSV filtrés dans ta base de données")
print("2. Lancer : python ml_prediction.py")
print("3. Lancer: Streamlit")
