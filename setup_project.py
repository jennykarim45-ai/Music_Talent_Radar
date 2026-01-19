import os
import sqlite3

def create_project_structure():
    """Cree la structure de dossiers du projet"""
    
    print("\n" + "="*60)
    print("MUSICTALENTRADAR V2 - SETUP INITIAL")
    print("="*60)
    
    # Creer dossier data
    if not os.path.exists('data'):
        os.makedirs('data')
        print("OK - Dossier 'data' cree")
    else:
        print("OK - Dossier 'data' existe deja")
    
    # Initialiser la base de donnees
    db_path = 'data/music_talent_radar_v2.db'
    
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Table artistes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS artistes (
                id_unique TEXT PRIMARY KEY,
                nom TEXT NOT NULL,
                source TEXT NOT NULL,
                genre TEXT NOT NULL,
                date_premiere_detection DATE NOT NULL,
                date_derniere_maj DATE NOT NULL
            )
        ''')
        
        # Table metriques historique
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS metriques_historique (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_unique TEXT NOT NULL,
                date_collecte DATE NOT NULL,
                fans_followers INTEGER,
                popularity INTEGER,
                score REAL,
                categorie TEXT,
                url TEXT,
                image_url TEXT,
                FOREIGN KEY (id_unique) REFERENCES artistes(id_unique)
            )
        ''')
        
        # Index
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON metriques_historique(date_collecte)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON artistes(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_genre ON artistes(genre)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_score ON metriques_historique(score)')
        
        conn.commit()
        conn.close()
        
        print("OK - Base de donnees initialisee")
    else:
        print("OK - Base de donnees existe deja")
    
    # Creer fichier .gitignore si necessaire
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# Data
data/*.csv
*.db

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
"""
    
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write(gitignore_content)
        print("OK - Fichier .gitignore cree")
    else:
        print("OK - Fichier .gitignore existe deja")
    
    print("\n" + "="*60)
    print("SETUP TERMINE!")
    print("="*60)
    print("\nProchaines etapes:")
    print("1. Configurez vos credentials Spotify dans spotify_scraper_v2.py")
    print("2. Lancez la collection: python collecteur_automatique_v2.py")
    print("3. Lancez le dashboard: streamlit run streamlit_app_v2.py")
    print("\nConsultez le README.md pour plus de details")
    print("="*60)

if __name__ == "__main__":
    create_project_structure()