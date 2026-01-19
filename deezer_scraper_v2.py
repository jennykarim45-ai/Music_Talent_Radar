import requests
import pandas as pd
from datetime import datetime
import time
import re

BASE_URL = "https://api.deezer.com"

MIN_FANS = 1000
MAX_FANS = 100000  # Remonté à 100k pour Deezer

PLAYLISTS_BY_GENRE = {
    'Pop': [1266970221, 1313621735],
    'Rap-HipHop-RnB': [1266982681, 2478989424, 1479461285],
    'Afrobeat-Amapiano': [1479458785, 7791005622],
    'Reggaeton-Latin': [2156279102, 1206772625],
    'Rock-Metal': [1282495565, 1479454995],
    'Indie-Alternative': [1362496635, 5221412382],
    'Jazz': [1363127927, 1479461595],
    'Country-Folk': [1282488055],
    'Soul-Funk': [1363127987]
}

SEED_ARTISTS = {
    'Pop': ['Angèle', 'Clara Luciani', 'Louane', 'Videoclub', 'Julien Doré'],
    'Rap-HipHop-RnB': ['Ninho', 'Jul', 'SCH', 'Gazo', 'Tiakola', 'Lomepal'],
    'Afrobeat-Amapiano': ['Dadju', 'KeBlack', 'Vegedream', 'MHD', 'Naza'],
    'Rock-Metal': ['Gojira', 'Shaka Ponk', 'Tagada Jones'],
    'Indie-Alternative': ['Phoenix', 'Polo & Pan', 'L\'Impératrice', 'Voyou'],
    'Jazz': ['Ibrahim Maalouf', 'Thomas Dutronc'],
    'Country-Folk': ['Ben Mazué', 'Vianney', 'Pomme'],
    'Soul-Funk': ['Yadam', 'Fishbach', 'Imany', 'Jain']
}

