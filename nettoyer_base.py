#!/usr/bin/env python3
"""
Script pour nettoyer la table metriques_historique et supprimer les colonnes en double
"""

import sqlite3
import pandas as pd

DB_PATH = 'data/music_talent_radar_v2.db'

print("🔧 NETTOYAGE DE LA TABLE METRIQUES_HISTORIQUE\n")
print("=" * 60)

conn = sqlite3.connect(DB_PATH)

# 1. Charger toutes les métriques
print("\n📊 Chargement des données...")
metriques_df = pd.read_sql_query("SELECT * FROM metriques_historique", conn)
print(f"   {len(metriques_df)} métriques chargées")
print(f"   Colonnes actuelles : {metriques_df.columns.tolist()}")

# 2. Identifier les colonnes à garder
colonnes_a_garder = [
    'id',
    'id_unique',
    'plateforme',
    'fans_followers',
    'followers',
    'fans',
    'popularity',
    'score_potentiel',
    'score',
    'date_collecte'
]

# Garder seulement les colonnes qui existent
colonnes_finales = [col for col in colonnes_a_garder if col in metriques_df.columns]
print(f"\n✅ Colonnes à garder : {colonnes_finales}")

# 3. Créer nouveau DataFrame nettoyé
metriques_clean = metriques_df[colonnes_finales].copy()
print(f"\n📊 Données nettoyées : {len(metriques_clean)} lignes, {len(metriques_clean.columns)} colonnes")

# 4. Sauvegarder dans une nouvelle table temporaire
print("\n🗑️  Suppression de l'ancienne table...")
cursor = conn.cursor()
cursor.execute("DROP TABLE IF EXISTS metriques_historique_backup")
cursor.execute("ALTER TABLE metriques_historique RENAME TO metriques_historique_backup")
conn.commit()
print("   ✅ Ancienne table sauvegardée en backup")

# 5. Créer nouvelle table propre
print("\n📝 Création de la nouvelle table...")
metriques_clean.to_sql('metriques_historique', conn, if_exists='replace', index=False)
print("   ✅ Nouvelle table créée")

# 6. Vérifier
print("\n🔍 Vérification...")
cursor.execute("PRAGMA table_info(metriques_historique)")
colonnes_finales = cursor.fetchall()
print("\n   Colonnes finales :")
for col in colonnes_finales:
    print(f"     - {col[1]} ({col[2]})")

# Test de jointure
test_df = pd.read_sql_query("""
    SELECT 
        m.*,
        a.nom as nom_artiste,
        a.genre,
        a.image_url
    FROM metriques_historique m
    LEFT JOIN artistes a ON m.id_unique = a.id_unique
    LIMIT 5
""", conn)

print("\n📊 Test de jointure (comme Streamlit) :")
print(test_df[['id_unique', 'nom_artiste', 'plateforme', 'score']].to_string())

# Vérifier qu'il n'y a plus de doublons
if 'nom_artiste' in test_df.columns:
    noms_null = test_df['nom_artiste'].isna().sum()
    if noms_null == 0:
        print("\n✅ SUCCÈS : Tous les artistes ont un nom !")
    else:
        print(f"\n⚠️ Attention : {noms_null}/5 artistes sans nom")
else:
    print("\n✅ Colonne nom_artiste OK (vient de la jointure)")

conn.close()

print("\n" + "=" * 60)
print("✅ NETTOYAGE TERMINÉ !")
print("\n📋 PROCHAINES ÉTAPES :")
print("1. Relance Streamlit : streamlit run app/streamlit.py")
print("2. Vérifie que les graphiques s'affichent")
print("3. Si OK, tu peux supprimer le backup :")
print("   DROP TABLE metriques_historique_backup;")
