

"""
Script pour importer les CSV filtrés dans la base de données SQLite (VERSION ADAPTATIVE)
"""

import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = 'data/music_talent_radar_v2.db'

print("IMPORT DES CSV FILTRÉS DANS LA BASE DE DONNÉES\n")

# Vérifier que les fichiers existent
if not os.path.exists('data/spotify_artists_filtered.csv'):
    print("Fichier manquant : data/spotify_artists_filtered.csv")
    print("Lance d'abord : python filtrer_csv_emergents.py")
    exit(1)

if not os.path.exists('data/deezer_artists_filtered.csv'):
    print("Fichier manquant : data/deezer_artists_filtered.csv")
    print("Lance d'abord : python filtrer_csv_emergents.py")
    exit(1)

# Connexion à la base
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# DÉTECTER LES COLONNES DE LA TABLE ARTISTES
print("Détection des colonnes de la table artistes...")
cursor.execute("PRAGMA table_info(artistes)")
columns_info = cursor.fetchall()
artistes_columns = [col[1] for col in columns_info]
print(f"   Colonnes disponibles : {artistes_columns}\n")

# DÉTECTER LES COLONNES DE LA TABLE METRIQUES_HISTORIQUE
cursor.execute("PRAGMA table_info(metriques_historique)")
columns_info = cursor.fetchall()
metriques_columns = [col[1] for col in columns_info]
print(f"   Colonnes metriques : {metriques_columns}\n")

# 1. VIDER LES TABLES EXISTANTES
print(" Nettoyage des tables existantes...")
cursor.execute("DELETE FROM artistes")
cursor.execute("DELETE FROM metriques_historique")
conn.commit()
print("Tables vidées\n")

# 2. CHARGER SPOTIFY
print("SPOTIFY")
spotify_df = pd.read_csv('data/spotify_artists_filtered.csv')
print(f"  Chargé : {len(spotify_df)} artistes")

# Créer id_unique (nom + source)
spotify_df['id_unique'] = spotify_df['nom'].str.lower().str.strip() + '_spotify'

# PRÉPARER LES DONNÉES POUR ARTISTES (ADAPTATIF)
artistes_data = []
for idx, row in spotify_df.iterrows():
    data_dict = {
        'id_unique': row['id_unique'],
        'nom': row['nom'],
        'source': 'Spotify',
        'genre': row.get('genre', ''),
    }
    
    # Ajouter colonnes optionnelles si elles existent
    if 'url_spotify' in artistes_columns:
        data_dict['url_spotify'] = row.get('url_spotify', '')
    if 'image_url' in artistes_columns:
        data_dict['image_url'] = row.get('image_url', '')
    if 'date_ajout' in artistes_columns:
        data_dict['date_ajout'] = datetime.now().strftime('%Y-%m-%d')
    
    artistes_data.append(data_dict)

# Insérer dans artistes
artistes_inserted = 0
for data in artistes_data:
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO artistes ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        artistes_inserted += 1
    except sqlite3.IntegrityError:
        pass  # Déjà existant
    except Exception as e:
        print(f" Erreur artiste: {e}")

conn.commit()
print(f" {artistes_inserted} artistes insérés")

# PRÉPARER LES DONNÉES POUR MÉTRIQUES (ADAPTATIF)
metriques_data = []
for idx, row in spotify_df.iterrows():
    data_dict = {
        'id_unique': row['id_unique'],
        'plateforme': 'Spotify',
    }
    
    # Colonnes obligatoires ou communes
    if 'date_collecte' in metriques_columns:
        data_dict['date_collecte'] = row.get('date_collecte', datetime.now().strftime('%Y-%m-%d'))
    if 'followers' in metriques_columns:
        data_dict['followers'] = row.get('followers', 0)
    if 'fans_followers' in metriques_columns:
        data_dict['fans_followers'] = row.get('followers', 0)
    if 'popularity' in metriques_columns:
        data_dict['popularity'] = row.get('popularity', 0)
    if 'score' in metriques_columns:
        data_dict['score'] = row.get('score', 0)
    if 'score_potentiel' in metriques_columns:
        data_dict['score_potentiel'] = row.get('score', 0)
    
    metriques_data.append(data_dict)

