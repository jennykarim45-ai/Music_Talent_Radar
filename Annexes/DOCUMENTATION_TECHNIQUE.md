# DOCUMENTATION TECHNIQUE - MUSIC TALENT RADAR 
---

##  TABLE DES MATIÈRES

1. [Introduction & Contexte](#1-introduction--contexte)
2. [Architecture du Projet](#2-architecture-du-projet)
3. [Collecte des Données](#3-collecte-des-données)
4. [Base de Données](#4-base-de-données)
5. [Algorithme de Scoring](#5-algorithme-de-scoring)
6. [Machine Learning](#6-machine-learning)
7. [Interface Streamlit](#7-interface-streamlit)
8. [Système d'Alertes](#8-système-dalertes)
9. [Automatisation GitHub Actions](#9-automatisation-github-actions)


---

## 1. INTRODUCTION & CONTEXTE

###  Objectif du Projet

En tant que passionnée de musique et en formation pour devenir Data analyst, j'ai voulu créer un outil qui combine mes deux passions : **détecter les talents musicaux émergents grâce à l'analyse de données**.

L'idée est simple : identifier les artistes qui ont un fort potentiel avant qu'ils ne deviennent célèbres, en analysant leurs statistiques sur Spotify et Deezer.

###  Le Concept JEK2 Records

J'ai imaginé un **label de musique fictif** qui utilise la data pour repérer les futures stars. Le nom "JEK2" vient des initiales de ma famille. **Music Talent Radar** est le nom de l'application utilisée dans la découverte de nouveaux talents. 
J'ai également profité de ce projet pour vous faire découvrir mon univers à travers mes propres œuvres musicales. 

### Compétences Mobilisées

Ce projet m'a permis de mettre en pratique tout ce que j'ai appris en formation et dans mes recherches personnelles :
- **Python** : scripting, automatisation, gestion d'erreurs avancée
- **APIs REST** : Spotify & Deezer (authentification OAuth, rate limiting)
- **SQL** : gestion de base de données, requêtes complexes
- **Machine Learning** : Random Forest, feature engineering, GridSearchCV
- **Streamlit** : visualisation interactive, optimisation des performances
- **Git/GitHub** : versioning, résolution de conflits, GitHub Actions

---

## 2. ARCHITECTURE DU PROJET

###  Structure des Fichiers

Voici comment j'ai organisé mon projet (et pourquoi) :
```
MusicTalentRadarAll/
│
├── app/                          # Interface utilisateur
│   ├── assets/                   # Images, logo, musique
│   ├── auth.py                   # Système de connexion
│   └── streamlit.py              # Application principale (2400+ lignes!)
│
├── data/                         # Données collectées
│   ├── *.csv                     # Fichiers CSV (Spotify/Deezer)
│   ├── music_talent_radar_v2.db  # Base SQLite
│   └── predictions_ml.csv        # Prédictions ML
│
├── utils/                        # Scripts utilitaires
│   ├── diagnostic_base.py        # Vérifier la BDD
│   ├── nettoyer_base.py          # Nettoyage
│   ├── clean_doublon.py          # suppression doublon date (si plusieurs collectes par jour)
│   └── update_table_alertes.py   # Mise à jour alertes
│
├── .github/workflows/            # Automatisation
│   └── main.yml                  # GitHub Actions
│
├── collecte1.py                  # Collecte données APIs
├── music_talent_radar.py         # Import + Scoring
├── ml_prediction.py              # Prédictions ML (Random Forest)
├── generer_alertes.py            # Génération alertes
├── database_manager_v2.py        # Gestion BDD
├── import_data.py                # Import CSV → SQLite
│
├── artist_urls.csv               # Liste URLs artistes
├── requirements.txt              # Dépendances Python
├── .env                          # Secrets API 
├── .gitattributes                # Stratégie merge pour fichiers data
└── README.md                     # Énoncé des attentes du projet
```

###  Workflow Global
```
                  ┌─────────────────┐
                  │  COLLECTE1.PY   │      ← Récupère artistes Spotify/Deezer
                  └────────┬────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ ARTIST_URLS.CSV │      ← Liste centralisée des artistes
                  └────────┬────────┘
                           │
                           ↓
                  ┌─────────────────────┐
                  │MUSIC_TALENT_RADAR.PY│  ← Calcul des scores + Import BDD
                  └────────┬────────────┘
                           │
                           ↓
                  ┌─────────────────┐
                  │ML_PREDICTION.PY │      ← Modèle Random Forest (92.4%)
                  └────────┬────────┘
                           │
                           ↓
                  ┌──────────────────┐
                  │GENERER_ALERTES.PY│     ← Détection des tendances
                  └────────┬─────────┘
                           │
                           ↓
                  ┌───────────────┐
                  │ STREAMLIT.PY  │        ← Interface graphique
                  └───────────────┘
```
---

## 3. COLLECTE DES DONNÉES

###  Sources de Données

J'ai choisi **Spotify** et **Deezer** car :
1. Ce sont les plateformes les plus utilisées en France
2. Leurs APIs sont accessibles gratuitement
3. Elles offrent des données complémentaires

###  Résultats de Collecte : Spotify vs Deezer

**Statistiques actuelles :**
- **Spotify** : 300+ artistes émergents
- **Deezer** : 44 artistes émergents
- **Ratio** : 7:1 (Spotify/Deezer)

#### Pourquoi cette disparité ?

**1. Différences Méthodologiques**

**Spotify :**
-  Recherche par **50 mots-clés ciblés** (ex: "rap français émergent")
-  Endpoint `/search` très permissif
-  Large catalogue d'artistes indépendants

**Deezer :**
-  **Pas d'endpoint de recherche par mots-clés** pour artistes
-  Collecte limitée à **l'exploration de playlists** (13 playlists + recherche manuelle)
-  Moins d'artistes ultra-émergents dans les playlists officielles

**2. Limitations Techniques de l'API Deezer**

| Aspect                  | Spotify API        | Deezer API            |
|-------------------------|--------------------|-----------------------|
| **Recherche artistes**  | Par mots-clés      | Non disponible        |
| **Rate limits**         | Modérés (~100/30s) | Très stricts (~50/5s) |
| **Documentation**       | Complète           | Basique               |

**Conclusion :** Cette disparité **n'est pas un défaut mais reflète les contraintes techniques**. Deezer sert de **validation qualité** pour les artistes présents sur les deux plateformes (+10 points de score "Influence").

###  Fichier `collecte1.py`

C'est le **cœur de la collecte**. Voici comment il fonctionne :

#### **Étape 1 : Authentification Spotify (OAuth 2.0)**
```python
def get_spotify_token():
    """Authentification Spotify avec retry sur erreur 503"""
    client_id = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
    
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            auth_response = requests.post(
                'https://accounts.spotify.com/api/token',
                {
                    'grant_type': 'client_credentials',
                    'client_id': client_id,
                    'client_secret': client_secret,
                },
                timeout=10
            )
            
            if auth_response.status_code == 200:
                return auth_response.json()['access_token']
            
            elif auth_response.status_code == 503:
                wait_time = 10 + (retry_count * 5)
                print(f" Spotify indisponible (503). Attente {wait_time}s...")
                time.sleep(wait_time)
                retry_count += 1
                continue
            
            elif auth_response.status_code == 429:
                retry_after = int(auth_response.headers.get('Retry-After', 10))
                time.sleep(retry_after)
                retry_count += 1
                continue
                
        except requests.exceptions.Timeout:
            retry_count += 1
            time.sleep(5)
            continue
    
    raise Exception(f" Échec authentification après {max_retries} tentatives")
```

**Pourquoi cette complexité ?**  
Spotify utilise OAuth 2.0 et peut renvoyer des erreurs 503 (serveur indisponible) ou 429 (rate limit). J'ai implémenté un système de **retry avec backoff exponentiel** pour gérer ces cas.

#### **Étape 2 : Recherche d'Artistes**

J'utilise **50 mots-clés** répartis sur **7 genres** :
```python
SEARCH_KEYWORDS_SPOTIFY = {
    'Rap-HipHop-RnB': [
        'rap français émergent', 'hip hop underground france',
        'rnb français nouvelle génération', 'trap français',
        # ... 22 mots-clés au total
    ],
    'Pop': ['pop française indépendante', ...],  # 11 mots-clés
    'Afrobeat-Amapiano': ['afrobeat français', ...],  # 7 mots-clés
    # ... etc (7 genres)
}
```

**Pourquoi 50 mots-clés ?**  
Au début, j'en avais seulement 10 et je trouvais toujours les mêmes artistes. En multipliant les mots-clés, j'ai diversifié les résultats et couvert plus de niches musicales.

#### **Étape 3 : Filtres Stricts**

**Le défi :** éviter les artistes déjà connus ET les faux positifs (DJs, producteurs) !
```python
# Filtres quantitatifs
SPOTIFY_MIN_FOLLOWERS = 100      # Abaissé de 200 à 100
SPOTIFY_MAX_FOLLOWERS = 40000
SPOTIFY_MAX_POPULARITY = 60
ANNEE_MIN_PREMIER_ALBUM = 2018

# Filtres qualitatifs (BLACKLIST)
BLACKLIST_ARTISTS = [
    "ryan gosling", "Jean-Luc Lahaye", "Justin Hurwitz",
    "PLK", "Gorillaz", # ... 50+ artistes
]

def est_en_blacklist(nom):
    """Vérifier si un artiste est dans la blacklist (normalisation avancée)"""
    nom_normalise = normaliser_nom(nom)  # Enlève accents, ponctuation, espaces
    
    for blacklisted in BLACKLIST_ARTISTS:
        if normaliser_nom(blacklisted) == nom_normalise:
            return True
    
    return False
```

**Pourquoi MIN_FOLLOWERS = 100 ?**  
Pour capturer plus d'artistes **vraiment émergents** qui commencent tout juste leur carrière. Les filtres qualitatifs (blacklist, exclusion DJs/producteurs) compensent le risque de faux positifs.

#### **Étape 4 : Gestion Avancée des Rate Limits**

**Le problème :** Spotify limite à ~100 requêtes / 30 secondes. Au-delà → erreur 429.

**Ma solution :**
```python
# Retry logic avec backoff exponentiel
max_retries = 5
retry_count = 0

while retry_count < max_retries and not success:
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 429:
        retry_after = int(response.headers.get('Retry-After', 10))
        wait_time = max(retry_after, 10 + (retry_count * 5))
        
        print(f"⏳ Rate limit! Attente {wait_time}s... (tentative {retry_count + 1}/{max_retries})")
        time.sleep(wait_time)
        retry_count += 1
        continue
    
    elif response.status_code == 200:
        # Succès
        success = True
        success_count += 1
        break
    
    else:
        # Autre erreur
        error_count += 1
        break

# Délai adaptatif entre artistes
if rate_limit_count > 5:
    time.sleep(1.0)  # Ralentir si beaucoup de rate limits
else:
    time.sleep(0.5)  # Délai normal
```

**Résultats mesurés :**
- **Avant** (sans retry) : 57% de succès
- **Après** (avec retry) : **80-90% de succès** 

#### **Étape 5 : Exclusions Intelligentes**
```python
# Patterns à exclure (regex)
DJ_PATTERNS = [
    r'\bdj\b', r'^dj\s', r'\sdj$', r'\sdj\s',
    r'DJ\s', r'\sDJ\b'
]

MOTS_EXCLUS_NOM = [
    # DJs et producteurs
    'dj', 'deejay', 'prod', 'producer', 'beat maker',
    
    # Orchestres
    'orchestre', 'symphony', 'philharmonique',
    
    # Enfants et comptines
    'titounis', 'enfant', 'comptine', 'kids',
    
    # Compilations
    'various artists', 'compilation', 'best of',
    
    # ... 50+ exclusions
]

def nom_contient_exclusions(nom):
    """Vérifier si le nom contient des mots exclus"""
    nom_lower = nom.lower()
    return any(exclus in nom_lower for exclus in MOTS_EXCLUS_NOM)
```

**Pourquoi ?**  
J'ai remarqué que je récupérais beaucoup de DJs et de producteurs, alors que je voulais des **chanteurs/rappeurs**. Ces exclusions ont amélioré la qualité des résultats de **40%**.

###  Matching Spotify ↔ Deezer

Les artistes ont souvent des noms légèrement différents sur les deux plateformes :
- Spotify : "Limsa d'Aulnay"
- Deezer : "Limsa d'Aulnay-sous-Bois"

**Ma solution : Normalisation + Distance de Levenshtein**
```python
def normaliser_nom_artiste(nom):
    """Normaliser pour améliorer le matching"""
    # Minuscules
    nom = nom.lower().strip()
    
    # Enlever accents : "Roméo" → "romeo"
    nom = unicodedata.normalize('NFKD', nom)
    nom = nom.encode('ASCII', 'ignore').decode('ASCII')
    
    # Enlever ponctuation : "L'Impératrice" → "limperatrice"
    nom = re.sub(r'[^\w\s]', '', nom)
    nom = re.sub(r'\s+', '', nom)
    
    return nom

def similarity_ratio(s1, s2):
    """Calcul de similarité (Levenshtein)"""
    # ... algorithme de distance
    similarity = ((max_len - distance) / max_len) * 100
    return round(similarity, 1)

def trouver_meilleur_match(nom_deezer, artistes_spotify_dict, seuil=85):
    """Trouver le meilleur match Spotify pour un artiste Deezer"""
    nom_deezer_normalise = normaliser_nom_artiste(nom_deezer)
    
    # Match exact d'abord
    if nom_deezer_normalise in artistes_spotify_dict:
        return artistes_spotify_dict[nom_deezer_normalise]
    
    # Sinon match approximatif (>= 85% de similarité)
    for nom_spotify_normalise, nom_spotify_original in artistes_spotify_dict.items():
        score = similarity_ratio(nom_deezer_normalise, nom_spotify_normalise)
        if score >= seuil:
            return nom_spotify_original
    
    return None
```

**Résultat :**  
- Avant normalisation : 10% de matching  
- Après normalisation + Levenshtein : **75% de matching** ! 

### Output : `artist_urls.csv`

Format du fichier final :
```csv
nom,url_spotify,url_deezer,categorie
SCH,https://open.spotify.com/artist/...,https://www.deezer.com/artist/...,Rap-HipHop-RnB
Angèle,https://open.spotify.com/artist/...,,Pop
Tayc,,https://www.deezer.com/artist/...,Afrobeat-Amapiano
```

**Colonnes :**
- `nom` : Nom de l'artiste
- `url_spotify` : URL Spotify (vide si absent)
- `url_deezer` : URL Deezer (vide si absent)
- `categorie` : Genre musical attribué

---

## 4. BASE DE DONNÉES

###  Pourquoi SQLite ?

Au début, je stockais tout en CSV. Problème : **lenteur** et **données dupliquées**.

J'ai choisi SQLite car :
-  Pas de serveur à installer
-  Fichier unique (`.db`)
-  Requêtes SQL rapides
-  Facile à migrer vers PostgreSQL plus tard
-  Gestion de l'historique (contrairement aux CSV)

###  Schéma de la Base
```sql
-- Table des artistes
CREATE TABLE artistes (
    id INTEGER PRIMARY KEY,
    id_unique TEXT UNIQUE,           -- {nom}_spotify ou {nom}_deezer
    nom TEXT,
    source TEXT,                      -- 'Spotify' ou 'Deezer'
    genre TEXT,                       -- Catégorie principale
    image_url TEXT,
    url_spotify TEXT,
    url_deezer TEXT,
    date_ajout TEXT,
    date_maj TEXT                     -- Dernière mise à jour
);

-- Table des métriques (historique)
CREATE TABLE metriques_historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_unique TEXT,                   -- Lien avec artistes
    nom_artiste TEXT,
    plateforme TEXT,                  -- 'Spotify' ou 'Deezer'
    fans_followers INTEGER,           -- Unification Spotify/Deezer
    followers INTEGER,                -- Spotify uniquement
    fans INTEGER,                     -- Deezer uniquement
    popularity INTEGER,               -- 0-100 sur Spotify
    score_potentiel REAL,             -- Score calculé
    nb_albums INTEGER,
    nb_releases_recentes INTEGER,     -- Sorties 2 dernières années
    date_collecte TEXT,               -- Date de la collecte
    url TEXT,
    image_url TEXT,
    FOREIGN KEY (id_unique) REFERENCES artistes(id_unique)
);

-- Table des alertes
CREATE TABLE alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_artiste TEXT,
    type_alerte TEXT,                 -- 'Croissance', 'Baisse', 'TRENDING'
    message TEXT,
    date_alerte TEXT,
    vu BOOLEAN DEFAULT 0              -- Lu/non lu
);
```

###  Choix de Conception

**`id_unique` au lieu d'un ID auto-incrémenté :**

Pour éviter les doublons entre Spotify et Deezer.

Exemple :
- Artiste sur Spotify : `id_unique = "sch_spotify"`
- Même artiste sur Deezer : `id_unique = "sch_deezer"`

Ainsi, je peux suivre le même artiste sur 2 plateformes.

**`fans_followers` : colonne unifiée**

Spotify utilise `followers`, Deezer utilise `fans`. J'ai créé une colonne unique pour simplifier les requêtes :
```python
row['fans_followers'] = row.get('followers') or row.get('fans', 0)
```

###  Gestion de l'Historique

**Contrairement aux CSV qui écrasent les données, SQLite garde TOUT l'historique.**

Chaque jour, GitHub Actions insère une nouvelle ligne dans `metriques_historique` :
```python
cursor.execute("""
    INSERT INTO metriques_historique 
    (id_unique, nom_artiste, fans_followers, score_potentiel, date_collecte,
     nb_albums, nb_releases_recentes)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", (id_unique, nom, followers, score, datetime.now(), nb_albums, nb_releases))
```

**Avantage :** Je peux tracer l'évolution d'un artiste dans le temps et détecter les croissances/baisses ! 📈

---

## 5. ALGORITHME DE SCORING

###   Score Multi-Critères

J'ai créé un score sur **100 points** basé sur **4 critères** :
```
┌─────────────────────────────────────┐
│  SCORE TOTAL (0-100)                │
├─────────────────────────────────────┤
│  1. Audience          40%           │
│  2. Engagement        30%           │
│  3. Récurrence        20%           │
│  4. Influence         10%           │
└─────────────────────────────────────┘
```

###  Détail des Critères

#### **1. Audience (40%) - Taille de la communauté**
```python
def calculer_audience(fans_followers):
    """
    Normalise le nombre de fans entre 100 et 40,000
    100 fans = 0%
    40,000 fans = 40%
    """
    fans_norm = min(max(fans_followers, 100), 40000)
    audience_score = ((fans_norm - 100) / (40000 - 100)) * 40
    return audience_score
```

**Pourquoi 100-40k ?**
- < 100 : trop petit pour être viable (seuil abaissé de 200 à 100)
- \> 40k : déjà trop connu

**Exemple :**
- 100 fans → 0 points
- 20,000 fans → 19.9 points
- 40,000 fans → 40 points

#### **2. Engagement (30%) - Qualité de la relation avec les fans**

**Sur Spotify :**
```python
# Utilise la "popularity" comme proxy (0-100)
if popularity:
    pop_norm = min(max(popularity, 20), 65)
    engagement_score = ((pop_norm - 20) / (65 - 20)) * 30
```

**Sur Deezer :**
```python
# Calcule le ratio fans/albums
if nb_albums > 0 and fans_followers:
    ratio = fans_followers / nb_albums
    # Normaliser : 100 fans/album = 0%, 10000 fans/album = 30%
    ratio_norm = min(max(ratio, 100), 10000)
    engagement_score = ((ratio_norm - 100) / (10000 - 100)) * 30
```

**Pourquoi cette différence ?**  
Spotify fournit déjà une métrique `popularity`. Deezer non, donc j'ai créé ma propre formule basée sur le ratio fans/albums.

#### **3. Récurrence (20%) - Régularité des sorties**
```python
def calculer_recurrence(nb_releases_recentes):
    """
    Nombre de sorties dans les 2 dernières années
    0 sorties = 0%
    10+ sorties = 20%
    """
    recurrence_score = min(nb_releases_recentes / 10, 1) * 20
    return recurrence_score
```

**Pourquoi ?**  
Un artiste qui sort régulièrement de la musique montre sa **motivation** et son **professionnalisme**.

**Comment je récupère cette info ?**
```python
# Dans collecte1.py
albums_response = requests.get(
    f'https://api.spotify.com/v1/artists/{artist_id}/albums',
    headers=headers,
    params={'limit': 50, 'include_groups': 'album,single'}
)

# Compter releases des 2 dernières années
date_limite = datetime.now() - timedelta(days=730)
nb_releases_recentes = 0

for album in albums_data['items']:
    release_date = datetime.strptime(album['release_date'], '%Y-%m-%d')
    if release_date >= date_limite:
        nb_releases_recentes += 1
```

#### **4. Influence (10%) - Présence multi-plateforme**
```python
def calculer_influence(est_sur_spotify_et_deezer):
    """
    Artiste présent sur les 2 plateformes = 10 points
    Artiste sur 1 seule plateforme = 0 points
    """
    return 10 if est_sur_spotify_et_deezer else 0
```

**Pourquoi ?**  
Un artiste qui a réussi à se faire référencer sur **plusieurs plateformes** montre un début de notoriété et de sérieux dans sa carrière.

###  Calcul Final
```python
def calculer_score_potentiel(fans_followers, popularity, nb_releases, multi_plateforme):
    # 1. Audience (40%)
    audience = calculer_audience(fans_followers)
    
    # 2. Engagement (30%)
    engagement = calculer_engagement(popularity)
    
    # 3. Récurrence (20%)
    recurrence = calculer_recurrence(nb_releases)
    
    # 4. Influence (10%)
    influence = 10 if multi_plateforme else 0
    
    # Score total
    score_total = audience + engagement + recurrence + influence
    
    return round(score_total, 1)
```

### Exemples Réels

**Artiste A :**
- 5,000 fans
- Popularity 45
- 3 sorties récentes
- Sur Spotify uniquement
```
Audience:    (5000-100)/(40000-100) * 40 = 4.9
Engagement:  (45-20)/(65-20) * 30 = 16.7
Récurrence:  3/10 * 20 = 6.0
Influence:   0
────────────────────────────────────────
SCORE TOTAL: 27.6 / 100
```

**Artiste B :**
- 25,000 fans
- Popularity 55
- 8 sorties récentes
- Sur Spotify ET Deezer
```
Audience:    (25000-100)/(40000-100) * 40 = 24.9
Engagement:  (55-20)/(65-20) * 30 = 23.3
Récurrence:  8/10 * 20 = 16.0
Influence:   10
────────────────────────────────────────
SCORE TOTAL: 74.2 / 100 
```

---

## 6. MACHINE LEARNING

###  Objectif du Modèle

**Question :** Comment prédire quels artistes vont "exploser" dans les 3 prochains mois ?

**Ma démarche :**
1. Calculer la croissance **réelle** des artistes (pas juste le score)
2. Créer un label "a explosé" / "pas explosé" (>50% croissance en 90j)
3. Entraîner un Random Forest optimisé avec GridSearchCV
4. Prédire sur les nouveaux artistes

### Préparation des Données

**Fichier : `ml_prediction.py` (v3.0 - Rewrite complet)**

#### **Étape 1 : Calculer la Croissance réelle**


**Approche :**
```python
def calculer_croissance_et_features():
    """Calcule la VRAIE croissance entre première et dernière collecte"""
    
    # Historique trié par date
    historique = metriques_df.sort_values('date_collecte')
    
    # Premier et dernier point
    premiere_collecte = historique.iloc[0]
    derniere_collecte = historique.iloc[-1]
    
    followers_avant = premiere_collecte['fans_followers']
    followers_apres = derniere_collecte['fans_followers']
    jours = (derniere_collecte['date_collecte'] - premiere_collecte['date_collecte']).days
    
    # Croissance en %
    if followers_avant > 0 and jours > 0:
        croissance_pct = ((followers_apres - followers_avant) / followers_avant) * 100
        
        # Normaliser sur 90 jours
        croissance_90j = (croissance_pct / jours) * 90
        
        # Label : a explosé si >50% de croissance sur 90j
        a_explose = 1 if croissance_90j > 50 else 0
    else:
        a_explose = 0
    
    return a_explose, croissance_90j
```

**Résultat :** Sur 326 artistes avec historique :
- **17 stars** (>50% croissance)
- **309 non-stars**

#### **Étape 2 : Feature Engineering (13 Features)**

Au lieu de 4 features simples, j'en ai créé **13 dérivées** :
```python
features = {
    # RAW (5)
    'followers': followers_total,
    'popularity': popularity,
    'nb_albums': nb_albums,
    'nb_releases_recentes': nb_releases_recentes,
    'jours_observation': jours,
    
    # RATIOS (2)
    'ratio_followers_albums': followers / max(nb_albums, 1),
    'ratio_releases_albums': nb_releases_recentes / max(nb_albums, 1),
    
    # DYNAMIQUE (2)
    'velocite': croissance_pct / max(jours, 1),  # Vitesse de croissance
    'momentum': croissance_2 - croissance_1,      # Accélération
    
    # ENGAGEMENT (3)
    'engagement': followers / max(nb_albums, 1),
    'activite_recente': nb_releases_recentes,
    'taille_categorie': followers / genre_median,
    
    # MATURITÉ (1)
    'maturite': nb_albums / max(jours/365, 1)     # Albums par an
}
```

**Pourquoi ces features ?**
- **Vélocité** : Mesure la vitesse de croissance quotidienne
- **Momentum** : Détecte l'accélération (artiste qui "décolle")
- **Ratios** : Relativisent les chiffres bruts (10k fans avec 1 album > 10k fans avec 50 albums)

#### **Étape 3 : Équilibrage des Classes**

**Problème : Déséquilibre 17 stars / 309 non-stars (1:18 !)**

**Solution : SMOTE (Synthetic Minority Over-sampling)**
```python
from imblearn.over_sampling import SMOTE

# Sur-échantillonner la classe minoritaire
smote = SMOTE(sampling_strategy=0.33, random_state=42)  # 1:3 au lieu de 1:18
X_resampled, y_resampled = smote.fit_resample(X, y)
```

**Résultat :** 17 stars → 51 stars (synthétiques) pour un meilleur entraînement

###  Entraînement du Modèle

#### **Random Forest avec GridSearchCV**
```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import StandardScaler

# Normalisation
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_resampled)

# Grille de paramètres à tester
param_grid = {
    'n_estimators': [100, 200, 300],
    'max_depth': [8, 10, 12, 15],
    'min_samples_split': [5, 10, 15],
    'min_samples_leaf': [2, 5, 8],
    'max_features': ['sqrt', 'log2']
}

# GridSearch avec validation croisée 5-fold
rf = RandomForestClassifier(random_state=42, class_weight='balanced')
grid_search = GridSearchCV(
    rf, 
    param_grid, 
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)

grid_search.fit(X_scaled, y_resampled)

# Meilleurs paramètres trouvés
print(f"Meilleurs paramètres : {grid_search.best_params_}")
print(f"Accuracy CV : {grid_search.best_score_:.3f}")
```

**Résultat obtenu :**
```
Meilleurs paramètres:
  max_depth: 8
  min_samples_split: 5
  n_estimators: 100

Accuracy CV: 92.4% (+/- 6.9%)
Accuracy Test: 100.0%
```

**J'avais essayé avec Logistic Regression au départ**
**Avec ce modèle +17 points vs Logistic Regression (75% → 92.4%) !**

#### **Feature Importance**
```python
# Quelles features comptent le plus ?
importances = grid_search.best_estimator_.feature_importances_
feature_ranking = sorted(
    zip(feature_names, importances), 
    key=lambda x: x[1], 
    reverse=True
)

print("\nTop 3 features:")
for name, importance in feature_ranking[:3]:
    print(f"  {name}: {importance*100:.1f}%")
```

**Résultat :**
1. **Vélocité (37.6%)** → Vitesse de croissance = indicateur #1
2. **Ratio releases/albums (20.5%)** → Productivité compte beaucoup
3. **Activité récente (18.4%)** → Sorties récentes = signe de motivation

###  Prédictions
```python
# Calibrer les probabilités
from sklearn.calibration import CalibratedClassifierCV

calibrated_model = CalibratedClassifierCV(
    grid_search.best_estimator_, 
    method='sigmoid', 
    cv=5
)
calibrated_model.fit(X_scaled, y_resampled)

# Prédire sur tous les artistes
X_all_scaled = scaler.transform(X_all)
probas = calibrated_model.predict_proba(X_all_scaled)[:, 1]

df['proba_explosion'] = probas * 100  # En %

# Sauvegarder
predictions = df[['nom', 'plateforme', 'proba_explosion', 'followers']].copy()
predictions = predictions.sort_values('proba_explosion', ascending=False)
predictions.to_csv('data/predictions_ml.csv', index=False)
```

**Distribution des probabilités :**
```
Min:  4.6%
Moy: 18.4%
Max: 90.9%
```

** Beaucoup plus réaliste que l'ancienne version (qui mettait tout le monde à 100%) !**

###  Pourquoi Random Forest plutôt que Logistic Regression ?

| Critère                 | Logistic Regression | Random Forest                     |
|-------------------------|---------------------|-----------------------------------|
| **Précision**           | 75-80%              | **92.4%**                         |
| **Gère non-linéarités** | Non                 |  Oui                              |
| **Feature importance**  | Coefficients        |  Importances claires              |
| **Overfitting**         | Peu risqué          |  Risqué (maîtrisé par GridSearch) |
| **Vitesse**             | Rapide              |  Moyen                            |
| **Interprétabilité**    | Haute               |  Moyenne                          |

**Mon choix :** Random Forest car **+17% de précision** vaut le léger compromis sur vitesse/interprétabilité.

###  Erreurs Corrigées

**Erreur 1 : Data Leakage**
- Avant : J'utilisais `score_potentiel` comme feature (calculé à partir des données!)
- Après : Calcul croissance réelle indépendante

**Erreur 2 : Label arbitraire**
- Avant : Top 10% des scores = "star"
- Après : >50% croissance sur 90j = définition objective

**Erreur 3 : Pas d'optimisation**
- Avant : Paramètres par défaut
- Après : GridSearchCV pour trouver les meilleurs paramètres

**Erreur 4 : Probabilités non calibrées**
- Avant : Probabilités de 100% partout (bug)
- Après : CalibratedClassifierCV pour des probas réalistes (4.6% - 90.9%)

### 📊 Comparaison Avant/Après

| Métrique | v1.0 (Logistic) | v3.0 (Random Forest) |
|----------|-----------------|---------------------|
| **Accuracy** | 75-80% | **92.4%** |
| **Features** | 4 | **13**  |
| **Label** | Quantile score | **Croissance réelle**  |
| **Optimisation** | Aucune | **GridSearchCV**  |
| **Probas** | 100% partout (bug) | **4.6% - 90.9%** |
| **Équilibrage** | class_weight | **SMOTE + class_weight**  |

---

** Résumé :** Le modèle ML v3.0 est **infiniment meilleur** que la version documentée. Il prédit la croissance réelle au lieu d'un score artificiel, avec **92.4% de précision** !

---

## 7. INTERFACE STREAMLIT

### Structure de l'Application

**Fichier : `app/streamlit.py` (2400+ lignes)**
```python
# 1. Configuration
st.set_page_config(
    page_title="JEK2 Records - Music Talent Radar",
    page_icon="🎵",
    layout="wide"
)

# 2. Authentification
if not auth.require_authentication():
    if st.session_state.get('show_login', False):
        auth.login_form()
    else:
        auth.public_page_about()
    st.stop()

# 3. Chargement des données (avec cache optimisé)
@st.cache_data(ttl=600, show_spinner=False)  # 10 min au lieu de 5 min
def load_data():
    # ... chargement depuis SQLite
    return artistes_df, metriques_df, alertes_df

artistes_df, metriques_df, alertes_df = load_data()

# 4. Filtres sidebar
with st.sidebar:
    selected_plateforme = st.selectbox("🌐 Source", ['Tous', 'Spotify', 'Deezer'])
    selected_genre = st.selectbox("🎵 Genre", genres)
    min_score = st.slider("⭐ Score minimum", 0, 100, 0)

# 5. Navigation directe (sans flags intermédiaires)
if selected_page != st.session_state.active_page:
    st.session_state.active_page = selected_page
    st.rerun()  # Un seul rerun, pas trois !

# 6. Pages
if st.session_state.active_page == "Vue d'ensemble":
    # Code de la page Vue d'ensemble
    
elif st.session_state.active_page == "Les artistes":
    # Code de la page Les artistes
    
# ... etc
```

### Optimisations Performances

**Cache optimisé :**
```python
@st.cache_data(ttl=600, show_spinner=False)  
def load_data():
    # Chargement depuis SQLite
    conn = sqlite3.connect('data/music_talent_radar_v2.db')
    
    artistes_df = pd.read_sql("SELECT * FROM artistes", conn)
    metriques_df = pd.read_sql("SELECT * FROM metriques_historique", conn)
    alertes_df = pd.read_sql("SELECT * FROM alertes WHERE vu = 0", conn)
    
    conn.close()
    
    return artistes_df, metriques_df, alertes_df
```

**Navigation directe (sans flags intermédiaires) :**
```python
# AVANT (lent - 3 reruns)
if st.button("Voir évolution"):
    st.session_state.go_to_evolution = True
    st.session_state.selected_artist = artist_name
    time.sleep(0.1)  
    st.rerun()

if st.session_state.get('go_to_evolution'):
    st.session_state.active_page = "Évolution"
    st.session_state.go_to_evolution = False
    st.rerun()

# APRÈS (rapide - 1 seul rerun)
if st.button("Voir évolution"):
    st.session_state.active_page = "Évolution"
    st.session_state.selected_artist = artist_name
    st.rerun()  
```

**Résultat :** Changement de page en **<0.5s** au lieu de 2-3s.

### Design Système

**J'ai créé une identité visuelle cohérente :**
```python
COLORS = {
    'primary': '#FF1B8D',      # Rose vif
    'secondary': "#323A79",     # Bleu foncé
    'accent1': "#47559D",       # Bleu-violet
    'accent2': "#4A0B7E",       # Violet
    'accent3': "#21B178",       # Vert
    'bg_dark': "#070707",       # Noir
    'bg_card': "#000000",       # Noir pur
    'text': "#B18E57"           # Beige/or
}
```

**Fond personnalisé :**
```python
def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

bg_image = get_base64_image("app/assets/back.png")

st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{bg_image}");
        background-size: cover;
        background-attachment: fixed;
    }}
    </style>
""", unsafe_allow_html=True)
```

### Les 8 Pages de l'Application

#### **1. Vue d'ensemble**

Tableau de bord avec :
- Métriques clés (nombre d'artistes, alertes)
- Distribution des scores (histogramme)
- Répartition par genre (camembert)
- Top 5 Spotify / Deezer (barres horizontales)
```python
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🎤 ARTISTES", len(filtered_df))
with col2:
    spotify_count = (filtered_df['plateforme'] == 'Spotify').sum()
    st.metric("🟢 SPOTIFY", spotify_count)
# ... etc
```

#### **2. Les Tops**

- Top 30 meilleurs scores (graphique géant)
- Top 5 meilleures évolutions (% de croissance)
- Répartition Spotify/Deezer dans le Top 50
- Distribution followers dans le Top 50

**Feature préférée :**
```python
# Calculer l'évolution entre première et dernière collecte
evolution_data = []
for artiste in top_df['nom_artiste'].unique():
    artist_data = metriques_df[metriques_df['nom_artiste'] == artiste]
    if len(artist_data) > 1:
        first_score = artist_data.iloc[0]['score_potentiel']
        last_score = artist_data.iloc[-1]['score_potentiel']
        evolution_pct = ((last_score - first_score) / first_score) * 100
        evolution_data.append({'nom_artiste': artiste, 'evolution': evolution_pct})
```

#### **3. Les Artistes**

**Grille de 5 colonnes avec :**
- Photo de l'artiste
- Nom + plateforme + genre
- Score + followers
- Checkbox de sélection
- Boutons "Écouter" + "Détails"

**Pagination (50 par page) :**
```python
ITEMS_PER_PAGE = 50
total_pages = math.ceil(len(artistes_sorted) / ITEMS_PER_PAGE)

start_idx = (st.session_state.page_artistes - 1) * ITEMS_PER_PAGE
end_idx = start_idx + ITEMS_PER_PAGE
page_artistes = artistes_sorted.iloc[start_idx:end_idx]
```

#### **4. Évolution**

Page de détail d'un artiste avec :
- Photo + infos
- Métriques actuelles
- Graphique d'évolution des followers
- Graphique d'évolution du score
- Artistes similaires (KNN)

**Algorithme de similarité :**
```python
from sklearn.neighbors import NearestNeighbors

# Features pour le KNN
X = candidates[['followers_total', 'score_potentiel', 'popularity']].fillna(0)

# Trouver les 5 plus proches
knn = NearestNeighbors(n_neighbors=6, metric='cosine')
knn.fit(X)

distances, indices = knn.kneighbors([current_features])
similar_artists = candidates.iloc[indices[0][:5]]
```

**Pourquoi cosine et pas euclidean ?**  
La distance cosinus mesure la **direction** (similarité de profil), pas la **magnitude** (taille absolue). Parfait pour comparer des artistes de tailles différentes.

#### **5. Alertes**

- Affichage des alertes triées
- Filtres (type, date)
- Boutons "Écouter" + "Détails"
- Fonction "Marquer comme lu"

#### **6. Prédictions**

- Top 10 artistes émergents (selon ML Random Forest 92.4%)
- Graphique de probabilité
- Grille de photos
- Boutons "Écouter" + "Détails"

**Filtrage intelligent :**
```python
# Exclure les artistes déjà connus (>80k)
predictions_df = predictions_df[predictions_df['followers'] < 80000]
```

#### **7. À Propos**

Page de présentation avec :
- Mission de JEK2 Records
- Explication du score
- Tableau coloré des critères
- Ma bio + mes chansons (avec player audio!)
```python
audio_path = "app/assets/ma_famille.m4a"
audio_base64 = get_base64_image(audio_path)
st.markdown(f"""
    <audio controls>
        <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
    </audio>
""", unsafe_allow_html=True)
```

#### **8. Mon Profil**

- Liste des artistes marqués comme "intéressés"
- Stats (nombre, répartition)
- Boutons "Écouter" + "Détails" + "Retirer"

**Gestion du state :**
```python
# Initialisation
if 'artistes_interesses' not in st.session_state:
    st.session_state.artistes_interesses = []

# Ajout
if is_checked and artiste not in st.session_state.artistes_interesses:
    st.session_state.artistes_interesses.append(artiste)

# Suppression
if st.button("Retirer"):
    st.session_state.artistes_interesses.remove(artiste)
    st.rerun()
```

---

## 8. SYSTÈME D'ALERTES

###  Objectif

**Détecter automatiquement les artistes qui "buzzent" pour réagir vite !**

Types d'alertes :
- 🚀 **Croissance rapide** (+20% de followers)
- ⚠️ **Baisse inquiétante** (-15% de followers)
- ⭐ **Progression de score** (+10 points)
- 🔥 **TRENDING** (score >80)

###  Fichier `generer_alertes.py`
```python
import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect('data/music_talent_radar_v2.db')
cursor = conn.cursor()

# Récupérer les 2 dernières collectes par artiste
cursor.execute("""
    SELECT 
        id_unique,
        nom_artiste,
        plateforme,
        fans_followers,
        score_potentiel,
        date_collecte,
        ROW_NUMBER() OVER (
            PARTITION BY id_unique 
            ORDER BY date_collecte DESC
        ) as rang
    FROM metriques_historique
""")

# Grouper par artiste
artistes_data = {}
for row in cursor.fetchall():
    id_unique = row[0]
    if id_unique not in artistes_data:
        artistes_data[id_unique] = []
    artistes_data[id_unique].append(row)

# Analyser chaque artiste
for id_unique, historique in artistes_data.items():
    if len(historique) < 2:
        continue  # Pas assez de données
    
    # Dernière et avant-dernière collecte
    derniere = historique[0]
    precedente = historique[1]
    
    nom = derniere[1]
    plateforme = derniere[2]
    
    # Calculs
    followers_avant = precedente[3]
    followers_apres = derniere[3]
    score_avant = precedente[4]
    score_apres = derniere[4]
    
    if followers_avant > 0:
        variation_followers = ((followers_apres - followers_avant) / followers_avant) * 100
    else:
        variation_followers = 0
    
    variation_score = score_apres - score_avant
    
    # ALERTE 1 : Croissance followers
    if variation_followers >= 20:
        cursor.execute("""
            INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte)
            VALUES (?, ?, ?, ?)
        """, (
            nom,
            "Croissance Followers",
            f"Croissance de {variation_followers:.1f}% sur {plateforme} ! Passe de {int(followers_avant):,} à {int(followers_apres):,} followers.",
            datetime.now()
        ))
    
    # ALERTE 2 : Baisse followers
    elif variation_followers <= -15:
        cursor.execute("""
            INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte)
            VALUES (?, ?, ?, ?)
        """, (
            nom,
            " Baisse Followers",
            f"Baisse de {abs(variation_followers):.1f}% sur {plateforme}. De {int(followers_avant):,} à {int(followers_apres):,} followers.",
            datetime.now()
        ))
    
    # ALERTE 3 : Progression score
    if variation_score >= 10:
        cursor.execute("""
            INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte)
            VALUES (?, ?, ?, ?)
        """, (
            nom,
            " Progression Score",
            f"Score en hausse de {variation_score:.1f} points ! Passe de {score_avant:.1f} à {score_apres:.1f}.",
            datetime.now()
        ))
    
    # ALERTE 4 : Trending (score >80)
    if score_apres >= 80 and score_avant < 80:
        cursor.execute("""
            INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte)
            VALUES (?, ?, ?, ?)
        """, (
            nom,
            " TRENDING",
            f"Artiste à surveiller de près ! Score actuel : {score_apres:.1f}/100",
            datetime.now()
        ))

conn.commit()
conn.close()

print(f" Alertes générées !")
```

### Seuils Choisis

| Alerte     | Seuil      | Justification                                    |
|------------|------------|--------------------------------------------------|
| Croissance | +20%       | Croissance significative mais pas exceptionnelle |
| Baisse     | -15%       | Perte préoccupante de fans                       |
| Score      | +10 points | Amélioration notable                             |
| Trending   | >80        | Potentiel star                                   |

**Ces seuils sont ajustables** en fonction des retours utilisateurs.

### Statistiques d'Alertes

Sur ma base de ~300 artistes :
- 🚀 Croissances : ~15 par semaine
- ⚠️ Baisses : ~5 par semaine
- ⭐ Progressions : ~10 par semaine
- 🔥 Trending : ~2-3 par mois

---

## 9. AUTOMATISATION GITHUB ACTIONS

### ⚙️ Objectif

**Automatiser la collecte quotidienne pour suivre l'évolution des artistes dans le temps !**

###  Fichier `.github/workflows/main.yml`
```yaml
name: Update Music Data Daily

on:
  schedule:
    - cron: '0 2 * * *'  # Tous les jours à 2h UTC (3h Paris)
  workflow_dispatch:      # Bouton manuel

jobs:
  collect-and-update:
    runs-on: ubuntu-latest
    
    permissions:
      contents: write
    
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Collect data
        env:
          SPOTIFY_CLIENT_ID: ${{ secrets.SPOTIFY_CLIENT_ID }}
          SPOTIFY_CLIENT_SECRET: ${{ secrets.SPOTIFY_CLIENT_SECRET }}
        run: |
          python collecte1.py
          python music_talent_radar.py --all
          python ml_prediction.py
          python generer_alertes.py
      
      - name: Commit and push
        run: |
          git config user.name "GitHub Actions Bot"
          git config user.email "actions@github.com"
          
          # Forcer l'ajout des fichiers data
          git add -f artist_urls.csv
          git add -f data/*.csv
          git add -f data/*.db
          
          git diff --quiet && git diff --staged --quiet || (
            git commit -m " Collecte automatique $(date +'%Y-%m-%d %H:%M')" &&
            git push
          )
```

###  Secrets GitHub

**Configuration dans GitHub → Settings → Secrets :**
```
SPOTIFY_CLIENT_ID = abc123...
SPOTIFY_CLIENT_SECRET = xyz789...


---

## CONCLUSION

**La data analysis n'est pas qu'une question de code : c'est aussi de la créativité, de la rigueur, et de la passion.**

---

**Merci à la Wild Code School pour cette formation incroyable !** 

---

**Jenny**  
*Data Analyst / Parolière / Interprète / Chasseuse de talents*

**Contact :** jennybenmouhoub45@gmail.com  
**GitHub :** https://github.com/jennykarim45-ai  
---