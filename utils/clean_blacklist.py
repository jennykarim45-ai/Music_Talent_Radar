"""
Nettoyage de la blacklist 
Nettoie les fichiers CSV + DB
"""
import pandas as pd
import sqlite3
import unicodedata
import re
import os

BLACKLIST_ARTISTS = [
    "ryan gosling", "Missan", "La Plaie", "Jungle Jack", "Bleu Soleil","Soul Blues Icons "
    "emma stone", "Nour", "Oasis de musique jazz", "elyasbitum93200", "John Weezy B","Jazz de bonne humeur ",
    "Ebony"," ZZ", "Lauren Spencer-Smith", "Keshi","SG Lewis","Francis Lalanne","Église Momentum", 
    "Limsa d'aulnay", "Justin Hurwitz","A Flock of Seagulls","Prefab Sprout","Gary Numan",
    "RDN","Ultravox", "Ryflo", "Nakk Mendosa", "La Clinique", "Rich Chigga","Momentum Musique"
    "OPINEL 21", "ATK", "Tookie2Beriz","93PUNX","Adrian von Ziegler","Aztec Camera","Rap and Hip Hop Beat Mister"
    "Grandmaster Flash & The Furious Five", "Gorillaz", "Gary Numan", "Tubeway Army","François Dal's",
    "Philip Oakey", "Rich Brian", "Nicola Sirkis", "PLK","Kheops", "Janet Jackson","Barbie François",
    "Luther Vandross", "Eric Elmosnino","Sons de la Nature Projet France"," Marseille Capitale du Rap "
    "FUNK DEMON", "Ashvma","Lully Hill","DL91 Era","Jeez Suave", "Thisizlondon","Coco"
    "The Soul Jazz Era","Jamso", "Lenaïg", "Theomaa","19s Soulers","FRENCHGRL","Les Folies Françoises ",
    "Pescado Rabioso", "Jean-Luc Lahaye", "Starley", "Ici c'est Paris", "PARIS.","Walk in Paris",
    'Nicola Sirkis', 'Alain Chamfort', 'Francis Lalanne', 'David Castello-Lopes', 'ATK', 'F.F.F.',
    'Frànçois & The Atlas Mountains', 'Francis And The Lights', 'Francis Mercier', 'Charles Pasi', 'Ryan Paris', 'Stardust', 'Pop Will Eat Itself', 'Soulive',
    'Victoire Musique', 'Peppa Pig (Français)', 'Pinkfong en Français', 'Hazbin Hotel',"Jazz douce musique d'ambiance",
    "Oasis de musique jazz relaxant","The Paris Match ","Baroque Jazz Trio ","Jeremstar","K-Pop Demon Hunter","K-Pop",
    "Algéric","Elyon","Francis M","Félix Radu","KLN 93","Kham Meslien","Killemv","Lila-May","Marius Psalmiste","Mirella","Molière l'opéra urbain",
    "Pinpin OSP","RORI","Rock Bones","SKUNK","Sam Sauvage","Tommy Lyon","ZZCCMXTP","jean","Marseille Capitale du Rap","Sons de la Nature Projet France","Francis sentinelle",
]
    

def normaliser_nom(nom):
    if not nom or pd.isna(nom):
        return ""
    nom = str(nom).lower().strip()
    nom = unicodedata.normalize("NFD", nom)
    nom = "".join(c for c in nom if unicodedata.category(c) != "Mn")
    nom = re.sub(r"[^a-z0-9\s]", "", nom)
    nom = re.sub(r"\s+", " ", nom).strip()
    return nom

def est_en_blacklist(nom):
    """Vérifie si un artiste est dans la blacklist (matching strict)"""
    if not nom or pd.isna(nom):
        return False
    
    nom_normalise = normaliser_nom(nom)
    
    for blacklisted in BLACKLIST_ARTISTS:
        blacklisted_normalise = normaliser_nom(blacklisted)
        
        # Match exact
        if nom_normalise == blacklisted_normalise:
            return True
        
        # Match avec mots-clés pour noms composés
        # Ex: "Jean-Luc Lahaye" matche "jean luc lahaye"
        if len(blacklisted_normalise.split()) > 1:
            # Tous les mots doivent être présents
            mots = blacklisted_normalise.split()
            if all(mot in nom_normalise for mot in mots):
                return True
    
    return False