# Insérer dans metriques_historique
metriques_inserted = 0
for data in metriques_data:
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO metriques_historique ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        metriques_inserted += 1
    except Exception as e:
        print(f" Erreur métrique: {e}")

conn.commit()
print(f" {metriques_inserted} métriques insérées\n")

# 3. CHARGER DEEZER
print(" DEEZER")
deezer_df = pd.read_csv('data/deezer_artists_filtered.csv')
print(f"  Chargé : {len(deezer_df)} artistes")

# Créer id_unique
deezer_df['id_unique'] = deezer_df['nom'].str.lower().str.strip() + '_deezer'

# PRÉPARER LES DONNÉES POUR ARTISTES (ADAPTATIF)
artistes_data = []
for idx, row in deezer_df.iterrows():
    data_dict = {
        'id_unique': row['id_unique'],
        'nom': row['nom'],
        'source': 'Deezer',
        'genre': row.get('genre', ''),
    }
    
    # Ajouter colonnes optionnelles
    if 'url_deezer' in artistes_columns:
        data_dict['url_deezer'] = row.get('url_deezer', '')
    if 'image_url' in artistes_columns:
        data_dict['image_url'] = row.get('image_url', '')
    if 'date_ajout' in artistes_columns:
        data_dict['date_ajout'] = datetime.now().strftime('%Y-%m-%d')
    
    artistes_data.append(data_dict)

# Insérer
artistes_inserted = 0
for data in artistes_data:
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO artistes ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        artistes_inserted += 1
    except sqlite3.IntegrityError:
        pass
    except Exception as e:
        print(f"Erreur artiste: {e}")

conn.commit()
print(f" {artistes_inserted} artistes insérés")

# PRÉPARER LES DONNÉES POUR MÉTRIQUES (ADAPTATIF)
metriques_data = []
for idx, row in deezer_df.iterrows():
    data_dict = {
        'id_unique': row['id_unique'],
        'plateforme': 'Deezer',
    }
    
    # Colonnes communes
    if 'date_collecte' in metriques_columns:
        data_dict['date_collecte'] = row.get('date_collecte', datetime.now().strftime('%Y-%m-%d'))
    if 'fans' in metriques_columns:
        data_dict['fans'] = row.get('fans', 0)
    if 'fans_followers' in metriques_columns:
        data_dict['fans_followers'] = row.get('fans', 0)
    if 'score' in metriques_columns:
        data_dict['score'] = row.get('score', 0)
    if 'score_potentiel' in metriques_columns:
        data_dict['score_potentiel'] = row.get('score', 0)
    
    metriques_data.append(data_dict)

# Insérer
metriques_inserted = 0
for data in metriques_data:
    try:
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO metriques_historique ({columns}) VALUES ({placeholders})"
        cursor.execute(query, tuple(data.values()))
        metriques_inserted += 1
    except Exception as e:
        print(f" Erreur métrique: {e}")

conn.commit()
print(f" {metriques_inserted} métriques insérées\n")

# 4. STATISTIQUES FINALES
print("=" * 60)
print(" STATISTIQUES FINALES\n")

# Total artistes
total_artistes = cursor.execute("SELECT COUNT(*) FROM artistes").fetchone()[0]
print(f"Total artistes dans la base : {total_artistes}")

# Par plateforme
spotify_count = cursor.execute("SELECT COUNT(*) FROM artistes WHERE source='Spotify'").fetchone()[0]
deezer_count = cursor.execute("SELECT COUNT(*) FROM artistes WHERE source='Deezer'").fetchone()[0]
print(f"  - Spotify : {spotify_count}")
print(f"  - Deezer  : {deezer_count}")

# Total métriques
total_metriques = cursor.execute("SELECT COUNT(*) FROM metriques_historique").fetchone()[0]
print(f"\nTotal métriques historique : {total_metriques}")

conn.close()

print("\n" + "=" * 60)
print(" IMPORT TERMINÉ !")
print("\n PROCHAINES ÉTAPES :")
print("1. Lance : python ml_prediction.py")
print("2. Lance : streamlit run app/streamlit.py")
print("3. Va dans l'onglet Prédictions")
print("4. Vérifie que le Top 10 contient des vrais émergents !")