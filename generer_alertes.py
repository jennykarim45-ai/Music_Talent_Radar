
"""
Script pour générer automatiquement des alertes
Détecte les artistes avec croissance > 5% et crée des alertes
Version corrigée avec gestion des colonnes dupliquées
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'data/music_talent_radar_v2.db'
SEUIL_CROISSANCE = 5.0  # 5% minimum pour déclencher une alerte

print(" GÉNÉRATION DES ALERTES AUTOMATIQUES v2.0")


# Connexion à la base
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Vérifier si table alertes existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alertes'")
if not cursor.fetchone():
    print(" Création de la table alertes...")
    cursor.execute("""
        CREATE TABLE alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_artiste TEXT,
            type_alerte TEXT,
            message TEXT,
            date_alerte TEXT,
            followers_avant INTEGER,
            followers_apres INTEGER,
            pourcentage_followers REAL,
            score_avant REAL,
            score_apres REAL,
            pourcentage_score REAL,
            date_formatted TEXT,
            mois_annee TEXT,
            vu BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    print(" Table créée")

# 2. Charger toutes les métriques historiques
# CORRECTION : Utiliser DISTINCT pour éviter les doublons de colonnes
metriques_df = pd.read_sql_query("""
    SELECT 
        m.id,
        m.id_unique,
        a.nom as nom_artiste,
        m.source,
        m.plateforme,
        m.genre,
        m.fans_followers,
        m.followers,
        m.fans,
        m.popularity,
        m.score_potentiel,
        m.score,
        m.categorie,
        m.date_collecte,
        m.url,
        m.image_url
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    ORDER BY m.date_collecte ASC
""", conn)

print(f"\n {len(metriques_df)} métriques chargées")

# DEBUG : Vérifier les colonnes
print(f" Colonnes : {list(metriques_df.columns)}")

# CORRECTION : Supprimer colonnes dupliquées si elles existent
metriques_df = metriques_df.loc[:, ~metriques_df.columns.duplicated()]

# DEBUG : Compter les collectes par artiste
artistes_uniques = metriques_df['nom_artiste'].dropna().unique()
print(f"\n🎤 {len(artistes_uniques)} artistes uniques")

collectes_par_artiste = metriques_df.groupby('nom_artiste').size()
artistes_avec_2plus = (collectes_par_artiste >= 2).sum()
print(f"{artistes_avec_2plus} artistes avec 2+ collectes (éligibles pour alertes)")

if artistes_avec_2plus == 0:
    print("\n AUCUN ARTISTE N'A 2+ COLLECTES !")
    print(" Solution : Relance music_talent_radar.py pour créer une 2e collecte")
    conn.close()
    exit(0)

# 3. Analyser les évolutions par artiste
alertes_generees = 0
alertes_a_inserer = []

