import pandas as pd
import sqlite3
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

DATABASE_PATH = "data/music_talent_radar_v2.db"

def main():
    print("Entrainement du modele ML...")
    
    # Charger les donnees DEPUIS LA BASE DE DONNEES
    conn = sqlite3.connect(DATABASE_PATH)
    
    query = """
        SELECT 
            a.nom,
            a.genre,
            a.source as plateforme,
            m.fans_followers,
            m.popularity,
            m.score
        FROM artistes a
        INNER JOIN metriques_historique m ON a.id_unique = m.id_unique
        WHERE m.date_collecte = (
            SELECT MAX(date_collecte) FROM metriques_historique WHERE id_unique = a.id_unique
        )
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if len(df) == 0:
        print("ERREUR: Aucune donnee disponible dans la base")
        return
    
    print(f"OK: {len(df)} artistes charges depuis la base de donnees")
    
    # Features avec normalisation
    df['popularity'] = df['popularity'].fillna(df['fans_followers'] / 1000)
    df['engagement'] = df['popularity'] / (df['fans_followers'] / 1000)
    df['engagement'] = df['engagement'].fillna(0).replace([float('inf'), float('-inf')], 0)
    
    # Ajouter feature ratio score/followers
    df['score_per_follower'] = df['score'] / (df['fans_followers'] / 1000)
    df['score_per_follower'] = df['score_per_follower'].fillna(0).replace([float('inf'), float('-inf')], 0)
    
    # Label : top 10% = potentiel star (au lieu de 30%)
    threshold = df['score'].quantile(0.90)  # TOP 10% uniquement
    df['is_star'] = (df['score'] >= threshold).astype(int)
    
    print(f"Seuil 'star': {threshold:.1f}")
    print(f"{df['is_star'].sum()} artistes classes 'star' (top 10%)")
    
    # Preparer X et y avec plus de features
    X = df[['fans_followers', 'popularity', 'engagement', 'score_per_follower']].fillna(0)
    y = df['is_star']
    
    # Verifier qu'on a assez de donnees
    if len(df) < 10:
        print("ATTENTION: Pas assez de donnees pour entrainer le modele (minimum 10)")
        return
    
    # Split
    test_size = min(0.2, 5 / len(df))  # Au moins 5 exemples en test
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)
    
    # Normalisation
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Modele avec regularisation forte pour eviter overfitting
    model = LogisticRegression(
        max_iter=1000, 
        random_state=42,
        C=0.1,  # Regularisation forte
        class_weight='balanced'  # Equilibrer les classes
    )
    model.fit(X_train_scaled, y_train)
    
    # Score
    score = model.score(X_test_scaled, y_test)
    print(f"Precision du modele: {score:.2%}")
    
    # Predictions sur tout le dataset
    X_all_scaled = scaler.transform(X)
    df['proba_star'] = model.predict_proba(X_all_scaled)[:, 1]
    
    # Sauvegarder avec colonne 'followers' pour Streamlit
    predictions = df[['nom', 'genre', 'plateforme', 'score', 'proba_star']].copy()
    predictions['followers'] = df['fans_followers']
    predictions = predictions.sort_values('proba_star', ascending=False)
    predictions.to_csv('data/predictions_ml.csv', index=False, encoding='utf-8-sig')
    
    print(f"Predictions sauvegardees: data/predictions_ml.csv")
    print(f"\nTop 5 artistes a fort potentiel:")
    for idx, row in predictions.head(5).iterrows():
        print(f"  - {row['nom']}: {row['proba_star']:.1%} (score: {row['score']:.1f}, {int(row['followers'])} followers)")

if __name__ == "__main__":
    main()