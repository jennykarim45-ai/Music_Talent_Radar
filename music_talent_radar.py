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
    python music_talent_radar.py --all --auto       # Mode automatique (GitHub Actions)
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
import unicodedata  
from dotenv import load_dotenv
load_dotenv()

# ============================================================================
# CONFIGURATION
# ============================================================================

# Liste noire artistes (normalisée)
BLACKLIST_ARTISTS = [
    'ryan gosling', 'Missan', 'La Plaie', 'Jungle Jack', 'Bleu Soleil','Soul Blues Icons','New Old Blues','91 Days',
    'emma stone', 'Nour', 'Oasis de musique jazz', 'elyasbitum93200', 'John Weezy B','Jazz de bonne humeur',
    'Ebony',' ZZ', 'Lauren Spencer-Smith', 'Keshi','SG Lewis','Francis Lalanne','Église Momentum', 'AMOR',
    'Limsa d\'aulnay', 'Justin Hurwitz','A Flock of Seagulls','Prefab Sprout','Gary Numan','Rema Loseke','Vanou','91','Zaka Lavista','SoulWaxx Records','RIVIIERA',
    'RDN','Ultravox', 'Ryflo', 'Nakk Mendosa', 'La Clinique', 'Rich Chigga','Momentum Musique','Balla Diabaté','shad Hottaboy','Alliance Ethnkik','tn_490','MC Yoshi','Parishmita Phukan',
    'OPINEL 21', 'ATK', 'Tookie2Beriz','93PUNX','Adrian von Ziegler','Aztec Camera','Rap and Hip Hop Beat Mister',
    'Grandmaster Flash & The Furious Five', 'Gorillaz', 'Gary Numan', 'Tubeway Army','François Dal\'s','Alliance Ethnik',
    'Philip Oakey', 'Rich Brian', 'Nicola Sirkis', 'PLK','Kheops', 'Janet Jackson','Barbie François','& The Gospel',
    'Luther Vandross', 'Eric Elmosnino','Sons de la Nature Projet France',' Marseille Capitale du Rap',
    'FUNK DEMON', 'Ashvma','Lully Hill','DL91 Era','Jeez Suave', 'Thisizlondon','Coco','Gospel Wave Music','New Old Blues','91 Days',
    'The Soul Jazz Era','Jamso', 'Lenaïg', 'Theomaa','19s Soulers','FRENCHGRL','Les Folies Françoises','Selecta Killa',
    'Pescado Rabioso', 'Jean-Luc Lahaye', 'Starley', 'Ici c\'est Paris', 'PARIS.','Walk in Paris','soul flying star',
    'Nicola Sirkis', 'Alain Chamfort', 'Francis Lalanne', 'David Castello-Lopes', 'ATK', 'F.F.F.','Nouvelle Donne',
    'Frànçois & The Atlas Mountains', 'Francis And The Lights', 'Francis Mercier', 'Charles Pasi', 'Ryan Paris', 'Stardust', 'Pop Will Eat Itself', 'Soulive',
    'Victoire Musique', 'Peppa Pig (Français)', 'Pinkfong en Français', 'Hazbin Hotel','Jazz douce musique d\'ambiance',
    'Oasis de musique jazz relaxant','The Paris Match','Baroque Jazz Trio','Jeremstar','K-Pop Demon Hunter','K-Pop','Coco','François Sentinelle',
    'Algéric','Elyon','Francis M','Félix Radu','KLN 93','Kham Meslien','Killemv','Lila-May','Marius Psalmiste','Mirella','Molière l\'opéra urbain',
    'Pinpin OSP','RORI','Rock Bones','SKUNK','Sam Sauvage','Tommy Lyon','ZZCCMXTP','jean','Marseille Capitale du Rap','Sons de la Nature Projet France','Francis sentinelle',
    'Mani Deïz','Kozi','Bengous','Jeff Le Nerf','Lucio Bukowski','Jungle Jack','H JeuneCrack','USKY','Elh Kmer','Souffrance','Lacraps','Tuerie','Flynt','Rocca','X-Men','Grems','Tekilla','Le Juiice'
]
    

