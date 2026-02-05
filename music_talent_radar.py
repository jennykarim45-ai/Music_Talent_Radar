
"""
MUSIC TALENT RADAR - Script Principal 
Collecte, Découverte, Filtrage, Import, ML, Alertes

Usage:
    python music_talent_radar.py --all              # Tout faire
    python music_talent_radar.py --collect          # Collecter seulement
    python music_talent_radar.py --discover         # Découvrir nouveaux
    python music_talent_radar.py --filter           # Filtrer émergents
    python music_talent_radar.py --import           # Importer en base
    python music_talent_radar.py --ml               # ML + alertes
"""

import os
import sys
import re
import sqlite3
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import time
import argparse
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

DB_PATH = 'data/music_talent_radar_v2.db'
URLS_FILE = 'artist_urls.csv'

# Critères de filtrage
SPOTIFY_MIN_FOLLOWERS = 100
SPOTIFY_MAX_FOLLOWERS = 35000
SPOTIFY_MIN_POPULARITY = 10
SPOTIFY_MAX_POPULARITY = 60

DEEZER_MIN_FANS = 100
DEEZER_MAX_FANS = 35000
DEEZER_MIN_TITRES = 0 

MAX_NB_ALBUMS = 10

# ============================================================================
# MAPPING DES GENRES
# ============================================================================

def mapper_genre(genre_str):
    """Mapper les genres détaillés vers les catégories principales"""
    if not genre_str or pd.isna(genre_str):
        return "Autre"
    
    genre_lower = str(genre_str).lower()
    
    # Rap-HipHop-RnB
    if any(x in genre_lower for x in ['rap', 'hip hop', 'hip-hop', 'trap', 'drill', 'rnb', 'r&b', 'r & b', 'urban', 'grime', 'cloud rap', 'shatta', 'dancehall', 'conscious hip hop', 'southern hip hop', 'east coast', 'west coast', 'uk hip hop', 'french hip hop']):
        return "Rap-HipHop-RnB"
    
    # Pop
    if any(x in genre_lower for x in ['pop', 'chanson', 'variete', 'variété', 'french pop', 'art pop', 'dance pop', 'electropop', 'synthpop', 'indie poptimism', 'bedroom pop']):
        return "Pop"
    
    # Afrobeat-Amapiano
    if any(x in genre_lower for x in ['afro', 'amapiano', 'afrobeat', 'afrobeats', 'afropop', 'afro-trap', 'afro trap', 'coupé-décalé', 'ndombolo', 'azonto', 'kuduro']):
        return "Afrobeat-Amapiano"
    
    # Rock-Metal
    if any(x in genre_lower for x in ['rock', 'metal', 'punk', 'grunge', 'alternative rock', 'indie rock', 'garage rock', 'post-punk', 'new wave', 'shoegaze', 'noise']):
        return "Rock-Metal"
    
    # Indie-Alternative
    if any(x in genre_lower for x in ['indie', 'alternative', 'lo-fi', 'bedroom', 'chillwave', 'dream pop', 'slowcore']):
        return "Indie-Alternative"
    
    # Jazz-Soul
    if any(x in genre_lower for x in ['jazz', 'soul', 'funk', 'blues', 'gospel', 'neo soul', 'neo-soul', 'nu jazz']):
        return "Jazz-Soul"
    
    # Electro
    if any(x in genre_lower for x in ['electro', 'electronic', 'edm', 'house', 'techno', 'trance', 'dubstep', 'french touch', 'hyperpop', 'future bass', 'trap edm', 'bass music']):
        return "Electro"
    
    # Reggaeton-Latin
    if any(x in genre_lower for x in ['reggaeton', 'latin', 'latino', 'salsa', 'bachata', 'merengue', 'dembow']):
        return "Reggaeton-Latin"
    
    return "Autre"

# ============================================================================
# UTILITAIRES - EXTRACTION IDS
# ============================================================================

def extraire_id_spotify(url):
    """Extraire ID Spotify depuis URL"""
    if not url or pd.isna(url):
        return None
    url = str(url).strip()
    if re.match(r'^[a-zA-Z0-9]{22}$', url):
        return url
    match = re.search(r'artist/([a-zA-Z0-9]{22})', url)
    return match.group(1) if match else None

def extraire_id_deezer(url):
    """Extraire ID Deezer depuis URL"""
    if not url or pd.isna(url):
        return None
    url = str(url).strip()
    if re.match(r'^\d+$', url):
        return url
    match = re.search(r'artist/(\d+)', url)
    return match.group(1) if match else None

