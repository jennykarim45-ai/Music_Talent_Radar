import sqlite3
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configuration
DB_PATH = "data/music_talent_radar_v2.db"
SPOTIFY_CSV = "data/spotify_artists_20260112.csv"
DEEZER_CSV = "data/deezer_artists_20260112.csv"

def create_database():
    """Créer la base de données SQLite"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Supprimer les tables si elles existent
    cursor.execute("DROP TABLE IF EXISTS artistes")
    cursor.execute("DROP TABLE IF EXISTS metriques_historique")
    
    # Créer la table artistes (avec 'e' à la fin)
    cursor.execute("""
        CREATE TABLE artistes (
            id_unique TEXT PRIMARY KEY,
            nom TEXT NOT NULL,
            followers INTEGER,
            fans INTEGER,
            popularity INTEGER,
            genres TEXT,
            url_spotify TEXT,
            url_deezer TEXT,
            url TEXT,
            image_url TEXT,
            genre TEXT,
            source TEXT,
            score REAL,
            categorie TEXT,
            date_collecte TEXT
        )
    """)
    
    # Créer la table metriques_historique
    cursor.execute("""
        CREATE TABLE metriques_historique (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_unique TEXT,
            nom_artiste TEXT,
            source TEXT,
            plateforme TEXT,
            genre TEXT,
            fans_followers INTEGER,
            followers INTEGER,
            fans INTEGER,
            popularity INTEGER,
            score_potentiel REAL,
            score REAL,
            categorie TEXT,
            date_collecte TEXT,
            url TEXT,
            image_url TEXT,
            FOREIGN KEY (id_unique) REFERENCES artistes(id_unique)
        )
    """)
    
    conn.commit()
    conn.close()
    print("Base de données créée")

def import_spotify():
    """Importer les artistes Spotify"""
    if not Path(SPOTIFY_CSV).exists():
        print(f"Fichier non trouvé: {SPOTIFY_CSV}")
        return 0
    
    df = pd.read_csv(SPOTIFY_CSV)
    
    conn = sqlite3.connect(DB_PATH)
    date_now = datetime.now().strftime('%Y-%m-%d')
    
    for _, row in df.iterrows():
        try:
            # Import dans artistes
            id_unique = f"spotify_{row['id']}"
            
            conn.execute("""
                INSERT OR REPLACE INTO artistes (
                    id_unique, nom, followers, fans, popularity, genres, 
                    url_spotify, url_deezer, url, image_url, genre, source, 
                    score, categorie, date_collecte
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_unique,
                row['nom'],
                row.get('followers', 0),
                None,
                row.get('popularity', 0),
                row.get('genres', ''),
                row.get('url_spotify', ''),
                None,
                row.get('url_spotify', ''),
                row.get('image_url', ''),
                row.get('genre', ''),
                'Spotify',
                row.get('score', 0),
                row.get('categorie', ''),
                row.get('date_collecte', date_now)
            ))
            
            # Import dans metriques_historique
            conn.execute("""
                INSERT INTO metriques_historique (
                    id_unique, nom_artiste, source, plateforme, genre,
                    fans_followers, followers, fans, popularity,
                    score_potentiel, score, categorie, date_collecte,
                    url, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_unique,
                row['nom'],
                'Spotify',
                'Spotify',
                row.get('genre', ''),
                row.get('followers', 0),
                row.get('followers', 0),
                None,
                row.get('popularity', 0),
                row.get('score', 0),
                row.get('score', 0),
                row.get('categorie', ''),
                row.get('date_collecte', date_now),
                row.get('url_spotify', ''),
                row.get('image_url', '')
            ))
            
        except Exception as e:
            print(f"Erreur import Spotify {row.get('nom', 'inconnu')}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f" Import Spotify: {len(df)} artistes")
    return len(df)

def import_deezer():
    """Importer les artistes Deezer"""
    if not Path(DEEZER_CSV).exists():
        print(f" Fichier non trouvé: {DEEZER_CSV}")
        return 0
    
    df = pd.read_csv(DEEZER_CSV)
    
    conn = sqlite3.connect(DB_PATH)
    date_now = datetime.now().strftime('%Y-%m-%d')
    
    for _, row in df.iterrows():
        try:
            # Import dans artistes
            id_unique = f"deezer_{row['id']}"
            
            conn.execute("""
                INSERT OR REPLACE INTO artistes (
                    id_unique, nom, followers, fans, popularity, genres, 
                    url_spotify, url_deezer, url, image_url, genre, source, 
                    score, categorie, date_collecte
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_unique,
                row['nom'],
                None,
                row.get('fans', 0),
                None,
                None,
                None,
                row.get('url_deezer', ''),
                row.get('url_deezer', ''),
                row.get('image_url', ''),
                row.get('genre', ''),
                'Deezer',
                row.get('score', 0),
                row.get('categorie', ''),
                row.get('date_collecte', date_now)
            ))
            
            # Import dans metriques_historique
            conn.execute("""
                INSERT INTO metriques_historique (
                    id_unique, nom_artiste, source, plateforme, genre,
                    fans_followers, followers, fans, popularity,
                    score_potentiel, score, categorie, date_collecte,
                    url, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                id_unique,
                row['nom'],
                'Deezer',
                'Deezer',
                row.get('genre', ''),
                row.get('fans', 0),
                None,
                row.get('fans', 0),
                None,
                row.get('score', 0),
                row.get('score', 0),
                row.get('categorie', ''),
                row.get('date_collecte', date_now),
                row.get('url_deezer', ''),
                row.get('image_url', '')
            ))
            
        except Exception as e:
            print(f"Erreur import Deezer {row.get('nom', 'inconnu')}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"Import Deezer: {len(df)} artistes")
    return len(df)

def get_statistics():
    """Afficher les statistiques"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total artistes
    cursor.execute("SELECT COUNT(*) FROM artistes")
    total = cursor.fetchone()[0]
    
    # Par source
    cursor.execute("SELECT source, COUNT(*) FROM artistes GROUP BY source")
    by_source = cursor.fetchall()
    
    # Par genre
    cursor.execute("SELECT genre, COUNT(*) FROM artistes WHERE genre IS NOT NULL AND genre != '' GROUP BY genre ORDER BY COUNT(*) DESC")
    by_genre = cursor.fetchall()
    
    # Par catégorie
    cursor.execute("SELECT categorie, COUNT(*) FROM artistes WHERE categorie IS NOT NULL AND categorie != '' GROUP BY categorie")
    by_category = cursor.fetchall()
    
    conn.close()
    
    print("STATISTIQUES BASE DE DONNÉES")
    print("="*70)
    print(f"\nTotal artistes: {total}")
    
    print(f"\n Par source:")
    for source, count in by_source:
        print(f"   - {source}: {count} artistes")
    
    print(f"\n Par genre:")
    for genre, count in by_genre[:10]:
        print(f"   - {genre}: {count} artistes")
    
    print(f"\n Par catégorie:")
    for cat, count in by_category:
        print(f"   - {cat}: {count} artistes")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    print("Import Base de Données")
    print("="*70)
    
    # Créer la base
    create_database()
    
    # Importer les données
    spotify_count = import_spotify()
    deezer_count = import_deezer()
    
    # Afficher les statistiques
    get_statistics()
    
    print("\nImport terminé")
    print(f"Base de données: {DB_PATH}")