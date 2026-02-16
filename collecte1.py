
"""
collecte1.py - Découverte automatique Spotify + Deezer avec filtres ultra-stricts
Spotify : Filtre premier album >= 2018
Deezer : Pas de filtre premier album (limitation API)
Élimine : DJs, Producteurs, Choristes, Fans, Anciens artistes (Spotify)
"""

import os
import requests
import pandas as pd
from datetime import datetime
import time
import re
import unicodedata
import sys
import json
# Chargement optionnel du fichier .env (local uniquement)
try:
    from dotenv import load_dotenv
    load_dotenv()
    print(" Variables d'environnement chargées depuis .env")
except ImportError:
    print(" Utilisation des variables d'environnement système (GitHub Actions)")
    
# Détection automatique du mode non-interactif
IS_AUTO_MODE = (
    '--auto' in sys.argv or 
    '--force' in sys.argv or 
    os.getenv('GITHUB_ACTIONS') == 'true' or
    os.getenv('CI') == 'true'
)

if IS_AUTO_MODE:
    print(" MODE AUTOMATIQUE ACTIVÉ (pas d'interaction utilisateur)")
    
    # Fonction pour remplacer tous les input()
    def input(prompt=""):
        print(f"{prompt} [AUTO: oui]")
        return 'o'  # Toujours répondre 'oui'

# ============================================================================
# CONFIGURATION API
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
    
    return auth_response.json()['access_token']

BASE_URL_DEEZER = "https://api.deezer.com"

# ============================================================================
# MOTS-CLÉS SPOTIFY (50 MOTS-CLÉS)
# ============================================================================

SEARCH_KEYWORDS_SPOTIFY = {
    'Rap-HipHop-RnB': [
        'rap français', 'rappeur français', 'nouveau rappeur français',
        'trap français', 'drill français', 'rap underground français','hip hop soul français',
        'rap paris', 'rap marseille', 'rap lyon', 'rap lille','hip hop rnb français',
        'rap 91', 'rap 92', 'rap 93', 'rap 94','hiphop français','new style français',
        'rap indépendant', 'rap soundcloud français', 'urban français', 'rnb français','r&b français','hip hop français',
        'rap alternatif français', 'rap émergent français', 'rap indépendant français',
        'rap underground français', 'rap conscient français', 'rap politique français',
        'rap social français', 'rap engagé français', 'rap de rue français', 'rap hardcore français',
    ],
    'Pop': [
        'pop français', 'chanson française', 'nouvelle scène française',
        'indie pop français', 'chanteur français', 'chanteuse française',
        'pop alternative française', 'electro pop français',
        'nouveau talent pop français', 'artiste pop émergent','pop rock français',
        'pop paris', 'pop marseille', 'pop lyon', 'pop lille',
    ],
    'Afrobeat-Amapiano': [
        'afrobeat français', 'afrobeat france', 'amapiano',
        'afrobeats', 'afro trap français', 'afro drill',
        'dancehall français', 'afro pop française',
        'afro paris', 'afro marseille', 'afro lyon', 'afro hip hop français',
        'afro rnb français', 'afro soul français', 'afro underground français',
        'afro house français', 'afro techno français', 'afro électro français',
    ],
    'Rock-Metal': [
        'rock français', 'indie rock français', 'metal français',
        'punk français', 'rock alternatif français','rock','post rock français',
        'rock paris', 'rock marseille', 'rock lyon', 'rock lille',
        'rock 91', 'rock 92', 'rock 93', 'rock 94','metal alternatif français',
        'rock indépendant français', 'rock underground français', 'rock garage français',
    ],
    'Indie-Alternative': [
        'indie français', 'indie pop français', 'alternative français',
        'bedroom pop français', 'folk français', 'indie rock français',
        'nouvelle scène française', 'artiste émergent français', 'indie paris', 'indie marseille',
    ],
    'Jazz-Soul': [
        'jazz français', 'soul français','jazz soul français', 'funk français',
        'jazz moderne français', 'neo soul français', 'nu jazz français','gospel français',
        'soul neo français', 'soul neo-soul français', 'new jazz français',
        'soul paris', 'soul marseille', 'soul lyon', 'soul lille',
        'gospel paris', 'gospel marseille', 'gospel lyon', 'gospel lille',

    ],
    'Electro': [
        'french touch', 'électro moderne', 'électro urbaine',
        'artiste électro français', 'nouveau talent électro',
        'électro paris', 'électro marseille', 'électro lyon', 'électro lille',
        'electro techno français', 'electro indie français', 'electro pop français',
        'electro underground français', 'electro dance français', 'electro expérimentale français',
        'electro hip hop français', 'electro rnb français', 'electro soul français',
        'electro funk français', 'electro jazz français', 'electro gospel français',
        'electro trap français', 'electro drill français', 'electro afro français',
    ]
}


