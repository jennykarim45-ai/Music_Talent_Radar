#!/usr/bin/env python3
"""
Script pour vérifier si music_talent_radar.py écrase l'historique
"""

print("🔍 DIAGNOSTIC : Pourquoi une seule date de collecte ?")
print("=" * 70)

# 1. Chercher DELETE dans music_talent_radar.py
print("\n📋 Recherche de DELETE dans music_talent_radar.py...")

try:
    with open('music_talent_radar.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    delete_found = False
    for i, line in enumerate(lines, 1):
        if 'DELETE FROM metriques_historique' in line and not line.strip().startswith('#'):
            print(f"\n⚠️  TROUVÉ ligne {i} :")
            print(f"   {line.strip()}")
            delete_found = True
            
            # Afficher contexte (5 lignes avant et après)
            print("\n📄 Contexte :")
            start = max(0, i - 6)
            end = min(len(lines), i + 5)
            for j in range(start, end):
                prefix = ">>> " if j == i - 1 else "    "
                print(f"{prefix}{j+1:4d} | {lines[j]}")
    
    if delete_found:
        print("\n" + "=" * 70)
        print("❌ PROBLÈME IDENTIFIÉ !")
        print("=" * 70)
        print("""
music_talent_radar.py SUPPRIME les anciennes données avant d'insérer les nouvelles.

Conséquence :
- Chaque run GitHub Actions ÉCRASE l'historique
- Tu as toujours une seule date de collecte
- Impossible de calculer des évolutions
- Pas d'alertes dynamiques

SOLUTION :
Il faut COMMENTER ou SUPPRIMER les lignes qui font DELETE FROM metriques_historique
pour que les nouvelles collectes s'AJOUTENT à l'historique au lieu de le remplacer.
""")
    else:
        print("\n✅ Aucun DELETE trouvé dans music_talent_radar.py")
        print("   Le problème est ailleurs...")
        
except FileNotFoundError:
    print("❌ Fichier music_talent_radar.py introuvable")
    print("   Es-tu dans le bon répertoire ?")

# 2. Vérifier la structure actuelle de la base
print("\n" + "=" * 70)
print("📊 Vérification de la base de données")
print("=" * 70)

import sqlite3
import pandas as pd

try:
    conn = sqlite3.connect('data/music_talent_radar_v2.db')
    
    # Compter les dates
    dates = pd.read_sql_query("""
        SELECT DISTINCT date_collecte, COUNT(*) as nb_artistes
        FROM metriques_historique
        GROUP BY date_collecte
        ORDER BY date_collecte DESC
    """, conn)
    
    print(f"\n📅 Nombre de dates de collecte : {len(dates)}")
    print(dates.to_string(index=False))
    
    if len(dates) == 1:
        print("\n❌ Une seule date → Impossible de calculer des évolutions")
    else:
        print(f"\n✅ {len(dates)} dates → Les évolutions sont possibles")
        
        # Vérifier combien d'artistes ont 2+ collectes
        artistes_multi = pd.read_sql_query("""
            SELECT COUNT(*) as total
            FROM (
                SELECT id_unique, COUNT(DISTINCT date_collecte) as nb
                FROM metriques_historique
                GROUP BY id_unique
                HAVING nb >= 2
            )
        """, conn).iloc[0]['total']
        
        print(f"   {artistes_multi} artistes avec 2+ collectes")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur : {e}")

print("\n" + "=" * 70)
print("📝 RÉSUMÉ")
print("=" * 70)

if delete_found:
    print("""
✅ PROBLÈME TROUVÉ : music_talent_radar.py supprime l'historique

SOLUTION :
1. Ouvre music_talent_radar.py
2. Cherche la/les ligne(s) avec DELETE FROM metriques_historique
3. Commente-les en ajoutant # au début
4. Sauvegarde
5. Relance : python music_talent_radar.py --all
6. Tu auras une 2e date de collecte !
""")
else:
    print("""
🤔 DELETE non trouvé mais une seule date existe

SOLUTIONS POSSIBLES :
1. Lance manuellement : python music_talent_radar.py --all
   (pour créer une 2e collecte maintenant)
   
2. OU utilise le script de simulation : python simuler_collectes.py
   (pour créer 7 jours d'historique simulé)
""")
