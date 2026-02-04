import sqlite3
from datetime import datetime

DB_PATH = 'data/music_talent_radar_v2.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

print(" NETTOYAGE DES DOUBLONS")

# 1. Compter les doublons AVANT
cursor.execute("""
    SELECT date(date_collecte), id_unique, COUNT(*) as nb
    FROM metriques_historique
    GROUP BY date(date_collecte), id_unique
    HAVING COUNT(*) > 1
""")
doublons_avant = cursor.fetchall()
print(f" {len(doublons_avant)} artistes avec doublons")

# 2. SUPPRIMER les doublons (garder seulement le plus récent)
cursor.execute("""
    DELETE FROM metriques_historique
    WHERE id NOT IN (
        SELECT MAX(id)
        FROM metriques_historique
        GROUP BY date(date_collecte), id_unique
    )
""")

nb_supprimes = cursor.rowcount
conn.commit()

print(f" {nb_supprimes} lignes en doublon supprimées")

# 3. Vérifier après
cursor.execute("""
    SELECT date(date_collecte), COUNT(DISTINCT id_unique) as nb_artistes
    FROM metriques_historique
    GROUP BY date(date_collecte)
    ORDER BY date_collecte DESC
    LIMIT 5
""")

print("\n Dates après nettoyage:")
for row in cursor.fetchall():
    print(f"  {row[0]} → {row[1]} artistes")

conn.close()
print("\n NETTOYAGE TERMINÉ")