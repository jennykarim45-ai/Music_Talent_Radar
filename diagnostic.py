import os
import pandas as pd
import sqlite3

print("="*70)
print("🔍 DIAGNOSTIC - Base de Données MusicTalentRadar")
print("="*70)

# 1. Vérifier les CSV
print("\n📂 ÉTAPE 1 : Vérification des CSV")
print("-"*70)

spotify_csv = "data/spotify_artists_20260112.csv"
deezer_csv = "data/deezer_artists_20260112.csv"

if os.path.exists(spotify_csv):
    df_spotify = pd.read_csv(spotify_csv)
    print(f"✅ {spotify_csv} trouvé")
    print(f"   📊 {len(df_spotify)} lignes")
    print(f"   📋 Colonnes : {', '.join(df_spotify.columns.tolist()[:5])}...")
else:
    print(f"❌ {spotify_csv} NON TROUVÉ")
    print(f"   📁 Cherche dans : {os.path.abspath('data/')}")

if os.path.exists(deezer_csv):
    df_deezer = pd.read_csv(deezer_csv)
    print(f"✅ {deezer_csv} trouvé")
    print(f"   📊 {len(df_deezer)} lignes")
    print(f"   📋 Colonnes : {', '.join(df_deezer.columns.tolist()[:5])}...")
else:
    print(f"❌ {deezer_csv} NON TROUVÉ")

# 2. Vérifier la base de données
print("\n💾 ÉTAPE 2 : Vérification de la Base de Données")
print("-"*70)

db_path = "data/music_talent_radar_v2.db"

if os.path.exists(db_path):
    print(f"✅ {db_path} trouvé")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Lister les tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"   📋 Tables : {[t[0] for t in tables]}")
    
    # Compter les artistes
    try:
        cursor.execute("SELECT COUNT(*) FROM artistes")
        count_artistes = cursor.fetchone()[0]
        print(f"   🎤 Artistes dans la DB : {count_artistes}")
        
        if count_artistes == 0:
            print("\n   ⚠️  LA BASE EST VIDE !")
            print("   💡 Solution : Exécute 'python database_manager_v2.py'")
        else:
            # Afficher quelques exemples
            cursor.execute("SELECT nom, source, score FROM artistes LIMIT 5")
            examples = cursor.fetchall()
            print("\n   📊 Exemples d'artistes :")
            for ex in examples:
                print(f"      - {ex[0]} ({ex[1]}) - Score: {ex[2]}")
    except Exception as e:
        print(f"   ❌ Erreur lecture table artistes : {e}")
    
    # Compter les métriques
    try:
        cursor.execute("SELECT COUNT(*) FROM metriques_historique")
        count_metriques = cursor.fetchone()[0]
        print(f"   📈 Métriques dans la DB : {count_metriques}")
    except:
        print("   ⚠️  Table metriques_historique non trouvée")
    
    conn.close()
else:
    print(f"❌ {db_path} NON TROUVÉ")
    print(f"   📁 Cherche dans : {os.path.abspath('data/')}")
    print(f"   💡 Solution : Exécute 'python database_manager_v2.py'")

# 3. Résumé
print("\n" + "="*70)
print("📊 RÉSUMÉ")
print("="*70)

csv_ok = os.path.exists(spotify_csv) and os.path.exists(deezer_csv)
db_ok = os.path.exists(db_path)

if csv_ok and db_ok:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM artistes")
    count = cursor.fetchone()[0]
    conn.close()
    
    if count > 0:
        print("✅ TOUT EST OK !")
        print(f"   {count} artistes dans la base")
    else:
        print("⚠️  BASE DE DONNÉES VIDE")
        print("\n💡 SOLUTION :")
        print("   python database_manager_v2.py")
elif csv_ok and not db_ok:
    print("⚠️  CSV OK mais base de données manquante")
    print("\n💡 SOLUTION :")
    print("   python database_manager_v2.py")
elif not csv_ok:
    print("❌ CSV MANQUANTS")
    print("\n💡 SOLUTION :")
    print("   1. Vérifie que les CSV sont dans data/")
    print("   2. Renomme-les en :")
    print("      - spotify_artists_20260112.csv")
    print("      - deezer_artists_20260112.csv")
else:
    print("❌ PROBLÈME DÉTECTÉ")
    print("\n💡 Vérifie les étapes ci-dessus")

print("\n" + "="*70)