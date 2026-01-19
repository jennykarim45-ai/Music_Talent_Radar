"""
PIPELINE ETL - MusicTalentRadar v2
===================================
Pipeline Extract-Transform-Load pour la collecte et l'analyse 
d'artistes musicaux émergents depuis Spotify et Deezer.


"""

import subprocess
import sys
import pandas as pd
import os
from datetime import datetime
import logging
import json

# Configuration du logging
os.makedirs('logs', exist_ok=True)
log_filename = f"logs/pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class MusicTalentRadarETL:
    """Pipeline ETL pour MusicTalentRadar v2"""
    
    def __init__(self):
        self.stats = {
            'start_time': datetime.now(),
            'end_time': None,
            'duration_seconds': None,
            'spotify_artists': 0,
            'deezer_artists': 0,
            'total_artists': 0,
            'artists_after_cleaning': 0,
            'duplicates_removed': 0,
            'orchestres_removed': 0,
            'enfants_removed': 0,
            'errors': []
        }
        
        self.data_dir = 'data'
        os.makedirs(self.data_dir, exist_ok=True)
    
    def run_script(self, script_name, description):
        """
        Exécute un script Python et gère les erreurs.
        
        Args:
            script_name (str): Nom du script à exécuter
            description (str): Description de l'étape
            
        Returns:
            bool: True si succès, False sinon
        """
        logger.info("="*70)
        logger.info(f" {description}")
        logger.info("="*70)
        
        try:
            result = subprocess.run(
                [sys.executable, script_name],
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            # Afficher la sortie
            if result.stdout:
                print(result.stdout)
            
            logger.info(f" {description} - SUCCÈS")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f" {description} - ÉCHEC")
            logger.error(f"Code erreur: {e.returncode}")
            
            if e.stdout:
                logger.error(f"Sortie: {e.stdout[:500]}")
            if e.stderr:
                logger.error(f"Erreur: {e.stderr[:500]}")
            
            self.stats['errors'].append({
                'script': script_name,
                'description': description,
                'error': str(e)
            })
            
            return False
            
        except FileNotFoundError:
            logger.error(f" Fichier introuvable: {script_name}")
            self.stats['errors'].append({
                'script': script_name,
                'description': description,
                'error': 'Fichier introuvable'
            })
            return False
    
    def extract(self):
        """
        PHASE 1 - EXTRACT: Collecte des données depuis APIs
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 1 - EXTRACT: Collecte des données")
        logger.info("="*70)
        
        today = datetime.now().strftime('%Y%m%d')
        spotify_file = f"{self.data_dir}/spotify_artists_{today}.csv"
        deezer_file = f"{self.data_dir}/deezer_artists_{today}.csv"
        
        # Vérifier si les CSV existent déjà
        spotify_exists = os.path.exists(spotify_file)
        deezer_exists = os.path.exists(deezer_file)
        
        if spotify_exists and deezer_exists:
            logger.info(" Les données du jour existent déjà !")
            logger.info(f"   • {spotify_file}")
            logger.info(f"   • {deezer_file}")
            logger.info("   → Skip de la collecte, utilisation des données existantes")
            
            # Compter les artistes existants
            try:
                df_spotify = pd.read_csv(spotify_file)
                self.stats['spotify_artists'] = len(df_spotify)
                logger.info(f" Spotify: {self.stats['spotify_artists']} artistes (existants)")
            except Exception as e:
                logger.warning(f" Impossible de lire {spotify_file}: {e}")
            
            try:
                df_deezer = pd.read_csv(deezer_file)
                self.stats['deezer_artists'] = len(df_deezer)
                logger.info(f" Deezer: {self.stats['deezer_artists']} artistes (existants)")
            except Exception as e:
                logger.warning(f" Impossible de lire {deezer_file}: {e}")
            
            self.stats['total_artists'] = self.stats['spotify_artists'] + self.stats['deezer_artists']
            logger.info(f"\n Phase Extract terminée: {self.stats['total_artists']} artistes au total")
            return True
        
        # Sinon, lancer les scrapers
        logger.info(" Lancement de la collecte...\n")
        
        # Spotify
        if not spotify_exists:
            logger.info(" Collecte Spotify nécessaire...")
            spotify_success = self.run_script(
                'spotify_scraper_v2.py',
                'Collecte Spotify'
            )
        else:
            logger.info(" Spotify déjà collecté aujourd'hui, skip")
            spotify_success = True
        
        if spotify_success:
            # Compter les artistes Spotify
            try:
                if os.path.exists(spotify_file):
                    df_spotify = pd.read_csv(spotify_file)
                    self.stats['spotify_artists'] = len(df_spotify)
                    logger.info(f" Spotify: {self.stats['spotify_artists']} artistes collectés")
            except Exception as e:
                logger.warning(f" Impossible de lire le fichier Spotify: {e}")
        
        # Deezer
        if not deezer_exists:
            logger.info("\n Collecte Deezer nécessaire...")
            deezer_success = self.run_script(
                'deezer_scraper_v2.py',
                'Collecte Deezer'
            )
        else:
            logger.info(" Deezer déjà collecté aujourd'hui, skip")
            deezer_success = True
        
        if deezer_success:
            # Compter les artistes Deezer
            try:
                if os.path.exists(deezer_file):
                    df_deezer = pd.read_csv(deezer_file)
                    self.stats['deezer_artists'] = len(df_deezer)
                    logger.info(f" Deezer: {self.stats['deezer_artists']} artistes collectés")
            except Exception as e:
                logger.warning(f" Impossible de lire le fichier Deezer: {e}")
        
        self.stats['total_artists'] = self.stats['spotify_artists'] + self.stats['deezer_artists']
        
        if not spotify_success and not deezer_success:
            logger.error(" ÉCHEC TOTAL DE LA COLLECTE")
            return False
        
        logger.info(f"\n Phase Extract terminée: {self.stats['total_artists']} artistes au total")
        return True
    
    def transform(self):
        """
        PHASE 2 - TRANSFORM: Nettoyage et transformation des données
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 2 - TRANSFORM: Nettoyage des données")
        logger.info("="*70)
        
        # Étape 1 : Nettoyage initial (doublons, etc.)
        nettoyage1_success = self.run_script(
            'nettoyage_spotify_scraper.py',
            'Nettoyage initial (doublons, données invalides)'
        )
        
        if nettoyage1_success:
            try:
                today = datetime.now().strftime('%Y%m%d')
                cleaned_file = f"{self.data_dir}/spotify_artists_cleaned_{today}.csv"
                
                if os.path.exists(cleaned_file):
                    df_cleaned = pd.read_csv(cleaned_file)
                    logger.info(f" Après nettoyage initial: {len(df_cleaned)} artistes")
            except Exception as e:
                logger.warning(f" Impossible de lire le fichier nettoyé: {e}")
        
        # Étape 2 : Suppression orchestres, DJs, contenu enfants
        nettoyage2_success = self.run_script(
            'suppressionorchestrespotify.py',
            'Suppression orchestres, DJs, contenu enfants'
        )
        
        if nettoyage2_success:
            # Calculer les statistiques finales
            try:
                today = datetime.now().strftime('%Y%m%d')
                # Chercher le fichier final (peut avoir différents noms)
                possible_files = [
                    f"{self.data_dir}/spotify_artists_final_{today}.csv",
                    f"{self.data_dir}/spotify_artists_cleaned_{today}.csv"
                ]
                
                for final_file in possible_files:
                    if os.path.exists(final_file):
                        df_final = pd.read_csv(final_file)
                        self.stats['artists_after_cleaning'] = len(df_final)
                        self.stats['duplicates_removed'] = self.stats['total_artists'] - len(df_final)
                        
                        logger.info(f" Après nettoyage final: {self.stats['artists_after_cleaning']} artistes")
                        logger.info(f" Total supprimés: {self.stats['duplicates_removed']} artistes")
                        break
            except Exception as e:
                logger.warning(f" Impossible de calculer les stats finales: {e}")
        
        success = nettoyage1_success or nettoyage2_success
        logger.info("\n Phase Transform terminée")
        return success
    
    def load(self):
        """
        PHASE 3 - LOAD: Chargement en base de données
        """
        logger.info("\n" + "="*70)
        logger.info("PHASE 3 - LOAD: Chargement en base de données")
        logger.info("="*70)
        
        success = self.run_script(
            'database_manager_v2.py',
            'Import dans SQLite'
        )
        
        if success:
            # Vérifier la base de données
            db_file = f"{self.data_dir}/music_talent_radar_v2.db"
            if os.path.exists(db_file):
                db_size = os.path.getsize(db_file) / (1024 * 1024)  # En MB
                logger.info(f" Base de données: {db_size:.2f} MB")
        
        logger.info("\nPhase Load terminée")
        return success
    
    def generate_report(self):
        """Génère un rapport final du pipeline"""
        self.stats['end_time'] = datetime.now()
        self.stats['duration_seconds'] = (
            self.stats['end_time'] - self.stats['start_time']
        ).total_seconds()
        
        logger.info("\n" + "="*70)
        logger.info(" RAPPORT FINAL DU PIPELINE ETL")
        logger.info("="*70)
        
        logger.info(f"\n Durée totale: {self.stats['duration_seconds']:.0f} secondes "
                   f"({self.stats['duration_seconds']/60:.1f} minutes)")
        
        logger.info(f"\n EXTRACT:")
        logger.info(f"  • Spotify: {self.stats['spotify_artists']} artistes")
        logger.info(f"  • Deezer: {self.stats['deezer_artists']} artistes")
        logger.info(f"  • Total collecté: {self.stats['total_artists']} artistes")
        
        logger.info(f"\n TRANSFORM:")
        logger.info(f"  • Après nettoyage: {self.stats['artists_after_cleaning']} artistes")
        logger.info(f"  • Supprimés: {self.stats['duplicates_removed']} artistes")
        
        logger.info(f"\n LOAD:")
        logger.info(f"  • Base de données: data/music_talent_radar_v2.db")
        
        if self.stats['errors']:
            logger.warning(f"\n ERREURS ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                logger.warning(f"  • {error['description']}: {error['error']}")
        else:
            logger.info("\n Aucune erreur")
        
        # Sauvegarder les stats en JSON
        stats_file = f"logs/stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convertir les datetime en string pour JSON
        stats_json = self.stats.copy()
        stats_json['start_time'] = stats_json['start_time'].isoformat()
        stats_json['end_time'] = stats_json['end_time'].isoformat()
        
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats_json, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n Statistiques sauvegardées: {stats_file}")
        logger.info(f" Logs sauvegardés: {log_filename}")
        
        logger.info("\n" + "="*70)
        logger.info(" PIPELINE ETL TERMINÉ")
        logger.info("="*70)
    
    def run(self):
        """
        Exécute le pipeline ETL complet.
        
        Returns:
            bool: True si succès complet, False sinon
        """
        logger.info("\n" + "="*70)
        logger.info(" MUSICTALENTRADAR v2 - PIPELINE ETL")
        logger.info("="*70)
        logger.info(f"Début: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("\nCritères de détection:")
        logger.info("  • Spotify: 1,000 - 50,000 followers")
        logger.info("  • Deezer: 1,000 - 20,000 fans")
        logger.info("  • 10 genres musicaux")
        
        try:
            # PHASE 1: Extract
            if not self.extract():
                logger.error(" La phase Extract a échoué")
                self.generate_report()
                return False
            
            # PHASE 2: Transform
            if not self.transform():
                logger.warning(" La phase Transform a échoué, mais on continue...")
            
            # PHASE 3: Load
            if not self.load():
                logger.warning(" La phase Load a échoué")
            
            # Rapport final
            self.generate_report()
            
            return len(self.stats['errors']) == 0
            
        except KeyboardInterrupt:
            logger.warning("\n Pipeline interrompu par l'utilisateur")
            self.generate_report()
            return False
            
        except Exception as e:
            logger.error(f"\n Erreur critique: {e}")
            import traceback
            logger.error(traceback.format_exc())
            self.generate_report()
            return False


def main():
    """Point d'entrée du pipeline"""
    print("""
    ╔════════════════════════════════════════════════════════════╗
    ║          MUSICTALENTRADAR v2 - PIPELINE ETL               ║
    ║                                                            ║
    ║  Détection d'artistes musicaux émergents                  ║
    ║  Wild Code School - Projet Data Analyst                   ║
    ╚════════════════════════════════════════════════════════════╝
    """)
    
    # Créer et exécuter le pipeline
    pipeline = MusicTalentRadarETL()
    success = pipeline.run()
    
    # Code de sortie
    if success:
        print("\n Pipeline ETL exécuté avec succès !")
        print(f"\n Prochaine étape: streamlit run streamlit.py")
        sys.exit(0)
    else:
        print("\n Le pipeline a rencontré des erreurs.")
        print(f" Consultez les logs: {log_filename}")
        sys.exit(1)


if __name__ == "__main__":
    main()