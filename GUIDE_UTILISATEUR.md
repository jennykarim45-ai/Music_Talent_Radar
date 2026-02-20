# 📘 GUIDE UTILISATEUR - MUSIC TALENT RADAR

## 🎵 Introduction

**Music Talent Radar** est une plateforme d'analyse et de détection de talents musicaux émergents développée pour **JEK2 Records**. Cet outil permet d'identifier les artistes à fort potentiel avant leur percée médiatique en analysant leurs données Spotify et Deezer avec un modèle de Machine Learning à **92.4% de précision**.

**URL du site :** https://music-talent-radar.streamlit.app/

---

## 🚀 Démarrage Rapide

### 1. Connexion à l'application

1. **Ouvrez votre navigateur** et accédez à l'application
2. **Page de connexion** s'affiche automatiquement
3. **Saisissez vos identifiants** :
   - **Nom d'utilisateur** : `admin`
   - **Mot de passe** : `admin123`
4. **Cliquez** sur "Se connecter"

---

## 🧭 Découverte de l'Interface

### Barre latérale (Sidebar)

**Située à gauche**, elle contient :
- **Logo JEK2 Records**
- **Filtres de recherche** :
  - 🌐 **Source** : Spotify, Deezer ou Tous
  - 🎵 **Genre Musical** : Pop, Rap, Jazz, Rock, Afrobeat, etc.
  - 👥 **Nombre de fans** : Micro, Petit, Moyen, Large (de 1k à 35K)
  - ⭐ **Score minimum** : Curseur de 0 à 100

### Onglets Principaux

L'application comporte **8 onglets** :

1. **🏠 VUE D'ENSEMBLE** - Statistiques globales
2. **🏆 LES TOP** - Classements des meilleurs artistes
3. **🎤 LES ARTISTES** - Catalogue complet avec recherche
4. **📈 ÉVOLUTION** - Suivi temporel détaillé
5. **🔔 ALERTES** - Notifications importantes
6. **🔮 PRÉDICTIONS** - Modèle d'Intelligence Artificielle (Random Forest 92.4%)
7. **ℹ️ À PROPOS** - Présentation du label, de l'application et de sa créatrice
8. **👤 MON PROFIL** - Gestion de vos artistes favoris

---

## 📊 Guide par Onglet

### 🏠 VUE D'ENSEMBLE

**Objectif :** Vision panoramique de votre base de talents

**Métriques affichées :**
- 🎤 **Nombre total d'artistes** suivis (~300+)
- 🟢 **Artistes Spotify** dans la base
- 🔵 **Artistes Deezer** dans la base
- 🔔 **Alertes actives** non lues

**Graphiques disponibles :**
- **Distribution des scores** : Histogramme montrant la répartition des scores de potentiel (0-100)
- **Répartition par genre** : Camembert des genres musicaux (Rap, Pop, Afrobeat, etc.)
- **Top 5 Spotify** : Barres horizontales des meilleurs scores
- **Top 5 Deezer** : Barres horizontales des meilleurs scores

**Utilisation :**
1. Appliquez vos filtres dans la sidebar
2. Observez les tendances générales
3. Identifiez les genres dominants
4. Repérez les plateformes les plus prometteuses

---

### 🏆 LES TOP

**Objectif :** Explorer les artistes les plus performants

**Sections disponibles :**

#### 🏆 Top 30 Meilleurs Scores
- **Graphique en barres** horizontales
- **Tri automatique** par score décroissant
- **Code couleur** : gradient du bleu au rose selon le score
- **Information affichée** : Nom + Score de potentiel (calculé sur 4 critères : Audience 40%, Engagement 30%, Récurrence 20%, Influence 10%)

#### 📈 Top 5 Meilleures Évolutions
- Artistes ayant connu la **plus forte progression**
- Calcul automatique du **% de croissance** entre première et dernière collecte
- Identification des **talents en pleine ascension**

#### 🌐 Répartition Plateforme (Top 50)
- **Camembert** Spotify vs Deezer
- Visualisation de la **dominance** d'une plateforme
- **Note :** Spotify représente ~87% des artistes (300+) vs Deezer ~13% (44)

#### 👥 Distribution Followers (Top 50)
- **Histogramme** de distribution
- Identification de la zone de followers la plus représentée (100-40,000)

