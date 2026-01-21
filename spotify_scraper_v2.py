import spotipy # type: ignore
from spotipy.oauth2 import SpotifyClientCredentials # type: ignore
import pandas as pd
from datetime import datetime
import time
import re
import requests

# Configuration API Spotify
CLIENT_ID = '521adaf36b6948bb82d6c6f398f9004e'
CLIENT_SECRET = '11fcdc06df214181bfa8e8580c86126d'

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# CRITERES
MIN_FOLLOWERS = 1000
MAX_FOLLOWERS = 60000  
MIN_POPULARITY = 10
MAX_POPULARITY = 60

# MOTS-CLES
SEARCH_KEYWORDS = {
    'Rap-HipHop-RnB': [
        # 18 mots-clés essentiels
        'rap français', 'rappeur français', 'nouveau rappeur français',
        'trap français', 'drill français', 'rap underground français',
        'rap paris', 'rap marseille', 'rap lyon', 'rap lille',
        'rap 91', 'rap 92', 'rap 93', 'rap 94',
        'rap indépendant', 'rap soundcloud français', 'urban français', 'rnb français',
    ],
    'Pop': [
        # 10 mots-clés essentiels
        'pop français', 'chanson française', 'nouvelle scène française',
        'indie pop français', 'chanteur français', 'chanteuse française',
        'pop alternative française', 'electro pop français',
        'nouveau talent pop français', 'artiste pop émergent',
    ],
    'Afrobeat-Amapiano': [
        # 7 mots-clés essentiels
        'afrobeat français', 'afrobeat france', 'amapiano',
        'afrobeats', 'afro trap français', 'afro drill',
        'dancehall français',
    ],
    'Rock-Metal': [
        # 5 mots-clés essentiels
        'rock français', 'indie rock français', 'metal français',
        'punk français', 'rock alternatif français',
    ],
    'Indie-Alternative': [
        # 3 mots-clés essentiels
        'indie français', 'indie pop français', 'alternative français',
    ],
    'Jazz-Soul': [
        # 2 mots-clés essentiels
        'jazz français', 'soul français',
    ],
    'electro': [
        'french touch', 'électro moderne', 'électro urbaine',
        'artiste électro français', 'nouveau talent électro',
    ]
}

SEED_ARTISTS = {
    'Pop': ['Angèle', 'Clara Luciani', 'Louane', 'Videoclub', 'Julien Doré','Hoshi'],
    'Rap-HipHop-RnB': ['Ninho', 'Jul', 'SCH', 'Gazo', 'Tiakola', 'Freeze Corleone', 'Lomepal'],
    'Afrobeat-Amapiano': ['Dadju', 'KeBlack', 'Vegedream', 'MHD', 'Naza', 'Tayc'],
    'Rock-Metal': ['Gojira', 'Shaka Ponk', 'Tagada Jones','Ultra Vomit'],
    'Indie-Alternative': ['Phoenix', 'Polo & Pan', 'L\'Impératrice','La Femme','Voyou'],
    'Jazz': ['Ibrahim Maalouf', 'Thomas Dutronc', 'Melody Gardot'],
    'Country-Folk': ['Ben Mazué', 'Vianney', 'Pomme','Hugo TSR'],
    'Soul-Funk': ['Yadam', 'Fishbach', 'Imany', 'Ayo','Jain']
}

MOTS_EXCLUS_NOM = [
    'orchestre', 'orchestra', 'symphonique', 'symphony', 'philharmonique',
    'ensemble', 'quartet', 'quintet', 'choir', 'choeur', 'chorale',
    'brass band', 'big band', 'chamber',
    ' dj ', 'dj-', '-dj', 'dj.',
    'titounis', 'enfant', 'comptine', 'bébé', 'baby', 'kids', 'children',
    'playlist', 'compilation', 'various artists', 'collectif'
]