# ============================================================================
# SPOTIFY API
# ============================================================================

def get_spotify_token():
    """Authentification Spotify"""
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        raise ValueError(" Variables SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET requises")
    
    auth_response = requests.post('https://accounts.spotify.com/api/token', {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    })
    
    if auth_response.status_code != 200:
        raise Exception(f"Erreur authentification Spotify: {auth_response.status_code}")
    
    return auth_response.json()['access_token']

# ============================================================================
# MODULE 1 : COLLECTE
# ============================================================================

def collecter_donnees():
    """Collecter données depuis artist_urls.csv (IDs extraits automatiquement)"""
    print(" MODULE 1 : COLLECTE DES DONNÉES")
    
    if not os.path.exists(URLS_FILE):
        print(f" Fichier {URLS_FILE} introuvable")
        print(f"Créer {URLS_FILE} avec format: nom,url_spotify,url_deezer,categorie")
        return False
    
    # Charger URLs
    df = pd.read_csv(URLS_FILE)
    
    # Vérifier si colonne categorie existe
    if 'categorie' not in df.columns:
        print(" Colonne 'categorie' manquante, ajout de 'Autre'")
        df['categorie'] = 'Autre'
    
    spotify_df = df[df['url_spotify'].notna()].copy() if 'url_spotify' in df.columns else pd.DataFrame()
    deezer_df = df[df['url_deezer'].notna()].copy() if 'url_deezer' in df.columns else pd.DataFrame()
    
    print(f"\nArtistes à collecter:")
    print(f"   Spotify: {len(spotify_df)}")
    print(f"   Deezer: {len(deezer_df)}")
    
    # Token Spotify
    try:
        token = get_spotify_token()
    except Exception as e:
        print(f" Erreur authentification: {e}")
        return False
    
    # Collecter Spotify
    spotify_data = []
    if len(spotify_df) > 0:
        print(f"Collecte Spotify...")
        
        # Compteurs pour stats
        success_count = 0
        error_count = 0
        rate_limit_count = 0
        
        for idx, row in spotify_df.iterrows():
            nom = row['nom']
            artist_id = extraire_id_spotify(row['url_spotify'])
            categorie = row.get('categorie', 'Autre')
            
            if not artist_id:
                print(f" {nom}: URL invalide")
                error_count += 1
                continue
            
            #  RETRY LOGIC AVEC BACKOFF EXPONENTIEL
            max_retries = 5
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    # 1️ Infos artiste
                    response = requests.get(
                        f'https://api.spotify.com/v1/artists/{artist_id}',
                        headers={'Authorization': f'Bearer {token}'},
                        timeout=10
                    )
                    
                    #  GESTION 429 RATE LIMIT
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', 10))
                        wait_time = max(retry_after, 10 + (retry_count * 5))  # Backoff exponentiel
                        
                        if retry_count == 0:
                            rate_limit_count += 1
                            print(f"⏳ {nom}: Rate limit! Attente {wait_time}s... (tentative {retry_count + 1}/{max_retries})")
                        
                        time.sleep(wait_time)
                        retry_count += 1
                        continue
                    
                    # Autres erreurs HTTP
                    if response.status_code == 404:
                        print(f" {nom}: Artiste introuvable")
                        error_count += 1
                        break
                    
                    if response.status_code != 200:
                        print(f" {nom}: Erreur {response.status_code}")
                        error_count += 1
                        break
                    
                    #  Succès - récupération des données
                    data = response.json()
                    
                    #  Albums de l'artiste (pour récurrence)
                    time.sleep(0.3)  # Petit délai avant deuxième requête
                    
                    albums_response = requests.get(
                        f'https://api.spotify.com/v1/artists/{artist_id}/albums',
                        headers={'Authorization': f'Bearer {token}'},
                        params={'limit': 50, 'include_groups': 'album,single'},
                        timeout=10
                    )
                    
                    nb_albums = 0
                    nb_releases_recentes = 0
                    
                    if albums_response.status_code == 200:
                        albums_data = albums_response.json()
                        nb_albums = albums_data['total']
                        
                        # Compter releases des 2 dernières années
                        from datetime import datetime, timedelta
                        date_limite = datetime.now() - timedelta(days=730)
                        
                        for album in albums_data['items']:
                            try:
                                release_date = datetime.strptime(album['release_date'], '%Y-%m-%d')
                                if release_date >= date_limite:
                                    nb_releases_recentes += 1
                            except:
                                try:
                                    release_date = datetime.strptime(album['release_date'], '%Y')
                                    if release_date.year >= date_limite.year:
                                        nb_releases_recentes += 1
                                except:
                                    pass
                    
                    # Ajouter aux résultats
                    spotify_data.append({
                        'nom': nom,
                        'followers': data['followers']['total'],
                        'popularity': data['popularity'],
                        'genres': ', '.join(data.get('genres', [])),
                        'categorie': categorie,
                        'image_url': data['images'][0]['url'] if data.get('images') else '',
                        'url_spotify': row['url_spotify'],
                        'nb_albums': nb_albums,
                        'nb_releases_recentes': nb_releases_recentes
                    })
                    
                    print(f" {nom:30} → {data['followers']['total']:>8,} followers | {nb_releases_recentes} releases récentes")
                    success = True
                    success_count += 1
                    
                except requests.exceptions.Timeout:
                    print(f" {nom}: Timeout")
                    error_count += 1
                    break
                except requests.exceptions.ConnectionError:
                    print(f" {nom}: Erreur réseau")
                    error_count += 1
                    break
                except Exception as e:
                    print(f" {nom}: {e}")
                    error_count += 1
                    break
            
            # Si échec après tous les retries
            if not success and retry_count >= max_retries:
                print(f" {nom}: Échec après {max_retries} tentatives (rate limit persistant)")
                error_count += 1
            
            #  DÉLAI ADAPTATIF ENTRE ARTISTES
            if rate_limit_count > 5:
                time.sleep(1.0)  # Si beaucoup de rate limits → ralentir
            else:
                time.sleep(0.5)  # Sinon délai normal
        
        #  STATS FINALES
        print(f" RÉSULTATS COLLECTE SPOTIFY")
        print(f" Succès: {success_count}")
        print(f" Erreurs: {error_count}")
        print(f" Rate limits rencontrés: {rate_limit_count}")
        print(f" Taux de succès: {success_count/(success_count+error_count)*100:.1f}%")

    
    # Collecter Deezer
    deezer_data = []
    if len(deezer_df) > 0:
        print(f"\n Collecte Deezer...")
        for idx, row in deezer_df.iterrows():
            nom = row['nom']
            artist_id = extraire_id_deezer(row['url_deezer'])
            categorie = row.get('categorie', 'Autre')
            
            if not artist_id:
                print(f" {nom}: URL invalide")
                continue
            
            try:
                # Infos artiste
                response = requests.get(f'https://api.deezer.com/artist/{artist_id}')
                
                if response.status_code != 200:
                    print(f"  {nom}: Erreur {response.status_code}")
                    continue
                
                data = response.json()
                if 'error' in data:
                    print(f" {nom}: {data['error']}")
                    continue
                
                # Albums de l'artiste
                albums_response = requests.get(f'https://api.deezer.com/artist/{artist_id}/albums')
                nb_albums = 0
                nb_releases_recentes = 0
                
                if albums_response.status_code == 200:
                    albums_data = albums_response.json()
                    nb_albums = albums_data.get('total', 0)
                    
                    # Compter releases des 2 dernières années
                    from datetime import datetime, timedelta
                    date_limite = datetime.now() - timedelta(days=730)
                    
                    for album in albums_data.get('data', []):
                        try:
                            release_date = datetime.strptime(album['release_date'], '%Y-%m-%d')
                            if release_date >= date_limite:
                                nb_releases_recentes += 1
                        except:
                            pass
                
                deezer_data.append({
                    'nom': nom,
                    'fans': data.get('nb_fan', 0),
                    'nb_albums': nb_albums,
                    'nb_titres': data.get('nb_album', 0),
                    'categorie': categorie,
                    'image_url': data.get('picture_medium', ''),
                    'url_deezer': row['url_deezer'],
                    'nb_releases_recentes': nb_releases_recentes
                })
                print(f" {nom:30} → {data.get('nb_fan', 0):>8,} fans | {nb_releases_recentes} releases récentes")
                
            except Exception as e:
                print(f"{nom}: {e}")
            
            time.sleep(0.2)
    
    # Sauvegarder
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if spotify_data:
        spotify_collected = pd.DataFrame(spotify_data)
        spotify_collected.to_csv(f'data/spotify_collected_{timestamp}.csv', index=False)
        spotify_collected.to_csv('data/spotify_collected_latest.csv', index=False)
        print(f"\n Spotify: {len(spotify_collected)} artistes")
    
    if deezer_data:
        deezer_collected = pd.DataFrame(deezer_data)
        deezer_collected.to_csv(f'data/deezer_collected_{timestamp}.csv', index=False)
        deezer_collected.to_csv('data/deezer_collected_latest.csv', index=False)
        print(f" Deezer: {len(deezer_collected)} artistes")
    
    print("\n Collecte terminée")
    return True