for artiste in artistes_uniques:
    artist_data = metriques_df[metriques_df['nom_artiste'] == artiste].copy()
    
    if len(artist_data) < 2:
        continue  # Pas assez de données
    
    # Trier par date
    artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
    artist_data = artist_data.sort_values('date_collecte')
    
    # Dernière et avant-dernière collecte
    derniere = artist_data.iloc[-1]
    avant_derniere = artist_data.iloc[-2]
    
    # Récupérer followers
    if 'fans_followers' in derniere and pd.notna(derniere['fans_followers']):
        followers_apres = int(derniere['fans_followers'])
        followers_avant = int(avant_derniere.get('fans_followers', 0))
    else:
        followers_apres = int(derniere.get('followers', 0) if pd.notna(derniere.get('followers')) else derniere.get('fans', 0))
        followers_avant = int(avant_derniere.get('followers', 0) if pd.notna(avant_derniere.get('followers')) else avant_derniere.get('fans', 0))
    
    # Calculer croissance followers
    if followers_avant > 0:
        pourcentage_followers = ((followers_apres - followers_avant) / followers_avant) * 100
    else:
        pourcentage_followers = 0
    
    # Récupérer scores
    score_apres = float(derniere.get('score_potentiel', 0) or derniere.get('score', 0) or 0)
    score_avant = float(avant_derniere.get('score_potentiel', 0) or avant_derniere.get('score', 0) or 0)
    
    # Calculer croissance score
    if score_avant > 0:
        pourcentage_score = ((score_apres - score_avant) / score_avant) * 100
    else:
        pourcentage_score = 0
    
    # Date formatée
    date_alerte = datetime.now()
    date_formatted = date_alerte.strftime('%d/%m/%Y')
    mois_annee = date_alerte.strftime('%m/%Y')
    
    #  GÉNÉRATION DES ALERTES
    
    # Alerte 1 : Forte croissance followers (> 5%)
    if pourcentage_followers >= SEUIL_CROISSANCE:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '🚀 Forte Croissance',
            'message': f"Croissance de {pourcentage_followers:.1f}% des followers ({followers_avant:,} → {followers_apres:,})",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': followers_avant,
            'followers_apres': followers_apres,
            'pourcentage_followers': pourcentage_followers,
            'score_avant': score_avant,
            'score_apres': score_apres,
            'pourcentage_score': pourcentage_score,
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
        print(f"🚀 Croissance : {artiste} : +{pourcentage_followers:.1f}%")
    
    # Alerte 2 : Baisse importante (< -5%)
    elif pourcentage_followers <= -SEUIL_CROISSANCE:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '⚠️ Baisse Significative',
            'message': f"Baisse de {abs(pourcentage_followers):.1f}% des followers ({followers_avant:,} → {followers_apres:,})",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': followers_avant,
            'followers_apres': followers_apres,
            'pourcentage_followers': pourcentage_followers,
            'score_avant': score_avant,
            'score_apres': score_apres,
            'pourcentage_score': pourcentage_score,
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
        print(f"⚠️ Baisse : {artiste} : {pourcentage_followers:.1f}%")
    
    # Alerte 3 : Score en hausse (> 10%)
    if pourcentage_score >= 10:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '⭐ Score en Hausse',
            'message': f"Score en hausse de {pourcentage_score:.1f}% ({score_avant:.1f} → {score_apres:.1f})",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': followers_avant,
            'followers_apres': followers_apres,
            'pourcentage_followers': pourcentage_followers,
            'score_avant': score_avant,
            'score_apres': score_apres,
            'pourcentage_score': pourcentage_score,
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
        print(f"⭐ Score hausse : {artiste} : +{pourcentage_score:.1f}%")
    
    # Alerte 4 : TRENDING (croissance + score élevé)
    if pourcentage_followers >= SEUIL_CROISSANCE and score_apres >= 70:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '🔥 TRENDING',
            'message': f"Artiste en pleine ascension ! +{pourcentage_followers:.1f}% followers avec score {score_apres:.1f}",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': followers_avant,
            'followers_apres': followers_apres,
            'pourcentage_followers': pourcentage_followers,
            'score_avant': score_avant,
            'score_apres': score_apres,
            'pourcentage_score': pourcentage_score,
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
        print(f" TRENDING : {artiste} : +{pourcentage_followers:.1f}% et score {score_apres:.1f}")

# 4. Supprimer anciennes alertes
cursor.execute("DELETE FROM alertes")
conn.commit()

# 5. Insérer nouvelles alertes
if alertes_a_inserer:
    alertes_df = pd.DataFrame(alertes_a_inserer)
    alertes_df.to_sql('alertes', conn, if_exists='append', index=False)
    print(f"\n {len(alertes_a_inserer)} alertes générées et insérées dans la base")
else:
    print("\n  Aucune alerte générée (aucune variation significative détectée)")

conn.close()

print(" GÉNÉRATION TERMINÉE")
print("\n Prochaine étape : streamlit run app/streamlit.py")