DB_PATH = 'data/music_talent_radar_v2.db'
URLS_FILE = 'artist_urls.csv'

# Critères de filtrage
SPOTIFY_MIN_FOLLOWERS = 100
SPOTIFY_MAX_FOLLOWERS = 40000
SPOTIFY_MIN_POPULARITY = 10
SPOTIFY_MAX_POPULARITY = 60

DEEZER_MIN_FANS = 100
DEEZER_MAX_FANS = 40000
DEEZER_MIN_TITRES = 0 

MAX_NB_ALBUMS = 10

# ============================================================================
# CONFIGURATION RATE LIMITING - OPTIMISÉ POUR 800 ARTISTES
# ============================================================================

MAX_ARTISTS_PER_RUN = 800
DELAY_BETWEEN_REQUESTS = 0.5  # Délai entre requête artiste et albums (secondes)
DELAY_BETWEEN_ARTISTS = 2.0  # Délai entre chaque artiste (secondes)
DELAY_AFTER_RATE_LIMIT = 1000  # Attente si rate limit (10 minutes)
MAX_RETRIES_ON_RATE_LIMIT = 3  # Nombre de retries si rate limit

# Temps estimé pour 300 artistes : ~12.5 minutes
ESTIMATED_TIME_MINUTES = (MAX_ARTISTS_PER_RUN * (DELAY_BETWEEN_ARTISTS + DELAY_BETWEEN_REQUESTS)) / 60

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
    if any(x in genre_lower for x in ['jazz', 'soul', 'funk', 'blues', 'gospel', 'neo soul', 'neo-soul', 'nu jazz','new jazz']):
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

def normaliser_nom(nom):
    if not nom:
        return ""
    nom = nom.lower().strip()
    nom = unicodedata.normalize("NFD", nom)
    nom = "".join(c for c in nom if unicodedata.category(c) != "Mn")
    nom = re.sub(r"[^a-z0-9\s]", "", nom)
    nom = re.sub(r"\s+", " ", nom)
    return nom

