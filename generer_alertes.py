"""
Script pour générer automatiquement des alertes - Avec pourcentages, valeurs avant/après et dates formatées
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'data/music_talent_radar_v2.db'
SEUIL_CROISSANCE = 5.0  # 5% minimum pour déclencher une alerte

print(" GÉNÉRATION DES ALERTES AUTOMATIQUES v2.0\n")
print("=" * 60)

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
metriques_df = pd.read_sql_query("""
    SELECT 
        m.*,
        a.nom as nom_artiste
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    ORDER BY m.date_collecte ASC
""", conn)

print(f"\n {len(metriques_df)} métriques chargées")

# 3. Analyser les évolutions par artiste
alertes_generees = 0
alertes_a_inserer = []

metriques_df = metriques_df.loc[:, ~metriques_df.columns.duplicated()]

for artiste in metriques_df['nom_artiste'].dropna().unique():
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
        followers_apres = derniere['fans_followers']
        followers_avant = avant_derniere.get('fans_followers', 0)
    else:
        followers_apres = derniere.get('followers', 0) if pd.notna(derniere.get('followers')) else derniere.get('fans', 0)
        followers_avant = avant_derniere.get('followers', 0) if pd.notna(avant_derniere.get('followers')) else avant_derniere.get('fans', 0)
    
    # Calculer croissance followers
    if followers_avant > 0:
        pourcentage_followers = ((followers_apres - followers_avant) / followers_avant) * 100
    else:
        pourcentage_followers = 0
    
    # Récupérer scores
    score_apres = derniere.get('score_potentiel', 0) or derniere.get('score', 0)
    score_avant = avant_derniere.get('score_potentiel', 0) or avant_derniere.get('score', 0)
    
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
            'message': f"Croissance de {pourcentage_followers:.1f}% des followers",
            'date_alerte': date_alerte.strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': int(followers_avant),
            'followers_apres': int(followers_apres),
            'pourcentage_followers': round(pourcentage_followers, 2),
            'score_avant': round(score_avant, 2),
            'score_apres': round(score_apres, 2),
            'pourcentage_score': round(pourcentage_score, 2),
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 2 : Baisse importante (< -5%)
    elif pourcentage_followers <= -SEUIL_CROISSANCE:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '⚠️ Baisse Significative',
            'message': f"Baisse de {abs(pourcentage_followers):.1f}% des followers",
            'date_alerte': date_alerte.strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': int(followers_avant),
            'followers_apres': int(followers_apres),
            'pourcentage_followers': round(pourcentage_followers, 2),
            'score_avant': round(score_avant, 2),
            'score_apres': round(score_apres, 2),
            'pourcentage_score': round(pourcentage_score, 2),
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 3 : Score en forte hausse (> 10%)
    if pourcentage_score >= 10:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '⭐ Score en Hausse',
            'message': f"Score en hausse de {pourcentage_score:.1f}%",
            'date_alerte': date_alerte.strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': int(followers_avant),
            'followers_apres': int(followers_apres),
            'pourcentage_followers': round(pourcentage_followers, 2),
            'score_avant': round(score_avant, 2),
            'score_apres': round(score_apres, 2),
            'pourcentage_score': round(pourcentage_score, 2),
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 4 : Score en baisse (< -10%)
    if pourcentage_score <= -10:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '📉 Score en Baisse',
            'message': f"Score en baisse de {abs(pourcentage_score):.1f}%",
            'date_alerte': date_alerte.strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': int(followers_avant),
            'followers_apres': int(followers_apres),
            'pourcentage_followers': round(pourcentage_followers, 2),
            'score_avant': round(score_avant, 2),
            'score_apres': round(score_apres, 2),
            'pourcentage_score': round(pourcentage_score, 2),
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 5 : Trending (> 15% croissance + score > 60)
    if pourcentage_followers >= 15 and score_apres >= 60:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': '🔥 TRENDING',
            'message': f"Artiste en pleine ascension ! {pourcentage_followers:.1f}% de croissance",
            'date_alerte': date_alerte.strftime('%Y-%m-%d %H:%M:%S'),
            'followers_avant': int(followers_avant),
            'followers_apres': int(followers_apres),
            'pourcentage_followers': round(pourcentage_followers, 2),
            'score_avant': round(score_avant, 2),
            'score_apres': round(score_apres, 2),
            'pourcentage_score': round(pourcentage_score, 2),
            'date_formatted': date_formatted,
            'mois_annee': mois_annee,
            'vu': 0
        })
        alertes_generees += 1

# 4. Supprimer les anciennes alertes non lues (optionnel)
print(f"\n  Suppression des anciennes alertes...")
cursor.execute("DELETE FROM alertes WHERE vu = 0")
conn.commit()
print(" Anciennes alertes supprimées")

# 5. Insérer les nouvelles alertes
print(f"\n Insertion de {len(alertes_a_inserer)} nouvelles alertes...")

for alerte in alertes_a_inserer:
    cursor.execute("""
        INSERT INTO alertes (
            nom_artiste, type_alerte, message, date_alerte,
            followers_avant, followers_apres, pourcentage_followers,
            score_avant, score_apres, pourcentage_score,
            date_formatted, mois_annee, vu
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        alerte['nom_artiste'],
        alerte['type_alerte'],
        alerte['message'],
        alerte['date_alerte'],
        alerte['followers_avant'],
        alerte['followers_apres'],
        alerte['pourcentage_followers'],
        alerte['score_avant'],
        alerte['score_apres'],
        alerte['pourcentage_score'],
        alerte['date_formatted'],
        alerte['mois_annee'],
        alerte['vu']
    ))

conn.commit()
print(f" {len(alertes_a_inserer)} alertes insérées")

# 6. Afficher exemples avec détails
print(f"\n" + "=" * 60)
print(" EXEMPLES D'ALERTES GÉNÉRÉES\n")

alertes_sample = pd.read_sql_query("""
    SELECT 
        type_alerte, nom_artiste, message, date_formatted,
        followers_avant, followers_apres, pourcentage_followers,
        score_avant, score_apres, pourcentage_score
    FROM alertes
    WHERE vu = 0
    ORDER BY ABS(pourcentage_followers) DESC
    LIMIT 10
""", conn)

if len(alertes_sample) > 0:
    for idx, alerte in alertes_sample.iterrows():
        print(f"{alerte['type_alerte']}")
        print(f"  🎤 Artiste: {alerte['nom_artiste']}")
        print(f"  📅 Date: {alerte['date_formatted']}")
        print(f"  👥 Followers: {alerte['followers_avant']:,} → {alerte['followers_apres']:,} ({alerte['pourcentage_followers']:+.1f}%)")
        print(f"  ⭐ Score: {alerte['score_avant']:.1f} → {alerte['score_apres']:.1f} ({alerte['pourcentage_score']:+.1f}%)")
        print()
else:
    print("Aucune alerte générée (aucun artiste ne répond aux critères)")

conn.close()


print(f" GÉNÉRATION TERMINÉE")
