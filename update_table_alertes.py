
"""
Script pour mettre à jour la table alertes avec les nouvelles colonnes
"""

import sqlite3

DB_PATH = 'data/music_talent_radar_v2.db'

print(" MISE À JOUR DE LA TABLE ALERTES")
print("=" * 60)

# Connexion à la base
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 1. Vérifier si la table existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alertes'")
table_exists = cursor.fetchone()

if table_exists:
    print(" Table 'alertes' détectée")
    
    # Vérifier les colonnes existantes
    cursor.execute("PRAGMA table_info(alertes)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f" Colonnes actuelles : {', '.join(column_names)}")
    
    # Vérifier si les nouvelles colonnes existent
    nouvelles_colonnes = ['followers_avant', 'followers_apres', 'pourcentage_followers', 
                        'score_avant', 'score_apres', 'pourcentage_score',
                        'date_formatted', 'mois_annee']
    
    colonnes_manquantes = [col for col in nouvelles_colonnes if col not in column_names]
    
    if colonnes_manquantes:
        print(f"\n  Colonnes manquantes : {', '.join(colonnes_manquantes)}")
        print("\n Recréation de la table avec toutes les colonnes...")
        
        # Sauvegarder les anciennes alertes (si elles existent)
        cursor.execute("SELECT * FROM alertes")
        old_alerts = cursor.fetchall()
        
        # Supprimer l'ancienne table
        cursor.execute("DROP TABLE alertes")
        print(" Ancienne table supprimée")
        
        # Créer la nouvelle table avec toutes les colonnes
        cursor.execute("""
            CREATE TABLE alertes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_artiste TEXT,
                type_alerte TEXT,
                message TEXT,
                date_alerte TEXT,
                followers_avant INTEGER,
                followers_apres INTEGER,
                pourcentage_followers REAL,
                score_avant REAL,
                score_apres REAL,
                pourcentage_score REAL,
                date_formatted TEXT,
                mois_annee TEXT,
                vu BOOLEAN DEFAULT 0
            )
        """)
        conn.commit()
        print(" Nouvelle table créée avec toutes les colonnes")
        
        # Réinsérer les anciennes alertes (colonnes de base uniquement)
        if old_alerts:
            print(f"\n Réinsertion de {len(old_alerts)} anciennes alertes...")
            for alert in old_alerts:
                # Insérer seulement les colonnes de base (id, nom_artiste, type_alerte, message, date_alerte, vu)
                cursor.execute("""
                    INSERT INTO alertes (nom_artiste, type_alerte, message, date_alerte, vu)
                    VALUES (?, ?, ?, ?, ?)
                """, (alert[1], alert[2], alert[3], alert[4], alert[5] if len(alert) > 5 else 0))
            conn.commit()
            print(" Anciennes alertes réinsérées")
    else:
        print("\n Toutes les colonnes sont déjà présentes !")
else:
    print(" Table 'alertes' n'existe pas, création...")
    cursor.execute("""
        CREATE TABLE alertes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_artiste TEXT,
            type_alerte TEXT,
            message TEXT,
            date_alerte TEXT,
            followers_avant INTEGER,
            followers_apres INTEGER,
            pourcentage_followers REAL,
            score_avant REAL,
            score_apres REAL,
            pourcentage_score REAL,
            date_formatted TEXT,
            mois_annee TEXT,
            vu BOOLEAN DEFAULT 0
        )
    """)
    conn.commit()
    print(" Table créée")

# Vérifier le résultat final
cursor.execute("PRAGMA table_info(alertes)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

print("\n" + "=" * 60)
print(" STRUCTURE FINALE DE LA TABLE ALERTES")
print("=" * 60)
for col in columns:
    print(f"  {col[1]:<25} {col[2]:<10}")

conn.close()

print("\n" + "=" * 60)
print(" MISE À JOUR TERMINÉE !")
print("=" * 60)
print("\n Prochaines étapes :")
print("1. python generer_alertes.py")
print("2. streamlit run app/streamlit.py")