def est_en_blacklist(nom):
    """Vérifie si un artiste est dans la blacklist"""
    nom_normalise = normaliser_nom(nom)
    
    for blacklisted in BLACKLIST_ARTISTS:
        if normaliser_nom(blacklisted) == nom_normalise:
            return True
    
    return False

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
    """Authentification Spotify avec retry"""
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        print(" ERREUR CRITIQUE : Variables d'environnement manquantes")
        print(f"   SPOTIFY_CLIENT_ID = {' Présent' if client_id else '❌ MANQUANT'}")
        print(f"   SPOTIFY_CLIENT_SECRET = {'Présent' if client_secret else '❌ MANQUANT'}")
        raise ValueError(" Variables SPOTIFY_CLIENT_ID et SPOTIFY_CLIENT_SECRET requises")
    
    print(f" Tentative d'authentification Spotify...")
    print(f"   Client ID: {client_id[:10]}...")
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            auth_response = requests.post(
                'https://accounts.spotify.com/api/token',
                {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret,
                },
                timeout=30
            )
            
            if auth_response.status_code == 200:
                token = auth_response.json()['access_token']
                print(f" Token Spotify obtenu (tentative {attempt + 1}/{max_retries})")
                print(f"   Token: {token[:20]}...")
                return token
            
            elif auth_response.status_code == 401:
                print(f" ERREUR 401 : Credentials invalides (tentative {attempt + 1}/{max_retries})")
                print(f"   Réponse: {auth_response.text}")
                
                if attempt < max_retries - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f" Attente {wait_time}s avant retry...")
                    time.sleep(wait_time)
                else:
                    raise Exception(f" Authentification échouée après {max_retries} tentatives - Vérifiez vos credentials Spotify")
            
            else:
                print(f" Erreur {auth_response.status_code} (tentative {attempt + 1}/{max_retries})")
                print(f"   Réponse: {auth_response.text}")
                
                if attempt < max_retries - 1:
                    time.sleep(3)
                else:
                    raise Exception(f"Erreur authentification Spotify: {auth_response.status_code}")
        
        except requests.exceptions.Timeout:
            print(f" Timeout lors de l'authentification (tentative {attempt + 1}/{max_retries})")
            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                raise Exception(" Timeout persistant lors de l'authentification")
        
        except requests.exceptions.ConnectionError as e:
            print(f"Erreur réseau lors de l'authentification (tentative {attempt + 1}/{max_retries})")
            print(f"   Détails: {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                raise Exception(" Impossible de se connecter à Spotify API")
    
    raise Exception(" Authentification échouée après tous les retries")

# ============================================================================
# MODULE 1 : COLLECTE SANS BLOCAGE
# ============================================================================

def collecter_donnees():
    """Collecter données depuis artist_urls.csv - SANS BLOCAGE"""
    print(" MODULE 1 : COLLECTE DES DONNÉES")
    print(f" Configuration : MAX {MAX_ARTISTS_PER_RUN} artistes | Délai {DELAY_BETWEEN_ARTISTS}s")
    print(f"  Temps estimé : ~{ESTIMATED_TIME_MINUTES:.1f} minutes")
    
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
    
    #  LIMITER À MAX_ARTISTS_PER_RUN
    total_spotify = len(spotify_df)
    total_deezer = len(deezer_df)
    
    if len(spotify_df) > MAX_ARTISTS_PER_RUN:
        print(f"Limitation Spotify : {len(spotify_df)} → {MAX_ARTISTS_PER_RUN} artistes")
        spotify_df = spotify_df.head(MAX_ARTISTS_PER_RUN)
    
    if len(deezer_df) > MAX_ARTISTS_PER_RUN:
        print(f"Limitation Deezer : {len(deezer_df)} → {MAX_ARTISTS_PER_RUN} artistes")
        deezer_df = deezer_df.head(MAX_ARTISTS_PER_RUN)
    
    print(f"\n Artistes à collecter :")
    print(f"   Spotify : {len(spotify_df)}/{total_spotify}")
    print(f"   Deezer  : {len(deezer_df)}/{total_deezer}")
    
    # Token Spotify
    try:
        token = get_spotify_token()
    except Exception as e:
        print(f" Erreur authentification: {e}")
        return False
    
    # ========================================================================
    # COLLECTE SPOTIFY
    # ========================================================================
    spotify_data = []
    if len(spotify_df) > 0:
        print(f"\n Collecte Spotify ({len(spotify_df)} artistes)...")
        print(f"   Délai entre requêtes : {DELAY_BETWEEN_REQUESTS}s")
        print(f"   Délai entre artistes : {DELAY_BETWEEN_ARTISTS}s")
        
        success_count = 0
        error_count = 0
        rate_limit_count = 0
        start_time = time.time()
        
        for idx, row in spotify_df.iterrows():
            nom = row['nom']
            artist_id = extraire_id_spotify(row['url_spotify'])
            categorie = row.get('categorie', 'Autre')
            
            # Progression
            current = idx - spotify_df.index[0] + 1
            progress = (current / len(spotify_df)) * 100
            elapsed = (time.time() - start_time) / 60
            
            if current % 10 == 0:
                print(f"  Progression : {current}/{len(spotify_df)} ({progress:.0f}%) | {elapsed:.1f} min écoulées")
            
            if not artist_id:
                print(f" {nom}: URL invalide")
                error_count += 1
                continue
            
            # Vérifier blacklist
            if est_en_blacklist(nom):
                print(f" {nom}: En blacklist (ignoré)")
                error_count += 1
                continue
            
            # RETRY LOGIC
            max_retries = MAX_RETRIES_ON_RATE_LIMIT
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    #  Requête infos artiste
                    response = requests.get(
                        f'https://api.spotify.com/v1/artists/{artist_id}',
                        headers={'Authorization': f'Bearer {token}'},
                        timeout=30
                    )
                    
                    # GESTION STRICTE DU RATE LIMIT
                    if response.status_code == 429:
                        retry_after = int(response.headers.get('Retry-After', DELAY_AFTER_RATE_LIMIT))
                        
                        print(f"\n RATE LIMIT ATTEINT !")
                        print(f"   Artiste : {nom}")
                        print(f"   Retry-After : {retry_after}s ({retry_after/60:.1f} min)")
                        
                        #  SI > 1000s (16 min), ARRÊTER LA COLLECTE
                        if retry_after > 1000:
                            print(f"\n RATE LIMIT TROP LONG ({retry_after}s = {retry_after/60:.1f} min)")
                            print(f"   ARRÊT DE LA COLLECTE POUR AUJOURD'HUI")
                            print(f"   → {success_count} artistes collectés avec succès")
                            print(f"   → Relancer dans {retry_after/3600:.1f} heures")
                            
                            # Sauvegarder collecte partielle
                            if spotify_data:
                                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                                partial_df = pd.DataFrame(spotify_data)
                                partial_df.to_csv(f'data/spotify_collected_partial_{timestamp}.csv', index=False)
                                partial_df.to_csv('data/spotify_collected_latest.csv', index=False)
                                print(f"💾 {len(spotify_data)} artistes sauvegardés (collecte partielle)")
                            
                            return False
                        
                        # Sinon attendre
                        wait_time = retry_after + 10
                        print(f" Attente de {wait_time}s ({wait_time/60:.1f} min)...")
                        time.sleep(wait_time)
                        retry_count += 1
                        rate_limit_count += 1
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
                    
                    #  DÉLAI ENTRE REQUÊTE ARTISTE ET ALBUMS
                    time.sleep(DELAY_BETWEEN_REQUESTS)
                    
                    #  Requête albums de l'artiste
                    albums_response = requests.get(
                        f'https://api.spotify.com/v1/artists/{artist_id}/albums',
                        headers={'Authorization': f'Bearer {token}'},
                        params={'limit': 50, 'include_groups': 'album,single'},
                        timeout=30
                    )
                    
                    nb_albums = 0
                    nb_releases_recentes = 0
                    
                    if albums_response.status_code == 200:
                        albums_data = albums_response.json()
                        nb_albums = albums_data['total']
                        
                        # Compter releases des 2 dernières années
                        from datetime import timedelta
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
                    
                    print(f" {nom:30} → {data['followers']['total']:>8,} followers | {nb_releases_recentes} releases")
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
            
            #  DÉLAI ENTRE CHAQUE ARTISTE (CRITIQUE POUR RATE LIMITING)
            time.sleep(DELAY_BETWEEN_ARTISTS)
        
        # STATS FINALES SPOTIFY
        total_time = (time.time() - start_time) / 60
        print(f"\n RÉSULTATS COLLECTE SPOTIFY")
        print(f"  Succès        : {success_count}")
        print(f"  Erreurs       : {error_count}")
        print(f"  Rate limits   : {rate_limit_count}")
        print(f"  Temps total   : {total_time:.1f} min")
        if (success_count + error_count) > 0:
            print(f"   Taux succès   : {success_count/(success_count+error_count)*100:.1f}%")
            print(f"   Vitesse       : {success_count/total_time:.1f} artistes/min")
    
    # ========================================================================
    # COLLECTE DEEZER
    # ========================================================================
    deezer_data = []
    if len(deezer_df) > 0:
        print(f"\n Collecte Deezer ({len(deezer_df)} artistes)...")
        
        success_count_deezer = 0
        error_count_deezer = 0
        
        for idx, row in deezer_df.iterrows():
            nom = row['nom']
            artist_id = extraire_id_deezer(row['url_deezer'])
            categorie = row.get('categorie', 'Autre')
            
            if not artist_id:
                print(f" {nom}: URL invalide")
                error_count_deezer += 1
                continue
            
            # Vérifier blacklist
            if est_en_blacklist(nom):
                print(f" {nom}: En blacklist (ignoré)")
                error_count_deezer += 1
                continue
            
            try:
                # Infos artiste
                response = requests.get(f'https://api.deezer.com/artist/{artist_id}', timeout=30)
                
                if response.status_code != 200:
                    print(f" {nom}: Erreur {response.status_code}")
                    error_count_deezer += 1
                    continue
                
                data = response.json()
                if 'error' in data:
                    print(f" {nom}: {data['error']}")
                    error_count_deezer += 1
                    continue
                
                # Albums de l'artiste
                time.sleep(0.3)
                albums_response = requests.get(f'https://api.deezer.com/artist/{artist_id}/albums', timeout=30)
                nb_albums = 0
                nb_releases_recentes = 0
                
                if albums_response.status_code == 200:
                    albums_data = albums_response.json()
                    nb_albums = albums_data.get('total', 0)
                    
                    # Compter releases des 2 dernières années
                    from datetime import timedelta
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
                
                print(f" {nom:30} → {data.get('nb_fan', 0):>8,} fans | {nb_releases_recentes} releases")
                success_count_deezer += 1
                
            except Exception as e:
                print(f" {nom}: {e}")
                error_count_deezer += 1
            
            # Délai entre artistes Deezer (plus permissif)
            time.sleep(0.5)
        
        # STATS FINALES DEEZER
        print(f"\n RÉSULTATS COLLECTE DEEZER")
        print(f"   Succès  : {success_count_deezer}")
        print(f"   Erreurs : {error_count_deezer}")
        if (success_count_deezer + error_count_deezer) > 0:
            print(f"   Taux    : {success_count_deezer/(success_count_deezer+error_count_deezer)*100:.1f}%")
    
    # ========================================================================
    # SAUVEGARDE
    # ========================================================================
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if spotify_data:
        spotify_collected = pd.DataFrame(spotify_data)
        spotify_collected.to_csv(f'data/spotify_collected_{timestamp}.csv', index=False)
        spotify_collected.to_csv('data/spotify_collected_latest.csv', index=False)
        print(f"\n Spotify : {len(spotify_collected)} artistes sauvegardés")
    
    if deezer_data:
        deezer_collected = pd.DataFrame(deezer_data)
        deezer_collected.to_csv(f'data/deezer_collected_{timestamp}.csv', index=False)
        deezer_collected.to_csv('data/deezer_collected_latest.csv', index=False)
        print(f" Deezer  : {len(deezer_collected)} artistes sauvegardés")
    
    print("\n Collecte terminée avec succès")
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
                headers={'Authorization': f'Bearer {token}'},
                timeout=30
            )
            
            if response.status_code == 200:
                artists = response.json()['artists']
                print(f"   {len(artists)} artistes similaires trouvés")
                
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
                    print(f"      ✓ {artist['name']:30} ({followers:,} followers)")
        except Exception as e:
            print(f" Erreur: {e}")
        
        time.sleep(1.0)
    
    if not discovered:
        print("\n Aucun nouvel artiste découvert")
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
        print(f"\n Spotify avant filtrage : {len(spotify_df)}")
        
        spotify_filtered = spotify_df[
            (spotify_df['followers'] >= SPOTIFY_MIN_FOLLOWERS) &
            (spotify_df['followers'] <= SPOTIFY_MAX_FOLLOWERS) &
            (spotify_df['popularity'] >= SPOTIFY_MIN_POPULARITY) &
            (spotify_df['popularity'] <= SPOTIFY_MAX_POPULARITY) &
            (spotify_df['nb_albums'] <= MAX_NB_ALBUMS)
        ]
        
        spotify_filtered.to_csv('data/spotify_filtered.csv', index=False)
        print(f"   Après filtrage : {len(spotify_filtered)} ({len(spotify_filtered)/len(spotify_df)*100:.1f}%)")
    
    # Filtrer Deezer
    if os.path.exists(deezer_file):
        deezer_df = pd.read_csv(deezer_file)
        print(f"\n Deezer avant filtrage : {len(deezer_df)}")
        
        # Vérifier si colonne nb_titres existe
        if 'nb_titres' in deezer_df.columns:
            deezer_df['nb_titres'] = deezer_df['nb_titres'].fillna(0)
            
            deezer_filtered = deezer_df[
                (deezer_df['fans'] >= DEEZER_MIN_FANS) &
                (deezer_df['fans'] <= DEEZER_MAX_FANS) &
                (deezer_df['nb_titres'] >= DEEZER_MIN_TITRES) &
                (deezer_df['nb_albums'] <= MAX_NB_ALBUMS)
            ]
        else:
            deezer_filtered = deezer_df[
                (deezer_df['fans'] >= DEEZER_MIN_FANS) &
                (deezer_df['fans'] <= DEEZER_MAX_FANS)
            ]
        
        deezer_filtered.to_csv('data/deezer_filtered.csv', index=False)
        print(f"   Après filtrage : {len(deezer_filtered)} ({len(deezer_filtered)/len(deezer_df)*100:.1f}%)")
    
    print("\n Filtrage terminé")
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
            cursor.execute("ALTER TABLE artistes ADD COLUMN date_maj TEXT")
            conn.commit()
            
            date_now = datetime.now().strftime('%Y-%m-%d')
            cursor.execute("UPDATE artistes SET date_maj = ? WHERE date_maj IS NULL", (date_now,))
            conn.commit()
    except Exception as e:
        print(f" Erreur date_maj: {e}")

