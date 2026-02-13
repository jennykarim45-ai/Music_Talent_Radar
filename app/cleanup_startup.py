"""
Script de nettoyage des doublons - Exécuté au démarrage de l'app
"""
import sqlite3
import os

DB_PATH = 'data/music_talent_radar_v2.db'

def cleanup_duplicates():
    """Nettoie les doublons au démarrage"""
    if not os.path.exists(DB_PATH):
        return
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Supprimer les doublons
        cursor.execute("""
            DELETE FROM metriques_historique
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM metriques_historique
                GROUP BY date(date_collecte), id_unique
            )
        """)
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        print(f"Erreur nettoyage : {e}")

if __name__ == "__main__":
    cleanup_duplicates()