**Comment l'utiliser :**
1. Consultez le **Top 30** pour repérer les talents
2. Vérifiez les **évolutions** pour identifier les dynamiques positives
3. Analysez la **répartition** pour comprendre les tendances

---

### 🎤 LES ARTISTES

**Objectif :** Parcourir et sélectionner des artistes

**Fonctionnalités :**

#### Tri et Filtres
- **Trier par** : Score ou Followers/Fans
- **Ordre** : Croissant ou Décroissant
- **Filtres sidebar** : S'appliquent automatiquement

#### Affichage
- **Grille de 5 colonnes**
- **50 artistes par page**
- **Photo de profil** (ou icône 🎵 si indisponible)
- **Informations** : Nom, Plateforme, Genre, Score, Followers

#### Actions disponibles
- ☑️ **Case à cocher** : Marquer comme intéressé
- 🎵 **Bouton Écouter** : Ouvrir sur Spotify/Deezer
- **Pagination** : Naviguez entre les pages (flèches ← →)

#### Workflow de sélection
1. **Parcourez** les artistes
2. **Cochez** ceux qui vous intéressent
3. **Cliquez** sur "VALIDER MES SELECTIONS"
4. Les artistes sont ajoutés à **Mon Profil**

**💡 Astuce :** Utilisez les filtres pour affiner votre recherche (ex: Rap-HipHop-RnB + Score >60 + Spotify uniquement)

---

### 📈 ÉVOLUTION

**Objectif :** Analyser la trajectoire d'un artiste

**Sélection de l'artiste :**
- Menu déroulant avec tous les artistes disponibles
- Filtré selon vos critères sidebar

**Informations affichées :**

#### En-tête
- **Photo de profil**
- **Nom de l'artiste**
- **Genre musical**
- **Plateforme** (Spotify/Deezer)
- 🎵 **Bouton Écouter** : Lien direct vers l'artiste

#### Métriques clés
- 👥 **Followers/Fans actuels**
- ⭐ **Score de potentiel actuel** (sur 100)
- 📈 **Croissance** depuis la première collecte (en %)

**💡 Interprétation du score :**
- **80-100** : Talent exceptionnel, forte croissance
- **60-79** : Potentiel solide, à surveiller
- **40-59** : Émergent, suivi recommandé
- **0-39** : Début de carrière, patience requise

#### Graphiques temporels
- **Évolution des Followers/Fans** : Courbe temporelle montrant la croissance
- **Évolution du Score** : Courbe temporelle du score de potentiel
- **Période couverte** : Depuis le début du suivi (données quotidiennes via GitHub Actions)

#### Artistes Similaires
- **5 recommandations** basées sur un algorithme KNN (K-Nearest Neighbors)
- **Critères de similarité** :
  - Même genre musical
  - Même plateforme
  - Proximité des métriques (followers, score, popularité)
- **Distance cosinus** : Mesure la similarité de profil (pas la taille absolue)
- **Actions** : Écouter, Voir infos

#### Marquer comme intéressé
1. Cochez "Marquer comme intéressé"
2. Cliquez sur **VALIDER**
3. L'artiste est ajouté à **Mon Profil**

---

### 🔔 ALERTES

**Objectif :** Recevoir des notifications importantes

**Types d'alertes :**
- 🚀 **Croissance Followers** : +20% ou plus entre 2 collectes
- ⚠️ **Baisse Followers** : -15% ou moins entre 2 collectes
- ⭐ **Progression Score** : +10 points ou plus
- 🔥 **TRENDING** : Score >80 (artiste à très fort potentiel)

**Affichage :**
- **Cartes colorées** par type d'alerte
- **Nom de l'artiste** concerné
- **Message descriptif** (ex: "Croissance de 25.3% sur Spotify ! Passe de 5,240 à 6,566 followers.")
- **Date de l'alerte**

**Statut :**
- Seules les alertes **non lues** sont affichées
- Message "✅ Aucune alerte" si tout est OK

**💡 Astuce :** Les alertes sont générées automatiquement chaque jour par le système. Consultez cet onglet régulièrement pour ne rien manquer !

---

### 🔮 PRÉDICTIONS (Intelligence Artificielle)

**Objectif :** Identifier les futurs talents avec le Machine Learning

**Fonctionnement du modèle :**

