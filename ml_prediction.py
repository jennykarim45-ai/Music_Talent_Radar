"""
ml_prediction.py - Génération des prédictions ML optimisées pour le Music Talent Radar
"""

import pandas as pd
import numpy as np
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils import resample
from sklearn.metrics import classification_report, confusion_matrix
from datetime import datetime, timedelta
import json
import warnings
warnings.filterwarnings('ignore')

DB_PATH = 'data/music_talent_radar_v2.db'

def save_ml_metrics(y_true, y_pred, y_pred_proba):
    """Sauvegarde les métriques ML pour affichage dans Streamlit"""
    
    # Matrice de confusion
    cm = confusion_matrix(y_true, y_pred)
    
    # Rapport de classification
    report = classification_report(y_true, y_pred, output_dict=True)
    
    # Sauvegarder dans un fichier JSON
    metrics = {
        'confusion_matrix': cm.tolist(),
        'classification_report': report,
        'accuracy': report['accuracy'],
        'total_samples': len(y_true),
        'stars_count': int(y_true.sum()),
        'non_stars_count': int((y_true == 0).sum())
    }
    
    with open('data/ml_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print("Métriques ML sauvegardées dans data/ml_metrics.json")

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
        print(" Aucune donnée dans metriques_historique")
        return None
    
    print(f" {len(df)} métriques au total")
    
    df['date_collecte'] = pd.to_datetime(df['date_collecte'])
    
    artistes_uniques = df['id_unique'].nunique()
    print(f" {artistes_uniques} artistes uniques")
    
    collectes_par_artiste = df.groupby('id_unique').size()
    artistes_avec_historique = (collectes_par_artiste >= 2).sum()
    print(f" {artistes_avec_historique} artistes avec 2+ collectes")
    
    if artistes_avec_historique == 0:
        print(" PAS ASSEZ D'ARTISTES AVEC HISTORIQUE !")
        print(f"   Besoin : 2+ artistes avec au moins 2 collectes")
        print(f"   Actuellement : {artistes_avec_historique} artistes")
        return None
    
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
        
        followers_avant = premiere['fans_followers']
        followers_apres = derniere['fans_followers']
        
        if followers_avant > 0:
            croissance_pct = ((followers_apres - followers_avant) / followers_avant) * 100
            croissance_90j = (croissance_pct / jours) * 90
        else:
            croissance_pct = 0
            croissance_90j = 0
        
        a_explose = 1 if croissance_90j > 15 else 0
        
        # Features avancées
        ratio_followers_albums = derniere['fans_followers'] / max(derniere['nb_albums'], 1)
        ratio_releases_albums = derniere['nb_releases_recentes'] / max(derniere['nb_albums'], 1)
        velocite = croissance_pct / max(jours, 1)
        
        if len(artist_data) >= 3:
            milieu = artist_data.iloc[len(artist_data)//2]
            croissance_1 = ((milieu['fans_followers'] - premiere['fans_followers']) / max(premiere['fans_followers'], 1)) * 100
            croissance_2 = ((derniere['fans_followers'] - milieu['fans_followers']) / max(milieu['fans_followers'], 1)) * 100
            momentum = croissance_2 - croissance_1
        else:
            momentum = 0
        
        engagement = derniere['popularity'] if pd.notna(derniere['popularity']) else ratio_followers_albums / 1000
        activite_recente = derniere['nb_releases_recentes'] / max(derniere['nb_albums'], 1)
        
        if derniere['fans_followers'] < 5000:
            taille_categorie = 0
        elif derniere['fans_followers'] < 15000:
            taille_categorie = 1
        elif derniere['fans_followers'] < 30000:
            taille_categorie = 2
        else:
            taille_categorie = 3
        
        maturite = derniere['nb_albums'] / max(jours / 365, 0.1)
        
        croissances.append({
            'id_unique': id_unique,
            'nom': derniere['nom'],
            'plateforme': derniere['plateforme'],
            'genre': derniere['genre'],
            'followers': derniere['fans_followers'],
            'popularity': derniere['popularity'] if pd.notna(derniere['popularity']) else 0,
            'nb_albums': derniere['nb_albums'],
            'nb_releases_recentes': derniere['nb_releases_recentes'],
            'jours_observation': jours,
            'ratio_followers_albums': ratio_followers_albums,
            'ratio_releases_albums': ratio_releases_albums,
            'velocite': velocite,
            'momentum': momentum,
            'engagement': engagement,
            'activite_recente': activite_recente,
            'taille_categorie': taille_categorie,
            'maturite': maturite,
            'croissance_pct': croissance_pct,
            'croissance_90j': croissance_90j,
            'a_explose': a_explose
        })
    
    if not croissances:
        print(" Aucune croissance calculée !")
        return None
    
    df_croissance = pd.DataFrame(croissances)
    
    nb_stars = (df_croissance['a_explose']==1).sum()
    nb_non_stars = (df_croissance['a_explose']==0).sum()
    
    print(f" {len(df_croissance)} artistes avec historique")
    print(f"    Stars (>15% croissance): {nb_stars}")
    print(f"    Non-stars: {nb_non_stars}")
    
    return df_croissance

def main():
    """Générer prédictions ML optimisées"""
    print(" GÉNÉRATION DES PRÉDICTIONS ML v3.1")
    
    try:
        df = calculer_croissance_et_features()
        
        if df is None or len(df) < 10:
            print(" Pas assez de données pour ML optimisé")
            print("   Besoin de 10+ artistes avec historique")
            
            # Fallback basique
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
        
        # Compter stars
        nb_stars = (df['a_explose'] == 1).sum()
        
        print(f" Dataset : {len(df)} artistes, {nb_stars} stars")
        
        # Features
        feature_cols = [
            'followers', 'popularity', 'nb_albums', 'nb_releases_recentes',
            'jours_observation', 'ratio_followers_albums', 'ratio_releases_albums',
            'velocite', 'momentum', 'engagement', 'activite_recente',
            'taille_categorie', 'maturite'
        ]
        
        for col in feature_cols:
            df[col] = df[col].fillna(df[col].median())
            df[col] = df[col].replace([np.inf, -np.inf], df[col].median())
        
        X = df[feature_cols].copy()
        y = df['a_explose'].copy()
        
        # Équilibrage intelligent
        df_stars = df[df['a_explose'] == 1]
        df_non_stars = df[df['a_explose'] == 0]
        
        print(" Équilibrage des classes...")
        print(f"   Avant : {len(df_stars)} stars, {len(df_non_stars)} non-stars")
        
        if len(df_non_stars) > len(df_stars) * 3:
            df_non_stars = resample(df_non_stars, n_samples=len(df_stars) * 3, random_state=42)
        elif len(df_stars) > len(df_non_stars) * 3:
            df_stars = resample(df_stars, n_samples=len(df_non_stars) * 3, random_state=42)
        
        df_balanced = pd.concat([df_stars, df_non_stars]).sample(frac=1, random_state=42)
        
        X_balanced = df_balanced[feature_cols]
        y_balanced = df_balanced['a_explose']
        
        print(f"   Après : {(y_balanced==1).sum()} stars, {(y_balanced==0).sum()} non-stars")
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X_balanced, y_balanced, test_size=0.25, random_state=42, stratify=y_balanced
        )
        
        # Normalisation
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Modèle simple (pas de GridSearch si petit dataset)
        if nb_stars < 10:
            print("\n Mode simple (peu de stars, pas de GridSearch)")
            model = RandomForestClassifier(
                n_estimators=200,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                class_weight='balanced',
                n_jobs=-1
            )
        else:
            print("\n🔧 Mode optimisé (GridSearch)")
            from sklearn.model_selection import GridSearchCV
            
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [8, 10, 12],
                'min_samples_split': [5, 10],
                'min_samples_leaf': [2, 5]
            }
            
            rf_base = RandomForestClassifier(random_state=42, n_jobs=-1, class_weight='balanced')
            grid_search = GridSearchCV(rf_base, param_grid, cv=3, scoring='accuracy', n_jobs=-1)
            grid_search.fit(X_train_scaled, y_train)
            model = grid_search.best_estimator_
            
            print(f"   Meilleurs params: {grid_search.best_params_}")
        
        # Fit du modèle
        model.fit(X_train_scaled, y_train)
        
        # Validation croisée
        print("\n Validation croisée...")
        try:
            cv_folds = min(5, (y_train == 1).sum())
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=cv_folds, scoring='accuracy')
            print(f"   Accuracy CV ({cv_folds}-fold): {cv_scores.mean():.1%} ± {cv_scores.std():.1%}")
        except:
            print("    CV impossible (dataset trop petit)")
        
        # Test
        accuracy_test = model.score(X_test_scaled, y_test)
        y_pred_test = model.predict(X_test_scaled)
        
        print(f"   Accuracy Test : {accuracy_test:.1%}")
        
        # Calibration conditionnelle
        print("\n Calibration...")
        
        nb_stars_train = (y_train == 1).sum()
        
        if nb_stars_train >= 9:
            print(f"    Calibration possible ({nb_stars_train} stars en train)")
            try:
                model_calibre = CalibratedClassifierCV(model, cv=3, method='sigmoid')
                model_calibre.fit(X_train_scaled, y_train)
                print("    Calibration réussie")
            except Exception as e:
                print(f"    Erreur calibration: {e}")
                print("   → Utilisation modèle non calibré")
                model_calibre = model
        elif nb_stars_train >= 4:
            print(f"    Peu de stars ({nb_stars_train}), calibration 2-fold")
            try:
                model_calibre = CalibratedClassifierCV(model, cv=2, method='sigmoid')
                model_calibre.fit(X_train_scaled, y_train)
                print("    Calibration 2-fold réussie")
            except Exception as e:
                print(f"    Erreur calibration: {e}")
                print("   → Utilisation modèle non calibré")
                model_calibre = model
        else:
            print(f"    Trop peu de stars ({nb_stars_train}), pas de calibration")
            model_calibre = model
        
        #  SAUVEGARDER MÉTRIQUES POUR STREAMLIT
        print(" Sauvegarde métriques pour visualisation...")
        y_pred_proba_test = model_calibre.predict_proba(X_test_scaled)[:, 1]
        save_ml_metrics(y_test, y_pred_test, y_pred_proba_test)
        
        # Prédictions finales
        print(" Génération des prédictions finales...")
        
        X_all = df[feature_cols]
        X_all_scaled = scaler.transform(X_all)
        
        probas = model_calibre.predict_proba(X_all_scaled)[:, 1]
        df['proba_star'] = probas
        
        # Feature importance
        print(f"\ Top 5 features importantes:")
        importances = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        for idx, row in importances.head(5).iterrows():
            print(f"   {row['feature']:30} : {row['importance']:.1%}")
        
        # Sauvegarde
        predictions = df[['nom', 'plateforme', 'genre', 'followers', 'proba_star']].copy()
        predictions = predictions.drop_duplicates(subset=['nom', 'plateforme'], keep='last')
        predictions = predictions.sort_values('proba_star', ascending=False)
        predictions.to_csv('data/predictions_ml.csv', index=False)
        
        print(f"\ {len(predictions)} prédictions générées")
        
        # Stats
        print(f"\ Statistiques finales:")
        print(f"   Stars prédites (>15%): {(predictions['proba_star'] > 0.15).sum()}")
        print(f"   Haut potentiel (>5%): {(predictions['proba_star'] > 0.05).sum()}")
        print(f"   Probabilité moyenne: {predictions['proba_star'].mean():.1%}")
        print(f"   Min: {predictions['proba_star'].min():.1%}, Max: {predictions['proba_star'].max():.1%}")
        
        return True
        
    except Exception as e:
        print(f" Erreur: {e}")
        import traceback
        traceback.print_exc()
        
        # Créer fichier vide pour éviter erreur Streamlit
        pd.DataFrame({
            'nom': [], 'plateforme': [], 'genre': [], 'followers': [], 'proba_star': []
        }).to_csv('data/predictions_ml.csv', index=False)
        
        return False

if __name__ == '__main__':
    main()