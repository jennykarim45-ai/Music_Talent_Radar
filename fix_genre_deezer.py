"""
Script pour mapper les Autre → genre basé sur analyse
"""
import sqlite3

DB_PATH = 'data/music_talent_radar_v2.db'

def fix_autres_vers_rap():
    """Mapper tous les 'Autre' Deezer vers Rap-HipHop-RnB"""
    
    print(" MAPPING 'AUTRE' → RAP-HIPHOP-RNB\n")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Compter avant
    cursor.execute("""
        SELECT COUNT(*) FROM artistes 
        WHERE source = 'Deezer' AND genre = 'Autre'
    """)
    count_avant = cursor.fetchone()[0]
    
    print(f" Artistes Deezer 'Autre' : {count_avant}")
    
    # Mapper Autre → Rap-HipHop-RnB
    cursor.execute("""
        UPDATE artistes
        SET genre = 'Rap-HipHop-RnB'
        WHERE source = 'Deezer'
        AND genre = 'Autre'
    """)
    
    cursor.execute("""
        UPDATE metriques_historique
        SET genre = 'Rap-HipHop-RnB'
        WHERE plateforme = 'Deezer'
        AND genre = 'Autre'
    """)
    
    conn.commit()
    
    # Vérifier après
    cursor.execute("""
        SELECT genre, COUNT(*) 
        FROM artistes 
        WHERE source = 'Deezer'
        GROUP BY genre
        ORDER BY COUNT(*) DESC
    """)
    
    print("\n NOUVEAU RÉSULTAT:\n")
    for genre, count in cursor.fetchall():
        print(f"   {genre:20} : {count:3} artistes")
    
    conn.close()
    
    print("\n Tous les 'Autre' Deezer sont maintenant 'Rap-HipHop-RnB' !")

if __name__ == '__main__':
    fix_autres_vers_rap()