#### Algorithme
- **Type** : Random Forest (ensemble de 100 arbres de décision)
- **Précision** : **92.4%** (validation croisée 5-fold)
- **Optimisation** : GridSearchCV pour trouver les meilleurs hyperparamètres
- **Équilibrage** : SMOTE (Synthetic Minority Over-sampling) pour gérer le déséquilibre des classes

#### Features utilisées (13 au total)
Le modèle analyse 13 caractéristiques dérivées :

**RAW (5) :**
- Nombre de followers actuels
- Popularité sur la plateforme (0-100)
- Nombre d'albums total
- Nombre de releases récentes (2 dernières années)
- Jours d'observation

**RATIOS (2) :**
- Ratio followers/albums (engagement par album)
- Ratio releases/albums (productivité)

**DYNAMIQUE (2) :**
- **Vélocité** : Vitesse de croissance quotidienne (feature la plus importante : 37.6%)
- **Momentum** : Accélération (détecte si l'artiste "décolle")

**ENGAGEMENT (3) :**
- Engagement global
- Activité récente
- Taille relative dans sa catégorie

**MATURITÉ (1) :**
- Albums par an (productivité long terme)

#### Critères de prédiction
Le modèle prédit qu'un artiste va "exploser" si :
- **Croissance >50% sur 90 jours** (normalisé)
- **OU** combinaison de vélocité élevée + momentum positif + activité récente forte

**Probabilités retournées :** 4.6% - 90.9% (calibrées avec CalibratedClassifierCV)

#### Affichage

**Graphique principal :**
- **Top 10 artistes** à plus fort potentiel d'explosion
- **Barres horizontales** avec probabilité en %
- **Code couleur** : gradient du bleu au rose

**Grille d'artistes :**
- **Photos** des artistes
- **Nom** (tronqué si trop long)
- **Probabilité** de succès (en %)
- 📈 **Bouton "Voir évolution"** : Affiche directement les graphiques dans l'onglet Évolution

**Statistiques :**
- 🌟 **Stars Prédites** (>50%) : Nombre d'artistes
- 📊 **Probabilité Moyenne** : Score moyen (~18.4%)
- ⚡ **Haut Potentiel** (>30%) : Nombre d'artistes

**Comment l'utiliser :**
1. Le modèle **filtre automatiquement** les artistes >80k followers (déjà connus)
2. Consultez le **Top 10** prédit
3. Cliquez sur **"Voir évolution"** pour analyser
4. Identifiez les **opportunités** de signature

**💡 Interprétation des probabilités :**
- **>70%** : Très fort potentiel de percée (signer rapidement !)
- **50-70%** : Potentiel confirmé (suivre de près)
- **30-50%** : À surveiller (opportunité intéressante)
- **<30%** : Croissance lente attendue (patience)

**⚠️ Note importante :** Les prédictions sont basées sur des données historiques et des patterns identifiés. Elles constituent une **aide à la décision**, pas une garantie de succès. Le modèle a une précision de 92.4% sur les données d'entraînement.

---

### ℹ️ À PROPOS DE JEK2

**Objectif :** Découvrir JEK2 Records et l'auteure du projet

**Contenu :**

#### Présentation JEK2 Records
- **Mission** : Découvrir les talents avant leur percée grâce à la data
- **Méthode** : Analyse quotidienne de 300+ artistes avec algorithmes ML
- **Genres couverts** : Pop, Rap, Afrobeat, Jazz, Rock, Indie, Electro, Reggaeton
- **Localisation** : France

#### Music Talent Radar
- **Description** de l'outil
- **Objectif** : Analyse de milliers d'artistes émergents
- **Technologie** : 
  - APIs Spotify & Deezer
  - Base de données SQLite
  - Machine Learning (Random Forest 92.4%)
  - Automatisation GitHub Actions (collecte quotidienne)
  - Interface Streamlit

#### Système de Scoring
Tableau explicatif des **4 critères** du score (0-100) :

| Critère | Poids | Description |
|---------|-------|-------------|
| **Audience** | 40% | Taille de la communauté (100-40,000 fans) |
| **Engagement** | 30% | Qualité relation avec fans (popularité/ratio fans-albums) |
| **Récurrence** | 20% | Régularité sorties (releases 2 dernières années) |
| **Influence** | 10% | Présence multi-plateforme (Spotify + Deezer) |

**Exemple de calcul :**
- Artiste avec 25,000 fans, popularity 55, 8 releases récentes, sur 2 plateformes
- **Score = 74.2/100** (Audience: 24.9 + Engagement: 23.3 + Récurrence: 16.0 + Influence: 10)

#### L'Auteure
- **Photo de profil**
- **Bio** : Jenny Benmouhoub - Data Analyst & Musicienne
- **Parcours** : Reconversion professionnelle à la Wild Code School
- **Compétences** : Python, SQL, Machine Learning, Streamlit, Git/GitHub

#### Compositions musicales
- **Lecteur audio** intégré
- Écoute de compositions originales au piano
- Exemple : "Ma Famille" (format .m4a)

---

### 👤 MON PROFIL

**Objectif :** Gérer vos artistes d'intérêt

**Informations du compte :**
- 👤 **Nom d'utilisateur** connecté (admin)
- 🚪 **Bouton déconnexion**

**Mes Artistes Intéressés :**

#### Statistiques
- ⭐ **Nombre total** d'artistes suivis
- 🟢 **Nombre sur Spotify**
- 🔵 **Nombre sur Deezer**

#### Liste des artistes
Pour chaque artiste :
- **Case cochée** (confirmation visuelle)
- **Photo de profil**
- **Nom complet**
- **Informations** : Plateforme, Genre
- **Métriques** : Score, Followers/Fans
- **Bouton "Voir évolution"** : Redirection vers l'onglet Évolution
- 🗑️ **Bouton "Retirer"** : Suppression de la liste

#### Workflow
1. Ajoutez des artistes depuis **Les Artistes** ou **Évolution**
2. Retrouvez-les tous ici dans **Mon Profil**
3. Suivez leur évolution d'un clic
4. Gérez votre portefeuille de talents

---

##  Cas d'Usage Pratiques

### Scénario 1 : Découvrir de nouveaux talents Rap français

1. **Sidebar** : Sélectionnez "Rap-HipHop-RnB" dans Genre
2. **Score minimum** : Réglez sur 60 pour filtrer les meilleurs
3. **Onglet Top** : Consultez le Top 30
4. **Onglet Artistes** : Parcourez la grille
5. **Cochez** 3-5 artistes intéressants
6. **Validez** la sélection
7. **Mon Profil** : Retrouvez votre sélection

---

### Scénario 2 : Analyser un artiste en détail

1. **Onglet Évolution** : Sélectionnez l'artiste dans le menu déroulant
2. **Observez** les graphiques temporels (followers + score)
3. **Vérifiez** la croissance (%) depuis le début
4. **Consultez** les artistes similaires (algorithme KNN)
5. **Cliquez** sur 🎵 pour écouter sur Spotify/Deezer
6. **Marquez** comme intéressé si pertinent

---

### Scénario 3 : Identifier les futures stars avec l'IA

1. **Onglet Prédictions** : Consultez le Top 10 ML (Random Forest 92.4%)
2. **Observez** les probabilités d'explosion (%)
3. **Analysez** la distribution :
   - >70% : Signer rapidement
   - 50-70% : Suivre de très près
   - 30-50% : Opportunité intéressante
4. **Cliquez** sur "Voir évolution" d'un artiste à haute probabilité
5. **Analysez** les courbes temporelles (vélocité, momentum)
6. **Décidez** : signature ou suivi prolongé

---

### Scénario 4 : Filtrer par taille d'audience

1. **Sidebar** : Sélectionnez "Moyen (10k-30k)" dans Nombre de fans
2. **Score minimum** : Mettez à 50
3. **Plateforme** : Spotify uniquement
4. **Onglet Top** : Visualisez les meilleurs
5. **Onglet Artistes** : Parcourez la sélection filtrée (pagination 50/page)

---

### Scénario 5 : Suivre les alertes quotidiennes

1. **Onglet Alertes** : Consultez les notifications
2. **Identifiez** les croissances rapides (🚀 +20%)
3. **Repérez** les artistes TRENDING (🔥 score >80)
4. **Cliquez** sur "Écouter" pour vérifier
5. **Ajoutez** à Mon Profil si intéressant

---

## Conseils et Bonnes Pratiques

### Pour les A&R (Artists & Repertoire)

1. **Utilisez les filtres** pour cibler votre recherche
2. **Consultez régulièrement** l'onglet Alertes (nouvelles notifications quotidiennes)
3. **Analysez les évolutions** avant toute décision (graphiques temporels)
4. **Comparez** les artistes similaires (KNN)
5. **Suivez** vos favoris dans Mon Profil
6. **Exploitez les prédictions ML** pour anticiper les succès (92.4% précision)

### Pour les Managers

1. **Vue d'ensemble** : Suivez les tendances globales (distribution scores, genres)
2. **Top 30** : Identifiez les opportunités (meilleurs scores)
3. **Prédictions ML** : Anticipez les succès futurs (probabilités d'explosion)
4. **Statistiques** : Prenez des décisions data-driven (300+ artistes analysés)

### Interprétation des scores

- **Score 80-100** : ⭐⭐⭐ Talent exceptionnel, forte croissance
- **Score 60-79** : ⭐⭐ Potentiel solide, à surveiller
- **Score 40-59** : ⭐ Émergent, suivi recommandé
- **Score 0-39** : Début de carrière, patience requise

### Interprétation des prédictions ML

- **Probabilité >70%** : 🔥 Très fort potentiel de percée (signer rapidement !)
- **Probabilité 50-70%** : ✅ Potentiel confirmé (suivre de très près)
- **Probabilité 30-50%** : 👀 À surveiller (opportunité intéressante)
- **Probabilité <30%** : ⏳ Croissance lente attendue (patience)

**💡 Astuce avancée :** Combinez score élevé (>70) + prédiction ML élevée (>60%) pour identifier les **pépites à signer immédiatement** !

---

## Sécurité et Confidentialité

### Gestion des accès

- **Connexion obligatoire** pour accéder à l'application
- **Session** : Expire après inactivité prolongée
- **Déconnexion** : Disponible dans Mon Profil

### Protection des données

- **Données publiques** : Sources Spotify/Deezer API uniquement
- **Pas de données personnelles** sensibles collectées
- **Conformité** : Respect des CGU Spotify/Deezer
- **Blacklist** : 50+ artistes exclus pour éviter données inappropriées

---

##  Support et Assistance

### En cas de problème

1. **Rafraîchissez** la page (F5 ou Ctrl+R)
2. **Videz le cache** du navigateur (Ctrl+Shift+Delete)
3. **Vérifiez** vos filtres sidebar (remettre à "Tous")
4. **Déconnectez/Reconnectez-vous**
5. **Attendez 10 minutes** (cache Streamlit : 10 min)

### Contact

Pour toute question ou bug rencontré :
-  Email : jennybenmouhoub45@gmail.com
-  GitHub Issues : https://github.com/jennykarim45-ai

---

## Ressources Complémentaires

### Documentation

- **Documentation technique** : Pour les développeurs (architecture, ML, APIs)
- **Code source** : GitHub (https://github.com/jennykarim45-ai)

### Données

- **Source Spotify** : 300+ artistes (50 mots-clés × 7 genres)
- **Source Deezer** : 44 artistes (13 playlists - bientôt 50)
- **Taux de matching** : 75% (normalisation + Levenshtein)
- **Collecte quotidienne** : 3h du matin (GitHub Actions)

### Statistiques ML

- **Modèle** : Random Forest
- **Précision** : 92.4% (validation croisée)
- **Features** : 13 caractéristiques dérivées
- **Top 3 features importantes** :
  1. Vélocité (37.6%)
  2. Ratio releases/albums (20.5%)
  3. Activité récente (18.4%)

---

##  Conclusion

**Music Talent Radar** est un outil puissant pour identifier les talents musicaux émergents avant leur percée médiatique. En combinant :

- **Données objectives** (Spotify/Deezer - 300+ artistes)
- **Analyse temporelle** (évolutions quotidiennes)
- **Machine Learning** (Random Forest 92.4% précision)
- **Interface intuitive** (Streamlit - 8 onglets)
- **Automatisation** (GitHub Actions - collecte quotidienne)

Vous disposez d'un **avantage compétitif** pour **découvrir les stars de demain** ! 

**Bonne découverte musicale !** 🎵

---

*Guide Utilisateur Music Talent Radar - JEK2 Records - Février 2026*  
*Auteur : Jenny - Data Analyst & Parolière/interprète*  
