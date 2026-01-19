# 📘 MUSIC TALENT RADAR - DOCUMENTATION TECHNIQUE

## 🎯 Vue d'ensemble

**Nom du projet** : Music Talent Radar  
**Client** : JEK2 Records (label fictif)  
**Développeur** : Jenny - Wild Code School  
**Objectif** : Système de détection et d'analyse de talents musicaux émergents avec prédictions ML

---

## 📋 Table des matières

1. [Architecture du système](#architecture)
2. [Technologies utilisées](#technologies)
3. [Structure du projet](#structure)
4. [Base de données](#base-de-données)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Modules principaux](#modules)
8. [API et intégrations](#api)
9. [Machine Learning](#ml)
10. [Déploiement](#déploiement)
11. [Maintenance](#maintenance)

---

## 🏗️ Architecture du système {#architecture}

### Architecture globale

```
┌─────────────────────────────────────────────────────────┐
│                    INTERFACE UTILISATEUR                │
│                   (Streamlit Web App)                   │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                       APPLICATIVE                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ Authentif.   │  │ Visualisation│  │ Prédictions  │  │
│  │ (auth.py)    │  │ (streamlit)  │  │ (ml_pred.py) │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│                       DONNÉES                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ SQLite/      │  │ CSV Files    │  │ APIs         │  │
│  │ PostgreSQL   │  │ (import)     │  │ (Spotify/    │  │
│  │              │  │              │  │  Deezer)     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└────────────────────────────────────────────────────────┘
```

### Flux de données

1. **Collecte** : Import CSV Spotify/Deezer → Base de données
2. **Traitement** : Calcul de scores, nettoyage, agrégation
3. **Analyse** : Modèle ML pour prédictions
4. **Visualisation** : Dashboard Streamlit interactif
5. **Suivi** : Système d'alertes et tracking artistes

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

### Déploiement
- **Streamlit Community Cloud** (hébergement)
- **GitHub** (versioning)

---

## Structure du projet {#structure}

```
MusicTalentRadarAll/
│
├── app/
│   ├── streamlit.py              # Application principale
│   └── auth.py                   # Authentification
│
├── data/
│   ├── music_talent_radar_v2.db  # Base SQLite
│   ├── predictions_ml.csv        # Prédictions générées
│   ├── spotify_artists_*.csv     # Imports Spotify
│   └── deezer_artists_*.csv      # Imports Deezer
│
├── assets/
│   ├── logo.png                  # Logo JEK2
│   ├── back.png                  # Image fond
│   ├── moipiano.png              # Photo auteure
│   └── ma_famille.m4a            # Composition audio
│
├── ml_prediction.py              # Script prédictions ML
├── import_data.py                # Script import CSV
├── filtrer_csv_emergents.py      # Filtrage artistes (permet de modifier le nombre de followers)
├── nettoyer_base.py              # Nettoyage DB
├── diagnostic_base.py            # Diagnostic DB
│
├── requirements.txt              # Dépendances Python
├── .streamlit/
│   └── config.toml              # Configuration Streamlit
│
└── README.md                     # Documentation
```

---

##  Base de données {#base-de-données}

### Schéma SQLite

#### Table `artistes`
```sql
CREATE TABLE artistes (
    id_unique TEXT PRIMARY KEY,
    nom TEXT NOT NULL,
    source TEXT,              -- 'Spotify' ou 'Deezer'
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

#### Table `alertes` (optionnelle)
```sql
CREATE TABLE alertes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom_artiste TEXT,
    type_alerte TEXT,
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
```

---

##  Installation {#installation}

### Prérequis

- Python 3.9 ou supérieur
- pip (gestionnaire de paquets Python)
- Git (optionnel)

### Installation locale

```bash
# 1. Cloner le projet
git clone https://github.com/jennykarim45-ai/MusicTalentRadarv1.git
cd MusicTalentRadarAll

# 2. Créer environnement virtuel
python -m venv venv

# bash
source venv/Scripts/activate

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
psycopg2-binary==2.9.9  
```

---

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

### 1. streamlit.py (Application principale)

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
3. Les Artistes - Grille avec pagination
4. Évolution - Suivi temporel individuel
5. Alertes - Notifications
6. Prédictions - ML Top 10
7. À Propos - Présentation projet
8. Mon Profil - Artistes suivis

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
6. Export predictions_ml.csv
```

**Sortie** :
```csv
nom,proba_star,followers,popularity,score,genre,source
```

---

### 3. import_data.py (Import CSV)

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

### 4. filtrer_csv_emergents.py (Filtrage)

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

### 5. auth.py (Authentification)

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

**Sécurité** :
- Hachage passwords (recommandé en prod)
- Session persistence
- Logout fonctionnel

---

## 🔌 API et intégrations {#api}

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

## 🤖 Machine Learning {#ml}

### Modèle de prédiction

**Type** : Classification binaire (star vs non-star)

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

## 🌐 Déploiement {#déploiement}

### Déploiement Streamlit Cloud

```bash
# 1. Push sur GitHub
git add .
git commit -m "Deploy ready"
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

### Structure pour déploiement

```
MusicTalentRadarAll/
├── app/
│   ├── streamlit.py
│   └── auth.py
├── data/
│   └── music_talent_radar_v2.db
├── assets/
├── requirements.txt
└── .streamlit/
    └── config.toml
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

## 🔧 Maintenance {#maintenance}

### Tâches régulières

#### 1. Mise à jour des données
```bash
# Tous les 7 jours
python filtrer_csv_emergents.py
python import_data.py
python ml_prediction.py
```

#### 2. Nettoyage base
```bash
# Si colonnes dupliquées
python nettoyer_base.py
```

#### 3. Diagnostic
```bash
# En cas de problème
python diagnostic_base.py
```

### Monitoring

**Métriques à surveiller** :
- Nombre d'artistes actifs
- Temps de chargement pages
- Erreurs logs Streamlit
- Taille base de données

**Logs** :
```bash
# Streamlit génère logs automatiquement
~/.streamlit/logs/
```

### Troubleshooting

#### Problème : Colonnes dupliquées
```bash
python nettoyer_base.py
```

#### Problème : Images manquantes
```python
# Vérifier dans streamlit.py (ligne ~420)
# S'assurer du triple merge
```

#### Problème : Prédictions obsolètes
```bash
python ml_prediction.py
```

#### Problème : Artistes connus dans prédictions
```bash
# Vérifier colonne followers dans predictions_ml.csv
# Régénérer si nécessaire
```

---

## 📊 Performances

### Métriques actuelles

- **Base de données** : 515 artistes, 517 métriques
- **Temps chargement** : < 2 secondes
- **Cache TTL** : 5 minutes
- **Prédictions** : ~0.5 seconde (génération)

### Optimisations

```python
# Cache Streamlit
@st.cache_data(ttl=300)
def load_data():
    ...

# Index DB
CREATE INDEX idx_metriques_date ON metriques_historique(date_collecte);

# Filtres précoces
filtered_df = latest_metrics_df.query('score_potentiel >= 50')
```

---

## 🔒 Sécurité

### Authentification

- **Username** : `admin`
- **Password** : `admin123`
- **Session** : Persistante navigateur
- **Recommandation prod** : Hacher passwords avec bcrypt

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

# Toujours dans .gitignore
```

---

## 🧪 Tests

### Tests unitaires (à implémenter)

```python
# test_data_processing.py
def test_get_fan_category():
    assert get_fan_category(5000) == "Micro (1k-10k)"
    assert get_fan_category(50000) == "Moyen (30k-60k)"

def test_normalize_name():
    assert normalize_name("Mouh-Milano") == "mouh milano"
```

### Tests d'intégration

```bash
# Vérifier pipeline complet
python filtrer_csv_emergents.py
python import_data.py
python diagnostic_base.py
python ml_prediction.py
streamlit run app/streamlit.py
```

---

## 📞 Support

**Développeur** : Jenny  
**Projet** : Wild Code School - Projet Final  
**Contact** : [email ou GitHub]

**Ressources** :
- [Documentation Streamlit](https://docs.streamlit.io)
- [Scikit-learn](https://scikit-learn.org)
- [Plotly](https://plotly.com/python/)

---

## 📝 Changelog

### Version 1.0.0 (Janvier 2026)
- ✅ Application Streamlit complète
- ✅ Authentification fonctionnelle
- ✅ 8 pages/onglets
- ✅ Prédictions ML
- ✅ Système d'alertes
- ✅ 515 artistes émergents
- ✅ Design responsive

### À venir (v2.0)
- [ ] Tests unitaires complets
- [ ] CI/CD GitHub Actions
- [ ] PostgreSQL production
- [ ] API REST endpoints
- [ ] Collecte automatisée
- [ ] Dashboard admin

---

## 📜 Licence

Projet éducatif - Wild Code School  
© 2026 Jenny - Tous droits réservés

---

**FIN DE LA DOCUMENTATION TECHNIQUE**