# ============================================================================
# MAPPING GENRES DEEZER
# ============================================================================
DEEZER_GENRES = {
    'Pop': 132,
    'Rap-HipHop-RnB': 116,
    'Afrobeat-Amapiano': 113,
    'Rock-Metal': 152,
    'Indie-Alternative': 85,
    'Jazz-Soul': 129,
    'Electro': 106
}

def generer_playlists_deezer(limit=20):
    playlists = {genre: [] for genre in DEEZER_GENRES}

    # Editorial FR
    url = f"{BASE_URL_DEEZER}/editorial/1/selection"
    res = requests.get(url).json()

    for item in res.get("data", []):
        if item.get("type") != "playlist":
            continue

        playlist_id = item.get("id")
        title = item.get("title", "").lower()

        for genre in playlists.keys():
            genre_key = genre.lower().split('-')[0]  # ex: rap, pop, jazz
            if genre_key in title and len(playlists[genre]) < limit:
                playlists[genre].append(playlist_id)

    return playlists


# ============================================================================
# PLAYLISTS DEEZER (PAR GENRE)
# ============================================================================



def obtenir_playlists_deezer(limit=15, cache_file='playlists_deezer_cache.json'):
    """Récupère playlists Deezer avec cache"""
    
    # Essayer de charger depuis le cache
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                cached = json.load(f)
                print(f" Playlists chargées depuis cache ({cache_file})")
                return cached
        except:
            pass
    
    # Sinon, récupérer via API
    print(" Récupération des playlists Deezer éditoriales via API...")
    playlists = generer_playlists_deezer(limit=limit)
    
    # Sauvegarder dans le cache
    with open(cache_file, 'w') as f:
        json.dump(playlists, f, indent=2)
    
    print(f"Playlists sauvegardées dans {cache_file}")
    
    # Afficher le résultat
    total = sum(len(p) for p in playlists.values())
    print(f" {total} playlists récupérées au total")
    for genre, ids in playlists.items():
        print(f"   {genre}: {len(ids)} playlists")
    
    return playlists

# Utiliser la fonction
PLAYLISTS_DEEZER = obtenir_playlists_deezer(limit=15)

# ============================================================================
# RÉCUPÉRATION GENRES DEEZER
# ============================================================================

def get_deezer_artist_genre(artist_id):
    """Récupère le genre d'un artiste Deezer depuis ses albums"""
    try:
        # 1. Récupérer les albums de l'artiste
        albums_url = f"{BASE_URL_DEEZER}/artist/{artist_id}/albums"
        response = requests.get(albums_url, timeout=10)
        
        if response.status_code != 200:
            return "Autre"
        
        albums = response.json().get('data', [])
        
        if not albums:
            return "Autre"
        
        # 2. Prendre le premier album
        album_id = albums[0].get('id')
        
        time.sleep(0.2)  # Rate limiting
        
        # 3. Récupérer les détails de l'album
        album_url = f"{BASE_URL_DEEZER}/album/{album_id}"
        album_response = requests.get(album_url, timeout=10)
        
        if album_response.status_code != 200:
            return "Autre"
        
        album_data = album_response.json()
        
        # 4. Extraire le genre
        genres_data = album_data.get('genres', {}).get('data', [])
        
        if genres_data:
            genre_raw = genres_data[0].get('name', 'Autre')
            return map_deezer_genre(genre_raw)
        
        return "Autre"
        
    except Exception as e:
        return "Autre"


def map_deezer_genre(raw_genre):
    """Mappe un genre Deezer vers nos catégories standardisées"""
    
    GENRE_MAPPING_DEEZER = {
        # Rap / Hip-Hop / RnB
        'Rap/Hip Hop': 'Rap-HipHop-RnB',
        'Hip-Hop': 'Rap-HipHop-RnB',
        'Rap': 'Rap-HipHop-RnB',
        'R&B': 'Rap-HipHop-RnB',
        'RnB': 'Rap-HipHop-RnB',
        'Soul': 'Rap-HipHop-RnB',
        
        # Pop
        'Pop': 'Pop',
        'Variété française': 'Pop',
        'Variété Française': 'Pop',
        'Variété internationale': 'Pop',
        'Chanson française': 'Pop',
        'Chanson Française': 'Pop',
        
        # Rock / Metal
        'Rock': 'Rock-Metal',
        'Metal': 'Rock-Metal',
        'Hard Rock': 'Rock-Metal',
        'Rock Alternatif': 'Rock-Metal',
        
        # Jazz / Blues
        'Jazz': 'Jazz-Soul',
        'Blues': 'Jazz-Soul',
        
        # Electro / EDM
        'Electro': 'Electro',
        'Dance': 'Electro',
        'House': 'Electro',
        'Techno': 'Electro',
        'EDM': 'Electro',
        
        # Afro
        'Afro': 'Afrobeat-Amapiano',
        'Afrobeat': 'Afrobeat-Amapiano',
        'Afropop': 'Afrobeat-Amapiano',
        'African Music': 'Afrobeat-Amapiano',
        
        # Indie / Alternative
        'Indie': 'Indie-Alternative',
        'Alternative': 'Indie-Alternative',
        'Indie Rock': 'Indie-Alternative',
        
        # Country / Folk
        'Country': 'Country-Folk',
        'Folk': 'Country-Folk',
        
        # Reggae / Latin
        'Reggaeton': 'Reggaeton-Latin',
        'Latino': 'Reggaeton-Latin',
        'Latin': 'Reggaeton-Latin',
        'Reggae': 'Reggaeton-Latin',
    }
    
    if not raw_genre or raw_genre == '':
        return 'Rap-HipHop-RnB'  
    
    # Chercher correspondance exacte
    if raw_genre in GENRE_MAPPING_DEEZER:
        return GENRE_MAPPING_DEEZER[raw_genre]
    
    # Chercher correspondance partielle
    raw_lower = raw_genre.lower()
    for key, value in GENRE_MAPPING_DEEZER.items():
        if key.lower() in raw_lower or raw_lower in key.lower():
            return value
    
    return 'Rap-HipHop-RnB' 