MOTS_EXCLUS_NOM = [
    'orchestre', 'orchestra', 'symphonique', 'symphony', 'philharmonique',
    'ensemble', 'quartet', 'quintet', 'choir', 'choeur', 'chorale',
    ' dj ', 'dj-', '-dj', 'dj.',
    'titounis', 'enfant', 'comptine', 'bébé', 'baby', 'kids', 'children',
    'playlist', 'compilation', 'various', 'collectif'
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

def get_first_album_year_deezer(artist_id):
    """
    Récupère l'année du premier album de l'artiste sur Deezer
    Retourne None si pas d'album trouvé
    """
    try:
        url = f"https://api.deezer.com/artist/{artist_id}/albums"
        params = {'limit': 50}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        if not data or 'data' not in data or len(data['data']) == 0:
            return None
        
        years = []
        for album in data['data']:
            release_date = album.get('release_date', '')
            if release_date:
                # Extraire l'année (format: YYYY-MM-DD)
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

def get_artist_albums_count_deezer(artist_id):
    """
    Compte le nombre d'albums de l'artiste sur Deezer
    Retourne 0 si erreur
    """
    try:
        url = f"https://api.deezer.com/artist/{artist_id}/albums"
        params = {'limit': 50}
        
        response = requests.get(url, params=params, timeout=10)
        if response.status_code != 200:
            return 0
        
        data = response.json()
        
        if not data or 'data' not in data:
            return 0
        
        return len(data['data'])
        
    except Exception as e:
        return 0

def est_artiste_connu(artist_name, fans, artist_id=None):
    """
    Détecte si un artiste est connu/établi - CRITÈRES SIMPLIFIÉS (Phase 1)
    Retourne True si l'artiste est connu (donc à exclure)
    Note: Critère ancienneté désactivé pour Phase 1 (trop lent)
    """
    
    # Normaliser le nom pour vérification
    name_lower = artist_name.lower().strip()
    
    # CRITERE 1 : BLACKLIST (priorité absolue - RAPIDE)
    for known in ARTISTES_CONNUS_BLACKLIST:
        if known in name_lower:
            return True  # Dans la blacklist = EXCLU
    
    # CRITERE 2 : Trop de fans (RAPIDE)
    if fans > 100000:
        return True
    
    # CRITERE 3 : Ancienneté - DÉSACTIVÉ pour Phase 1
    # (Trop lent, on le remettra en Phase 2 après construction blacklist)
    # if not artist_id:
    #     return False
    # first_year = get_first_album_year_deezer(artist_id)
    # if first_year and first_year < 2015:
    #     return True
    
    return False  # Passe tous les tests = Émergent !

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

def get_artist_first_release_year(artist_id):
    try:
        url = f"{BASE_URL}/artist/{artist_id}/albums"
        params = {'limit': 100}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            albums = response.json().get('data', [])
            if not albums:
                return None
            years = []
            for album in albums:
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

def get_artist_info(artist_id):
    try:
        url = f"{BASE_URL}/artist/{artist_id}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filtrage 1 : Nom (orchestres, DJs, etc.)
            if est_nom_exclu(data['name']):
                return None
            
            # Filtrage 2 : DETECTION ARTISTE CONNU (Date premier album + fans)
            fans = data.get('nb_fan', 0)
            
            if est_artiste_connu(data['name'], fans, artist_id=data['id']):
                return None  # Artiste connu détecté = EXCLU !
            
            return {
                'id': data['id'],
                'nom': data['name'],
                'fans': fans,
                'url_deezer': data['link'],
                'image_url': data.get('picture_medium', '')
            }
    except Exception as e:
        return None
    return None

def is_eligible(fans):
    return MIN_FANS <= fans <= MAX_FANS

def search_artist_by_name(artist_name):
    try:
        url = f"{BASE_URL}/search/artist"
        params = {'q': artist_name, 'limit': 1}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            results = response.json().get('data', [])
            if results:
                return results[0]['id']
    except Exception as e:
        pass
    return None

def get_related_artists(artist_id, genre, max_results=20):
    related = []
    seen_ids = set()
    
    try:
        url = f"{BASE_URL}/artist/{artist_id}/related"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json().get('data', [])
            
            for artist_data in data[:max_results]:
                artist_id = artist_data['id']
                
                if artist_id not in seen_ids:
                    seen_ids.add(artist_id)
                    info = get_artist_info(artist_id)
                    
                    if info and is_eligible(info['fans']):
                        info['genre'] = genre
                        info['source'] = 'Deezer'
                        related.append(info)
        
        time.sleep(0.3)
    except Exception as e:
        pass
    
    return related

def get_artists_from_playlist(playlist_id, genre):
    artists = []
    seen_ids = set()
    
    try:
        print(f"  Playlist {playlist_id}...", end=' ')
        
        url = f"{BASE_URL}/playlist/{playlist_id}/tracks"
        params = {'limit': 2000}
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            tracks = response.json().get('data', [])
            
            count_found = 0
            for track in tracks:
                if 'artist' in track:
                    artist_id = track['artist']['id']
                    
                    if artist_id not in seen_ids:
                        seen_ids.add(artist_id)
                        info = get_artist_info(artist_id)
                        
                        if info and is_eligible(info['fans']):
                            info['genre'] = genre
                            info['source'] = 'Deezer'
                            artists.append(info)
                            count_found += 1
            
            print(f"OK {count_found} artistes")
        else:
            print(f"Erreur {response.status_code}")
        
        time.sleep(0.5)
    except Exception as e:
        print(f"Erreur {str(e)[:50]}")
    
    return artists

def calculate_score(row):
    fans_score = min(50, (row['fans'] / MAX_FANS) * 50)
    
    if row['fans'] < 5000:
        engagement_score = 30
    elif row['fans'] < 10000:
        engagement_score = 25
    else:
        engagement_score = 20
    
    current_year = datetime.now().year
    if 'premier_album' in row and pd.notna(row['premier_album']):
        years_since_debut = current_year - row['premier_album']
        if years_since_debut <= 1:
            recency_score = 15
        elif years_since_debut <= 3:
            recency_score = 12
        else:
            recency_score = 10
    else:
        recency_score = 10
    
    genre_bonus = 5
    total_score = fans_score + engagement_score + recency_score + genre_bonus
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
    print("MUSICTALENTRADAR v2 - SCRAPER DEEZER (Phase 1 - Scraping Large)")
    print("="*70)
    print(f"\nCriteres:")
    print(f"  - Fans: {MIN_FANS:,} - {MAX_FANS:,}")
    print(f"\nDetection artistes connus (2 criteres SEULEMENT):")
    print(f"  1. Blacklist (~220 artistes connus)")
    print(f"  2. Fans > 100k")
    print(f"\nNote: Critère 'premier album < 2015' DÉSACTIVÉ pour Phase 1")
    print(f"      (Trop lent - sera appliqué en Phase 2)")
    print(f"\nExclusions supplementaires:")
    print(f"  - Orchestres, DJs, Enfants, Compilations")
    
    print(f"\nGenres: {', '.join(PLAYLISTS_BY_GENRE.keys())}\n")
    print("Note: Criteres composites (pas de Wikipedia)\n")
    
    all_artists = []
    
    print("="*70)
    print("PHASE 1 : Playlists Officielles Deezer")
    print("="*70)
    
    for genre, playlists in PLAYLISTS_BY_GENRE.items():
        print(f"\n{genre} ({len(playlists)} playlists)")
        
        for playlist_id in playlists:
            artists = get_artists_from_playlist(playlist_id, genre)
            all_artists.extend(artists)
        
        genre_count = len([a for a in all_artists if a['genre'] == genre])
        print(f"  >> Total: {genre_count} artistes")
    
    print(f"\nApres playlists: {len(all_artists)} artistes")
    
    print(f"\n{'='*70}")
    print("PHASE 2 : Artistes Similaires (Related Artists)")
    print("="*70)
    
    for genre, seed_artists in SEED_ARTISTS.items():
        print(f"\n{genre} ({len(seed_artists)} seeds)")
        genre_count = 0
        
        for seed_name in seed_artists:
            seed_id = search_artist_by_name(seed_name)
            
            if seed_id:
                related = get_related_artists(seed_id, genre)
                all_artists.extend(related)
                genre_count += len(related)
                print(f"  - {seed_name}: {len(related)} similaires")
            else:
                print(f"  - {seed_name}: non trouve")
        
        print(f"  >> Total: {genre_count} artistes")
    
    print(f"\nApres recherche similaires: {len(all_artists)} artistes")
    
    df = pd.DataFrame(all_artists)
    
    if len(df) == 0:
        print("\nAUCUN ARTISTE TROUVE")
        print(f"Essayez de baisser ANNEE_MIN_PREMIER_ALBUM a {ANNEE_MIN_PREMIER_ALBUM - 2}") # type: ignore
        return
    
    initial_count = len(df)
    df = df.drop_duplicates(subset=['id'])
    print(f"\nDedoublonnage: {initial_count} -> {len(df)} artistes uniques")
    
    df['score'] = df.apply(calculate_score, axis=1)
    df['categorie'] = df['score'].apply(categorize_artist)
    df['date_collecte'] = datetime.now().strftime('%Y-%m-%d')
    df = df.sort_values('score', ascending=False)
    
    filename = f"data/deezer_artists_{datetime.now().strftime('%Y%m%d')}.csv"
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    
    print(f"\n{'='*70}")
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
            if pd.notna(year): # type: ignore
                pct = (count / len(df)) * 100
                print(f"  - {int(year)}: {count} artistes ({pct:.1f}%)") # type: ignore
    
    print(f"\nTop 5:")
    for _, row in df.head(5).iterrows():
        year_str = f" (depuis {int(row['premier_album'])})" if pd.notna(row.get('premier_album')) else ""
        print(f"  - {row['nom']} ({row['genre']}){year_str} - Score: {row['score']:.1f} - {row['fans']:,} fans")
    
    print(f"\n{'='*70}")
    print("TERMINE")
    print("="*70)

if __name__ == "__main__":
    main()