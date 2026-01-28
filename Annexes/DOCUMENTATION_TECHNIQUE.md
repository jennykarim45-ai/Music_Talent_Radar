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
10. [Difficultés Rencontrées](#10-difficultés-rencontrées)
11. [Ce Que J'ai Appris](#11-ce-que-jai-appris)
12. [Pistes d'Amélioration](#12-pistes-damélioration)

---

## 1. INTRODUCTION & CONTEXTE

###  Objectif du Projet

En tant que passionnée de musique et en formation pour devenir Data analyst, j'ai voulu créer un outil qui combine mes deux passions : **détecter les talents musicaux émergents grâce à l'analyse de données**.

L'idée est simple : identifier les artistes qui ont un fort potentiel avant qu'ils ne deviennent célèbres, en analysant leurs statistiques sur Spotify et Deezer.

### Le Concept JEK2 Records

J'ai imaginé un **label de musique fictif** qui utilise la data pour repérer les futures stars. Le nom "JEK2" vient des initiales de ma famille. **Music Talent Radar** est le nom de l'application utilisée dans la découverte de nouveaux talents. 
J'ai également profité de ce projet pour vour faire découvrir mon univers à travers mes propres oeuvres musicales. 

###  Compétences Mobilisées

Ce projet m'a permis de mettre en pratique tout ce que j'ai appris en formation et dans mes recherches personnelles :
- **Python** : scripting, automatisation
- **APIs REST** : Spotify & Deezer
- **SQL** : gestion de base de données
- **Machine Learning** : modèle de prédiction
- **Streamlit** : visualisation interactive
- **Git/GitHub** : versioning

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
│   └── update_table_alertes.py   # Mise à jour alertes
│
├── .github/workflows/            # Automatisation
│   └── main.yml                  # GitHub Actions
│
├── collecte1.py                  # Collecte données APIs
├── music_talent_radar.py         # Import + Scoring
├── ml_prediction.py              # Prédictions ML
├── generer_alertes.py            # Génération alertes
├── database_manager_v2.py        # Gestion BDD
├── import_data.py                # Import CSV → SQLite
│
├── artist_urls.csv               # Liste URLs artistes
├── requirements.txt              # Dépendances Python
├── .env                          # Secrets API 
└── README.md                     # Enoncé des attentes du projet par la Wild Code School
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
                  │ML_PREDICTION.PY │      ← Modèle de prédiction
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

###  Fichier `collecte1.py`

C'est le **cœur de la collecte**. Voici comment il fonctionne :

#### **Étape 1 : Connexion aux APIs**

```python
# Spotify nécessite une authentification OAuth
def get_spotify_token():
    auth_string = f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}"
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
    
    # Requête pour obtenir le token
    response = requests.post(
        "https://accounts.spotify.com/api/token",
        headers={"Authorization": f"Basic {auth_base64}"},
        data={"grant_type": "client_credentials"}
    )
    
    return response.json()["access_token"]
```

**Pourquoi cette complexité ?**  
Spotify utilise OAuth 2.0 pour sécuriser son API. Au début, je ne comprenais pas pourquoi ma simple requête ne marchait pas. J'ai dû apprendre le système d'authentification par token.

#### **Étape 2 : Recherche d'Artistes**

J'utilise **50 mots-clés** répartis sur **7 genres** :

```python
SEARCH_KEYWORDS = {
    'Rap-HipHop-RnB': [
        'rap français émergent', 'hip hop underground france',
        'rnb français nouvelle génération', ...
    ],
    'Pop': ['pop française indépendante', ...],
    'Afrobeat-Amapiano': ['afrobeat français', ...],
    # ... etc
}
```

**Pourquoi 50 mots-clés ?**  
Au début, j'en avais seulement 10 et je trouvais toujours les mêmes artistes. En multipliant les mots-clés, j'ai diversifié les résultats.

#### **Étape 3 : Filtres Stricts**

**Le défi :** éviter les artistes déjà connus !

```python
# Filtres pour artistes VRAIMENT émergents
SPOTIFY_MIN_FOLLOWERS = 200
SPOTIFY_MAX_FOLLOWERS = 40000  # Pas plus de 40k car au delà il y a beaucoup d'artistes connus
DEEZER_MAX_FANS = 40000
ANNEE_MIN_PREMIER_ALBUM = 2018  # Uniquement artistes récents car beaucoup d'anciens artistes non pas beaucoup de followers/fans
```

#### **Étape 4 : Exclusions Intelligentes**

```python
# Patterns à exclure (regex)
DJ_PATTERNS = [
    r'\bdj\b', r'^dj\s', r'\sdj$', r'\sdj\s',
    r'DJ\s', r'\sDJ\b'
]

PRODUCER_KEYWORDS = [
    'prod', 'producer', 'beat maker', 'beatmaker',
    'instrumental', 'type beat'
]

EXCLUDED_CATEGORIES = [
    'orchestre', 'compilation', 'various artists',
    'karaoke', 'enfants', 'kids'
]
```

**Pourquoi ?**  
J'ai remarqué que je récupérais beaucoup de DJs et de producteurs, alors que je voulais des **chanteurs/rappeurs**. Ces exclusions ont amélioré la qualité des résultats.

###  Matching Spotify ↔ Deezer

Les artistes ont souvent des noms légèrement différents sur les deux plateformes :
- Spotify : "Limsa d'Aulnay"
- Deezer : "Limsa d'Aulnay-sous-Bois"

**Ma solution :**

```python
def normalize_artist_name(name):
    """Normalise un nom pour le matching"""
    import unicodedata
    
    # Minuscules
    name = name.lower().strip()
    
    # Enlever accents
    name = unicodedata.normalize('NFD', name)
    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
    
    # Enlever caractères spéciaux
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name)
    
    return name


# Puis j'utilise la distance de Levenshtein
from Levenshtein import distance

def fuzzy_match(name1, name2, threshold=0.85):
    """Match flou entre deux noms"""
    norm1 = normalize_artist_name(name1)
    norm2 = normalize_artist_name(name2)
    
    max_len = max(len(norm1), len(norm2))
    if max_len == 0:
        return False
    
    similarity = 1 - (distance(norm1, norm2) / max_len)
    return similarity >= threshold
```

**Résultat :**  
Avant : 10% de matching  
Après : **75% de matching** ! 

###  Output : `artist_urls.csv`

---

## 4. BASE DE DONNÉES

###  Pourquoi SQLite ?

Au début, je stockais tout en CSV. Problème : **lenteur** et **données dupliquées**.

J'ai choisi SQLite car :
-  Pas de serveur à installer
- Fichier unique (`.db`)
- Requêtes SQL rapides
- Facile à migrer vers PostgreSQL plus tard

### Schéma de la Base

```sql
-- Table des artistes
CREATE TABLE artistes (
    id_unique TEXT PRIMARY KEY,          -- spotify_123 ou deezer_456
    nom TEXT NOT NULL,
    genre TEXT,
    source TEXT,                         -- 'Spotify' ou 'Deezer'
    url_spotify TEXT,
    url_deezer TEXT,
    image_url TEXT,
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table des métriques (historique)
CREATE TABLE metriques_historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_unique TEXT,                      -- Lien avec artistes
    nom_artiste TEXT,
    plateforme TEXT,
    fans_followers INTEGER,              -- Unification Spotify/Deezer
    followers INTEGER,                   -- Spotify uniquement
    fans INTEGER,                        -- Deezer uniquement
    popularity INTEGER,                  -- 0-100 sur Spotify
    score_potentiel REAL,                -- Score
    nb_albums INTEGER,
    nb_releases_recentes INTEGER,        -- Sorties dans les 2 dernières années
    date_collecte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_unique) REFERENCES artistes(id_unique)
);

-- Table des alertes
CREATE TABLE alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_artiste TEXT,
    type_alerte TEXT,                    -- 'Croissance', 'Baisse', 'TRENDING'
    message TEXT,
    date_alerte TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    vu BOOLEAN DEFAULT 0
);
```

### Choix de Conception

**`id_unique` au lieu d'un ID auto-incrémenté :**

Pour éviter les doublons entre Spotify et Deezer.

Exemple :
- Artiste sur Spotify : `id_unique = "spotify_12345"`
- Même artiste sur Deezer : `id_unique = "deezer_67890"`

Ainsi, je peux avoir le même artiste sur 2 plateformes.

**`fans_followers` : colonne unifiée**

Spotify utilise `followers`, Deezer utilise `fans`. J'ai créé une colonne unique pour simplifier les requêtes :

```python
row['fans_followers'] = row.get('followers') or row.get('fans', 0)
```

###  Gestion de l'Historique

**Contrairement aux CSV qui écrasent les données, SQLite garde TOUT l'historique.**

Chaque jour, j'insère une nouvelle ligne dans `metriques_historique` :

```python
cursor.execute("""
    INSERT INTO metriques_historique 
    (id_unique, nom_artiste, fans_followers, score_potentiel, date_collecte)
    VALUES (?, ?, ?, ?, ?)
""", (id_unique, nom, followers, score, datetime.now()))
```

**Avantage :** Je peux tracer l'évolution d'un artiste dans le temps ! 

---

## 5. ALGORITHME DE SCORING

###  Le Problème Initial

Au début, j'utilisais un score basé uniquement sur **le nombre de followers**. Problème :
- ❌ Un artiste avec 40k followers mais 0 engagement = score élevé
- ❌ Un artiste avec 5k followers mais très actif = score faible

**Cela ne m'a pas semblé juste l'objectif étant de trouver des artistes émergents**

### La Solution : Score Multi-Critères

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

```
def calculer_audience(fans_followers):
    """
    Normalise le nombre de fans entre 200 et 40,000
    200 fans = 0%
    40,000 fans = 40%
    """
    fans_norm = min(max(fans_followers, 200), 40000)
    audience_score = ((fans_norm - 200) / (40000 - 200)) * 40
    return audience_score
```

**Pourquoi 200-40k ?**
- < 200 : trop petit pour être viable
- \> 40k : déjà trop connu

**Exemple :**
- 200 fans → 0 points
- 20,000 fans → 20 points
- 40,000 fans → 40 points

#### **2. Engagement (30%) - Qualité de la relation avec les fans**

**Sur Spotify :**
```python
# J'utilise la "popularity" comme proxy (0-100)
engagement_spotify = ((popularity - 20) / (65 - 20)) * 30
```

**Sur Deezer :**
```python
# Je calcule le ratio fans/albums
engagement_deezer = (fans / nb_albums) / 10000 * 30
```

**Pourquoi cette différence ?**  
Spotify fournit déjà une métrique `popularity` qui reflète l'engagement. Deezer non, donc j'ai dû créer ma propre formule.


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

**Pourquoi? :**  
Un artiste qui sort régulièrement de la musique montre sa motivation et son professionnalisme.

**Comment je récupère cette info ?**

```python
# Dans collecte1.py
albums = requests.get(
    f"https://api.spotify.com/v1/artists/{artist_id}/albums",
    headers=headers,
    params={"limit": 50}
).json()

# Je compte les sorties des 2 dernières années
two_years_ago = datetime.now() - timedelta(days=730)
recent_releases = 0

for album in albums.get('items', []):
    release_date = album.get('release_date', '')
    if release_date:
        try:
            release_dt = datetime.strptime(release_date, '%Y-%m-%d')
            if release_dt >= two_years_ago:
                recent_releases += 1
        except:
            pass
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

**Pourquoi?:**  
Un artiste qui a réussi à se faire référencer sur **plusieurs plateformes** montre un début de notoriété et de sérieux.

### Calcul Final

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
Audience:    (5000-200)/(40000-200) * 40 = 4.8
Engagement:  (45-20)/(65-20) * 30 = 16.7
Récurrence:  3/10 * 20 = 6.0
Influence:   0
────────────────────────────────────────
SCORE TOTAL: 27.5 / 100
```

**Artiste B :**
- 25,000 fans
- Popularity 55
- 8 sorties récentes
- Sur Spotify ET Deezer

```
Audience:    (25000-200)/(40000-200) * 40 = 24.9
Engagement:  (55-20)/(65-20) * 30 = 23.3
Récurrence:  8/10 * 20 = 16.0
Influence:   10
────────────────────────────────────────
SCORE TOTAL: 74.2 / 100 ⭐
```


## 6. MACHINE LEARNING

###  Objectif du Modèle

**Question :** Comment prédire quels artistes vont "exploser" ?

**Ma démarche :**
1. Utiliser les données historiques
2. Créer un label "star" / "pas star"
3. Entraîner un modèle de classification
4. Prédire sur les nouveaux artistes

### Préparation des Données

**Fichier : `ml_prediction.py`**

#### **Étape 1 : Charger les Données**

```python
import pandas as pd
import sqlite3

conn = sqlite3.connect('data/music_talent_radar_v2.db')

df = pd.read_sql_query("""
    SELECT 
        a.nom,
        a.genre,
        a.source as plateforme,
        m.fans_followers,
        m.popularity,
        m.score_potentiel as score,
        m.nb_albums,
        m.nb_releases_recentes
    FROM artistes a
    INNER JOIN metriques_historique m ON a.id_unique = m.id_unique
    WHERE m.date_collecte = (
        SELECT MAX(date_collecte) 
        FROM metriques_historique 
        WHERE id_unique = a.id_unique
    )
""", conn)

conn.close()
```
 
Je ne prends que la **dernière** métrique de chaque artiste (la plus récente).

#### **Étape 2 : Feature Engineering**

```python
# Normaliser popularity
df['popularity'] = df['popularity'].fillna(df['fans_followers'] / 1000)

# Créer feature "engagement"
df['engagement'] = df['popularity'] / (df['fans_followers'] / 1000)
df['engagement'] = df['engagement'].fillna(0).replace([float('inf')], 0)

# Créer feature "score par follower"
df['score_per_follower'] = df['score'] / (df['fans_followers'] / 1000)
df['score_per_follower'] = df['score_per_follower'].fillna(0).replace([float('inf')], 0)
```


#### **Étape 3 : Créer le Label**

**Le challenge :** Comment définir une "star" ?

**Ma solution :**
```python
# Les "stars" sont dans le TOP 10% des scores
threshold = df['score'].quantile(0.90)
df['is_star'] = (df['score'] >= threshold).astype(int)

print(f"Seuil 'star': {threshold:.1f}")
print(f"{df['is_star'].sum()} artistes classés 'star' (top 10%)")
```

**Exemple :**
- Si le seuil est 75, tous les artistes avec score ≥ 75 sont des "stars"
- Environ 10% de ma base (les meilleurs)

**Pourquoi 10% et pas 30% ?**  
J'ai testé différents seuils. À 30%, le modèle trouvait trop d'artistes "star" (peu sélectif). À 5%, pas assez de données d'entraînement. **10% est le bon équilibre.**

###  Entraînement du Modèle

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

# Features
X = df[['fans_followers', 'popularity', 'engagement', 'score_per_follower']].fillna(0)
y = df['is_star']

# Split 80% train / 20% test
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Normalisation (TRÈS IMPORTANT!)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Modèle
model = LogisticRegression(
    max_iter=1000,
    random_state=42,
    C=0.1,                    # Régularisation forte
    class_weight='balanced'   # Équilibrer les classes
)

model.fit(X_train_scaled, y_train)

# Score
accuracy = model.score(X_test_scaled, y_test)
print(f"Précision: {accuracy:.2%}")
```

**Résultat : ~75-80% de précision** 

### Pourquoi ces Choix ?

**StandardScaler :**  
Mes features ont des échelles très différentes :
- `fans_followers` : 200 - 40,000
- `popularity` : 0 - 100
- `engagement` : 0 - 5

Sans normalisation, le modèle serait biaisé vers les grandes valeurs.

**Logistic Regression :**  
J'ai testé plusieurs modèles :
- Logistic Regression 
- Random Forest → overfitting
- SVM → trop lent

La régression logistique est simple, rapide et performante pour mon cas d'usage.

**class_weight='balanced' :**  
Problème : J'ai beaucoup plus d'artistes "pas star" (90%) que de "stars" (10%).  
Solution : Dire au modèle de donner plus d'importance à la classe minoritaire.

###  Prédictions

```python
# Prédire sur tous les artistes
X_all_scaled = scaler.transform(X)
df['proba_star'] = model.predict_proba(X_all_scaled)[:, 1]

# Sauvegarder
predictions = df[['nom', 'genre', 'plateforme', 'score', 'proba_star']].copy()
predictions['followers'] = df['fans_followers']
predictions = predictions.sort_values('proba_star', ascending=False)
predictions.to_csv('data/predictions_ml.csv', index=False)

# Top 5
print("\nTop 5 artistes à fort potentiel:")
for idx, row in predictions.head(5).iterrows():
    print(f"  - {row['nom']}: {row['proba_star']:.1%} (score: {row['score']:.1f})")
```




###  Erreurs que J'ai Faites

**Erreur 1 : Pas de normalisation**  
Résultat : Précision de 60%  
Solution : Ajouter StandardScaler → 75%

**Erreur 2 : Seuil "star" trop bas (30%)**  
Résultat : Trop de "stars", modèle peu discriminant  
Solution : Monter à 10%

**Erreur 3 : Ne pas gérer les valeurs infinies**  
Problème : Division par 0 → `inf` → crash  
Solution : `.replace([float('inf')], 0)`

---

## 7. INTERFACE STREAMLIT

###  Structure de l'Application

**Fichier : `app/streamlit.py` 

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

# 3. Chargement des données
artistes_df, metriques_df, alertes_df = load_data()

# 4. Filtres sidebar
with st.sidebar:
    selected_plateforme = st.selectbox("🌐 Source", ['Tous', 'Spotify', 'Deezer'])
    selected_genre = st.selectbox("🎵 Genre", genres)
    min_score = st.slider("⭐ Score minimum", 0, 100, 0)

# 5. Pages
if st.session_state.active_page == "Vue d'ensemble":
    # Code de la page Vue d'ensemble
    
elif st.session_state.active_page == "Les artistes":
    # Code de la page Les artistes
    
# ... etc
```

###  Design Système

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

###  Les 8 Pages de l'Application

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

- Top 10 artistes émergents (selon ML)
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
            "🚀 Croissance Followers",
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
            "⚠️ Baisse Followers",
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
            "⭐ Progression Score",
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
            "🔥 TRENDING",
            f"Artiste à surveiller de près ! Score actuel : {score_apres:.1f}/100",
            datetime.now()
        ))

conn.commit()
conn.close()

print(f" Alertes générées !")
```

### 🎯 Seuils Choisis

| Alerte | Seuil | Justification |
|--------|-------|---------------|
| Croissance | +20% | Croissance significative mais pas exceptionnelle |
| Baisse | -15% | Perte préoccupante de fans |
| Score | +10 points | Amélioration notable |
| Trending | >80 | Top tier, potentiel star |

**Ces seuils sont ajustables** en fonction des retours utilisateurs.

###  Statistiques d'Alertes

Sur ma base de ~200 artistes :
- 🚀 Croissances : ~15 par semaine
- ⚠️ Baisses : ~5 par semaine
- ⭐ Progressions : ~10 par semaine
- 🔥 Trending : ~2-3 par mois

---

## 9. AUTOMATISATION GITHUB ACTIONS

###  Objectif

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
          git add data/
          git commit -m "🤖 Auto-update $(date +'%Y-%m-%d')" || exit 0
          git push
```

###  Secrets GitHub

**Configuration dans GitHub → Settings → Secrets :**

```
SPOTIFY_CLIENT_ID = abc123...
SPOTIFY_CLIENT_SECRET = xyz789...
```

---

## 10. COMPETENCES MOBILISEES


**Python avancé :**
-  Requêtes HTTP avec `requests`
-  Manipulation de JSON
-  Pandas : merge, groupby, pivot
-  Gestion d'erreurs try/except
-  List comprehensions
-  Lambda functions

**SQL :**
-  Créer des tables
-  Jointures (INNER JOIN, LEFT JOIN)
-  Agrégations (GROUP BY, HAVING)
-  Sous-requêtes
-  Window functions (ROW_NUMBER)

**Machine Learning :**
-  Préparation des données
-  Feature engineering
-  Train/test split
-  Normalisation (StandardScaler)
-  Régression logistique
-  KNN
-  Évaluation de modèle

**Visualisation :**
- Plotly : barres, lignes, camemberts
- Streamlit : layouts, widgets, state
- CSS personnalisé
- Responsive design

**DevOps :**
- Git (commit, push, pull)
- GitHub Actions
- Gestion de secrets
- CI/CD basique

---

##  CONCLUSION

Ce projet a été un véritable marathon. J'ai appris énormément. La data analysis n'est pas qu'une question de code : c'est aussi de la créativité, de la rigueur, et de la passion.


Mais surtout, je suis **fière du résultat** ! Music Talent Radar fonctionne, il est beau, et il pourrait vraiment aider un label à découvrir les talents de demain.

**Merci à la Wild Code School pour cette formation incroyable !** 

---

**Jenny BENMOUHOUB**
*Data Analyst / Parolière / Interprète / Chasseuse de talents*

---

**Contact :** jennybenmouhoub45@gmail.com
**GitHub :** https://github.com/jennykarim45-ai