# ============================================================================
# FILTRES D'EXCLUSION ULTRA-STRICTS
# ============================================================================

MOTS_EXCLUS_NOM = [
    # DJs (toutes variations)
    ' dj ', 'dj-', '-dj', 'dj.', 'dj_', '_dj', 'dj[', ']dj', '(dj', 'dj)',
    'deejay', 'dee jay', 'disc jockey', 'disk jockey',
    
    # Producteurs
    'prod', 'producer', 'producteur', 'beat maker', 'beatmaker',
    'beatz', 'instrumental', 'type beat',
    
    # Orchestres et ensembles
    'orchestre', 'orchestra', 'symphonique', 'symphony', 'philharmonique',
    'ensemble', 'quartet', 'quintet', 'sextet', 'septet', 'octet',
    'choir', 'choeur', 'chorale', 'chorus',
    'brass band', 'big band', 'chamber', 'philharmonie',
    
    # Enfants et comptines
    'titounis', 'enfant', 'comptine', 'bébé', 'baby', 'kids', 'children',
    'nursery', 'berceuse','chanson enfantine', 'musique pour enfants', 'kids music',
    'chansons','comptines pour enfants','musique enfantine','chansons pour enfants',
    
    # Compilations et collections
    'playlist', 'compilation', 'various', 'various artists', 'collectif',
    'tribute', 'hommage', 'best of', 'greatest hits', 'hit','hits','mix','mixtape','chanson française','chansons françaises',
    'meilleur','meilleure','meilleurs','meilleures','classique','classiques','incontournable','incontournables',
    'variétés','variété française','variétés françaises',
    
    # Karaoke et covers
    'karaoke', 'backing track', 'cover', 'tribute band',
    
    # Fans et unofficial
    'fan', 'fanmade', 'unofficial', 'bootleg',
    
    # Remixes et versions
    'remix', 'remixes', 'remixed', 'remixer',
    
    # Autres à exclure
    'sound effect', 'sound effects', 'sfx', 'foley',
    'radio edit', 'radio version', 'clean version',
    'acapella', 'a capella', 'cappella','Ebony'
]

GENRES_EXCLUS = [
    'classical', 'baroque', 'opera', 'medieval', 'renaissance',
    'romantic', 'contemporary classical', 'modern classical',
    'swing', 'bebop', 'hard bop', 'orchestre', 'chorale',
    'children', 'kids', 'nursery', 'comptines',
    'edm', 'trance', 'hardstyle', 'drum and bass', 'dubstep',
    'techno', 'minimal', 'ambient', 'downtempo',
    'world', 'folk', 'traditional', 'ethnic',
    'comedy', 'spoken word', 'audiobook', 'podcast',
    'sleep', 'meditation', 'relaxation', 'healing',
    'christmas', 'holiday', 'seasonal',
]

DJ_PATTERNS = [
    r'\bdj\b', r'^dj\s', r'\sdj$', r'dj[-_\.]', r'[-_\.]dj',
]

# ============================================================================
# CRITÈRES DE FILTRAGE
# ============================================================================

# Spotify
SPOTIFY_MIN_FOLLOWERS = 100
SPOTIFY_MAX_FOLLOWERS = 40000
SPOTIFY_MAX_POPULARITY = 60
ANNEE_MIN_PREMIER_ALBUM = 2020

# Deezer
DEEZER_MIN_FANS = 100
DEEZER_MAX_FANS = 40000

# ============================================================================
# FONCTIONS DE VALIDATION
# ============================================================================

def est_probablement_dj(nom):
    """Détecter si c'est probablement un DJ"""
    nom_lower = nom.lower()
    for pattern in DJ_PATTERNS:
        if re.search(pattern, nom_lower):
            return True
    mots_dj = ['deejay', 'dee jay', 'disc jockey', 'disk jockey']
    return any(mot in nom_lower for mot in mots_dj)

