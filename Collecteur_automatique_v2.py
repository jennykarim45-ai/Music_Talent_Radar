import subprocess
import sys
from datetime import datetime
import os

def run_command(command, description):
    """Execute une commande et affiche le resultat"""
    print(f"\n{'='*60}")
    print(f"ETAPE: {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        
        if result.stdout:
            print(result.stdout)
        
        print(f"OK - {description} termine avec succes")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"ERREUR lors de: {description}")
        print(f"Code erreur: {e.returncode}")
        if e.stdout:
            print(f"Sortie: {e.stdout}")
        if e.stderr:
            print(f"Erreur: {e.stderr}")
        return False

def main():
    print("\n" + "="*60)
    print("MUSIC TALENT RADAR v2 - COLLECTEUR AUTOMATIQUE")
    print("="*60)
    print(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Creer dossier data si necessaire
    os.makedirs('data', exist_ok=True)
    
    # Etape 1: Scraper Spotify
    success_spotify = run_command(
        f"{sys.executable} spotify_scraper_v2.py",
        "Scraping Spotify"
    )
    
    # Etape 2: Scraper Deezer
    success_deezer = run_command(
        f"{sys.executable} deezer_scraper_v2.py",
        "Scraping Deezer"
    )
    
    # Etape 3: Mise a jour base de donnees
    if success_spotify or success_deezer:
        success_db = run_command(
            f"{sys.executable} database_manager_v2.py",
            "Mise a jour base de donnees"
        )
    else:
        print("\nAucun scraping reussi, base de donnees non mise a jour")
        success_db = False
    
    # Rapport final
    print("\n" + "="*60)
    print("RAPPORT FINAL")
    print("="*60)
    print(f"Spotify: {'OK' if success_spotify else 'ECHEC'}")
    print(f"Deezer: {'OK' if success_deezer else 'ECHEC'}")
    print(f"Base de donnees: {'OK' if success_db else 'ECHEC'}")
    
    if success_spotify or success_deezer:
        print("\nCollection terminee avec succes!")
        print("Vous pouvez maintenant lancer le dashboard:")
        print("  streamlit run streamlit_app_v2.py")
    else:
        print("\nCollection echouee. Verifiez vos credentials API.")
    
    print("="*60)

if __name__ == "__main__":
    main()