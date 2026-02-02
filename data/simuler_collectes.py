#!/usr/bin/env python3
"""
Script pour simuler plusieurs collectes en dupliquant les données existantes
avec des dates différentes et des variations aléatoires
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import random

DB_PATH = 'data/music_talent_radar_v2.db'

print("🎲 SIMULATION DE COLLECTES HISTORIQUES")
print("=" * 70)
print("⚠️  Ce script va créer des données simulées pour tester les alertes")
print("=" * 70)

confirmation = input("\n⚠️  Continuer ? (o/n) : ").lower()
if confirmation != 'o':
    print("❌ Annulé")
    exit()

conn = sqlite3.connect(DB_PATH)

# 1. Charger les données existantes
metriques_df = pd.read_sql_query("SELECT * FROM metriques_historique", conn)
print(f"\n📊 {len(metriques_df)} métriques existantes chargées")

# 2. Dates à créer (7 jours avant aujourd'hui)
dates_a_creer = []
for i in range(7, 0, -1):
    date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
    dates_a_creer.append(date)

print(f"\n📅 Création de {len(dates_a_creer)} dates historiques :")
for date in dates_a_creer:
    print(f"   - {date}")

# 3. Pour chaque date, dupliquer les données avec variations
nouvelles_lignes = []

for idx, date in enumerate(dates_a_creer):
    print(f"\n🔄 Génération des données pour {date}...")
    
    for _, row in metriques_df.iterrows():
        # Copier la ligne
        nouvelle_ligne = row.to_dict()
        
        # Changer la date
        nouvelle_ligne['date_collecte'] = date
        
        # Ajouter des variations aléatoires pour simuler des évolutions
        # Plus on est proche d'aujourd'hui, plus les valeurs augmentent
        facteur_croissance = 1 + (idx * 0.02)  # +2% par jour
        variation_aleatoire = random.uniform(0.95, 1.05)  # ±5% aléatoire
        
        # Appliquer aux followers
        if 'fans_followers' in nouvelle_ligne and nouvelle_ligne['fans_followers']:
            nouvelle_ligne['fans_followers'] = int(
                nouvelle_ligne['fans_followers'] * facteur_croissance * variation_aleatoire
            )
        
        if 'followers' in nouvelle_ligne and nouvelle_ligne['followers']:
            nouvelle_ligne['followers'] = int(
                nouvelle_ligne['followers'] * facteur_croissance * variation_aleatoire
            )
        
        if 'fans' in nouvelle_ligne and nouvelle_ligne['fans']:
            nouvelle_ligne['fans'] = int(
                nouvelle_ligne['fans'] * facteur_croissance * variation_aleatoire
            )
        
        # Appliquer aux scores (plus subtil)
        if 'score_potentiel' in nouvelle_ligne and nouvelle_ligne['score_potentiel']:
            nouvelle_ligne['score_potentiel'] = round(
                nouvelle_ligne['score_potentiel'] * (1 + idx * 0.01) * variation_aleatoire,
                2
            )
        
        if 'score' in nouvelle_ligne and nouvelle_ligne['score']:
            nouvelle_ligne['score'] = round(
                nouvelle_ligne['score'] * (1 + idx * 0.01) * variation_aleatoire,
                2
            )
        
        # Ne pas copier l'id (auto-increment)
        del nouvelle_ligne['id']
        
        nouvelles_lignes.append(nouvelle_ligne)

print(f"\n✅ {len(nouvelles_lignes)} nouvelles lignes générées")

# 4. Insérer dans la base
print("\n💾 Insertion dans la base de données...")

nouvelles_df = pd.DataFrame(nouvelles_lignes)
nouvelles_df.to_sql('metriques_historique', conn, if_exists='append', index=False)

print(f"✅ {len(nouvelles_lignes)} lignes insérées")

# 5. Vérification
print("\n📊 Vérification :")
dates_finales = pd.read_sql_query("""
    SELECT DISTINCT date_collecte, COUNT(*) as nb_artistes
    FROM metriques_historique
    GROUP BY date_collecte
    ORDER BY date_collecte
""", conn)

print(dates_finales.to_string(index=False))

# Compter les artistes avec 2+ collectes
artistes_multi = pd.read_sql_query("""
    SELECT COUNT(DISTINCT id_unique) as total
    FROM (
        SELECT id_unique, COUNT(DISTINCT date_collecte) as nb_collectes
        FROM metriques_historique
        GROUP BY id_unique
        HAVING nb_collectes >= 2
    )
""", conn).iloc[0]['total']

print(f"\n✅ {artistes_multi} artistes ont maintenant 2+ collectes")
print("\n🎉 Les alertes devraient maintenant fonctionner !")
print("\n💡 Prochaine étape : python generer_alertes.py")

conn.close()