def verifier_et_ajouter_colonnes_recurrence(cursor, conn):
    """Ajouter colonnes pour la récurrence"""
    try:
        cursor.execute("PRAGMA table_info(metriques_historique)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'nb_albums' not in columns:
            cursor.execute("ALTER TABLE metriques_historique ADD COLUMN nb_albums INTEGER DEFAULT 0")
            conn.commit()
        
        if 'nb_releases_recentes' not in columns:
            cursor.execute("ALTER TABLE metriques_historique ADD COLUMN nb_releases_recentes INTEGER DEFAULT 0")
            conn.commit()
    except Exception as e:
        print(f" Erreur colonnes: {e}")

def importer_en_base():
    """Importer données filtrées en base"""
    print(" MODULE 4 : IMPORT EN BASE DE DONNÉES")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # CRÉER TABLES
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
    date_now = datetime.now().strftime('%Y-%m-%d')
    
    # Importer Spotify
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
                row.get('image_url', ''), row['url_spotify'], date_now))
            count += 1
        print(f" Spotify : {len(spotify_df)} artistes importés")
    
    # Importer Deezer
    if os.path.exists('data/deezer_filtered.csv'):
        deezer_df = pd.read_csv('data/deezer_filtered.csv')
        for _, row in deezer_df.iterrows():
            id_unique = f"{row['nom'].lower().strip()}_deezer"
            
            #  Lire la colonne 'genre' (pas 'categorie')
            genre = row.get('genre', row.get('categorie', 'Autre'))
            
            #  Si genre est "Autre", mettre Rap-HipHop-RnB par défaut
            if genre == 'Autre' or not genre or pd.isna(genre):
                genre = 'Rap-HipHop-RnB'
            
            cursor.execute("""
                INSERT OR REPLACE INTO artistes 
                (id_unique, nom, source, genre, image_url, url_deezer, date_maj)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_unique, row['nom'], 'Deezer', genre,
                row.get('image_url', ''), row['url_deezer'], date_now))
            count += 1
        print(f" Deezer : {len(deezer_df)} artistes importés")
    
    conn.commit()
    print(f"\n Total : {count} artistes dans table 'artistes'")
    
    # Synchronisation metriques_historique
    print("\n Synchronisation metriques_historique...")
    
    try:
        count_inserted = 0
        
        # Insertion Spotify
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
                    print(f" Erreur Spotify - {row['nom']}: {e}")
        
        # Insertion Deezer
        if os.path.exists('data/deezer_filtered.csv'):
            deezer_df = pd.read_csv('data/deezer_filtered.csv')
            
            for _, row in deezer_df.iterrows():
                id_unique = f"{row['nom'].lower().strip()}_deezer"
                
                #  Lire la colonne 'genre'
                genre_deezer = row.get('genre', row.get('categorie', 'Autre'))
                
                #  Si genre est "Autre", mettre Rap-HipHop-RnB
                if genre_deezer == 'Autre' or not genre_deezer or pd.isna(genre_deezer):
                    genre_deezer = 'Rap-HipHop-RnB'
                
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
                    print(f" Erreur Deezer - {row['nom']}: {e}")
        
        conn.commit()
        
        cursor.execute("SELECT COUNT(*) FROM metriques_historique")
        count_total = cursor.fetchone()[0]
        
        print(f" {count_inserted} nouvelles métriques insérées")
        print(f" Total en base : {count_total} métriques")
        
    except Exception as e:
        print(f" Erreur synchronisation : {e}")
    
    conn.close()
    return True

# ============================================================================
# MODULE 5 : ML ET ALERTES
# ============================================================================

def ml_et_alertes():
    """Module ML : Calcul des scores CORRIGÉ + Génération d'alertes"""
    print(" MODULE 5 : CALCUL SCORES CORRIGÉ + ALERTES")
    
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
        
        # CALCUL DES SCORES CORRIGÉ
        print("\n Calcul des scores (version corrigée)...")
        
        cursor.execute("""
            SELECT 
                id, 
                fans_followers, 
                popularity, 
                plateforme, 
                nom_artiste, 
                id_unique,
                nb_albums,
                nb_releases_recentes
            FROM metriques_historique
        """)
        
        rows = cursor.fetchall()
        scores_updated = 0
        
        debug_scores = []  # Pour debug
        
        for row in rows:
            (metric_id, fans_followers, popularity, plateforme, 
            nom_artiste, id_unique, nb_albums, nb_releases_recentes) = row
            
            # Debug : collecter infos
            debug_info = {
                'nom': nom_artiste,
                'plateforme': plateforme,
                'fans': fans_followers or 0,
                'popularity': popularity or 0,
                'albums': nb_albums or 0,
                'releases': nb_releases_recentes or 0
            }
            
            # CRITÈRE 1 : AUDIENCE (35%) - ZONE 100-20,000
            audience_score = 0
            
            if fans_followers:
                # Normaliser entre 100 et 20,000 (zone émergente)
                fans_norm = min(max(fans_followers, 100), 20000)
                
                # Formule progressive avec boost 5k-15k
                if fans_followers <= 5000:
                    # 100-5000 : 0 à 12 pts
                    audience_score = ((fans_norm - 100) / (5000 - 100)) * 12
                
                elif fans_followers <= 15000:
                    # 5000-15000 : 12 à 30 pts (BOOST)
                    audience_score = 12 + ((fans_norm - 5000) / (15000 - 5000)) * 18
                
                else:
                    # 15000-20000 : 30 à 35 pts
                    audience_score = 30 + ((fans_norm - 15000) / (20000 - 15000)) * 5
            
            debug_info['audience_score'] = round(audience_score, 1)
            
            # CRITÈRE 2 : ENGAGEMENT (30%)
            engagement_score = 0
            
            if plateforme == 'Spotify':
                # CORRECTION : Popularity 0-50 (au lieu de 20-65)
                if popularity is not None:
                    pop_norm = min(max(popularity or 0, 0), 50)
                    engagement_score = (pop_norm / 50) * 30
            
            elif plateforme == 'Deezer':
                # Ratio fans/albums
                if nb_albums and nb_albums > 0 and fans_followers:
                    ratio = fans_followers / nb_albums
                    # Normaliser : 50-5000 fans/album
                    ratio_norm = min(max(ratio, 50), 5000)
                    engagement_score = ((ratio_norm - 50) / (5000 - 50)) * 30
            
            debug_info['engagement_score'] = round(engagement_score, 1)
            
            # CRITÈRE 3 : PRODUCTIVITÉ (25%) - UTILISE DIRECTEMENT LA BDD
            productivite_score = 0
            
            # Sous-critère A : Releases récentes (15 pts)
            # CORRECTION : Utiliser directement nb_releases_recentes de la BDD
            if nb_releases_recentes is not None and nb_releases_recentes > 0:
                # Normaliser : 1-5 releases
                releases_norm = min(nb_releases_recentes, 5)
                productivite_score += (releases_norm / 5) * 15
            
            # Sous-critère B : Catalogue total (10 pts)
            if nb_albums is not None and nb_albums > 0:
                # Normaliser : 1-3 albums
                albums_norm = min(nb_albums, 3)
                productivite_score += (albums_norm / 3) * 10
            
            debug_info['productivite_score'] = round(productivite_score, 1)
            
            # CRITÈRE 4 : INFLUENCE (10%)
            influence_score = 0
            
            # Sous-critère A : Multi-plateforme (5 pts)
            cursor.execute("""
                SELECT COUNT(DISTINCT plateforme) 
                FROM metriques_historique
                WHERE nom_artiste = ?
            """, (nom_artiste,))
            
            nb_plateformes = cursor.fetchone()[0]
            if nb_plateformes >= 2:
                influence_score += 5
            
            # Sous-critère B : Activité récente (5 pts)
            if nb_releases_recentes and nb_releases_recentes >= 2:
                influence_score += 5
            
            debug_info['influence_score'] = round(influence_score, 1)
            
            # SCORE FINAL
            score_final = audience_score + engagement_score + productivite_score + influence_score
            score_final = round(score_final, 1)
            
            debug_info['score_final'] = score_final
            debug_scores.append(debug_info)
            
            # Mise à jour BDD
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
                    "👥 AUDIENCE IMPORTANTE",
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
                    " POPULARITÉ ÉLEVÉE",
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
                    " ÉMERGENT",
                    f"{nom} montre un potentiel prometteur (score {score:.1f}/100)",
                    datetime.now().strftime('%Y-%m-%d'),
                    0
                ))
                alertes_count += 1
        
        conn.commit()
        print(f" {alertes_count} alertes générées")
        
        cursor.execute("SELECT AVG(score_potentiel) FROM metriques_historique WHERE score_potentiel > 0")
        avg_score = cursor.fetchone()[0]
        
        cursor.execute("SELECT MAX(score_potentiel) FROM metriques_historique")
        max_score = cursor.fetchone()[0]
        
        print(f"\n Statistiques :")
        print(f"   Score moyen   : {avg_score:.1f}/100")
        print(f"   Score maximum : {max_score:.1f}/100")
        print(f"   Alertes       : {alertes_count}")
        
        conn.close()
        
        print("\n Module ML + Alertes terminé")
        return True
        
    except Exception as e:
        print(f" Erreur : {e}")
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
    parser.add_argument('--auto', action='store_true', help='Mode automatique (GitHub Actions)')
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    # LOGS MODE AUTO
    if args.auto:
        print(" MODE AUTOMATIQUE (GitHub Actions)")
        print(f" Date          : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f" Python        : {sys.version.split()[0]}")
        print(f" Working dir   : {os.getcwd()}")
        print(f" Max artistes  : {MAX_ARTISTS_PER_RUN}")
        print(f"  Temps estimé  : ~{ESTIMATED_TIME_MINUTES:.1f} min")
    
    print("\n🎵 MUSIC TALENT RADAR - Workflow Automatique\n")
    
    # WORKFLOW
    if args.all or args.collect:
        if not collecter_donnees():
            print("\n Erreur lors de la collecte")
            if args.auto:
                sys.exit(1)
            return
    
    if args.all or args.discover:
        decouvrir_nouveaux()
    
    if args.all or args.filter:
        if not filtrer_emergents():
            print("\n Erreur lors du filtrage")
            if args.auto:
                sys.exit(1)
            return
    
    if args.all or args.import_db:
        if not importer_en_base():
            print("\n Erreur lors de l'import")
            if args.auto:
                sys.exit(1)
            return
    
    if args.all or args.ml:
        ml_et_alertes()
    
    print(" WORKFLOW TERMINÉ AVEC SUCCÈS")


if __name__ == '__main__':
    main()