# LISTE NOIRE : Artistes connus à exclure EXPLICITEMENT
ARTISTES_CONNUS_BLACKLIST = [
    # Acteurs/Célébrités qui chantent
    'ryan gosling', 'emma stone', 'johnny depp', 'scarlett johansson',
    'ronan keating', 'kore', 'ade', 'adé',
    
    # Rap FR - Anciens/Établis
    'matt houston', 'priscilla', 'la brigade', 'beat de boul',
    'mc jean gab', '3eme oeil', '3ème oeil', 'troisieme oeil',
    'iam', 'ntm', 'suprême ntm', 'arsenik', 'lunatic', 'ministere amer',
    'fonky family', '113', 'ideal j', 'stomy bugsy', 'passi',
    'doc gyneco', 'rohff', 'sinik', 'booba', 'la fouine', 'kaaris',
    'oxmo puccino', 'disiz', 'kery james', 'soprano', 'akhenaton',
    'shurik\'n', 'freeman', 'sat', 'rim\'k', 'mokobe', 'ali',
    'sniper', 'tandem', 'salif', 'diam\'s', 'keny arkana',
    'youssoupha', 'sexion d\'assaut', 'black m', 'gims', 'maitre gims',
    'nekfeu', 'alpha wann', 's-crew', '1995', 'jazzy bazz',
    'orelsan', 'gringe', 'casseurs flowters', 'scylla', 'kekra',
    'kamelancien', 'rocca', 'shurik\'n', 'l\'skadrille',
    'monsieur nov', 'mr nov', 'nov',
    'pnl', 'damso', 'hamza', 'aya nakamura',
    'naps', 'soolking', 'niska', 'gradur', 'lacrim',
    'bramsito', 'lartiste', 'maes', 'plk',
    'sefyu', 'la rumeur', 'casey', 'hocus pocus', 'saian supa crew',
    'fabe', 'mc solaar', 'abd al malik', 'oxmo', 'ben l\'oncle soul',
    'saja boys', 'saja', 'alonzo', 'rim\'k', 'sat l\'artificier',
    'koba lad', 'zola',
    '2l', 'ssissik', 'sissik', 'cut killer', 'cutee b', 'lord kossity',
    'dj abdel', 'dj kore', 'dj quick', 'dj mehdi', 'dj cam',
    'raggasonic', 'ideal j', 'pit baccardi', 'intouchable',
    'coluche', 'organiz', 'paga', 'kayna samet',
    'rohff', 'rim-k', 'sat', 'tunisiano', 'dany synthé',
    
    # Artistes hip-hop FR détectés dans les résultats
    'lacraps', '13ème art', '13eme art', 'kohndo', 'rockin squat',
    'rocé', 'roce', 'dee nasty', 'def bond', 'ttc', 'dany dan', 'imhotep',
    
    # Autres artistes hip-hop FR connus similaires
    'assassin', 'oxmo puccino', 'stomy bugsy', 'doc gyneco',
    'arsenik', 'lunatic', 'ali', 'mafia k1 fry', 'ideal j',
    '113', 'ap', 'rim k', 'mokobé', 'mokobe',
    'fonky family', 'iam members', 'shurik\'n', 'freeman', 'akhenaton',
    'la cliqua', 'busta flex', 'menelik', 'la caution',
    'x-men', 'lucien', 'casseurs flowters', 'gringe',
    'ärsenik', 'calbo', 'lino', 'pit baccardi',
    'tandem', 'salif', 'diam\'s', 'keny arkana', 'casey',
    'la rumeur', 'hamé', 'ekoué', 'philippe fragione',
    
    # Pop/Variété FR - Établis
    'celine dion', 'johnny hallyday', 'patricia kaas', 'mylene farmer',
    'francis cabrel', 'jean-jacques goldman', 'pascal obispo',
    'patrick bruel', 'florent pagny', 'zazie', 'carla bruni',
    'vanessa paradis', 'benjamin biolay', 'pierre lapointe',
    'camille', 'christine and the queens', 'stromae',
    'coeur de pirate', 'zaz', 'shy\'m', 'tal', 'jenifer',
    'nolwenn leroy', 'calogero', 'christophe mae', 'm pokora',
    'amel bent', 'vitaa', 'slimane', 'kendji girac',
    'claudio capeo', 'patrick fiori',
    'axelle red', 'axel red', 'wejdene', 'imen es', 'vitaa',
    'amir', 'matt pokora', 'soprano', 'kendji', 'claudio capéo',
    
    # ========== BLACKLIST PHASE 2 (Détectés dans les 855 résultats) ==========
    # Pop
    'lou doillon', 'cats on trees', 'bertrand belin', 'ycare',
    'naive new beaters', 'la grande sophie', 'la zarra',
    'adèle castillon', 'adele castillon', 'addison rae', 'doris day',
    'cody johnson', 'shaboozey', 'lola young', 'olivia dean',
    
    # Rap/Hip-Hop détectés Phase 2
    'booska-p', 'booska p', 'le rat luciano', 'swing',
    'alpha 5.20', 'alpha 520', 'ol\'kainry', 'olkainry',
    
    # Afrobeat/Reggae/Dancehall détectés Phase 2
    'pierpoljak', 'nuttea', 'slaï', 'slai',
    
    # Jazz/Soul détectés Phase 2
    'zoufris maracas', 'kimberose', 'sacha distel', 'jehro',
    'pauline croze', 'lynda lemay', 'dom la nena',
    'albin de la simone', 'jay-jay johanson', 'winston mcanuff',
    'justin hurwitz', 'grandmaster flash', 'moondog',
    
    # Electro détectés Phase 2
    'general elektriks', 'laurent wolf', 'agar agar',
    'kris kross amsterdam', 'sofi tukker', 'a-trak',
    'neiked', 'boostee', 'philip george', 'sg lewis',
    
    # Rock/Metal détectés Phase 2
    'les ramoneurs de menhirs', 'didier super',
    'amorphis', 'devildriver', 'bananarama',
    'guerilla poubelle', 'electric guest', 'daniel powter',
    'black bomb a', 'the beautiful south', 'igorrr',
    'ultravox', 'melanie c', 'viagra boys',
    
    # Indie/Alternative détectés Phase 2
    'jamie xx', 'miike snow', 'battle beast', 'django django',
    'kid francescoli', 'friendly fires', 'future islands',
    'the pirouettes', 'françois & the atlas mountains',
    'francois atlas mountains', 'kakkmaddafakka',
    
    # Soul/Funk détectés Phase 2
    'puggy', 'blood orange', 'hollysiz',
    
    # Légendes internationales détectés Phase 2
    'the band', 'alex aiono', 'gavin greenaway', 'emil gilels',
    
    # Rock/Metal FR - Établis
    'noir desir', 'mano negra', 'les negresses vertes', 'telephone',
    'trust', 'indochine', 'rita mitsouko', 'bashung', 'bertignac',
    'noir désir', 'bertrand cantat', 'renaud', 'goldman', 
    'luke', 'mickey 3d', 'deportivo', 'bb brunes', 'tahiti 80',
    'air', 'justice', 'daft punk', 'kavinsky',
    'mass hysteria', 'dagoba',
    
    # Electro/DJ FR - Établis  
    'david guetta', 'bob sinclar', 'martin solveig', 'kungs',
    'madeon', 'tchami', 'malaa', 'dj snake', 'gesaffelstein',
    'sebastien leger', 'fred falke', 'breakbot',
    
    # Chanson FR - Classiques
    'brel', 'brassens', 'ferré', 'barbara', 'piaf', 'aznavour',
    'serge gainsbourg', 'france gall', 'hardy', 'birkin',
    
    # Groupes années 90-2000
    'manau', 'les inconnus', 'worlds apart', 'plus belle la vie',
    '2be3', 'g-squad', 'linkup', 'alliance ethnik', 'little nicky',
    
    # LÉGENDES INTERNATIONALES - Blues/Jazz/Soul/Rock Classique
    'memphis slim', 'b.b. king', 'bb king', 'muddy waters', 'howlin wolf',
    'john lee hooker', 'robert johnson', 'buddy guy', 'albert king',
    'freddie king', 'lightnin hopkins', 'lightnin\' hopkins',
    'ray charles', 'james brown', 'aretha franklin', 'otis redding',
    'sam cooke', 'marvin gaye', 'stevie wonder', 'curtis mayfield',
    'etta james', 'nina simone', 'billie holiday', 'ella fitzgerald',
    'louis armstrong', 'duke ellington', 'miles davis', 'john coltrane',
    'charlie parker', 'dizzy gillespie', 'thelonious monk',
    'chuck berry', 'little richard', 'fats domino', 'bo diddley',
    'elvis presley', 'elvis', 'the beatles', 'beatles', 'rolling stones',
    'led zeppelin', 'pink floyd', 'the doors', 'jimi hendrix',
    'bob dylan', 'neil young', 'david bowie', 'lou reed',
    'iggy pop', 'the clash', 'sex pistols', 'ramones',
]

