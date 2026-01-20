#!/usr/bin/env python3
"""
Script de diagnostic de la base de données
"""

import sqlite3
import pandas as pd

DB_PATH = 'data/music_talent_radar_v2.db'

print(" DIAGNOSTIC DE LA BASE DE DONNÉES\n")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)

# 1. VÉRIFIER LA TABLE ARTISTES
print("\n TABLE ARTISTES\n")

# Colonnes
cursor = conn.cursor()
cursor.execute("PRAGMA table_info(artistes)")
columns = cursor.fetchall()
print("Colonnes :")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Nombre total
total = cursor.execute("SELECT COUNT(*) FROM artistes").fetchone()[0]
print(f"\nTotal artistes : {total}")

# Exemples
print("\n Exemples d'artistes :")
artistes_sample = pd.read_sql_query("SELECT * FROM artistes LIMIT 5", conn)
print(artistes_sample[['id_unique', 'nom', 'source', 'genre']].to_string())

# Vérifier les noms vides
noms_vides = cursor.execute("SELECT COUNT(*) FROM artistes WHERE nom IS NULL OR nom = ''").fetchone()[0]
if noms_vides > 0:
    print(f"\n PROBLÈME : {noms_vides} artistes ont un nom vide !")
else:
    print(f"\n Tous les artistes ont un nom")

# Vérifier les images
if 'image_url' in [col[1] for col in columns]:
    images_vides = cursor.execute("SELECT COUNT(*) FROM artistes WHERE image_url IS NULL OR image_url = ''").fetchone()[0]
    images_ok = total - images_vides
    print(f"Images : {images_ok}/{total} artistes ont une image ({images_ok/total*100:.1f}%)")
else:
    print(" Colonne image_url n'existe pas")

# 2. VÉRIFIER LA TABLE METRIQUES_HISTORIQUE
print("\n" + "=" * 60)
print("\n TABLE METRIQUES_HISTORIQUE\n")

# Colonnes
cursor.execute("PRAGMA table_info(metriques_historique)")
columns = cursor.fetchall()
print("Colonnes :")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# Nombre total
total_metriques = cursor.execute("SELECT COUNT(*) FROM metriques_historique").fetchone()[0]
print(f"\nTotal métriques : {total_metriques}")

# Exemples
print("\n Exemples de métriques :")
metriques_sample = pd.read_sql_query("SELECT * FROM metriques_historique LIMIT 5", conn)
print(metriques_sample.head().to_string())

# 3. VÉRIFIER LA JOINTURE
print("\n" + "=" * 60)
print("\n TEST DE JOINTURE\n")

query = """
    SELECT 
        a.nom as nom_artiste,
        a.source as plateforme,
        a.genre,
        m.date_collecte,
        m.score
    FROM artistes a
    LEFT JOIN metriques_historique m ON a.id_unique = m.id_unique
    LIMIT 10
"""

jointure_df = pd.read_sql_query(query, conn)
print(jointure_df.to_string())

# Vérifier combien de métriques n'ont pas d'artiste associé
orphelins = cursor.execute("""
    SELECT COUNT(*) 
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    WHERE a.id_unique IS NULL
""").fetchone()[0]

if orphelins > 0:
    print(f"\n PROBLÈME : {orphelins} métriques n'ont pas d'artiste associé !")
else:
    print(f"\n Toutes les métriques sont associées à un artiste")

# 4. VÉRIFIER LA COLONNE UTILISÉE PAR STREAMLIT
print("\n" + "=" * 60)
print("\n VÉRIFICATION POUR STREAMLIT\n")

# Streamlit utilise cette requête
query = """
    SELECT 
        m.*, 
        a.nom as nom_artiste, 
        a.source as plateforme
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    ORDER BY m.date_collecte DESC
    LIMIT 5
"""

streamlit_df = pd.read_sql_query(query, conn)
print("Données que Streamlit va charger :")
print(streamlit_df.to_string())

# Vérifier si nom_artiste est NULL
noms_null = streamlit_df['nom_artiste'].isna().sum()
if noms_null > 0:
    print(f"\n PROBLÈME : {noms_null}/5 artistes ont nom_artiste = NULL !")
else:
    print(f"\n Tous les artistes ont un nom_artiste")

conn.close()

print("\n" + "=" * 60)
print("\n RÉSUMÉ\n")

if total == 0:
    print(" PROBLÈME CRITIQUE : La table artistes est vide !")
    print("  Relance : python import_data.py")
elif total_metriques == 0:
    print(" PROBLÈME CRITIQUE : La table metriques_historique est vide !")
    print(" Relance : python import_data.py")
elif noms_vides > 0:
    print(f" PROBLÈME : {noms_vides} artistes ont un nom vide")
    print("  Vérifie tes CSV sources")
elif orphelins > 0:
    print(f"PROBLÈME : {orphelins} métriques orphelines")
    print(" Problème de jointure id_unique")
else:
    print(" La base semble OK !")
    print(f"   - {total} artistes")
    print(f"   - {total_metriques} métriques")
    print(f"   - Jointures OK")
    print("\nSi Streamlit affiche encore des graphiques vides :")
    print("   1. Vérifie les filtres (Genre, Plateforme, Score)")
    print("   2. Vide le cache Streamlit")
    print("   3. Relance Streamlit")
