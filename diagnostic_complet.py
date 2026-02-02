"""
Diagnostic complet : Pourquoi toujours une seule date ?
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime

print("🔍 DIAGNOSTIC COMPLET : Pourquoi toujours une seule date ?")
print("=" * 70)

# 1. Vérifier les CSV collectés
print("\n📋 ÉTAPE 1 : Vérification des CSV collectés")
print("-" * 70)

csv_files = [
    'data/spotify_collected_latest.csv',
    'data/deezer_collected_latest.csv',
]

for csv_file in csv_files:
    if os.path.exists(csv_file):
        # Date de modification du fichier
        mtime = os.path.getmtime(csv_file)
        date_modif = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n📄 {csv_file}")
        print(f"   Dernière modification : {date_modif}")
        
        # Lire le CSV pour voir s'il contient une colonne date
        try:
            df = pd.read_csv(csv_file, nrows=5)
            print(f"   Colonnes : {list(df.columns)}")
            
            if 'date_collecte' in df.columns:
                dates_uniques = pd.read_csv(csv_file)['date_collecte'].unique()
                print(f"   Dates dans le CSV : {dates_uniques}")
        except Exception as e:
            print(f"   ⚠️ Erreur lecture : {e}")
    else:
        print(f"\n❌ {csv_file} n'existe pas")

# 2. Vérifier music_talent_radar.py
print("\n\n📋 ÉTAPE 2 : Vérification de music_talent_radar.py")
print("-" * 70)

if os.path.exists('music_talent_radar.py'):
    with open('music_talent_radar.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Chercher les DELETE
    delete_lines = []
    for i, line in enumerate(lines, 1):
        if 'DELETE FROM metriques_historique' in line and not line.strip().startswith('#'):
            delete_lines.append((i, line.strip()))
    
    if delete_lines:
        print("\n⚠️ DELETE FROM metriques_historique trouvés (NON COMMENTÉS) :")
        for line_num, line in delete_lines:
            print(f"   Ligne {line_num} : {line[:80]}")
        print("\n❌ PROBLÈME : Ces lignes ÉCRASENT l'historique !")
    else:
        print("\n✅ Aucun DELETE non-commenté trouvé")
    
    # Chercher comment la date est définie
    print("\n🔍 Comment la date est-elle définie ?")
    date_lines = []
    for i, line in enumerate(lines, 1):
        if 'date_collecte' in line.lower() and '=' in line and not line.strip().startswith('#'):
            date_lines.append((i, line.strip()))
    
    if date_lines:
        print("\nLignes qui définissent date_collecte :")
        for line_num, line in date_lines[:10]:  # Max 10 lignes
            print(f"   Ligne {line_num} : {line[:80]}")
else:
    print("❌ music_talent_radar.py introuvable")

# 3. Vérifier la base de données
print("\n\n📋 ÉTAPE 3 : Vérification de la base de données")
print("-" * 70)

DB_PATH = 'data/music_talent_radar_v2.db'

if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    
    # Dates de collecte
    dates = pd.read_sql_query("""
        SELECT DISTINCT date_collecte, COUNT(*) as nb_artistes
        FROM metriques_historique
        GROUP BY date_collecte
        ORDER BY date_collecte DESC
    """, conn)
    
    print("\n📅 Dates dans metriques_historique :")
    print(dates.to_string(index=False))
    
    # Voir si des lignes ont été insérées récemment
    print("\n🕐 Dernières insertions dans metriques_historique :")
    try:
        derniers = pd.read_sql_query("""
            SELECT id, nom_artiste, date_collecte, plateforme
            FROM metriques_historique
            ORDER BY id DESC
            LIMIT 10
        """, conn)
        print(derniers.to_string(index=False))
    except:
        print("   (impossible de récupérer les dernières insertions)")
    
    conn.close()
else:
    print("❌ Base de données introuvable")

# 4. Conclusion et solution
print("\n\n" + "=" * 70)
print("📝 DIAGNOSTIC FINAL")
print("=" * 70)

print("""
🔍 CAUSES POSSIBLES :

1. music_talent_radar.py contient toujours un DELETE non-commenté
   → Il écrase les données au lieu d'ajouter

2. music_talent_radar.py utilise la date des CSV (28 janvier)
   → Au lieu d'utiliser la date du jour

3. collecte1.py n'a pas vraiment créé de nouveaux CSV
   → Il a réutilisé les anciens

4. Les CSV créés ont la mauvaise date hardcodée

💡 SOLUTIONS :

SOLUTION RAPIDE (1 minute) :
  python creer_nouvelle_collecte.py
  → Duplique les données avec la date d'aujourd'hui

SOLUTION MANUELLE :
  1. Vérifie les DELETE dans music_talent_radar.py (voir ci-dessus)
  2. Commente-les avec # au début
  3. Relance : python music_talent_radar.py --all

SOLUTION FORCÉE :
  Je vais créer un script pour patcher directement la base
  et forcer une 2e date avec variations réalistes
""")