def est_probablement_producteur(nom):
    """Détecter si c'est probablement un producteur"""
    nom_lower = nom.lower()
    mots_prod = ['prod', 'producer', 'producteur', 'beat maker', 'beatmaker',
                'beatz', 'instrumental', 'type beat', 'beats']
    return any(mot in nom_lower for mot in mots_prod)

def nom_contient_exclusions(nom):
    """Vérifier si le nom contient des mots exclus"""
    nom_lower = nom.lower()
    return any(exclus in nom_lower for exclus in MOTS_EXCLUS_NOM)

def genres_sont_valides(genres):
    """Vérifier que les genres ne sont pas dans la liste d'exclusion"""
    if not genres:
        return True
    genres_lower = [g.lower() for g in genres]
    return not any(genre_exclus in genre for genre_exclus in GENRES_EXCLUS for genre in genres_lower)

def get_premier_album_annee(artist_id, token):
    """Récupérer l'année du premier album d'un artiste (Spotify uniquement)"""
    try:
        url = f'https://api.spotify.com/v1/artists/{artist_id}/albums'
        headers = {'Authorization': f'Bearer {token}'}
        params = {'include_groups': 'album,single', 'limit': 50, 'market': 'FR'}
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            data = response.json()
            albums = data.get('items', [])
            
            if not albums:
                return None
            
            annees = []
            for album in albums:
                release_date = album.get('release_date', '')
                if release_date:
                    try:
                        annee = int(release_date.split('-')[0])
                        annees.append(annee)
                    except:
                        continue
            
            if annees:
                return min(annees)
            return None
        
        elif response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 2))
            time.sleep(retry_after)
            return get_premier_album_annee(artist_id, token)
        
        return None
    
    except Exception as e:
        return None

# ============================================================================
# RECHERCHE SPOTIFY
# ============================================================================