GENRES_EXCLUS = [
    'classical', 'orchestra', 'symphonic', 'chamber', 'opera',
    'children', 'kids', 'baby', 'nursery',
    'christmas', 'holiday', 'noel',
    'compilation', 'soundtrack', 'anime', 'gaming'
]

def get_first_album_year(artist_id, sp):
    """
    Récupère l'année du premier album de l'artiste
    Retourne None si pas d'album trouvé
    """
    try:
        # Récupérer les albums de l'artiste (limite 50)
        albums = sp.artist_albums(artist_id, album_type='album', limit=50)
        
        if not albums or 'items' not in albums or len(albums['items']) == 0:
            return None
        
        years = []
        for album in albums['items']:
            release_date = album.get('release_date', '')
            if release_date:
                # Extraire l'année (format: YYYY-MM-DD ou YYYY)
                year_str = release_date.split('-')[0]
                if year_str.isdigit():
                    year = int(year_str)
                    # Valider l'année (entre 1900 et 2025)
                    if 1900 <= year <= 2025:
                        years.append(year)
        
        if years:
            return min(years)  # Année du premier album
        
        return None
        
    except Exception as e:
        return None

def get_artist_albums_count(artist_id, sp):
    """
    Compte le nombre d'albums de l'artiste
    Retourne 0 si erreur
    """
    try:
        albums = sp.artist_albums(artist_id, album_type='album', limit=50)
        
        if not albums or 'items' not in albums:
            return 0
        
        # Compter uniquement les albums (pas singles, compilations)
        return len(albums['items'])
        
    except Exception as e:
        return 0

