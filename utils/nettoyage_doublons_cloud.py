"""
NETTOYAGE FORCÉ DES DOUBLONS
Version agressive qui supprime TOUS les doublons (même avec heures différentes)
"""

import sqlite3
from datetime import datetime

DB_PATH = 'data/music_talent_radar_v2.db'

print("🧹 NETTOYAGE FORCÉ DES DOUBLONS\n")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# ÉTAPE 1 : Diagnostic
print(" ÉTAPE 1 : Diagnostic...")

cursor.execute("SELECT COUNT(*) FROM metriques_historique")
total_avant = cursor.fetchone()[0]
print(f"   Total de lignes AVANT : {total_avant}")

cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT 1
        FROM metriques_historique
        GROUP BY date(date_collecte), nom_artiste, plateforme
        HAVING COUNT(*) > 1
    )
""")
nb_doublons_artistes = cursor.fetchone()[0]
print(f"   Artistes avec doublons : {nb_doublons_artistes}")

# ÉTAPE 2 : Sauvegarde (au cas où)
print("\n ÉTAPE 2 : Sauvegarde...")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS metriques_historique_backup AS
    SELECT * FROM metriques_historique
""")
conn.commit()
print("    Backup créé (table metriques_historique_backup)")

# ÉTAPE 3 : Suppression des doublons (garder le dernier ID = le plus récent)
print("\n ÉTAPE 3 : Suppression des doublons...")

# Stratégie : Pour chaque combinaison (date, artiste, plateforme), garder seulement le MAX(id)
cursor.execute("""
    DELETE FROM metriques_historique
    WHERE id NOT IN (
        SELECT MAX(id)
        FROM metriques_historique
        GROUP BY date(date_collecte), nom_artiste, plateforme
    )
""")

nb_supprimes = cursor.rowcount
conn.commit()
print(f"    {nb_supprimes} doublons supprimés")

# ÉTAPE 4 : Vérification
print("\n ÉTAPE 4 : Vérification...")

cursor.execute("SELECT COUNT(*) FROM metriques_historique")
total_apres = cursor.fetchone()[0]
print(f"   Total de lignes APRÈS : {total_apres}")
print(f"   Lignes supprimées : {total_avant - total_apres}")

cursor.execute("""
    SELECT COUNT(*) FROM (
        SELECT 1
        FROM metriques_historique
        GROUP BY date(date_collecte), nom_artiste, plateforme
        HAVING COUNT(*) > 1
    )
""")
nb_doublons_restants = cursor.fetchone()[0]

if nb_doublons_restants == 0:
    print("    AUCUN doublon restant")
else:
    print(f"    {nb_doublons_restants} doublons restants (vérifier manuellement)")

# ÉTAPE 5 : Afficher les dates uniques restantes
print("\n ÉTAPE 5 : Dates de collecte après nettoyage...")

cursor.execute("""
    SELECT 
        date(date_collecte) as date_jour,
        COUNT(*) as nb_lignes,
        COUNT(DISTINCT nom_artiste) as nb_artistes
    FROM metriques_historique
    GROUP BY date(date_collecte)
    ORDER BY date_jour DESC
    LIMIT 10
""")

print("\n   Date        | Lignes | Artistes")
print("   " + "-"*40)
for row in cursor.fetchall():
    print(f"   {row[0]:12} | {row[1]:6} | {row[2]:8}")

# ÉTAPE 6 : Vérifier spécifiquement le 12/02
print("\n ÉTAPE 6 : Vérification spécifique du 12/02...")

cursor.execute("""
    SELECT 
        COUNT(*) as nb_lignes,
        COUNT(DISTINCT nom_artiste) as nb_artistes,
        MIN(date_collecte) as premiere_heure,
        MAX(date_collecte) as derniere_heure
    FROM metriques_historique
    WHERE date(date_collecte) = '2025-02-12'
""")

row = cursor.fetchone()
if row and row[0] > 0:
    print(f"   Lignes le 12/02 : {row[0]}")
    print(f"   Artistes uniques : {row[1]}")
    print(f"   Première collecte : {row[2]}")
    print(f"   Dernière collecte : {row[3]}")
    
    # Vérifier si encore des doublons ce jour-là
    cursor.execute("""
        SELECT COUNT(*) FROM (
            SELECT 1
            FROM metriques_historique
            WHERE date(date_collecte) = '2025-02-12'
            GROUP BY nom_artiste, plateforme
            HAVING COUNT(*) > 1
        )
    """)
    doublons_feb12 = cursor.fetchone()[0]
    
    if doublons_feb12 == 0:
        print("    AUCUN doublon le 12/02")
    else:
        print(f"    {doublons_feb12} doublons restants le 12/02")
else:
    print("    Pas de données du 12/02")

# ÉTAPE 7 : Optimiser la base
print("\n ÉTAPE 7 : Optimisation de la base...")

cursor.execute("VACUUM")
conn.commit()
print("   Base optimisée")

conn.close()

print(" NETTOYAGE TERMINÉ")

