# 📘 MUSIC TALENT RADAR - DOCUMENTATION TECHNIQUE v1.1

## 🎯 Vue d'ensemble

**Nom du projet** : Music Talent Radar  
**Client** : JEK2 Records (label fictif)  
**Développeur** : Jenny - Wild Code School  
**Version** : 1.1.0 (Janvier 2026)  
**Objectif** : Système de détection et d'analyse de talents musicaux émergents avec prédictions ML et alertes automatiques

---

## 📋 Table des matières

1. [Architecture du système](#architecture)
2. [Technologies utilisées](#technologies)
3. [Structure du projet](#structure)
4. [Base de données](#base-de-données)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Modules principaux](#modules)
8. [Système d'alertes](#alertes)
9. [API et intégrations](#api)
10. [Machine Learning](#ml)
11. [Déploiement](#déploiement)
12. [Maintenance](#maintenance)

---

## 🏗️ Architecture du système {#architecture}

### Architecture globale

```
┌────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR               │
│                   (Streamlit Web App)                  │
│   ┌──────────┬──────────┬──────────┬──────────────┐    │
│   │ Vue      │ Top      │ Artistes │ Évolution    │    │
│   │ Ensemble │ Artistes │ (Search) │              │    │
│   ├──────────┼──────────┼──────────┼──────────────┤    │
│   │ Alertes  │ Prédic.  │ À Propos │ Mon Profil   │    │
│   │ (Auto)   │ (ML)     │          │ (Favoris)    │    │
│   └──────────┴──────────┴──────────┴──────────────┘    │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                      APPLICATIVE                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Authentif.   │  │ Visualisation│  │ Prédictions  │  │
│  │ (auth.py)    │  │ (streamlit)  │  │ (ml_pred.py) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐                    │
│  │ Alertes Auto │  │ Format Dates │                    │
│  │ (generer.py) │  │ (DD/MM/YYYY) │                    │
│  └──────────────┘  └──────────────┘                    │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                       DONNÉES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ SQLite/      │  │ CSV Files    │  │ APIs         │  │
│  │ PostgreSQL   │  │ (import)     │  │ (Spotify/    │  │
│  │  + Alertes   │  │              │  │  Deezer)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────┘
```

### Flux de données

1. **Collecte** : Import CSV Spotify/Deezer → Base de données
2. **Traitement** : Calcul de scores, nettoyage, agrégation
3. **Analyse** : Modèle ML pour prédictions
4. **Alertes** : Détection automatique croissance > 5%
5. **Visualisation** : Dashboard Streamlit interactif
6. **Suivi** : Système de favoris multi-sources

---

##  Technologies utilisées {#technologies}

### Backend
- **Python 3.9+**
- **Pandas** (manipulation données)
- **SQLite** (base locale) / **PostgreSQL** (prod)
- **Scikit-learn** (Machine Learning)

### Frontend
- **Streamlit** (framework web)
- **Plotly** (graphiques interactifs)
- **HTML/CSS** (personnalisation)

### Machine Learning
- **Régression Logistique** (prédictions)
- **K-Nearest Neighbors** (artistes similaires)
- **StandardScaler** (normalisation)

### Nouveautés v1.1
- **Système d'alertes automatiques** (détection anomalies)
- **Recherche dynamique** (liste déroulante)
- **Sélection multi-sources** (checkboxes)
- **Formatage dates** (DD/MM/YYYY)

### Déploiement
- **Streamlit Community Cloud** (hébergement)
- **GitHub** (versioning)

---

##  Structure du projet {#structure}

```
MusicTalentRadarAll/
│
├── app/
│   ├── streamlit.py                 # Application principale (v1.1)
│   └── auth.py                      # Authentification
│
├── data/
│   ├── music_talent_radar_v2.db     # Base SQLite
│   ├── predictions_ml.csv           # Prédictions générées
│   ├── spotify_artists_*.csv        # Imports Spotify
│   └── deezer_artists_*.csv         # Imports Deezer
│
├── assets/
│   ├── logo.png                     # Logo JEK2
│   ├── back.png                     # Image fond
│   ├── moipiano.png                 # Photo auteure
│   └── ma_famille.m4a               # Composition audio
│
├── collecter_donnees.py             # Collecte des données
├── ml_prediction.py                 # Script prédictions ML
├── generer_alertes.py               #Alertes auto
├── import_data.py                   # Script import CSV
├── filtrer_csv_emergents.py         # Filtrage artistes
├── nettoyer_base.py                 # Nettoyage DB
├── diagnostic_base.py               # Diagnostic DB
│
├── requirements.txt                 # Dépendances Python
├── .streamlit/
│   └── config.toml                  # Config Streamlit
├── Annexes
│   ├── DOCUMENTATION_TECHINQUE.md   #Documentation
│   └── GUIDE_UTILISATEUR.md         #Documentation 
└── README.md                        # Documentation
```

---

## Base de données {#base-de-données}

### Schéma SQLite

#### Table `artistes`
```sql
CREATE TABLE artistes (
    id_unique TEXT PRIMARY KEY,
    nom TEXT NOT NULL,
    source TEXT,              
    genre TEXT,
    followers INTEGER,
    fans INTEGER,
    popularity INTEGER,
    url_spotify TEXT,
    url_deezer TEXT,
    image_url TEXT,
    score REAL,
    categorie TEXT,
    date_collecte TEXT
);
```

#### Table `metriques_historique`
```sql
CREATE TABLE metriques_historique (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_unique TEXT,
    plateforme TEXT,
    fans_followers INTEGER,
    followers INTEGER,
    fans INTEGER,
    popularity INTEGER,
    score_potentiel REAL,
    score REAL,
    date_collecte TEXT,
    FOREIGN KEY (id_unique) REFERENCES artistes(id_unique)
);
```

#### Table `alertes` 
```sql
CREATE TABLE alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_artiste TEXT,
    type_alerte TEXT,         -- '🚀 Forte Croissance', '⚠️ Baisse', etc.
    message TEXT,
    date_alerte TEXT,
    vu BOOLEAN DEFAULT 0
);
```

### Clés et index

```sql
CREATE INDEX idx_artistes_source ON artistes(source);
CREATE INDEX idx_artistes_genre ON artistes(genre);
CREATE INDEX idx_metriques_date ON metriques_historique(date_collecte);
CREATE INDEX idx_metriques_id ON metriques_historique(id_unique);
CREATE INDEX idx_alertes_vu ON alertes(vu);  
```

---
## Collecte de données automatisée

Github /Actions/workflows
```
┌─────────────────────────────────────────────┐
│         TOUS LES JOURS À 8H                 │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  1. collecter_donnees.py                    │
│     └→ Appels APIs Spotify/Deezer           │
│     └→ Génération CSV                       │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  2. filtrer_csv_emergents.py                │
│     └→ Filtre < 60k followers               │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  3. import_data.py                          │
│     └→ Import dans SQLite                   │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  4. ml_prediction.py                        │
│     └→ Génération prédictions ML            │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  5. generer_alertes.py                      │
│     └→ Détection croissance > 5%            │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  6. Git Push                                │
│     └→ Mise à jour Streamlit Cloud          │
└─────────────────────────────────────────────┘
```
##  Installation {#installation}

### Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (optionnel)

### Installation locale

```bash
# 1. Cloner le projet
git clone https://github.com/username/MusicTalentRadar.git
cd MusicTalentRadarAll

# 2. Créer environnement virtuel
python -m venv venv

# Windows
source venv/Scrips/activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. Lancer l'application
streamlit run app/streamlit.py
```

### Dépendances (requirements.txt)

```txt
streamlit==1.31.0
pandas==2.1.4
plotly==5.18.0
scikit-learn==1.4.0
Pillow==10.2.0
psycopg2-binary==2.9.9  # Pour PostgreSQL prod
```

---

## Configuration {#configuration}

### Fichier `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#FF1B8D"
backgroundColor = "#070707"
secondaryBackgroundColor = "#000000"
textColor = "#B18E57"
font = "sans serif"

[server]
port = 8501
headless = true
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### Variables d'environnement

Pour PostgreSQL (production) :
```bash
# .env
DATABASE_URL=postgresql://user:password@host:5432/database
```

### Authentification

**Fichier** : `app/auth.py`

**Utilisateurs par défaut** :
- **Username** : `admin`
- **Password** : `admin123`

```python
# auth.py
USERS = {
    "admin": "admin123"
}
```

---

##  Modules principaux {#modules}

### 1. streamlit.py (Application principale )

**Responsabilités** :
- Interface utilisateur
- Visualisations interactives
- Gestion des filtres
- Navigation entre pages


**Fonctions clés** :
```python
@st.cache_data(ttl=300)
def load_data():
    """Charge artistes, métriques, alertes"""
    
def get_latest_metrics(metriques_df):
    """Récupère dernières métriques par artiste"""
    
def get_fan_category(fans):
    """Catégorise par nombre de fans"""
```

**Pages (Tabs)** :
1. Vue d'ensemble - KPIs et graphiques globaux
2. Les Top - Top 30 par score
3. Les Artistes - Grille avec **✨ recherche + checkboxes**
4. Évolution - Suivi temporel + **✨ artistes similaires (checkboxes)**
5. Alertes - **✨ Notifications automatiques**
6. Prédictions - ML Top 10 + **✨ checkboxes**
7. À Propos - Présentation projet
8. Mon Profil - **✨ Artistes suivis (ignore filtres)**

---

### 2. ml_prediction.py (Machine Learning)

**Algorithme** : Régression Logistique

**Features** :
- `fans_followers` : Nombre total de followers/fans
- `popularity` : Score de popularité (0-100)
- `engagement` : Ratio popularité/followers
- `score_per_follower` : Score normalisé

**Label** : `is_star` (top 10% des scores)

**Processus** :
```python
1. Charger données depuis DB
2. Calculer features engineered
3. Normalisation (StandardScaler)
4. Entraînement modèle
5. Génération probabilités
6. Export predictions_ml.csv (avec colonne 'followers')
```

**Sortie** :
```csv
nom,proba_star,followers,popularity,score,genre,source
```

---

### 3. generer_alertes.py 

**Objectif** : Détecter automatiquement les artistes avec évolutions significatives

**Critères de détection** :
```python
SEUIL_CROISSANCE = 5.0  # 5% minimum
```

**Types d'alertes générées** :

1. **Forte Croissance** : Croissance ≥ 5% followers
   ```
   "Croissance de 12.3% des followers (50,000 → 56,422)"
   ```

2. **Baisse Significative** : Baisse ≤ -5% followers
   ```
   "Baisse de 16.7% des followers (30,000 → 25,000)"
   ```

3. **Score en Hausse** : Score +10% ou plus
   ```
   "Score de potentiel en hausse de 15.2% (51.2 → 58.9)"
   ```

4. **TRENDING** : Croissance ≥ 15% + Score > 60
   ```
   "Artiste en pleine ascension ! Croissance 18.5% avec score 58.3"
   ```

**Utilisation** :
```bash
# Générer les alertes
python generer_alertes.py

# Résultat visible dans TAB5 - Alertes
```

**Processus** :
```python
1. Charger métriques historiques
2. Analyser évolutions par artiste
3. Comparer dernière vs avant-dernière collecte
4. Calculer croissance (%)
5. Générer alertes si critères remplis
6. Insérer dans table 'alertes'
```

---

### 4. import_data.py (Import CSV)

**Responsabilités** :
- Import CSV Spotify/Deezer filtrés
- Nettoyage colonnes dupliquées
- Insertion dans SQLite

**Flux** :
```python
1. Vérifier existence CSV filtrés
2. Vider tables artistes + metriques
3. Créer id_unique (nom + source)
4. Insérer artistes
5. Insérer métriques historiques
6. Afficher statistiques
```

---

### 5. filtrer_csv_emergents.py (Filtrage)

**Objectif** : Garder seulement artistes < 60k followers

**Processus** :
```python
1. Charger CSV originaux
2. Filtrer followers < SEUIL (60k par défaut)
3. Sauvegarder *_filtered.csv
4. Afficher stats avant/après
```

**Paramètre ajustable** :
```python
SEUIL_FOLLOWERS = 60000  # Modifiable
```

---

### 6. auth.py (Authentification)

**Système** : Session-based avec Streamlit

**Fonctions** :
```python
def require_authentication():
    """Vérifie si user connecté"""
    
def login_form():
    """Affiche formulaire login"""
    
def public_page_about():
    """Page publique À Propos"""
```

**Identifiants** :
- **Username** : `admin`
- **Password** : `admin123`


---

##  Système d'alertes {#alertes}

### Architecture des alertes

```
┌─────────────────────────────────────┐
│     generer_alertes.py              │
│  (Script exécutable manuellement)   │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Analyse métriques historiques      │
│  - Comparer dernières collectes     │
│  - Calculer croissance (%)          │
│  - Détecter anomalies               │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Génération alertes si critères     │
│  - Croissance > 5%                  │
│  - Baisse > 5%                      │
│  - Score +10%                       │
│  - Trending (Croissance +15%)       │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Insertion dans table 'alertes'     │
│  (vu = 0 par défaut)                │
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│  Affichage dans TAB5 - Alertes      │
│  (Streamlit lit WHERE vu = 0)       │
└─────────────────────────────────────┘
```

### Personnalisation

**Modifier le seuil** :
```python
# Dans generer_alertes.py, ligne 10
SEUIL_CROISSANCE = 3.0  # 3% au lieu de 5%
```

**Ajouter un nouveau type d'alerte** :
```python
# Exemple : Alerte seuil followers
if followers_derniere >= 100000 and followers_avant < 100000:
    alertes_a_inserer.append({
        'nom_artiste': artiste,
        'type_alerte': '🎯 Seuil Atteint',
        'message': f"100k followers atteints ! ({int(followers_derniere):,})",
        'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'vu': 0
    })
```

---

##  API et intégrations {#api}

### APIs utilisées (phase collecte)

#### Spotify Web API
- **Endpoint** : `https://api.spotify.com/v1/artists/{id}`
- **Auth** : OAuth 2.0 Client Credentials
- **Données** : followers, popularity, genres, image_url

#### Deezer API
- **Endpoint** : `https://api.deezer.com/artist/{id}`
- **Auth** : Aucune (API publique)
- **Données** : fans, nb_album, image_url

**Note** : Les APIs ne sont PAS appelées directement par l'app Streamlit. Les données sont pré-collectées et importées via CSV.

---

##  Machine Learning {#ml}

### Modèle de prédiction


**Algorithme** : Régression Logistique
```python
LogisticRegression(
    max_iter=1000,
    random_state=42,
    C=0.1,                    # Régularisation forte
    class_weight='balanced'   # Équilibrage classes
)
```

**Métriques** :
- Précision : ~95% (sur ensemble test)
- Classe positive : top 10% scores
- Sortie : Probabilité [0, 1]

### Feature Engineering

```python
# Engagement
engagement = popularity / (fans_followers / 1000)

# Score par follower
score_per_follower = score / (fans_followers / 1000)
```

### Normalisation

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
```

### Critères de succès

- **Artiste "star"** : score >= quantile 90%
- **Haut potentiel** : proba_star > 30%
- **Star prédite** : proba_star > 50%

---

##  Fonctionnalités Interface v1.1

### Recherche d'artistes (TAB3)



```python
# Interface
[🔍 Rechercher ▼] [📊 Trier par ▼] [📈 Ordre ▼]

# Fonctionnement
- "Tous" : Affiche tous les artistes (défaut)
- Sélectionner un nom : Affiche SEULEMENT cet artiste
```

**Code** :
```python
col_search, col_tri1, col_tri2 = st.columns([2, 1, 1])

with col_search:
    selected_search = st.selectbox(
        "🔍 Rechercher un artiste",
        ["Tous"] + artistes_list,
        key="search_artiste"
    )

if selected_search != "Tous":
    artistes_sorted = filtered_df[filtered_df['nom_artiste'] == selected_search].copy()
else:
    artistes_sorted = filtered_df.copy()
```

---

### Sélection multi-sources


#### TAB3 - Les Artistes (déjà existant)
```python
is_checked = st.checkbox("", value=artist['nom_artiste'] in temp_interesses)
```

#### TAB6 - Prédictions 
```python
# Grille Top 10 avec checkboxes
for artist in top10:
    is_checked = st.checkbox("", value=artist['nom'] in temp_interesses)
    [Photo + Nom + Score]
    [Bouton "Voir évolution"]

```

#### TAB4 - Artistes Similaires 
```python
# 5 artistes similaires avec checkboxes
for artist in similar_artists:
    is_checked = st.checkbox("", value=artist['nom'] in temp_interesses)
    [Photo + Nom + Score]
    [Boutons "Écouter" + "Infos"]

[VALIDER ARTISTES SIMILAIRES] # Bouton centralisé
```

**Workflow utilisateur** :
1. Cocher artistes dans TAB3, TAB4, ou TAB6
2. Cliquer "VALIDER"
3. Retrouver dans TAB8 - Mon Profil

---


## 🌐 Déploiement {#déploiement}

### Déploiement Streamlit Cloud

```bash
# 1. Push sur GitHub
git add .
git commit -m "Deploy ready v1.1"
git push origin main

# 2. Connecter Streamlit Cloud à GitHub
# 3. Configurer :
#    - Main file: app/streamlit.py
#    - Python version: 3.9
#    - Requirements: requirements.txt

# 4. Secrets (si PostgreSQL)
[secrets]
DATABASE_URL = "postgresql://..."
```

### Fichiers à inclure

```
MusicTalentRadarAll/
├── app/
├── data/
│   ├── music_talent_radar_v2.db  # Base SQLite
│   └── predictions_ml.csv        # Prédictions
├── assets/
├── requirements.txt
├── .streamlit/
└── generer_alertes.py 
```

### Variables d'environnement

**Streamlit Secrets** :
```toml
# .streamlit/secrets.toml (local)
DATABASE_URL = "sqlite:///data/music_talent_radar_v2.db"

# Streamlit Cloud (web interface)
DATABASE_URL = "postgresql://..."
```

---

### Monitoring

**Métriques à surveiller** :
- Nombre d'artistes actifs
- Nombre d'alertes générées
- Temps de chargement pages
- Erreurs logs Streamlit
- Taille base de données

**Logs** :
```bash
# Streamlit génère logs automatiquement
~/.streamlit/logs/
```

---

##  Performances

### Métriques actuelles au 19/01/2026

- **Base de données** : 515 artistes, 517 métriques
- **Temps chargement** : < 2 secondes
- **Cache TTL** : 5 minutes
- **Prédictions** : ~0.5 seconde (génération)
- **Alertes** : ~2 secondes (génération)

### Optimisations

```python
# Cache Streamlit
@st.cache_data(ttl=300)
def load_data():
    ...

# Index DB
CREATE INDEX idx_metriques_date ON metriques_historique(date_collecte);
CREATE INDEX idx_alertes_vu ON alertes(vu);

# Filtres précoces
filtered_df = latest_metrics_df.query('score_potentiel >= 50')
```

---

## Sécurité

### Authentification

- **Username** : `admin`
- **Password** : `admin123`


### Données sensibles

- Pas de données personnelles utilisateurs
- Données artistes publiques (APIs)
- Base SQLite locale (dev)
- PostgreSQL sécurisé (prod)

### Bonnes pratiques

```python
# Ne JAMAIS commit
.env
.streamlit/secrets.toml
*.db (si contient données sensibles)


```

### Tests d'intégration

```bash
# Vérifier pipeline complet
python filtrer_csv_emergents.py
python import_data.py
python diagnostic_base.py
python ml_prediction.py
python generer_alertes.py
streamlit run app/streamlit.py
```

---

## Support

**Développeur** : Jenny Benmouhoub 
**Projet** : Wild Code School - Projet Final  
**Contact** : [GitHub]

**Ressources** :
- [Documentation Streamlit](https://docs.streamlit.io)
- [Scikit-learn](https://scikit-learn.org)
- [Plotly](https://plotly.com/python/)

---

### Version 1.0.0 (Janvier 2026)
-  Application Streamlit complète
-  Authentification fonctionnelle
-  8 pages/onglets
-  Prédictions ML
-  Design responsive


*Dernière mise à jour : 19 janvier 2026*