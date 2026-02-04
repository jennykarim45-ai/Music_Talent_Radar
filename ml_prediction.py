"""
ml_prediction.py v3.0 - Prédiction optimisée 

"""

import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils import resample
from sklearn.metrics import classification_report, confusion_matrix
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/music_talent_radar_v2.db'

def calculer_croissance_et_features():
    """Calculer croissance + features avancées"""
    print("\n Calcul de la croissance et features avancées...")
    
    conn = sqlite3.connect(DB_PATH)
    
    df = pd.read_sql_query("""
        SELECT 
            id_unique,
            nom_artiste as nom,
            plateforme,
            genre,
            fans_followers,
            followers,
            fans,
            popularity,
            nb_albums,
            nb_releases_recentes,
            score_potentiel,
            date_collecte
        FROM metriques_historique
        ORDER BY id_unique, date_collecte
    """, conn)
    
    conn.close()
    
    if len(df) == 0:
        return None
    
    df['date_collecte'] = pd.to_datetime(df['date_collecte'])
    
    croissances = []
    
    for id_unique in df['id_unique'].unique():
        artist_data = df[df['id_unique'] == id_unique].sort_values('date_collecte')
        
        if len(artist_data) < 2:
            continue
        
        premiere = artist_data.iloc[0]
        derniere = artist_data.iloc[-1]
        
        jours = (derniere['date_collecte'] - premiere['date_collecte']).days
        
        if jours < 1:
            continue
        
        # Followers
        followers_avant = premiere['fans_followers']
        followers_apres = derniere['fans_followers']
        
        if followers_avant > 0:
            croissance_pct = ((followers_apres - followers_avant) / followers_avant) * 100
            croissance_90j = (croissance_pct / jours) * 90
        else:
            croissance_pct = 0
            croissance_90j = 0
        
        # Label : explosion si croissance > 50% sur 90 jours
        a_explose = 1 if croissance_90j > 50 else 0
        
        #  FEATURES AVANCÉES
        
        # 1. Ratios
        ratio_followers_albums = derniere['fans_followers'] / max(derniere['nb_albums'], 1)
        ratio_releases_albums = derniere['nb_releases_recentes'] / max(derniere['nb_albums'], 1)
        
        # 2. Vélocité (croissance par jour)
        velocite = croissance_pct / max(jours, 1)
        
        # 3. Momentum (accélération)
        if len(artist_data) >= 3:
            milieu = artist_data.iloc[len(artist_data)//2]
            croissance_1 = ((milieu['fans_followers'] - premiere['fans_followers']) / max(premiere['fans_followers'], 1)) * 100
            croissance_2 = ((derniere['fans_followers'] - milieu['fans_followers']) / max(milieu['fans_followers'], 1)) * 100
            momentum = croissance_2 - croissance_1  # Accélération
        else:
            momentum = 0
        
        # 4. Engagement (proxy : popularity ou ratio fans/albums)
        engagement = derniere['popularity'] if pd.notna(derniere['popularity']) else ratio_followers_albums / 1000
        
        # 5. Activité récente (ratio releases récentes / total albums)
        activite_recente = derniere['nb_releases_recentes'] / max(derniere['nb_albums'], 1)
        
        # 6. Score de base (mais PAS utilisé comme feature principale)
        score_base = derniere['score_potentiel'] / 100
        
        # 7. Catégorie de taille
        if derniere['fans_followers'] < 5000:
            taille_categorie = 0  # Micro
        elif derniere['fans_followers'] < 15000:
            taille_categorie = 1  # Petit
        elif derniere['fans_followers'] < 30000:
            taille_categorie = 2  # Moyen
        else:
            taille_categorie = 3  # Large
        
        # 8. Maturité (albums / années depuis première release)
        maturite = derniere['nb_albums'] / max(jours / 365, 0.1)
        
        croissances.append({
            'id_unique': id_unique,
            'nom': derniere['nom'],
            'plateforme': derniere['plateforme'],
            'genre': derniere['genre'],
            
            # Features brutes
            'followers': derniere['fans_followers'],
            'popularity': derniere['popularity'] if pd.notna(derniere['popularity']) else 0,
            'nb_albums': derniere['nb_albums'],
            'nb_releases_recentes': derniere['nb_releases_recentes'],
            'jours_observation': jours,
            
            # Features dérivées ( IMPORTANTES!)
            'ratio_followers_albums': ratio_followers_albums,
            'ratio_releases_albums': ratio_releases_albums,
            'velocite': velocite,
            'momentum': momentum,
            'engagement': engagement,
            'activite_recente': activite_recente,
            'taille_categorie': taille_categorie,
            'maturite': maturite,
            
            # Target
            'croissance_pct': croissance_pct,
            'croissance_90j': croissance_90j,
            'a_explose': a_explose
        })
    
    df_croissance = pd.DataFrame(croissances)
    
    print(f" {len(df_croissance)} artistes avec historique")
    print(f"   Stars (explosé >50%): {(df_croissance['a_explose']==1).sum()}")
    print(f"   Non-stars: {(df_croissance['a_explose']==0).sum()}")
    
    return df_croissance

def main():
    """Générer prédictions ML optimisées"""
    print(" GÉNÉRATION DES PRÉDICTIONS ML v3.0 - OPTIMISÉE")
    
    try:
        # 1. Calculer croissance + features
        df = calculer_croissance_et_features()
        
        if df is None or len(df) < 20:
            print(" Pas assez de données pour ML optimisé")
            print(" Besoin de 20+ artistes avec historique")
            
            # Fallback
            conn = sqlite3.connect(DB_PATH)
            df_basic = pd.read_sql_query("""
                SELECT 
                    nom_artiste as nom,
                    plateforme,
                    genre,
                    fans_followers as followers,
                    score_potentiel
                FROM metriques_historique
            """, conn)
            conn.close()
            
            df_basic['proba_star'] = (df_basic['score_potentiel'] / 100).clip(0, 1)
            predictions = df_basic[['nom', 'plateforme', 'genre', 'followers', 'proba_star']].copy()
            predictions.to_csv('data/predictions_ml.csv', index=False)
            
            print(f" {len(predictions)} prédictions (mode basique)")
            return True
        
        # 2. Sélection des features
        print("\n Sélection des features...")
        
        # Features à utiliser ( TOUTES LES FEATURES DÉRIVÉES)
        feature_cols = [
            'followers',
            'popularity',
            'nb_albums',
            'nb_releases_recentes',
            'jours_observation',
            'ratio_followers_albums',
            'ratio_releases_albums',
            'velocite',
            'momentum',
            'engagement',
            'activite_recente',
            'taille_categorie',
            'maturite'
        ]
        
        print(f"   {len(feature_cols)} features sélectionnées")
        
        # Nettoyer
        for col in feature_cols:
            df[col] = df[col].fillna(df[col].median())
            df[col] = df[col].replace([np.inf, -np.inf], df[col].median())
        
        X = df[feature_cols].copy()
        y = df['a_explose'].copy()
        
        # 3. Équilibrage intelligent
        print("\n⚖️ Équilibrage des classes...")
        
        df_stars = df[df['a_explose'] == 1]
        df_non_stars = df[df['a_explose'] == 0]
        
        ratio_initial = len(df_stars) / len(df)
        print(f"   Avant : {len(df_stars)} stars ({ratio_initial:.1%}), {len(df_non_stars)} non-stars")
        
        # Si trop déséquilibré, rééquilibrer
        if len(df_non_stars) > len(df_stars) * 3:
            df_non_stars = resample(df_non_stars, n_samples=len(df_stars) * 3, random_state=42)
        elif len(df_stars) > len(df_non_stars) * 3:
            df_stars = resample(df_stars, n_samples=len(df_non_stars) * 3, random_state=42)
        
        df_balanced = pd.concat([df_stars, df_non_stars]).sample(frac=1, random_state=42)
        
        X_balanced = df_balanced[feature_cols]
        y_balanced = df_balanced['a_explose']
        
        print(f"   Après : {(y_balanced==1).sum()} stars, {(y_balanced==0).sum()} non-stars")
        
        # 4. Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_balanced, y_balanced, test_size=0.25, random_state=42, stratify=y_balanced
        )
        
        # 5. Normalisation
        print("\n🔧 Normalisation...")
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 6. HYPERPARAMETER TUNING avec GridSearch
        print("\n Optimisation des hyperparamètres...")
        
        param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [8, 10, 12, 15],
            'min_samples_split': [5, 10, 15],
            'min_samples_leaf': [2, 5, 8],
            'max_features': ['sqrt', 'log2']
        }
        
        rf_base = RandomForestClassifier(random_state=42, n_jobs=-1, class_weight='balanced')
        
        grid_search = GridSearchCV(
            rf_base,
            param_grid,
            cv=5,
            scoring='accuracy',
            n_jobs=-1,
            verbose=0
        )
        
        print("   Recherche des meilleurs paramètres (cela peut prendre 1-2 min)...")
        grid_search.fit(X_train_scaled, y_train)
        
        print(f"   ✅ Meilleurs paramètres trouvés :")
        for param, value in grid_search.best_params_.items():
            print(f"      {param}: {value}")
        
        best_model = grid_search.best_estimator_
        
        # 7. Validation croisée avec meilleur modèle
        print("\n📈 Validation croisée (5-fold) avec modèle optimisé...")
        cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        
        print(f"   Accuracy CV : {cv_scores.mean():.1%} (+/- {cv_scores.std():.1%})")
        print(f"   Scores individuels : {[f'{s:.1%}' for s in cv_scores]}")
        
        # 8. Test set
        accuracy_test = best_model.score(X_test_scaled, y_test)
        y_pred = best_model.predict(X_test_scaled)
        
        print(f"   Accuracy Test : {accuracy_test:.1%}")
        
        # 9. Rapport détaillé
        print("\n📊 Rapport de classification (Test Set):")
        print(classification_report(y_test, y_pred, target_names=['Non-star', 'Star'], digits=3))
        
        print("\n🔢 Matrice de confusion:")
        cm = confusion_matrix(y_test, y_pred)
        print(f"   TN: {cm[0,0]:3d} | FP: {cm[0,1]:3d}")
        print(f"   FN: {cm[1,0]:3d} | TP: {cm[1,1]:3d}")
        
        # 10. Calibration
        print("\n🔧 Calibration des probabilités...")
        model_calibre = CalibratedClassifierCV(best_model, cv=3, method='sigmoid')
        model_calibre.fit(X_train_scaled, y_train)
        
        # 11. Prédictions sur toutes les données
        print("\n🔮 Génération des prédictions finales...")
        
        X_all = df[feature_cols]
        X_all_scaled = scaler.transform(X_all)
        
        probas = model_calibre.predict_proba(X_all_scaled)[:, 1]
        df['proba_star'] = probas
        
        # 12. Feature importance
        print(f"\n🔍 Importance des features (Top 10):")
        importances = pd.DataFrame({
            'feature': feature_cols,
            'importance': best_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in importances.head(10).iterrows():
            print(f"   {row['feature']:30} : {row['importance']:.1%}")
        
        # 13. Sauvegarder
        predictions = df[['nom', 'plateforme', 'genre', 'followers', 'proba_star']].copy()
        predictions = predictions.drop_duplicates(subset=['nom', 'plateforme'], keep='last')
        predictions = predictions.sort_values('proba_star', ascending=False)
        predictions.to_csv('data/predictions_ml.csv', index=False)
        
        print(f"\n✅ {len(predictions)} prédictions générées")
        
        # 14. Statistiques finales
        print(f"\n📊 Statistiques finales:")
        print(f"   Stars prédites (>50%): {(predictions['proba_star'] > 0.5).sum()}")
        print(f"   Haut potentiel (>30%): {(predictions['proba_star'] > 0.3).sum()}")
        print(f"   Probabilité moyenne: {predictions['proba_star'].mean():.1%}")
        print(f"   Min: {predictions['proba_star'].min():.1%}, Max: {predictions['proba_star'].max():.1%}")
        print(f"\n🎯 PERFORMANCES FINALES:")
        print(f"   ✅ Accuracy CV (5-fold): {cv_scores.mean():.1%} ± {cv_scores.std():.1%}")
        print(f"   ✅ Accuracy Test: {accuracy_test:.1%}")
        
        return True
        
    except Exception as e:
        print(f" Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        pd.DataFrame({
            'nom': [], 'plateforme': [], 'genre': [], 'followers': [], 'proba_star': []
        }).to_csv('data/predictions_ml.csv', index=False)
        
        return False

if __name__ == '__main__':
    main()