def est_artiste_connu(artist_name, followers, popularity, artist_id=None, sp=None):
    """
    Détecte si un artiste est connu/établi - CRITÈRES SIMPLIFIÉS (Phase 1)
    Retourne True si l'artiste est connu (donc à exclure)
    Note: Critère ancienneté désactivé pour Phase 1 (trop lent)
    """
    
    # Normaliser le nom pour vérification
    name_lower = artist_name.lower().strip()
    
    # CRITERE 1 : BLACKLIST 
    for known in ARTISTES_CONNUS_BLACKLIST:
        if known in name_lower:
            return True  # Dans la blacklist = EXCLU
    
    # CRITERE 2 : Trop de followers 
    if followers > 60000:
        return True

    
    return False  

def est_nom_exclu(nom):
    nom_lower = nom.lower().strip()
    
    # Vérifier la blacklist d'artistes connus
    for artiste_connu in ARTISTES_CONNUS_BLACKLIST:
        if artiste_connu in nom_lower:
            return True
    
    # Vérifier les mots génériques à exclure
    for mot in MOTS_EXCLUS_NOM:
        if mot in nom_lower:
            return True
    
    # DJ au début du nom
    if re.match(r'^dj[\s-]', nom_lower):
        return True
    
    return False

def est_genre_exclu(genres_list):
    if not genres_list:
        return False
    genres_str = ' '.join(genres_list).lower()
    for genre_exclu in GENRES_EXCLUS:
        if genre_exclu in genres_str:
            return True
    return False

def get_artist_first_release_year(artist_id):
    try:
        albums = sp.artist_albums(artist_id, album_type='album,single', limit=50)
        if not albums['items']: # type: ignore
            return None
        years = []
        for album in albums['items']: # type: ignore
            if 'release_date' in album:
                try:
                    year = int(album['release_date'][:4])
                    years.append(year)
                except:
                    pass
        if years:
            return min(years)
        return None
    except Exception as e:
        return None

def test_api_connection():
    try:
        print("Test connexion API...")
        results = sp.search(q='test', type='artist', limit=1)
        print("API fonctionne !\n")
        return True
    except Exception as e:
        print(f"Erreur API: {e}\n")
        return False

def get_artist_info(artist_id):
    try:
        artist = sp.artist(artist_id)
        
        # Filtrage 1 : Nom (orchestres, DJs, etc.)
        if est_nom_exclu(artist['name']): # type: ignore
            return None
        
        # Filtrage 2 : Genres exclus
        if est_genre_exclu(artist['genres']): # type: ignore
            return None
        
        # Filtrage 3 : DETECTION ARTISTE CONNU (Date premier album + popularité)
        if est_artiste_connu(
            artist['name'],  # type: ignore
            artist['followers']['total'], # type: ignore
            artist['popularity'], # type: ignore
            artist_id=artist['id'],  # ← Ajouté # type: ignore
            sp=sp  # ← Ajouté
        ):
            return None  # Artiste connu détecté = EXCLU !
        
        return {
            'id': artist['id'], # type: ignore
            'nom': artist['name'], # type: ignore
            'followers': artist['followers']['total'], # type: ignore
            'popularity': artist['popularity'], # type: ignore
            'genres': ', '.join(artist['genres'][:3]) if artist['genres'] else '', # type: ignore
            'url_spotify': artist['external_urls']['spotify'], # type: ignore
            'image_url': artist['images'][0]['url'] if artist['images'] else '' # type: ignore
        }
    except Exception as e:
        return None

