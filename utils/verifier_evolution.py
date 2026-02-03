#!/usr/bin/env python3
"""
Script pour vérifier les données d'évolution et comprendre pourquoi l'onglet est vide
"""

import sqlite3
import pandas as pd

DB_PATH = 'data/music_talent_radar_v2.db'

print("🔍 DIAGNOSTIC : Pourquoi l'onglet Évolution est vide ?")
print("=" * 70)

conn = sqlite3.connect(DB_PATH)

# 1. Vérifier les dates de collecte
print("\n📅 DATES DE COLLECTE DISPONIBLES :")
dates = pd.read_sql_query("""
    SELECT DISTINCT date_collecte, COUNT(*) as nb_artistes
    FROM metriques_historique
    GROUP BY date_collecte
    ORDER BY date_collecte
""", conn)

print(dates.to_string(index=False))
print(f"\n→ {len(dates)} date(s) de collecte")

if len(dates) < 2:
    print("\n❌ PROBLÈME : Moins de 2 dates !")
    print("   L'onglet Évolution nécessite au moins 2 dates pour afficher des graphiques.")
    print("\n💡 SOLUTION : Lance python music_talent_radar.py --all pour créer une 2e collecte")
    conn.close()
    exit(0)

# 2. Exemple d'évolution pour quelques artistes
print("\n📈 EXEMPLE D'ÉVOLUTION (5 premiers artistes) :")

evolution_sample = pd.read_sql_query("""
    SELECT 
        a.nom as nom_artiste,
        m.date_collecte,
        m.fans_followers,
        m.score_potentiel,
        m.plateforme
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    WHERE a.nom IS NOT NULL
    ORDER BY a.nom, m.date_collecte
    LIMIT 20
""", conn)

print(evolution_sample.to_string(index=False))

# 3. Compter les artistes avec évolution visible
artistes_avec_evolution = pd.read_sql_query("""
    SELECT 
        a.nom as nom_artiste,
        COUNT(DISTINCT m.date_collecte) as nb_dates,
        GROUP_CONCAT(DISTINCT m.date_collecte) as dates
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    WHERE a.nom IS NOT NULL
    GROUP BY a.nom
    HAVING nb_dates >= 2
    ORDER BY nb_dates DESC
    LIMIT 10
""", conn)

print(f"\n✅ ARTISTES AVEC ÉVOLUTION VISIBLE :")
print(f"   {len(artistes_avec_evolution)} artistes ont des données sur plusieurs dates")
print(artistes_avec_evolution.to_string(index=False))

# 4. Vérifier si les données sont identiques (stagnation)
print("\n🔍 VÉRIFICATION : Les données ont-elles changé ?")

# Prendre un artiste et comparer ses 2 collectes
if len(artistes_avec_evolution) > 0:
    artiste_test = artistes_avec_evolution.iloc[0]['nom_artiste']
    
    comparaison = pd.read_sql_query(f"""
        SELECT 
            m.date_collecte,
            m.fans_followers,
            m.score_potentiel
        FROM metriques_historique m
        LEFT JOIN artistes a ON m.id_unique = a.id_unique
        WHERE a.nom = '{artiste_test}'
        ORDER BY m.date_collecte
    """, conn)
    
    print(f"\nArtiste : {artiste_test}")
    print(comparaison.to_string(index=False))
    
    if len(comparaison) >= 2:
        followers_1 = comparaison.iloc[0]['fans_followers']
        followers_2 = comparaison.iloc[1]['fans_followers']
        
        if followers_1 == followers_2:
            print(f"\n⚠️  ATTENTION : Les données sont IDENTIQUES entre les 2 collectes !")
            print(f"   Followers : {followers_1} → {followers_2} (aucun changement)")
            print("\n💡 C'est normal si tu as lancé music_talent_radar.py 2 fois")
            print("   le même jour avec les mêmes CSV sources.")
            print("\n   Demain, avec GitHub Actions, les données seront différentes !")
        else:
            variation = ((followers_2 - followers_1) / followers_1) * 100
            print(f"\n✅ Les données ONT CHANGÉ !")
            print(f"   Followers : {followers_1:,} → {followers_2:,} ({variation:+.1f}%)")

# 5. Simuler ce que Streamlit afficherait
print("\n" + "=" * 70)
print("📊 CE QUE STREAMLIT DEVRAIT AFFICHER :")
print("=" * 70)

if len(dates) >= 2:
    print(f"\n✅ {len(dates)} dates disponibles → Graphiques d'évolution OK")
    print(f"✅ {len(artistes_avec_evolution)} artistes avec évolution → Sélection OK")
    
    if len(dates) == 2:
        print("\n💡 NOTE : Avec seulement 2 dates, les graphiques auront seulement 2 points.")
        print("   C'est une ligne droite, mais c'est normal !")
        print("   Après 3-4 collectes, les courbes seront plus intéressantes.")
else:
    print(f"\n❌ Seulement {len(dates)} date(s) → Graphiques impossibles")

conn.close()

print("\n" + "=" * 70)
print("📝 CONCLUSION :")
print("=" * 70)

if len(dates) >= 2:
    print("""
✅ TU AS ASSEZ DE DONNÉES pour afficher l'évolution !

Si l'onglet Évolution est vide dans Streamlit, c'est peut-être :
1. Un filtre actif qui masque les artistes
2. Un bug dans le code de l'onglet Évolution
3. Le graphique cherche plus de 2 dates

TESTE :
1. Relance Streamlit : streamlit run app/streamlit.py
2. Va dans l'onglet Évolution
3. Vérifie les filtres (genre, plateforme, etc.)
4. Sélectionne un artiste dans la liste déroulante

Si toujours vide, envoie-moi une capture d'écran !
""")
else:
    print("""
❌ PAS ASSEZ DE DONNÉES pour afficher l'évolution

SOLUTION :
python music_talent_radar.py --all

Puis relance ce diagnostic.
""")
