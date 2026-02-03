#!/usr/bin/env python3
"""
Script de diagnostic pour vérifier pourquoi les alertes ne se génèrent pas
"""

import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = 'data/music_talent_radar_v2.db'

print("🔍 DIAGNOSTIC : Pourquoi pas d'alertes ?\n")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)

# 1. Vérifier le nombre total de métriques
metriques_count = pd.read_sql_query("SELECT COUNT(*) as total FROM metriques_historique", conn).iloc[0]['total']
print(f"\n📊 Total de lignes dans metriques_historique : {metriques_count}")

# 2. Vérifier les dates de collecte
print("\n📅 Dates de collecte disponibles :")
dates = pd.read_sql_query("""
    SELECT DISTINCT date_collecte, COUNT(*) as nb_artistes
    FROM metriques_historique  
    GROUP BY date_collecte
    ORDER BY date_collecte DESC
    LIMIT 10
""", conn)
print(dates.to_string(index=False))

# 3. Vérifier combien d'artistes ont plusieurs collectes
print("\n🎤 Artistes avec plusieurs collectes (nécessaire pour les alertes) :")
artistes_multi = pd.read_sql_query("""
    SELECT 
        a.nom as nom_artiste,
        COUNT(DISTINCT m.date_collecte) as nb_collectes,
        MIN(m.date_collecte) as premiere_collecte,
        MAX(m.date_collecte) as derniere_collecte
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    WHERE a.nom IS NOT NULL
    GROUP BY a.nom
    HAVING nb_collectes >= 2
    ORDER BY nb_collectes DESC
    LIMIT 15
""", conn)

if len(artistes_multi) == 0:
    print("❌ AUCUN ARTISTE n'a 2+ collectes !")
    print("\n💡 PROBLÈME IDENTIFIÉ : Les alertes nécessitent au moins 2 collectes par artiste")
    print("   pour calculer les évolutions.")
else:
    print(f"✅ {len(artistes_multi)} artistes ont 2+ collectes")
    print(artistes_multi.to_string(index=False))

# 4. Vérifier un exemple concret d'évolution
if len(artistes_multi) > 0:
    artiste_test = artistes_multi.iloc[0]['nom_artiste']
    print(f"\n📈 Exemple d'évolution pour '{artiste_test}' :")
    
    evolution = pd.read_sql_query(f"""
        SELECT 
            date_collecte,
            plateforme,
            fans_followers,
            score_potentiel
        FROM metriques_historique m
        LEFT JOIN artistes a ON m.id_unique = a.id_unique
        WHERE a.nom = '{artiste_test}'
        ORDER BY date_collecte DESC
        LIMIT 5
    """, conn)
    
    print(evolution.to_string(index=False))
    
    # Calculer la variation
    if len(evolution) >= 2:
        derniere = evolution.iloc[0]
        avant_derniere = evolution.iloc[1]
        
        followers_derniere = derniere['fans_followers'] or 0
        followers_avant = avant_derniere['fans_followers'] or 0
        
        if followers_avant > 0:
            variation = ((followers_derniere - followers_avant) / followers_avant) * 100
            print(f"\n💡 Variation : {followers_avant:,} → {followers_derniere:,} = {variation:+.1f}%")
            
            if abs(variation) >= 5:
                print(f"✅ Cette variation déclencherait une alerte !")
            else:
                print(f"❌ Variation trop faible (< 5%) pour déclencher une alerte")

# 5. Vérifier la structure de la table metriques_historique
print("\n🗂️  Colonnes de la table metriques_historique :")
colonnes = pd.read_sql_query("PRAGMA table_info(metriques_historique)", conn)
print(colonnes[['name', 'type']].to_string(index=False))

# 6. Vérifier si les artistes dans artist_urls.csv sont bien suivis
try:
    artist_urls = pd.read_csv('artist_urls.csv')
    artistes_urls_count = len(artist_urls)
    print(f"\n📋 Artistes dans artist_urls.csv : {artistes_urls_count}")
    
    # Comparer avec les artistes dans la base
    artistes_db = pd.read_sql_query("SELECT COUNT(DISTINCT id_unique) as total FROM artistes", conn).iloc[0]['total']
    print(f"📊 Artistes dans la base de données : {artistes_db}")
    
    if artistes_urls_count != artistes_db:
        print(f"⚠️  ATTENTION : Décalage entre artist_urls.csv ({artistes_urls_count}) et la base ({artistes_db})")
except FileNotFoundError:
    print("\n⚠️  Fichier artist_urls.csv introuvable")

# 7. Conclusion et recommandations
print("\n" + "=" * 70)
print("📝 DIAGNOSTIC :")
print("=" * 70)

if len(artistes_multi) == 0:
    print("""
❌ PROBLÈME PRINCIPAL : Pas assez de données historiques

CAUSES POSSIBLES :
1. Les collectes automatiques ne tournent pas vraiment
2. Les collectes ne suivent pas les mêmes artistes à chaque fois
3. music_talent_radar.py ne sauvegarde pas dans metriques_historique

SOLUTIONS :
1. Vérifier les logs GitHub Actions pour voir si les collectes tournent
2. Lancer manuellement : python collecte1.py && python music_talent_radar.py --all
3. Attendre 2-3 jours que l'historique se construise
4. Vérifier que artist_urls.csv contient toujours les mêmes artistes
""")
else:
    print(f"""
✅ DONNÉES OK : {len(artistes_multi)} artistes avec historique

PROCHAINES ÉTAPES :
1. Corriger l'erreur dans generer_alertes.py (ligne 60)
2. Relancer : python generer_alertes.py
3. Les alertes devraient apparaître !
""")

conn.close()