def is_eligible(followers, popularity):
    return (MIN_FOLLOWERS <= followers <= MAX_FOLLOWERS and 
            MIN_POPULARITY <= popularity <= MAX_POPULARITY)

def search_artists_by_keyword(keyword, genre, limit=50):
    artists = []
    seen_ids = set()
    
    try:
        results = sp.search(q=keyword, type='artist', limit=limit)
        
        for artist in results['artists']['items']: # type: ignore
            artist_id = artist['id']
            
            if artist_id not in seen_ids:
                seen_ids.add(artist_id)
                
                if is_eligible(artist['followers']['total'], artist['popularity']):
                    info = get_artist_info(artist_id)
                    
                    if info:
                        info['genre'] = genre
                        info['source'] = 'Spotify'
                        artists.append(info)
        
        time.sleep(0.2)
        
    except Exception as e:
        if "429" in str(e) or "rate limit" in str(e).lower():
            print(f"      Rate limit - pause 15 sec")
            time.sleep(15)
    
    return artists

def get_similar_artists(artist_name, genre, max_results=20):
    similar = []
    
    try:
        results = sp.search(q=artist_name, type='artist', limit=1)
        if not results['artists']['items']: # type: ignore
            return []
        
        seed_id = results['artists']['items'][0]['id'] # type: ignore
        related = sp.artist_related_artists(seed_id)
        
        for artist in related['artists'][:max_results]: # type: ignore
            if is_eligible(artist['followers']['total'], artist['popularity']):
                info = get_artist_info(artist['id'])
                if info:
                    info['genre'] = genre
                    info['source'] = 'Spotify'
                    similar.append(info)
        
        time.sleep(0.3)
        
    except Exception as e:
        pass
    
    return similar

def calculate_score(row):
    followers_score = min(30, (row['followers'] / MAX_FOLLOWERS) * 30)
    popularity_score = min(40, ((row['popularity'] - MIN_POPULARITY) / (MAX_POPULARITY - MIN_POPULARITY)) * 40)
    
    engagement_ratio = (row['popularity'] / (row['followers'] / 1000)) if row['followers'] > 0 else 0
    engagement_score = min(20, engagement_ratio * 2)
    
    current_year = datetime.now().year
    if 'premier_album' in row and pd.notna(row['premier_album']):
        years_since_debut = current_year - row['premier_album']
        if years_since_debut <= 1:
            recency_score = 10
        elif years_since_debut <= 3:
            recency_score = 7
        else:
            recency_score = 5
    else:
        recency_score = 5
    
    total_score = followers_score + popularity_score + engagement_score + recency_score
    return round(total_score, 2)

def categorize_artist(score):
    if score >= 80:
        return 'Rising Star'
    elif score >= 60:
        return 'Prometteur'
    elif score >= 40:
        return 'A Surveiller'
    else:
        return 'Debutant'