def nettoyer_csv(filepath):
    """Nettoie un fichier CSV"""
    if not os.path.exists(filepath):
        print(f"  {filepath} n'existe pas")
        return
    
    print(f"\n Nettoyage {filepath}...")
    df = pd.read_csv(filepath)
    count_avant = len(df)
    
    # Filtrer
    df_clean = df[~df['nom'].apply(est_en_blacklist)]
    count_apres = len(df_clean)
    removed = count_avant - count_apres
    
    if removed > 0:
        # Sauvegarder
        df_clean.to_csv(filepath, index=False)
        print(f"   Avant: {count_avant} artistes")
        print(f"   Après: {count_apres} artistes")
        print(f"     {removed} artistes supprimés")
        
        # Afficher les noms supprimés
        removed_names = df[df['nom'].apply(est_en_blacklist)]['nom'].unique()
        for nom in removed_names:
            print(f"      - {nom}")
    else:
        print(f"    Aucun artiste blacklisté trouvé")

# ============================================================================
# NETTOYAGE DE TOUS LES FICHIERS
# ============================================================================

print("=" * 70)
print(" NETTOYAGE COMPLET DE LA BLACKLIST")
print("=" * 70)

# 1. artist_urls.csv
nettoyer_csv('artist_urls.csv')

# 2. spotify_collected_latest.csv
nettoyer_csv('data/spotify_collected_latest.csv')

# 3. spotify_filtered.csv (IMPORTANT!)
nettoyer_csv('data/spotify_filtered.csv')

# 4. deezer_collected_latest.csv
nettoyer_csv('data/deezer_collected_latest.csv')

# 5. deezer_filtered.csv (IMPORTANT!)
nettoyer_csv('data/deezer_filtered.csv')

# 6. Tous les fichiers timestampés
print(f"\n Nettoyage des fichiers timestampés...")
import glob

for pattern in ['data/spotify_collected_*.csv', 'data/deezer_collected_*.csv']:
    files = glob.glob(pattern)
    for filepath in files:
        if 'latest' not in filepath:  # Déjà fait plus haut
            nettoyer_csv(filepath)

# ============================================================================
# BASE DE DONNÉES
# ============================================================================

print(f"\n{'=' * 70}")
print(" NETTOYAGE BASE DE DONNÉES")
print("=" * 70)

conn = sqlite3.connect('data/music_talent_radar_v2.db')
cursor = conn.cursor()

# Compter avant
cursor.execute("SELECT COUNT(*) FROM artistes")
count_artistes_avant = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM metriques_historique")
count_metriques_avant = cursor.fetchone()[0]

print(f"\nAvant:")
print(f"   Artistes: {count_artistes_avant}")
print(f"   Métriques: {count_metriques_avant}")

# Supprimer artistes blacklistés
removed_artistes = []

cursor.execute("SELECT DISTINCT nom FROM artistes")
all_names = cursor.fetchall()

for (nom,) in all_names:
    if est_en_blacklist(nom):
        removed_artistes.append(nom)
        
        # Supprimer de toutes les tables
        cursor.execute("DELETE FROM artistes WHERE nom = ?", (nom,))
        cursor.execute("DELETE FROM metriques_historique WHERE nom_artiste = ?", (nom,))
        cursor.execute("DELETE FROM alertes WHERE nom_artiste = ?", (nom,))

# Compter après
cursor.execute("SELECT COUNT(*) FROM artistes")
count_artistes_apres = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM metriques_historique")
count_metriques_apres = cursor.fetchone()[0]

conn.commit()
conn.close()

print(f"\nAprès:")
print(f"   Artistes: {count_artistes_apres}")
print(f"   Métriques: {count_metriques_apres}")

if removed_artistes:
    print(f"\n  {len(removed_artistes)} artistes supprimés de la BDD:")
    for nom in removed_artistes:
        print(f"   - {nom}")
else:
    print(f"\n Aucun artiste blacklisté trouvé dans la BDD")

print(" NETTOYAGE TERMINÉ")

print("\n Prochaine étape:")
print("   1. Relance Streamlit: streamlit run app/streamlit.py")
print("   2. Appuie sur 'R' pour recharger le cache")
