#!/usr/bin/env python3
"""
Script pour générer automatiquement des alertes
Détecte les artistes avec croissance > 5% et crée des alertes
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'data/music_talent_radar_v2.db'
SEUIL_CROISSANCE = 5.0  # 5% minimum pour déclencher une alerte

print(" GÉNÉRATION DES ALERTES AUTOMATIQUES\n")
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

for artiste in metriques_df['nom_artiste'].dropna().unique():
    artist_data = metriques_df[metriques_df['nom_artiste'] == artiste].copy()
    
    if len(artist_data) < 2:
        continue  # Pas assez de données pour calculer une évolution
    
    # Trier par date
    artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
    artist_data = artist_data.sort_values('date_collecte')
    
    # Calculer evolution entre dernière et avant-dernière collecte
    derniere = artist_data.iloc[-1]
    avant_derniere = artist_data.iloc[-2]
    
    # Followers
    if 'fans_followers' in derniere and pd.notna(derniere['fans_followers']):
        followers_derniere = derniere['fans_followers']
        followers_avant = avant_derniere.get('fans_followers', 0)
    else:
        followers_derniere = derniere.get('followers', 0) if pd.notna(derniere.get('followers')) else derniere.get('fans', 0)
        followers_avant = avant_derniere.get('followers', 0) if pd.notna(avant_derniere.get('followers')) else avant_derniere.get('fans', 0)
    
    # Calculer croissance
    if followers_avant > 0:
        croissance = ((followers_derniere - followers_avant) / followers_avant) * 100
    else:
        croissance = 0
    
    # Score
    score_derniere = derniere.get('score_potentiel', 0) or derniere.get('score', 0)
    score_avant = avant_derniere.get('score_potentiel', 0) or avant_derniere.get('score', 0)
    
    if score_avant > 0:
        croissance_score = ((score_derniere - score_avant) / score_avant) * 100
    else:
        croissance_score = 0
    
    #  GÉNÉRATION DES ALERTES
    
    # Alerte 1 : Forte croissance followers (> 5%)
    if croissance >= SEUIL_CROISSANCE:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': ' Forte Croissance',
            'message': f"Croissance de {croissance:.1f}% des followers ({int(followers_avant):,} → {int(followers_derniere):,})",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 2 : Baisse importante (< -5%)
    elif croissance <= -SEUIL_CROISSANCE:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': ' Baisse Significative',
            'message': f"Baisse de {abs(croissance):.1f}% des followers ({int(followers_avant):,} → {int(followers_derniere):,})",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 3 : Score en forte hausse (> 10%)
    if croissance_score >= 10:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': ' Score en Hausse',
            'message': f"Score de potentiel en hausse de {croissance_score:.1f}% ({score_avant:.1f} → {score_derniere:.1f})",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vu': 0
        })
        alertes_generees += 1
    
    # Alerte 4 : Trending (> 15% croissance + score > 60)
    if croissance >= 15 and score_derniere >= 60:
        alertes_a_inserer.append({
            'nom_artiste': artiste,
            'type_alerte': ' TRENDING',
            'message': f"Artiste en pleine ascension ! Croissance {croissance:.1f}% avec score {score_derniere:.1f}",
            'date_alerte': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'vu': 0
        })
        alertes_generees += 1

# 4. Supprimer les anciennes alertes non lues (optionnel)
print(f"\n Suppression des anciennes alertes")
cursor.execute("DELETE FROM alertes WHERE vu = 0")
conn.commit()
print("Anciennes alertes supprimées")

# 5. Insérer les nouvelles alertes
print(f"\nInsertion de {len(alertes_a_inserer)} nouvelles alertes...")

for alerte in alertes_a_inserer:
    cursor.execute("""
        INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte, vu)
        VALUES (?, ?, ?, ?, ?)
    """, (
        alerte['nom_artiste'],
        alerte['type_alerte'],
        alerte['message'],
        alerte['date_alerte'],
        alerte['vu']
    ))

conn.commit()
print(f"{len(alertes_a_inserer)} alertes insérées")

# 6. Afficher quelques exemples
print(f"\n" + "=" * 60)
print("EXEMPLES D'ALERTES GÉNÉRÉES\n")

alertes_sample = pd.read_sql_query("""
    SELECT nom_artiste, type_alerte, message
    FROM alertes
    WHERE vu = 0
    ORDER BY date_alerte DESC
    LIMIT 10
""", conn)

if len(alertes_sample) > 0:
    for idx, alerte in alertes_sample.iterrows():
        print(f"{alerte['type_alerte']}")
        print(f"  → {alerte['nom_artiste']}: {alerte['message']}\n")
else:
    print("Aucune alerte générée (aucun artiste ne répond aux critères)")

conn.close()

print("=" * 60)
print(f"GÉNÉRATION TERMINÉE")
print(f"\n Statistiques :")
print(f"   - {alertes_generees} alertes générées")
print(f"   - Seuil croissance : {SEUIL_CROISSANCE}%")
print(f"\n Prochaines étapes :")
print(f"   1. Relance Streamlit : streamlit run app/streamlit.py")
print(f"   2. Va dans l'onglet Alertes")
print(f"   3. Consulte les nouvelles alertes !")