def main():
    import os
    os.makedirs('data', exist_ok=True)
    
    print("="*70)
    print("MUSICTALENTRADAR v2 - SCRAPER SPOTIFY (Phase 1 - Scraping Large)")
    print("="*70)
    print(f"\nCriteres:")
    print(f"  - Followers: {MIN_FOLLOWERS:,} - {MAX_FOLLOWERS:,}")
    print(f"  - Popularity: {MIN_POPULARITY} - {MAX_POPULARITY}")
    print(f"\nDetection artistes connus (2 criteres SEULEMENT):")
    print(f"  1. Blacklist (~220 artistes connus)")
    print(f"  2. Followers > 60k")
    print(f"\nNote: Critère 'premier album < 2015' DÉSACTIVÉ pour Phase 1")
    print(f"      (Trop lent - sera appliqué en Phase 2)")
    print(f"\nExclusions supplementaires:")
    print(f"  - Orchestres, DJs, Enfants, Compilations")
    print(f"  - Genres exclus (classical, children, etc.)")
    
    total_keywords = sum(len(keywords) for keywords in SEARCH_KEYWORDS.values())
    total_seeds = sum(len(seeds) for seeds in SEED_ARTISTS.values())
    print(f"\nRecherche:")
    print(f"  - Mots-cles: {total_keywords} (version équilibrée)")
    print(f"  - Seeds: {total_seeds}")
    print(f"  - Duree estimee: {(total_keywords * 1.5) / 60:.1f} heures")
    print(f"Note: 45 mots-clés = Compromis idéal vitesse/volume\n")
    
    if not test_api_connection():
        print("L'API ne repond pas.")
        return
    
    all_artists = []
    
    print("="*70)
    print("PHASE 1 : Recherche par Mots-Cles")
    print("="*70)
    
    for genre, keywords in SEARCH_KEYWORDS.items():
        print(f"\n{genre} ({len(keywords)} mots-cles)")
        genre_artists = []
        
        for i, keyword in enumerate(keywords, 1):
            print(f"    [{i}/{len(keywords)}] Recherche '{keyword}'...", end=' ', flush=True)
            artists = search_artists_by_keyword(keyword, genre)
            genre_artists.extend(artists)
            print(f"→ {len(artists)} trouvés (Total: {len(genre_artists)})")
        
        all_artists.extend(genre_artists)
        print(f"  >> Total {genre}: {len(genre_artists)} artistes")
    
    phase1_count = len(all_artists)
    print(f"\nPhase 1 terminee: {phase1_count} artistes")
    
    print(f"\n{'='*70}")
    print("PHASE 2 : Artistes Similaires (Related Artists)")
    print("="*70)
    
    for genre, seeds in SEED_ARTISTS.items():
        print(f"\n{genre} ({len(seeds)} seeds)")
        genre_artists = []
        
        for seed in seeds:
            similar = get_similar_artists(seed, genre)
            genre_artists.extend(similar)
            print(f"  - {seed}: {len(similar)} similaires")
        
        all_artists.extend(genre_artists)
        print(f"  >> Total {genre}: {len(genre_artists)} artistes")
    
    phase2_count = len(all_artists) - phase1_count
    print(f"\nPhase 2 terminee: +{phase2_count} artistes")
    print(f"Total avant dedoublonnage: {len(all_artists)} artistes")
    
    df = pd.DataFrame(all_artists)
    
    if len(df) == 0:
        print("\nAUCUN ARTISTE TROUVE")
        print("Les criteres sont peut-etre trop stricts.")
        print(f"Essayez de baisser ANNEE_MIN_PREMIER_ALBUM a {ANNEE_MIN_PREMIER_ALBUM - 2}") # type: ignore
        return
    
    df = df.drop_duplicates(subset=['id'])
    print(f"Apres dedoublonnage: {len(df)} artistes uniques")
    
    df['score'] = df.apply(calculate_score, axis=1)
    df['categorie'] = df['score'].apply(categorize_artist)
    df['date_collecte'] = datetime.now().strftime('%Y-%m-%d')
    df = df.sort_values('score', ascending=False)
    
    filename = f"data/spotify_artists_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print("\n" + "="*70)
    print("RESULTATS FINAUX")
    print("="*70)
    print(f"\nTotal artistes: {len(df)}")
    print(f"Score moyen: {df['score'].mean():.2f}")
    print(f"Fichier: {filename}")
    
    print(f"\nPar genre:")
    for genre, count in df['genre'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  - {genre}: {count} ({pct:.1f}%)")
    
    print(f"\nPar categorie:")
    for cat, count in df['categorie'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  - {cat}: {count} ({pct:.1f}%)")
    
    print(f"\nPar annee de debut:")
    if 'premier_album' in df.columns:
        for year, count in df['premier_album'].value_counts().sort_index(ascending=False).items():
            if pd.notna(year): # pyright: ignore[reportArgumentType, reportCallIssue]
                pct = (count / len(df)) * 100
                print(f"  - {int(year)}: {count} artistes ({pct:.1f}%)") # type: ignore
    
    print(f"\nTop 10:")
    for _, row in df.head(10).iterrows():
        year_str = f" (depuis {int(row['premier_album'])})" if pd.notna(row.get('premier_album')) else ""
        print(f"  - {row['nom']} ({row['genre']}){year_str} - {row['score']:.1f} pts - {row['followers']:,} followers")
    
    print("\n" + "="*70)
    print("COLLECTE TERMINEE")
    print("="*70)

if __name__ == "__main__":
    main()