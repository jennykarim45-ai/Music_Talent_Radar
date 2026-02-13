import sqlite3
from datetime import datetime
import pandas as pd

DB_PATH = 'data/music_talent_radar_v2.db'

print("🔍 DIAGNOSTIC COMPLET DES DOUBLONS\n")

conn = sqlite3.connect(DB_PATH)

# 1. Nombre total de lignes
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM metriques_historique")
total = cursor.fetchone()[0]
print(f"📊 Total de lignes : {total}")

# 2. Vérifier les doublons EXACTS (même date, même artiste)
print("\n🔍 Recherche doublons exacts (même date + même artiste)...")

doublons_query = """
SELECT 
    date(date_collecte) as date_jour,
    nom_artiste,
    plateforme,
    COUNT(*) as nb_occurrences,
    GROUP_CONCAT(id) as ids
FROM metriques_historique
GROUP BY date(date_collecte), nom_artiste, plateforme
HAVING COUNT(*) > 1
ORDER BY date_jour DESC, nb_occurrences DESC
"""

df_doublons = pd.read_sql_query(doublons_query, conn)

if len(df_doublons) == 0:
    print("✅ AUCUN doublon trouvé !")
else:
    print(f"❌ {len(df_doublons)} doublons trouvés :\n")
    print(df_doublons.to_string(index=False))
    
    # Total de lignes en doublon
    total_doublons = df_doublons['nb_occurrences'].sum() - len(df_doublons)
    print(f"\n📊 Total de lignes en doublon à supprimer : {total_doublons}")

# 3. Vérifier spécifiquement le 12/02
print("\n🔍 Vérification spécifique du 12/02/2025...")

feb12_query = """
SELECT 
    date_collecte,
    nom_artiste,
    plateforme,
    id,
    fans_followers
FROM metriques_historique
WHERE date(date_collecte) = '2025-02-12'
ORDER BY nom_artiste, plateforme, date_collecte
"""

df_feb12 = pd.read_sql_query(feb12_query, conn)

if len(df_feb12) > 0:
    print(f"📅 {len(df_feb12)} lignes le 12/02/2025")
    
    # Compter les doublons ce jour-là
    feb12_duplicates = df_feb12.groupby(['nom_artiste', 'plateforme']).size()
    feb12_dup_count = (feb12_duplicates > 1).sum()
    
    if feb12_dup_count > 0:
        print(f"❌ {feb12_dup_count} artistes en doublon le 12/02")
        print("\nExemples de doublons du 12/02 :")
        print(df_feb12[df_feb12.duplicated(['nom_artiste', 'plateforme'], keep=False)].head(10).to_string(index=False))
    else:
        print("✅ Pas de doublons le 12/02")
else:
    print("ℹ️ Aucune donnée du 12/02/2025")

# 4. Distribution par date
print("\n📅 Distribution des collectes par date :")

dates_query = """
SELECT 
    date(date_collecte) as date_jour,
    COUNT(*) as nb_lignes,
    COUNT(DISTINCT nom_artiste) as nb_artistes_uniques
FROM metriques_historique
GROUP BY date(date_collecte)
ORDER BY date_jour DESC
LIMIT 10
"""

df_dates = pd.read_sql_query(dates_query, conn)
print(df_dates.to_string(index=False))

# 5. Vérifier si dates avec heures différentes
print("\n⏰ Vérification des heures de collecte...")

heures_query = """
SELECT 
    date_collecte,
    COUNT(*) as nb
FROM metriques_historique
WHERE date(date_collecte) = '2025-02-12'
GROUP BY date_collecte
ORDER BY date_collecte
"""

df_heures = pd.read_sql_query(heures_query, conn)

if len(df_heures) > 0:
    print(f"🕐 Heures différentes le 12/02 :")
    print(df_heures.to_string(index=False))
    
    if len(df_heures) > 1:
        print("\n⚠️ PROBLÈME : Plusieurs heures de collecte le même jour !")
        print("   → Les doublons viennent probablement de collectes multiples le même jour")
else:
    print("ℹ️ Pas de données du 12/02")

conn.close()

print("\n" + "="*60)
print("📋 RECOMMANDATIONS :")
print("="*60)

if len(df_doublons) > 0:
    print("1. ❌ Des doublons existent encore → Exécuter nettoyage_doublons_FORCE.py")
elif len(df_heures) > 1:
    print("1. ⚠️ Plusieurs collectes le même jour → Consolider avec nettoyage_doublons_FORCE.py")
else:
    print("1. ✅ Base de données propre")
    print("2. 🔄 Vider le cache Streamlit : st.cache_data.clear()")
    print("3. ♻️ Redémarrer Streamlit")

print("="*60)