def rechercher_artistes_spotify(token):
    """Rechercher artistes via Spotify avec filtres ultra-stricts"""
    artistes_trouves = {}
    stats_rejets = {
        'DJ': 0, 'Producteur': 0, 'Mot exclus dans nom': 0,
        'Genre exclu': 0, 'Ancien artiste': 0, 'Critères followers/popularity': 0
    }
    
    print(" SPOTIFY - COLLECTE AVEC FILTRES ULTRA-STRICTS")

    print(f"\n Critères:")
    print(f"   Followers: {SPOTIFY_MIN_FOLLOWERS:,} à {SPOTIFY_MAX_FOLLOWERS:,}")
    print(f"   Popularity: max {SPOTIFY_MAX_POPULARITY}")
    print(f"   Premier album: >= {ANNEE_MIN_PREMIER_ALBUM}")
    
    total_keywords = sum(len(keywords) for keywords in SEARCH_KEYWORDS_SPOTIFY.values())
    print(f"\n Recherche: {total_keywords} mots-clés")
    print()
    
    for genre, keywords in SEARCH_KEYWORDS_SPOTIFY.items():
        print(f"🎵 {genre} ({len(keywords)} mots-clés)")
        genre_count = 0
        
        for i, keyword in enumerate(keywords, 1):
            print(f"    [{i}/{len(keywords)}] '{keyword}'...", end=' ', flush=True)
            
            url = 'https://api.spotify.com/v1/search'
            headers = {'Authorization': f'Bearer {token}'}
            params = {'q': keyword, 'type': 'artist', 'limit': 50, 'market': 'FR'}
            
            try:
                response = requests.get(url, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    artists = data.get('artists', {}).get('items', [])
                    
                    found_count = 0
                    for artist in artists:
                        artist_id = artist['id']
                        
                        if artist_id in artistes_trouves:
                            continue
                        
                        # Critères followers/popularity
                        followers = artist['followers']['total']
                        popularity = artist['popularity']
                        
                        if not (SPOTIFY_MIN_FOLLOWERS <= followers <= SPOTIFY_MAX_FOLLOWERS):
                            stats_rejets['Critères followers/popularity'] += 1
                            continue
                        
                        if popularity > SPOTIFY_MAX_POPULARITY:
                            stats_rejets['Critères followers/popularity'] += 1
                            continue
                        
                        # Filtres nom/genres
                        nom = artist['name']
                        genres = artist.get('genres', [])
                        
                        if est_probablement_dj(nom):
                            stats_rejets['DJ'] += 1
                            continue
                        
                        if est_probablement_producteur(nom):
                            stats_rejets['Producteur'] += 1
                            continue
                        
                        if nom_contient_exclusions(nom):
                            stats_rejets['Mot exclus dans nom'] += 1
                            continue
                        
                        if not genres_sont_valides(genres):
                            stats_rejets['Genre exclu'] += 1
                            continue
                        
                        # Filtre premier album >= 2018
                        premier_album_annee = get_premier_album_annee(artist_id, token)
                        if premier_album_annee and premier_album_annee < ANNEE_MIN_PREMIER_ALBUM:
                            stats_rejets['Ancien artiste'] += 1
                            continue
                        
                        #  Artiste valide
                        artistes_trouves[artist_id] = {
                            'nom': artist['name'],
                            'url_spotify': artist['external_urls']['spotify'],
                            'url_deezer': '',
                            'source': 'Spotify',
                            'followers': followers,
                            'popularity': popularity,
                            'genres': ', '.join(genres),
                            'categorie': genre
                        }
                        
                        found_count += 1
                    
                    print(f"→ {found_count} retenus")
                    genre_count += found_count
                
                elif response.status_code == 429:
                    retry_after = int(response.headers.get('Retry-After', 5))
                    print(f"⚠️ Rate limit {retry_after}s")
                    time.sleep(retry_after)
                else:
                    print(f"❌ Erreur {response.status_code}")
            
            except Exception as e:
                print(f"❌ {e}")
            
            time.sleep(0.3)
        
        print(f"  >> Total {genre}: {genre_count} artistes\n")
    
    # Stats
    print("\n" + "=" * 70)
    print("SPOTIFY - STATISTIQUES DE FILTRAGE")
    print("=" * 70)
    total_rejets = sum(stats_rejets.values())
    print(f"Total artistes rejetés: {total_rejets}")
    for raison, count in sorted(stats_rejets.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            pct = (count / total_rejets * 100) if total_rejets > 0 else 0
            print(f"  - {raison}: {count} ({pct:.1f}%)")
    
    return artistes_trouves

# ============================================================================
# RECHERCHE DEEZER
# ============================================================================

def rechercher_artistes_deezer():
    """Rechercher artistes via Deezer (playlists)"""
    artistes_trouves = {}
    stats_rejets = {
        'DJ': 0, 'Producteur': 0, 'Mot exclus dans nom': 0,
        'Critères fans': 0
    }
    
    (" DEEZER - COLLECTE VIA PLAYLISTS")

    print(f"\n Critères:")
    print(f"   Fans: {DEEZER_MIN_FANS:,} à {DEEZER_MAX_FANS:,}")
    print(f"\n NOTE: Deezer API ne permet pas de filtrer par 'premier album >= 2018'")
    print(f"           Seuls les filtres DJ/producteur/nom sont appliqués")
    
    total_playlists = sum(len(playlists) for playlists in PLAYLISTS_DEEZER.values())
    print(f"\n Recherche: {total_playlists} playlists")
    print()
    
    for genre, playlist_ids in PLAYLISTS_DEEZER.items():
        print(f"🎵 {genre} ({len(playlist_ids)} playlists)")
        genre_count = 0
        
        for i, playlist_id in enumerate(playlist_ids, 1):
            print(f"    [{i}/{len(playlist_ids)}] Playlist {playlist_id}...", end=' ', flush=True)
            
            try:
                url = f"{BASE_URL_DEEZER}/playlist/{playlist_id}/tracks"
                params = {'limit': 100}
                response = requests.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    tracks = data.get('data', [])
                    
                    artist_ids_seen = set()
                    found_count = 0
                    
                    for track in tracks:
                        artist_data = track.get('artist', {})
                        artist_id = artist_data.get('id')
                        
                        if not artist_id or artist_id in artist_ids_seen:
                            continue
                        
                        artist_ids_seen.add(artist_id)
                        
                        if artist_id in artistes_trouves:
                            continue
                        
                        # Récupérer détails artiste
                        artist_url = f"{BASE_URL_DEEZER}/artist/{artist_id}"
                        artist_response = requests.get(artist_url)
                        
                        if artist_response.status_code != 200:
                            continue
                        
                        artist = artist_response.json()
                        
                        # Critères fans
                        nb_fan = artist.get('nb_fan', 0)
                        
                        if not (DEEZER_MIN_FANS <= nb_fan <= DEEZER_MAX_FANS):
                            stats_rejets['Critères fans'] += 1
                            continue
                        
                        # Filtres nom
                        nom = artist.get('name', '')
                        
                        if est_probablement_dj(nom):
                            stats_rejets['DJ'] += 1
                            continue
                        
                        if est_probablement_producteur(nom):
                            stats_rejets['Producteur'] += 1
                            continue
                        
                        if nom_contient_exclusions(nom):
                            stats_rejets['Mot exclus dans nom'] += 1
                            continue
                        
                        #  Artiste valide
                        genre_api = get_deezer_artist_genre(artist_id)

                        artistes_trouves[artist_id] = {
                            'nom': artist.get('name', ''),
                            'url_spotify': '',
                            'url_deezer': artist.get('link', ''),
                            'source': 'Deezer',
                            'fans': nb_fan,
                            'categorie': genre,
                            'genre': genre_api 
                        }
                        
                        found_count += 1
                        
                        time.sleep(0.1)
                    
                    print(f"→ {found_count} retenus")
                    genre_count += found_count
                
                else:
                    print(f" Erreur {response.status_code}")
            
            except Exception as e:
                print(f" {e}")
            
            time.sleep(0.5)
        
        print(f"  >> Total {genre}: {genre_count} artistes\n")
    
    # Stats

    print(" DEEZER - STATISTIQUES DE FILTRAGE")

    total_rejets = sum(stats_rejets.values())
    print(f"Total artistes rejetés: {total_rejets}")
    for raison, count in sorted(stats_rejets.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            pct = (count / total_rejets * 100) if total_rejets > 0 else 0
            print(f"  - {raison}: {count} ({pct:.1f}%)")
    
    return artistes_trouves

def rechercher_artistes_deezer_par_mots_cles():
    """Rechercher artistes Deezer par mots-clés (comme Spotify)"""
    artistes_trouves = {}
    stats_rejets = {
        'DJ': 0, 'Producteur': 0, 'Mot exclus dans nom': 0,
        'Critères fans': 0
    }
    
    print(" DEEZER - COLLECTE PAR MOTS-CLÉS")
    print(f"\n Critères:")
    print(f"   Fans: {DEEZER_MIN_FANS:,} à {DEEZER_MAX_FANS:,}")
    
    KEYWORDS_DEEZER = [
        # Général FR
        'musique française', 'artiste français', 'nouvelle scène française',
        'artiste émergent français', 'musique actuelle française',

        # Rap / Hip-Hop / RnB
        'rap français', 'rappeur français', 'nouveau rappeur français',
        'trap français', 'drill français', 'rap underground français','hip hop soul français',
        'rap paris', 'rap marseille', 'rap lyon', 'rap lille','hip hop rnb français',
        'rap 91', 'rap 92', 'rap 93', 'rap 94','hiphop français','new style français',
        'rap indépendant', 'rap soundcloud français', 'urban français', 'rnb français','r&b français','hip hop français',
        'rap alternatif français', 'rap émergent français', 'rap indépendant français',
        'rap underground français', 'rap conscient français', 'rap politique français',
        'rap social français', 'rap engagé français', 'rap de rue français', 'rap hardcore français',

        # Pop / Chanson
        'pop français', 'chanson française', 'nouvelle scène française',
        'indie pop français', 'chanteur français', 'chanteuse française',
        'pop alternative française', 'electro pop français',
        'nouveau talent pop français', 'artiste pop émergent','pop rock français',
        'pop paris', 'pop marseille', 'pop lyon', 'pop lille',

        # Rock / Metal
        'rock français', 'rock alternatif français', 'indie rock français',
        'punk français', 'metal français', 'post rock français',

        # Indie / Alternative
        'indie français', 'musique alternative française',
        'bedroom pop français', 'folk français',

        # Jazz / Soul / Funk
        'jazz français', 'soul français','jazz soul français', 'funk français',
        'jazz moderne français', 'neo soul français', 'nu jazz français','gospel français',
        'soul neo français', 'soul neo-soul français', 'new jazz français',
        'soul paris', 'soul marseille', 'soul lyon', 'soul lille',
        'gospel paris', 'gospel marseille', 'gospel lyon', 'gospel lille',

        # Electro
        'electro français', 'électro pop française',
        'électro indé française', 'techno française',
        'house française', 'french touch',

        # Afro / influences
        'afrobeat français', 'afro pop française',
        'afro trap français', 'amapiano français'
    ]

    
    print(f"\n Recherche: {len(KEYWORDS_DEEZER)} mots-clés")
    
    for i, keyword in enumerate(KEYWORDS_DEEZER, 1):
        print(f"    [{i}/{len(KEYWORDS_DEEZER)}] '{keyword}'...", end=' ', flush=True)
        
        try:
            url = f"{BASE_URL_DEEZER}/search/artist"
            params = {'q': keyword, 'limit': 100}
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                artists = data.get('data', [])
                
                found_count = 0
                for artist in artists:
                    artist_id = artist.get('id')
                    
                    if artist_id in artistes_trouves:
                        continue
                    
                    # Critères fans
                    nb_fan = artist.get('nb_fan', 0)
                    
                    if not (150 <= nb_fan <= 50000):  # Critères assouplis
                        stats_rejets['Critères fans'] += 1
                        continue
                    
                    # Filtres nom
                    nom = artist.get('name', '')
                    
                    if est_probablement_dj(nom):
                        stats_rejets['DJ'] += 1
                        continue
                    
                    if est_probablement_producteur(nom):
                        stats_rejets['Producteur'] += 1
                        continue
                    
                    if nom_contient_exclusions(nom):
                        stats_rejets['Mot exclus dans nom'] += 1
                        continue
                    
                    #  Artiste valide
                    genre_api = get_deezer_artist_genre(artist_id)

                    artistes_trouves[artist_id] = {
                        'nom': artist.get('name', ''),
                        'url_spotify': '',
                        'url_deezer': artist.get('link', ''),
                        'source': 'Deezer',
                        'fans': nb_fan,
                        'categorie': 'Autre',
                        'genre': genre_api 
                    }
                    
                    found_count += 1
                
                print(f"→ {found_count} retenus")
            else:
                print(f" Erreur {response.status_code}")
        
        except Exception as e:
            print(f" {e}")
        
        time.sleep(0.5)
    
    print(f"\n Total Deezer (mots-clés): {len(artistes_trouves)} artistes")
    
    return artistes_trouves
# ============================================================================
# MATCHING INTELLIGENT
# ============================================================================

def normaliser_nom_artiste(nom):
    """
    Normaliser le nom d'un artiste pour améliorer le matching
    
    Transformations :
    - Enlever accents : "Roméo" → "Romeo"
    - Minuscules : "SCH" → "sch"
    - Enlever ponctuation : "L'Impératrice" → "limperatrice"
    - Enlever espaces multiples : "L  Imperatrice" → "limperatrice"
    """
    if not nom:
        return ""
    
    # Convertir en minuscules
    nom = nom.lower().strip()
    
    # Enlever accents
    nom = unicodedata.normalize('NFKD', nom)
    nom = nom.encode('ASCII', 'ignore').decode('ASCII')
    
    # Enlever ponctuation et espaces
    nom = re.sub(r'[^\w\s]', '', nom)
    nom = re.sub(r'\s+', '', nom)
    
    return nom

def similarity_ratio(s1, s2):
    """
    Calculer similarité entre deux chaînes (simple Levenshtein)
    Retourne un score entre 0 et 100
    """
    if s1 == s2:
        return 100
    
    if not s1 or not s2:
        return 0
    
    # Levenshtein simple
    len1, len2 = len(s1), len(s2)
    if len1 > len2:
        s1, s2 = s2, s1
        len1, len2 = len2, len1
    
    current_row = range(len1 + 1)
    for i in range(1, len2 + 1):
        previous_row, current_row = current_row, [i] + [0] * len1
        for j in range(1, len1 + 1):
            add, delete, change = previous_row[j] + 1, current_row[j-1] + 1, previous_row[j-1]
            if s1[j-1] != s2[i-1]:
                change += 1
            current_row[j] = min(add, delete, change)
    
    distance = current_row[len1]
    max_len = max(len(s1), len(s2))
    similarity = ((max_len - distance) / max_len) * 100
    
    return round(similarity, 1)

def trouver_meilleur_match(nom_deezer, artistes_spotify_dict, seuil=85):
    """
    Trouver le meilleur match Spotify pour un artiste Deezer
    
    Args:
        nom_deezer: Nom de l'artiste Deezer
        artistes_spotify_dict: Dict {nom_normalise: nom_original}
        seuil: Score minimum pour accepter un match (défaut: 85%)
    
    Returns:
        nom_original_spotify ou None
    """
    nom_deezer_normalise = normaliser_nom_artiste(nom_deezer)
    
    # D'abord chercher match exact
    if nom_deezer_normalise in artistes_spotify_dict:
        return artistes_spotify_dict[nom_deezer_normalise]
    
    # Sinon chercher match approximatif
    meilleur_score = 0
    meilleur_match = None
    
    for nom_spotify_normalise, nom_spotify_original in artistes_spotify_dict.items():
        score = similarity_ratio(nom_deezer_normalise, nom_spotify_normalise)
        
        if score > meilleur_score and score >= seuil:
            meilleur_score = score
            meilleur_match = nom_spotify_original
    
    return meilleur_match

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Point d'entrée principal"""
    
    # 1. Recherche Spotify
    try:
        token = get_spotify_token()
    except Exception as e:
        print(f"Erreur authentification Spotify: {e}")
        return False
    
    artistes_spotify = rechercher_artistes_spotify(token)
    
    # 2. Recherche Deezer (DOUBLE MÉTHODE)
    artistes_deezer_playlists = rechercher_artistes_deezer()
    artistes_deezer_keywords = rechercher_artistes_deezer_par_mots_cles()
    
    # Fusionner les 2 sources Deezer
    artistes_deezer = {**artistes_deezer_playlists, **artistes_deezer_keywords}
    
    print(f"\n Deezer combiné:")
    print(f"   Playlists: {len(artistes_deezer_playlists)}")
    print(f"   Mots-clés: {len(artistes_deezer_keywords)}")
    print(f"   Total unique: {len(artistes_deezer)}")
    
    # 3. Merger les résultats avec MATCHING INTELLIGENT
    print("\n" + "=" * 70)
    print(" FUSION SPOTIFY + DEEZER (Matching Intelligent)")
    print("=" * 70)
    
    # Créer dictionnaire Spotify : {nom_normalise: données}
    artistes_spotify_par_nom = {}
    spotify_normalise_to_original = {}
    
    for artist_id, data in artistes_spotify.items():
        nom_original = data['nom']
        nom_normalise = normaliser_nom_artiste(nom_original)
        
        artistes_spotify_par_nom[nom_normalise] = {
            'nom': nom_original,
            'url_spotify': data['url_spotify'],
            'url_deezer': '',
            'categorie': data.get('categorie', 'Autre'),
            'genre': data.get('categorie', 'Autre')
        }
        spotify_normalise_to_original[nom_normalise] = nom_original
    
    # Fusionner avec Deezer (matching intelligent)
    matches_count = 0
    nouveaux_deezer = 0
    
    print(f"\n Recherche de correspondances Spotify ↔ Deezer...")
    
    for artist_id, data in artistes_deezer.items():
        nom_deezer = data['nom']
        nom_deezer_normalise = normaliser_nom_artiste(nom_deezer)
        
        # Chercher match dans Spotify
        match_spotify = trouver_meilleur_match(nom_deezer, spotify_normalise_to_original, seuil=85)
        
        if match_spotify:
            # Match trouvé !
            nom_spotify_normalise = normaliser_nom_artiste(match_spotify)
            
            # Ajouter URL Deezer à l'artiste Spotify
            artistes_spotify_par_nom[nom_spotify_normalise]['url_deezer'] = data['url_deezer']
            
            matches_count += 1
            
            # Afficher si noms différents
            if nom_deezer != match_spotify:
                print(f" Match: '{nom_deezer}' (Deezer) ↔ '{match_spotify}' (Spotify)")
        else:
            # Pas de match - nouvel artiste uniquement Deezer
            artistes_spotify_par_nom[nom_deezer_normalise] = {
                'nom': nom_deezer,
                'url_spotify': '',
                'url_deezer': data['url_deezer'],
                'categorie': data.get('categorie', 'Autre'),
                'genre': data.get('genre', 'Autre')
            }
            nouveaux_deezer += 1
    
    print(f"\n Résultats du matching:")
    print(f"   Artistes Spotify: {len(artistes_spotify)}")
    print(f"   Artistes Deezer: {len(artistes_deezer)}")
    print(f"   Matches trouvés: {matches_count} ")
    print(f"   Nouveaux (Deezer seul): {nouveaux_deezer}")
    print(f"   Total unique: {len(artistes_spotify_par_nom)}")
    
    # Compter artistes avec les deux
    both = sum(1 for a in artistes_spotify_par_nom.values() if a['url_spotify'] and a['url_deezer'])
    spotify_only = sum(1 for a in artistes_spotify_par_nom.values() if a['url_spotify'] and not a['url_deezer'])
    deezer_only = sum(1 for a in artistes_spotify_par_nom.values() if a['url_deezer'] and not a['url_spotify'])
    
    print(f"\n Détail:")
    print(f"  - Spotify + Deezer: {both} ")
    print(f"  - Spotify uniquement: {spotify_only}")
    print(f"  - Deezer uniquement: {deezer_only}")
    
    # 4. Créer DataFrame AVEC CATÉGORIE
    df_data = []
    for data in artistes_spotify_par_nom.values():
        df_data.append({
            'nom': data['nom'],
            'url_spotify': data.get('url_spotify', ''),
            'url_deezer': data.get('url_deezer', ''),
            'categorie': data.get('categorie', 'Autre'),
            'genre': data.get('genre', 'Autre')
        })

    df = pd.DataFrame(df_data)
    
    # 5. Sauvegarder
    if os.path.exists('artist_urls.csv'):
        print(f"\n artist_urls.csv existe déjà")
        response = input("Écraser ? (o/n): ")
        if response.lower() != 'o':
            existing_df = pd.read_csv('artist_urls.csv')
            existing_names = set(existing_df['nom'].str.lower().str.strip())
            nouveaux = df[~df['nom'].str.lower().str.strip().isin(existing_names)]
            
            if not nouveaux.empty:
                merged_df = pd.concat([existing_df, nouveaux], ignore_index=True)
                merged_df.to_csv('artist_urls.csv', index=False)
                print(f"\n {len(nouveaux)} nouveaux artistes ajoutés")
                print(f"   Total: {len(merged_df)} artistes")
            else:
                print("\n Tous déjà présents")
            
            return True

    df.to_csv('artist_urls.csv', index=False)
    print(f" COLLECTE TERMINÉE - SPOTIFY + DEEZER")

    print(f"\n Résultat:")
    print(f"Total artistes: {len(df)}")
    print(f"Fichier créé: artist_urls.csv")

    print()
    print(f" PROCHAINE ÉTAPE:")
    print(f"   python music_talent_radar.py --all")
    print()
        
    return True

if __name__ == '__main__':
    main()