# ============================================================================
# MODULE 2 : DÉCOUVERTE
# ============================================================================

def decouvrir_nouveaux(seed_urls=None):
    """Découvrir nouveaux artistes et les ajouter automatiquement"""
    print(" MODULE 2 : DÉCOUVERTE AUTOMATIQUE")
    
    if seed_urls is None:
        if not os.path.exists(URLS_FILE):
            print(" Aucun seed disponible")
            return False
        
        df = pd.read_csv(URLS_FILE)
        seed_urls = df['url_spotify'].dropna().tolist()[:5]
        print(f"Utilisation de {len(seed_urls)} seeds existants")
    
    token = get_spotify_token()
    
    discovered = {}
    
    for i, url in enumerate(seed_urls, 1):
        seed_id = extraire_id_spotify(url)
        if not seed_id:
            continue
        
        print(f"\n Seed {i}/{len(seed_urls)}: {seed_id}")
        
        try:
            response = requests.get(
                f'https://api.spotify.com/v1/artists/{seed_id}/related-artists',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if response.status_code == 200:
                artists = response.json()['artists']
                print(f"    {len(artists)} artistes similaires")
                
                for artist in artists:
                    followers = artist['followers']['total']
                    popularity = artist['popularity']
                    
                    if not (SPOTIFY_MIN_FOLLOWERS <= followers <= SPOTIFY_MAX_FOLLOWERS):
                        continue
                    if popularity > SPOTIFY_MAX_POPULARITY:
                        continue
                    
                    discovered[artist['id']] = {
                        'nom': artist['name'],
                        'url_spotify': artist['external_urls']['spotify'],
                        'url_deezer': '',
                        'followers': followers,
                        'popularity': popularity
                    }
                    print(f"       ✓ {artist['name']:30} ({followers:,} followers)")
        except Exception as e:
            print(f" Erreur: {e}")
        
        time.sleep(0.5)
    
    if not discovered:
        print("\nAucun nouvel artiste découvert")
        return False
    
    nouveaux_df = pd.DataFrame(list(discovered.values()))[['nom', 'url_spotify', 'url_deezer']]
    
    if os.path.exists(URLS_FILE):
        existing_df = pd.read_csv(URLS_FILE)
        existing_urls = set(existing_df['url_spotify'].dropna())
        nouveaux_df = nouveaux_df[~nouveaux_df['url_spotify'].isin(existing_urls)]
        
        if not nouveaux_df.empty:
            merged_df = pd.concat([existing_df[['nom', 'url_spotify', 'url_deezer']], nouveaux_df], ignore_index=True)
            merged_df.to_csv(URLS_FILE, index=False)
            print(f"\n {len(nouveaux_df)} nouveaux artistes ajoutés")
        else:
            print(f"\n Tous déjà présents")
    else:
        nouveaux_df.to_csv(URLS_FILE, index=False)
        print(f"\n {len(nouveaux_df)} artistes ajoutés")
    
    return True

# ============================================================================
# MODULE 3 : FILTRAGE
# ============================================================================

def filtrer_emergents():
    """Filtrer les artistes émergents"""
    print(" MODULE 3 : FILTRAGE DES ÉMERGENTS")
    
    spotify_file = 'data/spotify_collected_latest.csv'
    deezer_file = 'data/deezer_collected_latest.csv'
    
    if not os.path.exists(spotify_file) and not os.path.exists(deezer_file):
        print(" Aucune donnée collectée trouvée")
        return False
    
    # Filtrer Spotify
    if os.path.exists(spotify_file):
        spotify_df = pd.read_csv(spotify_file)
        print(f"\n Spotify avant filtrage: {len(spotify_df)}")
        
        spotify_filtered = spotify_df[
            (spotify_df['followers'] >= SPOTIFY_MIN_FOLLOWERS) &
            (spotify_df['followers'] <= SPOTIFY_MAX_FOLLOWERS) &
            (spotify_df['popularity'] >= SPOTIFY_MIN_POPULARITY) &
            (spotify_df['popularity'] <= SPOTIFY_MAX_POPULARITY) &
            (spotify_df['nb_albums'] <= MAX_NB_ALBUMS)
        ]
        
        spotify_filtered.to_csv('data/spotify_filtered.csv', index=False)
        print(f"   Après filtrage: {len(spotify_filtered)} ({len(spotify_filtered)/len(spotify_df)*100:.1f}%)")
    
    # Filtrer Deezer
    if os.path.exists(deezer_file):
        deezer_df = pd.read_csv(deezer_file)
        print(f"\n Deezer avant filtrage: {len(deezer_df)}")
        
        # Vérifier si colonne nb_titres existe
        if 'nb_titres' in deezer_df.columns:
            print(f" Colonne nb_titres trouvée")
            deezer_df['nb_titres'] = deezer_df['nb_titres'].fillna(0)
            
            deezer_filtered = deezer_df[
                (deezer_df['fans'] >= DEEZER_MIN_FANS) &
                (deezer_df['fans'] <= DEEZER_MAX_FANS) &
                (deezer_df['nb_titres'] >= DEEZER_MIN_TITRES) &
                (deezer_df['nb_albums'] <= MAX_NB_ALBUMS)
            ]
        else:
            print(f" Colonne nb_titres absente, filtre UNIQUEMENT sur fans")
            deezer_filtered = deezer_df[
                (deezer_df['fans'] >= DEEZER_MIN_FANS) &
                (deezer_df['fans'] <= DEEZER_MAX_FANS)
            ]
        
        deezer_filtered.to_csv('data/deezer_filtered.csv', index=False)
        print(f"   Après filtrage: {len(deezer_filtered)} ({len(deezer_filtered)/len(deezer_df)*100:.1f}%)")
    
    print("\nFiltrage terminé")
    return True

# ============================================================================
# MODULE 4 : IMPORT BASE
# ============================================================================

def verifier_et_ajouter_colonne_date_maj(cursor, conn):
    """Vérifier et ajouter la colonne date_maj si elle n'existe pas"""
    try:
        cursor.execute("PRAGMA table_info(artistes)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'date_maj' not in columns:
            print("Colonne date_maj manquante, ajout automatique...")
            cursor.execute("ALTER TABLE artistes ADD COLUMN date_maj TEXT")
            conn.commit()
            
            date_now = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("UPDATE artistes SET date_maj = ? WHERE date_maj IS NULL", (date_now,))
            conn.commit()
            print("Colonne date_maj ajoutée")
    except Exception as e:
        print(f"Erreur date_maj: {e}")

def verifier_et_ajouter_colonnes_recurrence(cursor, conn):
    """Ajouter colonnes pour la récurrence"""
    try:
        cursor.execute("PRAGMA table_info(metriques_historique)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'nb_albums' not in columns:
            print(" Ajout colonne nb_albums...")
            cursor.execute("ALTER TABLE metriques_historique ADD COLUMN nb_albums INTEGER DEFAULT 0")
            conn.commit()
        
        if 'nb_releases_recentes' not in columns:
            print(" Ajout colonne nb_releases_recentes...")
            cursor.execute("ALTER TABLE metriques_historique ADD COLUMN nb_releases_recentes INTEGER DEFAULT 0")
            conn.commit()
        
        print(" Colonnes de récurrence OK")
    except Exception as e:
        print(f" Erreur colonnes: {e}")

def importer_en_base():
    """Importer données filtrées en base"""
    print(" MODULE 4 : IMPORT EN BASE DE DONNÉES")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # CRÉER TABLE ARTISTES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS artistes (
            id INTEGER PRIMARY KEY,
            id_unique TEXT UNIQUE,
            nom TEXT,
            source TEXT,
            genre TEXT,
            image_url TEXT,
            url_spotify TEXT,
            url_deezer TEXT,
            date_ajout TEXT,
            date_maj TEXT
        )
    """)
    
    # CRÉER TABLE METRIQUES_HISTORIQUE
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metriques_historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_unique TEXT,
            nom_artiste TEXT,
            source TEXT,
            plateforme TEXT,
            genre TEXT,
            fans_followers INTEGER,
            followers INTEGER,
            fans INTEGER,
            popularity INTEGER,
            score_potentiel REAL,
            score REAL,
            categorie TEXT,
            date_collecte TEXT,
            url TEXT,
            image_url TEXT
        )
    """)
    
    # CRÉER TABLE ALERTES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_artiste TEXT,
            type_alerte TEXT,
            message TEXT,
            date_alerte TEXT,
            vu INTEGER DEFAULT 0
        )
    """)
    
    conn.commit()
    
    verifier_et_ajouter_colonne_date_maj(cursor, conn)
    verifier_et_ajouter_colonnes_recurrence(cursor, conn)
    
    count = 0
    
    # Importer Spotify dans artistes
    if os.path.exists('data/spotify_filtered.csv'):
        spotify_df = pd.read_csv('data/spotify_filtered.csv')
        for _, row in spotify_df.iterrows():
            id_unique = f"{row['nom'].lower().strip()}_spotify"
            categorie = row.get('categorie', mapper_genre(row.get('genres', '')))
            
            cursor.execute("""
                INSERT OR REPLACE INTO artistes 
                (id_unique, nom, source, genre, image_url, url_spotify, date_maj)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_unique, row['nom'], 'Spotify', categorie,
                row.get('image_url', ''), row['url_spotify'], datetime.now().strftime('%Y-%m-%d')))
            count += 1
        print(f" Spotify: {len(spotify_df)} artistes importés")
    
    # Importer Deezer dans artistes
    if os.path.exists('data/deezer_filtered.csv'):
        deezer_df = pd.read_csv('data/deezer_filtered.csv')
        for _, row in deezer_df.iterrows():
            id_unique = f"{row['nom'].lower().strip()}_deezer"
            categorie = row.get('categorie', 'Autre')
            
            cursor.execute("""
                INSERT OR REPLACE INTO artistes 
                (id_unique, nom, source, genre, image_url, url_deezer, date_maj)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_unique, row['nom'], 'Deezer', categorie,
                row.get('image_url', ''), row['url_deezer'], datetime.now().strftime('%Y-%m-%d')))
            count += 1
        print(f" Deezer: {len(deezer_df)} artistes importés")
    
    conn.commit()
    print(f"\n Total: {count} artistes importés dans table 'artistes'")
    
    # ========================================================================
    # SYNCHRONISATION metriques_historique
    # ========================================================================
    print("\n Synchronisation de metriques_historique...")
    
    try:
        cursor.execute("SELECT COUNT(*) FROM metriques_historique")
        count_avant = cursor.fetchone()[0]
        
        print(f"   État actuel: {count_avant} lignes")
        
        #  NE PLUS SUPPRIMER L'HISTORIQUE 
        # cursor.execute("DELETE FROM metriques_historique")
        
        # Date d'aujourd'hui
        date_now = datetime.now().strftime('%Y-%m-%d')
        count_inserted = 0
        
        # ====================================================================
        # INSERTION SPOTIFY
        # ====================================================================
        if os.path.exists('data/spotify_filtered.csv'):
            spotify_df = pd.read_csv('data/spotify_filtered.csv')
            
            for _, row in spotify_df.iterrows():
                id_unique = f"{row['nom'].lower().strip()}_spotify"
                genre_mappe = row.get('categorie', mapper_genre(row.get('genres', '')))
                
                try:
                    cursor.execute("""
                        INSERT INTO metriques_historique (
                            id_unique, nom_artiste, source, plateforme, genre,
                            fans_followers, followers, fans, popularity,
                            score_potentiel, score, date_collecte, url, image_url,
                            nb_albums, nb_releases_recentes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_unique,
                        row['nom'],
                        'Spotify',
                        'Spotify',
                        genre_mappe,
                        int(row.get('followers', 0)),
                        int(row.get('followers', 0)),
                        None,
                        int(row.get('popularity', 0)),
                        0,
                        0,
                        date_now,
                        row.get('url_spotify', ''),
                        row.get('image_url', ''),
                        int(row.get('nb_albums', 0)),
                        int(row.get('nb_releases_recentes', 0))
                    ))
                    
                    count_inserted += 1
                    
                except Exception as e:
                    print(f"    Erreur Spotify - {row['nom']}: {e}")
        
        # ====================================================================
        # INSERTION DEEZER
        # ====================================================================
        if os.path.exists('data/deezer_filtered.csv'):
            deezer_df = pd.read_csv('data/deezer_filtered.csv')
            
            for _, row in deezer_df.iterrows():
                id_unique = f"{row['nom'].lower().strip()}_deezer"
                genre_deezer = row.get('categorie', 'Autre')
                
                try:
                    cursor.execute("""
                        INSERT INTO metriques_historique (
                            id_unique, nom_artiste, source, plateforme, genre,
                            fans_followers, followers, fans, popularity,
                            score_potentiel, score, date_collecte, url, image_url,
                            nb_albums, nb_releases_recentes
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        id_unique,
                        row['nom'],
                        'Deezer',
                        'Deezer',
                        genre_deezer,
                        int(row.get('fans', 0)),
                        None,
                        int(row.get('fans', 0)),
                        None,
                        0,
                        0,
                        date_now,
                        row.get('url_deezer', ''),
                        row.get('image_url', ''),
                        int(row.get('nb_albums', 0)),
                        int(row.get('nb_releases_recentes', 0))
                    ))
                    
                    count_inserted += 1
                    
                except Exception as e:
                    print(f"    Erreur Deezer - {row['nom']}: {e}")
        
        # ====================================================================
        # COMMIT ET VÉRIFICATION
        # ====================================================================
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM metriques_historique")
        count_final = cursor.fetchone()[0]
        
        print(f"   {count_inserted} nouvelles lignes insérées")
        print(f"   Total dans la base: {count_final} métriques")
        
    except Exception as e:
        print(f"    Erreur synchronisation: {e}")
        import traceback
        traceback.print_exc()
    
    conn.close()
    return True

# ============================================================================
# MODULE 5 : ML ET ALERTES
# ============================================================================

def ml_et_alertes():
    """Module ML : Calcul des scores + Génération d'alertes"""
    print(" MODULE 5 : CALCUL SCORES + ALERTES")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM metriques_historique")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(" Aucune donnée dans metriques_historique")
            conn.close()
            return False
        
        print(f" {count} artistes dans la base")
        

        # CALCUL DES SCORES - CRITÈRES OFFICIELS


        print("\n Calcul des scores...")

        cursor.execute("""
            SELECT id, fans_followers, popularity, plateforme, nom_artiste, id_unique
            FROM metriques_historique
        """)

        rows = cursor.fetchall()
        scores_updated = 0

        for row in rows:
            metric_id, fans_followers, popularity, plateforme, nom_artiste, id_unique = row
            

            # CRITÈRE 1 : AUDIENCE (40%)

            audience_score = 0
            if fans_followers:
                fans_norm = min(max(fans_followers, 100), 35000)
                audience_score = ((fans_norm - 100) / (35000 - 100)) * 40
            

            # CRITÈRE 2 : ENGAGEMENT (30%)

            engagement_score = 0
            
            if plateforme == 'Spotify':
                # Pour Spotify : utiliser popularity comme proxy d'engagement
                if popularity:
                    pop_norm = min(max(popularity, 20), 65)
                    engagement_score = ((pop_norm - 20) / (65 - 20)) * 30
            
            elif plateforme == 'Deezer':
                # Pour Deezer : calculer ratio fans/albums comme proxy d'engagement
                cursor.execute("""
                    SELECT nb_albums FROM metriques_historique
                    WHERE id = ?
                """, (metric_id,))
                
                result = cursor.fetchone()
                nb_albums = result[0] if result and result[0] else 1
                
                if nb_albums > 0 and fans_followers:
                    ratio = fans_followers / nb_albums
                    # Normaliser : 100 fans/album = score 0, 10000 fans/album = score 30
                    ratio_norm = min(max(ratio, 100), 10000)
                    engagement_score = ((ratio_norm - 100) / (10000 - 100)) * 30
            

            # CRITÈRE 3 : RÉCURRENCE (20%)

            recurrence_score = 0
            
            # Récupérer nb_releases_recentes depuis les CSV
            if plateforme == 'Spotify' and os.path.exists('data/spotify_filtered.csv'):
                spotify_df = pd.read_csv('data/spotify_filtered.csv')
                artist_row = spotify_df[spotify_df['nom'] == nom_artiste]
                
                if not artist_row.empty and 'nb_releases_recentes' in artist_row.columns:
                    nb_releases = artist_row.iloc[0]['nb_releases_recentes']
                    # Normaliser : 0 release = 0%, 10+ releases = 20%
                    recurrence_score = min(nb_releases / 10, 1) * 20
            
            elif plateforme == 'Deezer' and os.path.exists('data/deezer_filtered.csv'):
                deezer_df = pd.read_csv('data/deezer_filtered.csv')
                artist_row = deezer_df[deezer_df['nom'] == nom_artiste]
                
                if not artist_row.empty and 'nb_releases_recentes' in artist_row.columns:
                    nb_releases = artist_row.iloc[0]['nb_releases_recentes']
                    recurrence_score = min(nb_releases / 10, 1) * 20
            
            # CRITÈRE 4 : INFLUENCE MULTI-PLATEFORME (10%)
            influence_score = 0
            
            # Vérifier si l'artiste existe sur l'autre plateforme
            if plateforme == 'Spotify':
                cursor.execute("""
                    SELECT COUNT(*) FROM metriques_historique
                    WHERE nom_artiste = ? AND plateforme = 'Deezer'
                """, (nom_artiste,))
                
                if cursor.fetchone()[0] > 0:
                    influence_score = 10  # Présence sur les 2 plateformes
            
            elif plateforme == 'Deezer':
                cursor.execute("""
                    SELECT COUNT(*) FROM metriques_historique
                    WHERE nom_artiste = ? AND plateforme = 'Spotify'
                """, (nom_artiste,))
                
                if cursor.fetchone()[0] > 0:
                    influence_score = 10
            
            # SCORE FINAL
            score_final = audience_score + engagement_score + recurrence_score + influence_score
            score_final = round(score_final, 1)
            
            cursor.execute("""
                UPDATE metriques_historique
                SET score_potentiel = ?, score = ?
                WHERE id = ?
            """, (score_final, score_final, metric_id))
            
            scores_updated += 1

        conn.commit()
        print(f" {scores_updated} scores calculés")
        
        # GÉNÉRATION D'ALERTES
        print("\n Génération d'alertes...")
        
        cursor.execute("DELETE FROM alertes")
        
        cursor.execute("""
            SELECT nom_artiste, fans_followers, popularity, score_potentiel, plateforme
            FROM metriques_historique
            WHERE score_potentiel > 0
            ORDER BY score_potentiel DESC
            LIMIT 20
        """)
        
        top_artistes = cursor.fetchall()
        
        alertes_count = 0
        
        for artiste in top_artistes:
            nom, fans, popularity, score, plateforme = artiste
            
            if score >= 70:
                cursor.execute("""
                    INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte, vu)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nom,
                    " POTENTIEL ÉLEVÉ",
                    f"{nom} a un score de {score:.1f}/100 sur {plateforme}",
                    datetime.now().strftime('%Y-%m-%d'),
                    0
                ))
                alertes_count += 1
            
            if fans and fans > 15000:
                cursor.execute("""
                    INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte, vu)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nom,
                    " AUDIENCE IMPORTANTE",
                    f"{nom} a {fans:,} fans sur {plateforme}",
                    datetime.now().strftime('%Y-%m-%d'),
                    0
                ))
                alertes_count += 1
            
            if popularity and popularity > 55:
                cursor.execute("""
                    INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte, vu)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nom,
                    "POPULARITÉ ÉLEVÉE",
                    f"{nom} a une popularité de {popularity}/100 sur Spotify",
                    datetime.now().strftime('%Y-%m-%d'),
                    0
                ))
                alertes_count += 1
            
            if 30 <= score < 60:
                cursor.execute("""
                    INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte, vu)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    nom,
                    "ÉMERGENT",
                    f"{nom} montre un potentiel prometteur (score {score:.1f}/100)",
                    datetime.now().strftime('%Y-%m-%d'),
                    0
                ))
                alertes_count += 1
        
        conn.commit()
        print(f"{alertes_count} alertes générées")
        
        cursor.execute("SELECT AVG(score_potentiel) FROM metriques_historique WHERE score_potentiel > 0")
        avg_score = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(score_potentiel) FROM metriques_historique")
        max_score = cursor.fetchone()[0]
        
        print(f"\n Statistiques:")
        print(f"   Score moyen: {avg_score:.1f}/100")
        print(f"   Score maximum: {max_score:.1f}/100")
        print(f"   Alertes générées: {alertes_count}")
        
        conn.close()
        
        print("\n Module ML + Alertes terminé")
        return True
        
    except Exception as e:
        print(f" Erreur: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Point d'entrée principal"""
    
    parser = argparse.ArgumentParser(description='Music Talent Radar - Script Unifié')
    parser.add_argument('--all', action='store_true', help='Exécuter tous les modules')
    parser.add_argument('--collect', action='store_true', help='Collecter données')
    parser.add_argument('--discover', action='store_true', help='Découvrir nouveaux artistes')
    parser.add_argument('--filter', action='store_true', help='Filtrer émergents')
    parser.add_argument('--import', dest='import_db', action='store_true', help='Importer en base')
    parser.add_argument('--ml', action='store_true', help='ML + Alertes')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    print(" MUSIC TALENT RADAR - Workflow Automatique")
    
    if args.all or args.collect:
        if not collecter_donnees():
            print("\n Erreur lors de la collecte")
            return
    
    if args.all or args.discover:
        decouvrir_nouveaux()
    
    if args.all or args.filter:
        if not filtrer_emergents():
            print("\n Erreur lors du filtrage")
            return
    
    if args.all or args.import_db:
        if not importer_en_base():
            print("\n Erreur lors de l'import")
            return
    
    if args.all or args.ml:
        ml_et_alertes()
    
    print(" WORKFLOW TERMINÉ")

if __name__ == '__main__':
    main()