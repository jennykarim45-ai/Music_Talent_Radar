"""
ml_prediction.py - Prédiction des futurs talents avec ML
Utilise un modèle simple pour identifier les artistes à fort potentiel
"""

import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/music_talent_radar_v2.db'

def main():
    """Générer prédictions ML"""
    print("GÉNÉRATION DES PRÉDICTIONS ML")
    
    try:
        # 1. Charger les données
        conn = sqlite3.connect(DB_PATH)
        
        df = pd.read_sql_query("""
            SELECT 
                nom_artiste as nom,
                plateforme,
                genre,
                fans_followers,
                followers,
                fans,
                popularity,
                score_potentiel,
                nb_albums,
                nb_releases_recentes
            FROM metriques_historique
            WHERE fans_followers > 0
        """, conn)
        
        conn.close()
        
        if len(df) == 0:
            print(" Aucune donnée dans la base")
            return False
        
        print(f" {len(df)} artistes chargés")
        
        # 2. Préparer les features
        df['followers'] = df['fans_followers'].fillna(0)
        df['popularity'] = df['popularity'].fillna(df['popularity'].mean())
        df['nb_albums'] = df['nb_albums'].fillna(0)
        df['nb_releases_recentes'] = df['nb_releases_recentes'].fillna(0)
        
        # Créer target (star = score > 70)
        df['is_star'] = (df['score_potentiel'] > 70).astype(int)
        
        # Features pour le modèle
        feature_cols = ['followers', 'popularity', 'score_potentiel', 'nb_albums', 'nb_releases_recentes']
        
        # Vérifier que les colonnes existent
        available_features = [col for col in feature_cols if col in df.columns]
        
        if len(available_features) < 3:
            print(" Pas assez de features disponibles")
            # Créer prédictions basiques sans ML
            df['proba_star'] = df['score_potentiel'] / 100
            predictions = df[['nom', 'plateforme', 'genre', 'followers', 'proba_star']].copy()
            predictions.to_csv('data/predictions_ml.csv', index=False)
            print(f" {len(predictions)} prédictions générées (mode basique)")
            return True
        
        X = df[available_features].fillna(0)
        y = df['is_star']
        
        # 3. Entraîner modèle simple
        if len(y.unique()) < 2:
            # Pas assez de variance - prédictions basiques
            df['proba_star'] = df['score_potentiel'] / 100
        else:
            # Normaliser
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Modèle Random Forest simple
            model = RandomForestClassifier(
                n_estimators=50,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_scaled, y)
            
            # Prédictions
            probas = model.predict_proba(X_scaled)[:, 1]
            df['proba_star'] = probas
        
        # 4. Sauvegarder
        predictions = df[['nom', 'plateforme', 'genre', 'followers', 'proba_star']].copy()
        predictions = predictions.sort_values('proba_star', ascending=False)
        predictions.to_csv('data/predictions_ml.csv', index=False)
        
        print(f" {len(predictions)} prédictions générées")
        
        # Stats
        stars_predicted = (predictions['proba_star'] > 0.5).sum()
        high_potential = (predictions['proba_star'] > 0.3).sum()
        
        print(f"\n Statistiques:")
        print(f"   Stars prédites (>50%): {stars_predicted}")
        print(f"   Haut potentiel (>30%): {high_potential}")
        print(f"   Probabilité moyenne: {predictions['proba_star'].mean():.1%}")
        
        return True
        
    except Exception as e:
        print(f" Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        # Créer fichier vide pour éviter erreurs
        pd.DataFrame({
            'nom': [],
            'plateforme': [],
            'genre': [],
            'followers': [],
            'proba_star': []
        }).to_csv('data/predictions_ml.csv', index=False)
        
        return False

if __name__ == '__main__':
    main()