import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import os
import json
from PIL import Image
import math
import base64
import auth  
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Détection de l'environnement
try:
    import psycopg2 # type: ignore
    from psycopg2.extras import RealDictCursor # type: ignore
    USE_POSTGRES = True
    DB_URL = st.secrets["DATABASE_URL"]
except:
    import sqlite3
    USE_POSTGRES = False
    DB_NAME = 'data/music_talent_radar_v2.db'

st.set_page_config(
    page_title="JEK2 Records - Music Talent Radar",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

import streamlit.components.v1 as components

# Désactive les reruns automatiques sur certains événements
if 'init' not in st.session_state:
    st.session_state.init = True
    
# Initialiser les artistes intéressés dans session_state
if 'artistes_interesses' not in st.session_state:
    st.session_state.artistes_interesses = []

if 'temp_interesses_artistes' not in st.session_state:
    st.session_state.temp_interesses_artistes = []

if 'temp_interesse_evolution' not in st.session_state:
    st.session_state.temp_interesse_evolution = None

if 'page_artistes' not in st.session_state:
    st.session_state.page_artistes = 1
    
if 'selected_artist_evolution' not in st.session_state:
    st.session_state.selected_artist_evolution = None

if 'go_to_evolution' not in st.session_state:
    st.session_state.go_to_evolution = False

# ==================== NAVIGATION ====================
# Au début du fichier, après les imports

# Initialiser la page active (UNE SEULE FOIS)
if 'active_page' not in st.session_state:
    st.session_state.active_page = "Vue d'ensemble"

# Gérer les demandes de navigation AVANT le reste
if st.session_state.get('go_to_evolution', False):
    st.session_state.active_page = "Évolution"
    st.session_state.go_to_evolution = False



# ============= AUTHENTIFICATION =============
if not auth.require_authentication(): # type: ignore
    if st.session_state.get('show_login', False):
        auth.login_form() # type: ignore
    else:
        auth.public_page_about() # type: ignore
    st.stop()
# ============= SIDEBAR =============
with st.sidebar:
    # Liste des pages
    pages = ["Vue d'ensemble", "Les Tops", "Les artistes", "Évolution", "Alertes", "Prédictions", "A propos", "Mon Profil"]
    
    # Trouver l'index de la page active
    try:
        current_index = pages.index(st.session_state.active_page)
    except:
        current_index = 0
        st.session_state.active_page = pages[0]
    
    # Radio sans callback
    selected_page = st.radio(
        "",
        pages,
        index=current_index,
        label_visibility="collapsed",  
        key="nav_radio"
    )

    if selected_page != st.session_state.active_page:
        st.session_state.active_page = selected_page
        st.rerun()  
# ============================================

COLORS = {
    'primary': '#FF1B8D',
    'secondary': "#323A79",
    'accent1': "#47559D",
    'accent2': "#4A0B7E",
    'accent3': "#21B178",
    'bg_dark': "#070707",
    'bg_card': "#000000",
    'text': "#B18E57"
}

# Fonction pour charger l'image de fond
def get_base64_image(image_path):
    """Convertit une image en base64 pour l'utiliser en CSS"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Charger l'image de fond
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
background_path = os.path.join(BASE_DIR, "assets", "back.png")
bg_image = get_base64_image(background_path)

# CSS avec image de fond
if bg_image:
    bg_style = f"""
    background-image: url("data:image/jpg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
    """
else:
    bg_style = f"background: linear-gradient(135deg, {COLORS['bg_dark']} 0%, #1a0a2e 100%);"

st.markdown(f"""
    <style>
    
    /* MASQUER BARRE STREAMLIT */
    [data-testid="stHeader"] {{ display: none !important; }}
    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}

    /* HEADER FIXE */
    .fixed-header {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 999;
        background: linear-gradient(135deg, #070707 0%, #1a0a2e 100%);
        padding: 1rem 2rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
        border-bottom: 2px solid #FF1B8D;
    }}

    .fixed-header::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(7, 7, 7, 0.85);
        z-index: -1;
    }}

    /* MODIFIER CETTE LIGNE EXISTANTE (cherche ".main > div") */
    .main > div {{
        padding-top: 180px !important;  /* Au lieu de 1rem */
        position: relative;
        z-index: 1;
    }}

    /* RESPONSIVE */
    @media (max-width: 768px) {{
        .fixed-header {{ padding: 0.5rem 1rem; }}
        .main > div {{ padding-top: 140px !important; }}
        .fixed-header img {{ width: 80px !important; }}
    }}
    /* Fond principal avec image */
    .stApp {{
        {bg_style}
        font-size: 0.99rem !important;
    }}
    
    /* Overlay semi-transparent */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(7, 7, 7, 0.7);
        z-index: 0;
        pointer-events: none;
    }}
    
    /* Contenu au-dessus de l'overlay */
    .main > div {{
        position: relative;
        z-index: 1;
    }}
    
    /* RÉDUCTION GLOBALE DRASTIQUE */
    .main {{
        padding-top: 180px !important;
        padding-bottom: 1rem !important;
        max-width: 1400px !important;
    }}
    
    /* Header principal - TRÈS RÉDUIT */
    .main-header {{
        font-size: 1.5rem !important;
        font-weight: 900;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent1']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0.3rem 0 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }}
    
    .subtitle {{
        color: {COLORS['accent3']};
        text-align: center;
        font-size: 0.99rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    /* Sidebar ULTRA COMPACT */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['bg_card']} 0%, #1a0a2e 100%);
        padding-top: 0 !important;
        min-width: 200px !important;
        max-width: 240px !important;
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.5rem !important;
        margin-top: 0 !important;
        padding-left: 0.5rem !important;
        padding-right: 0.5rem !important;
    }}
    
    /* Labels sidebar */
    [data-testid="stSidebar"] label {{
        font-size: 0.99rem !important;
        margin-bottom: 0.2rem !important;
    }}
    
    /* Selectbox sidebar */
    [data-testid="stSidebar"] .stSelectbox {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Slider sidebar */
    [data-testid="stSidebar"] .stSlider {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Radio buttons sidebar */
    [data-testid="stSidebar"] .stRadio {{
        font-size: 0.99rem !important;
    }}
    
    [data-testid="stSidebar"] .stRadio > label {{
        font-size: 0.99rem !important;
        padding: 0.3rem 0 !important;
    }}
    
    /* Logo sidebar */
    [data-testid="stSidebar"] img {{
        max-width: 120px !important;
        margin: 0.5rem auto !important;
    }}
    
    /* Boutons - TRÈS RÉDUITS */
    .stButton button {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent2']});
        color: white;
        border: none;
        border-radius: 15px !important;
        padding: 0.3rem 1rem !important;
        font-weight: bold !important;
        font-size: 0.99rem !important;
        min-height: 30px !important;
    }}
    
    /* Link buttons */
    .stLinkButton a {{
        padding: 0.3rem 1rem !important;
        font-size: 0.99rem !important;
        min-height: 30px !important;
    }}
    
    /* Titres h1, h2, h3 - TRÈS RÉDUITS */
    h1, h2, h3 {{
        color: {COLORS['accent3']} !important;
        font-weight: 900 !important;
        font-size: 1.5rem !important;
        margin-top: 0.3rem !important;
        margin-bottom: 0.3rem !important;
        line-height: 1.3 !important;
    }}
    
    h2 {{
        font-size: 1.5rem !important;
    }}
    
    h3 {{
        font-size: 1.1rem !important;
    }}
    
    /* Markdown headers */
    .stMarkdown h1 {{
        font-size: 1.5rem !important;
    }}
    
    .stMarkdown h2 {{
        font-size: 1.5rem !important;
    }}
    
    .stMarkdown h3 {{
        font-size: 1.1rem !important;
    }}
    
    /* Métriques - TRÈS RÉDUITES */
    [data-testid="stMetricValue"] {{
        color: white !important;
        font-size: 1.5rem !important;
        font-weight: bold !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {COLORS['text']} !important;
        font-weight: 600 !important;
        font-size: 0.99rem !important;
    }}
    
    [data-testid="stMetric"] {{
        padding: 0.3rem !important;
        background: rgba(0,0,0,0.3) !important;
        border-radius: 8px !important;
    }}
    
    /* Cartes métriques - TRÈS RÉDUITES */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #2a1a3e 100%);
        padding: 0.8rem !important;
        border-radius: 8px !important;
        border-left: 2px solid {COLORS['primary']} !important;
        box-shadow: 0 4px 8px rgba(255, 27, 141, 0.2) !important;
        margin: 0.5rem 0 !important;
    }}
    
    .metric-card h3 {{
        font-size: 1.1rem !important;
        margin-bottom: 0.5rem !important;
    }}
    
    .metric-card p {{
        font-size: 0.99rem !important;
        line-height: 1.4 !important;
        margin-bottom: 0.3rem !important;
    }}
    
    /* Textes */
    .stMarkdown, p, li {{
        color: {COLORS['text']} !important;
        font-size: 0.99rem !important;
        line-height: 1.4 !important;
    }}
    
    .info-box {{
        background: linear-gradient(135deg, #1a0a2e 0%, #2a1a3e 100%);
        padding: 0.8rem !important;
        border-radius: 8px !important;
        border-left: 2px solid {COLORS['accent1']} !important;
        margin: 0.5rem 0 !important;
    }}
    
    .info-box h4 {{
        font-size: 1.5rem !important;
        margin-bottom: 0.4rem !important;
    }}
    
    .info-box p {{
        font-size: 0.99rem !important;
    }}
    
    /* Captions */
    .stCaption {{
        font-size: 0.99rem !important;
        line-height: 1.3 !important;
    }}
    
    /* Espacement des colonnes - TRÈS RÉDUIT */
    [data-testid="column"] {{
        padding: 0.3rem !important;
    }}
    
    /* Dividers */
    hr {{
        margin: 0.8rem 0 !important;
        border-color: rgba(255,255,255,0.1) !important;
    }}
    
    /* Checkbox */
    .stCheckbox {{
        font-size: 0.99rem !important;
    }}
    
    /* Images artistes */
    [data-testid="stImage"] {{
        margin-bottom: 0.3rem !important;
    }}
    
    /* Graphiques Plotly - RÉDUIRE MARGES */
    .js-plotly-plot {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* Espacement entre sections */
    .element-container {{
        margin-bottom: 0.5rem !important;
    }}
    
    /* RESPONSIVE */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: 1.5rem !important;
        }}
        
        .subtitle {{
            font-size: 0.99rem !important;
        }}
    }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=600, show_spinner="Chargement des données...")
def load_data():
    """Charge les données depuis PostgreSQL ou SQLite"""
    try:
        if USE_POSTGRES:
            conn = psycopg2.connect(DB_URL)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='artistes' AND column_name='genre'
            """)
            has_genre = cursor.fetchone() is not None
            
            artistes_df = pd.read_sql_query("SELECT * FROM artistes", conn)
            
            metriques_df = pd.read_sql_query("""
                SELECT m.*, a.nom as nom_artiste, a.url, a.plateforme as platform
                FROM metriques_historique m
                LEFT JOIN artistes a ON m.artist_id = a.artist_id AND m.plateforme = a.plateforme
                ORDER BY m.date_collecte DESC
            """, conn)
            
            if has_genre:
                metriques_df = metriques_df.merge(
                    artistes_df[['artist_id', 'plateforme', 'genre']], 
                    on=['artist_id', 'plateforme'], 
                    how='left'
                )
            else:
                metriques_df['genre'] = 'Tous'
            
            alertes_df = pd.read_sql_query(
                "SELECT * FROM alertes WHERE vu = FALSE ORDER BY date_alerte DESC", conn
            )
            
        else:
            conn = sqlite3.connect(DB_NAME)
            
            artistes_df = pd.read_sql_query("SELECT * FROM artistes", conn)
            
            artistes_df['artist_id'] = artistes_df['id_unique']
            artistes_df['plateforme'] = artistes_df['source']
            
            metriques_df = pd.read_sql_query("""
                SELECT 
                    m.*,
                    a.nom as nom_artiste,
                    a.source as plateforme,
                    a.genre
                FROM metriques_historique m
                LEFT JOIN artistes a ON m.id_unique = a.id_unique
                ORDER BY m.date_collecte DESC
            """, conn)
            
            metriques_df['artist_id'] = metriques_df['id_unique']
            
            # Ajouter url et image_url depuis artistes_df
            if 'url_spotify' in artistes_df.columns or 'url_deezer' in artistes_df.columns:
                # Créer colonne url unifiée
                artistes_df['url'] = artistes_df.apply(
                    lambda row: row.get('url_spotify') if pd.notna(row.get('url_spotify')) else row.get('url_deezer', ''),
                    axis=1
                )
                # Merger url et image_url
                if 'image_url' in artistes_df.columns:
                    metriques_df = metriques_df.merge(
                        artistes_df[['id_unique', 'url', 'image_url']], 
                        on='id_unique', 
                        how='left'
                    )
                else:
                    metriques_df = metriques_df.merge(
                        artistes_df[['id_unique', 'url']], 
                        on='id_unique', 
                        how='left'
                    )
                    metriques_df['image_url'] = ''
            
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alertes'")
            if cursor.fetchone():
                alertes_df = pd.read_sql_query(
                    "SELECT * FROM alertes WHERE vu = 0 ORDER BY date_alerte DESC", conn
                )
            else:
                alertes_df = pd.DataFrame()
        
        conn.close()
        return artistes_df, metriques_df, alertes_df
        
    except Exception as e:
        st.error(f" Erreur chargement données: {e}")
        import traceback
        st.error(traceback.format_exc())
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
# APRÈS la fonction load_data()

@st.cache_data(ttl=3600)
def get_latest_metrics_cached(metriques_df_json):
    """Version cachée de get_latest_metrics"""
    metriques_df = pd.read_json(metriques_df_json)
    return get_latest_metrics(metriques_df)

@st.cache_data(ttl=3600)
def apply_filters(df, plateforme, genre, fans_cat, min_score, max_fans):
    """Applique les filtres - CACHED"""
    filtered = df.copy()
    
    # Exclure Electro-EDM
    if 'genre' in filtered.columns:
        filtered = filtered[filtered['genre'] != "Electro-EDM"]
    
    if plateforme != 'Tous':
        filtered = filtered[filtered['plateforme'] == plateforme]
    if genre != 'Tous':
        filtered = filtered[filtered['genre'] == genre]
    if fans_cat != 'Tous':
        filtered = filtered[filtered['categorie_fans'] == fans_cat]
    
    filtered = filtered[filtered['score_potentiel'] >= min_score]
    filtered = filtered[filtered['followers_total'] <= max_fans]
    
    return filtered.reset_index(drop=True)

@st.cache_data(ttl=3600)
def create_bar_chart(data, x, y, color, title):
    """Crée un graphique Plotly - CACHED"""
    fig = px.bar(data, x=x, y=y, color=color)
    fig.update_layout(
        plot_bgcolor=COLORS['bg_card'],
        paper_bgcolor=COLORS['bg_card'],
        font_color=COLORS['text'],
        title=title
    )
    return fig

@st.cache_data(ttl=600)  
def get_latest_metrics(metriques_df_json):
    """Récupère les dernières métriques par artiste/plateforme - CACHED"""
    # Convertir JSON → DataFrame
    metriques_df = pd.read_json(metriques_df_json, orient='split')
    
    if metriques_df.empty:
        return pd.DataFrame()
    
    try:
        # Convertir date_collecte en datetime
        metriques_df['date_collecte'] = pd.to_datetime(metriques_df['date_collecte'], errors='coerce')
        
        # Trier par date (plus récent en premier)
        metriques_df = metriques_df.sort_values('date_collecte', ascending=False)
        
        # Garder seulement la première ligne (la plus récente) pour chaque artiste/plateforme
        if 'id_unique' in metriques_df.columns and 'plateforme' in metriques_df.columns:
            latest = metriques_df.drop_duplicates(subset=['id_unique', 'plateforme'], keep='first')
        elif 'nom_artiste' in metriques_df.columns and 'plateforme' in metriques_df.columns:
            latest = metriques_df.drop_duplicates(subset=['nom_artiste', 'plateforme'], keep='first')
        else:
            if 'nom_artiste' in metriques_df.columns:
                latest = metriques_df.drop_duplicates(subset=['nom_artiste'], keep='first')
            else:
                latest = metriques_df
        
        return latest.reset_index(drop=True)
        
    except Exception as e:
        print(f"  Erreur dans get_latest_metrics: {e}")
        return metriques_df.sort_values('date_collecte', ascending=False) if 'date_collecte' in metriques_df.columns else metriques_df

def get_fan_category(fans):
    """Catégorise par nombre de fans"""
    if fans < 500:
        return "Micro (1k-5k)"
    elif fans < 10000:
        return "Petit (5k-10k)"
    elif fans < 20000:
        return "Moyen (10k-20k)"
    else:
        return "Large (20k-40k)"

# ==================== CHARGEMENT DONNÉES ====================
try:
    artistes_df, metriques_df, alertes_df = load_data()
    
    #  NETTOYER TOUS LES DATAFRAMES (CRITIQUE!)
    artistes_df = artistes_df.loc[:, ~artistes_df.columns.duplicated()]
    metriques_df = metriques_df.loc[:, ~metriques_df.columns.duplicated()]
    if not alertes_df.empty:
        alertes_df = alertes_df.loc[:, ~alertes_df.columns.duplicated()]
    
    #  RÉCUPÉRER image_url depuis artistes_df
    if 'id_unique' in metriques_df.columns and 'id_unique' in artistes_df.columns and 'image_url' in artistes_df.columns:
        temp_images = artistes_df[['id_unique', 'image_url']].drop_duplicates('id_unique')
        metriques_df = metriques_df.merge(temp_images, on='id_unique', how='left', suffixes=('', '_from_artistes'))
        if 'image_url_from_artistes' in metriques_df.columns:
            if 'image_url' not in metriques_df.columns:
                metriques_df['image_url'] = metriques_df['image_url_from_artistes']
            else:
                metriques_df['image_url'] = metriques_df['image_url'].fillna(metriques_df['image_url_from_artistes'])
            metriques_df = metriques_df.drop('image_url_from_artistes', axis=1)
    
    if artistes_df.empty or metriques_df.empty:
        st.error(" Base de données vide ou inaccessible")
        st.info(" Importez vos données avec le script approprié")
        st.stop()
    
    # ==================== TRAITEMENT DES MÉTRIQUES ====================
    
    # Fonction cachée pour ajouter les URLs
    @st.cache_data(ttl=600)
    def add_urls_to_metrics(metrics_json, artistes_json):
        """Ajoute les URLs aux métriques - CACHED"""
        metrics_df = pd.read_json(metrics_json, orient='split')
        artistes_df = pd.read_json(artistes_json, orient='split')
        
        if 'url' not in metrics_df.columns:
            metrics_df['url'] = ''
            
            if 'id_unique' in metrics_df.columns and 'id_unique' in artistes_df.columns:
                # Créer un mapping id_unique → url
                url_mapping = {}
                
                for _, artist_row in artistes_df.iterrows():
                    id_unique = artist_row.get('id_unique')
                    url_spotify = artist_row.get('url_spotify', '')
                    url_deezer = artist_row.get('url_deezer', '')
                    
                    url = url_spotify if url_spotify and pd.notna(url_spotify) else url_deezer
                    if url and pd.notna(url):
                        url_mapping[id_unique] = url
                
                # Appliquer le mapping
                metrics_df['url'] = metrics_df['id_unique'].map(url_mapping).fillna('')
        
        return metrics_df
    
    # Récupérer les dernières métriques (avec cache)
    latest_metrics_df = get_latest_metrics(metriques_df.to_json(orient='split'))
    
    # Ajouter les URLs (CACHED)
    latest_metrics_df = add_urls_to_metrics(
        latest_metrics_df.to_json(orient='split'),
        artistes_df.to_json(orient='split')
    )
    
    # Pareil pour metriques_df complet
    metriques_df = add_urls_to_metrics(
        metriques_df.to_json(orient='split'),
        artistes_df.to_json(orient='split')
    )
    
    # Conversion scores
    if 'score' in latest_metrics_df.columns and 'score_potentiel' not in latest_metrics_df.columns:
        latest_metrics_df['score_potentiel'] = pd.to_numeric(latest_metrics_df['score'], errors='coerce')
        metriques_df['score_potentiel'] = pd.to_numeric(metriques_df['score'], errors='coerce')
    else:
        latest_metrics_df['score_potentiel'] = pd.to_numeric(latest_metrics_df.get('score_potentiel', 0), errors='coerce')
        metriques_df['score_potentiel'] = pd.to_numeric(metriques_df.get('score_potentiel', 0), errors='coerce')
    
    # Calcul followers total
    if 'fans_followers' in latest_metrics_df.columns:
        latest_metrics_df['followers_total'] = latest_metrics_df['fans_followers'].fillna(0)
    else:
        latest_metrics_df['followers_total'] = latest_metrics_df.get('followers', 0).fillna(0) + latest_metrics_df.get('fans', 0).fillna(0)
    
    # Catégorie fans
    latest_metrics_df['categorie_fans'] = latest_metrics_df['followers_total'].apply(get_fan_category)
    
except Exception as e:
    st.error(f" Erreur critique: {e}")
    st.stop()
    

# ==================== HEADER FIXE ====================
logo_base64 = get_base64_image(os.path.join(BASE_DIR, "assets", "logo.png"))

if logo_base64:
    st.markdown(f"""
        <div class="fixed-header">
            <div style="display: flex; align-items: center; justify-content: center; gap: 250px; max-width: 1400px; margin: 0 auto;">
                <div style="flex-shrink: 0;">
                    <img src="data:image/png;base64,{logo_base64}" style="width: 150px; height: auto;">
                </div>
                <div style="text-align: center;">
                    <div class="main-header">JEK2 RECORDS</div>
                    <div class="subtitle">⭐ MUSIC TALENT RADAR ⭐</div>
                </div>
                <div style="flex-shrink: 0;">
                    <img src="data:image/png;base64,{logo_base64}" style="width: 150px; height: auto;">
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="fixed-header">
            <div style="display: flex; align-items: center; justify-content: center; gap: 250px; max-width: 1400px; margin: 0 auto;">
                <div style="flex-shrink: 0;">
                    <div style="width: 100px; height: 100px; background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; box-shadow: 0 4px 12px rgba(255, 27, 141, 0.4);">🎵</div>
                </div>
                <div style="text-align: center;">
                    <div class="main-header">JEK2 RECORDS</div>
                    <div class="subtitle">⭐ MUSIC TALENT RADAR ⭐</div>
                </div>
                <div style="flex-shrink: 0;">
                    <div style="width: 100px; height: 100px; background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2.5rem; box-shadow: 0 4px 12px rgba(255, 27, 141, 0.4);">🎵</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
# ==================== SIDEBAR ====================
with st.sidebar:
    # Filtres
    plateformes_disponibles = []
    if 'plateforme' in latest_metrics_df.columns and len(latest_metrics_df) > 0:
        try:
            plateformes_disponibles = list(latest_metrics_df['plateforme'].dropna().unique())
        except:
            plateformes_disponibles = []
    plateformes = ['Tous'] + sorted([p for p in plateformes_disponibles if p])
    selected_plateforme = st.selectbox("🌐 Source", plateformes)
    
    genres_disponibles = []
    if 'genre' in latest_metrics_df.columns and len(latest_metrics_df) > 0:
        try:
            genres_disponibles = list(latest_metrics_df['genre'].dropna().unique())
            genres_disponibles = [g for g in genres_disponibles if g and g != 'Electro-EDM']
        except:
            genres_disponibles = []
    genres = ['Tous'] + sorted(genres_disponibles)
    selected_genre = st.selectbox("🎵 Genre Musical", genres)
    
    categories_fans = ['Tous', 'Micro (1k-5k)', 'Petit (5k-10k)', 'Moyen (10k-20k)', 'Large (20k-40k)']
    selected_fans = st.selectbox("👥 Nombre de fans", categories_fans)
    max_fans = st.slider("👥 Followers/Fans maximum", 100, 40000, 40000, 1000)    
    min_score = st.slider("⭐ Score minimum", 0, 100, 0, 5)

    # Logo sans espace
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
    if os.path.isfile(logo_path):
        st.image(logo_path, width=200)
# ==================== FILTRES ====================
filtered_df = apply_filters(
    latest_metrics_df,
    selected_plateforme,
    selected_genre,
    selected_fans,
    min_score,
    max_fans
)


# Top artistes
top_df = filtered_df.sort_values('score_potentiel', ascending=False).reset_index(drop=True)

# SUPPRIMER COLONNES DUPLIQUÉES + RESET INDEX
filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
top_df = top_df.loc[:, ~top_df.columns.duplicated()]
filtered_df = filtered_df.reset_index(drop=True)
top_df = top_df.reset_index(drop=True)

# ==================== GÉNÉRER PRÉDICTIONS SI MANQUANT ====================
if not os.path.exists('data/predictions_ml.csv'):
    st.info(" Génération des prédictions ML en cours...")
    try:
        import ml_prediction
        ml_prediction.main()
        st.success(" Prédictions générées !")
    except Exception as e:
        st.warning(f" Impossible de générer les prédictions : {e}")
        
# ==================== TAB CLASSIQUES ====================
# Gérer les query params pour la navigation
query_params = st.query_params

# Déterminer l'onglet actif
if 'tab' in query_params:
    tab_actif = query_params['tab']
else:
    tab_actif = 'vue_ensemble'

# Mapper les noms d'onglets
TAB_MAPPING = {
    'vue_ensemble': 0,
    'top': 1,
    'explorer': 2,
    'evolution': 3,
    'alertes': 4,
    'predictions': 5,
    'profil': 6,
    'connexion': 7
}

# Index de l'onglet actif
if tab_actif in TAB_MAPPING:
    selected_tab_index = TAB_MAPPING[tab_actif]
else:
    selected_tab_index = 0

# ==================== STYLE PERSONNALISÉ POUR LES TABS ====================
st.markdown("""
    <style>
    /* Style des onglets (tabs) */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: #0E0E0E;  /* Fond noir */
        padding: 10px;
        border-radius: 10px;
    }}
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;  /* Hauteur augmentée */
        background-color: #1a1a1a;  /* Fond gris foncé pour chaque tab */
        border-radius: 8px;
        padding: 0 24px;  /* Plus d'espace horizontal */
        font-size: 1.1rem;  /* Texte plus grand */
        font-weight: 600;  /* Texte en gras */
        color: #FFFFFF;  /* Texte blanc */
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #2a2a2a;  /* Fond plus clair au survol */
        border: 2px solid #FF1B8D;  /* Bordure rose au survol */
        transform: translateY(-2px);  /* Petit effet de levée */
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #FF1B8D 0%, #47559D 100%);  /* Dégradé rose-bleu */
        color: #FFFFFF !important;
        border: 2px solid #FF1B8D;
        font-weight: 700;
        box-shadow: 0 4px 12px rgba(255, 27, 141, 0.4);  /* Ombre lumineuse */
    }
    
    /* Icônes/emojis plus grands */
    .stTabs [data-baseweb="tab"] span {
        font-size: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)


# ==================== AFFICHAGE SELON PAGE ACTIVE ====================

# Initialiser session_state pour la navigation
if 'artiste_selectionne' not in st.session_state:
    st.session_state['artiste_selectionne'] = None

# ==================== TAB 1: VUE D'ENSEMBLE ====================
@st.cache_data(ttl=3600)
def generer_camembert_streamlit():
    """Génère le camembert Spotify vs Deezer - PLOTLY (style uniforme)"""
    
    if USE_POSTGRES:
        conn = psycopg2.connect(DB_URL)
    else:
        conn = sqlite3.connect(DB_NAME)
    
    query = """
        SELECT plateforme, COUNT(DISTINCT nom_artiste) as nb_artistes
        FROM metriques_historique
        GROUP BY plateforme
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        return None
    
    #  PLOTLY PIE CHART
    fig = px.pie(
        df,
        values='nb_artistes',
        names='plateforme',
        color='plateforme',
        color_discrete_map={
            'Spotify': '#1DB954',  # Vert Spotify
            'Deezer': '#4169E1'    # Bleu Deezer
        },
        hole=0  # 
    )
    #  STYLE IDENTIQUE 
    fig.update_layout(
        plot_bgcolor=COLORS['bg_card'],     # Fond noir
        paper_bgcolor=COLORS['bg_card'],    # Fond noir
        font_color=COLORS['text'],          # Texte doré
        height=350,                         # Hauteur réduite
        margin=dict(l=25, r=25, t=25, b=25),
        showlegend=True,
        legend=dict(
            font=dict(color='white', size=12),
            orientation='v',
            yanchor='middle',
            y=0.5,
            xanchor='left',
            x=1.02
        )
    )
    
    # Texte blanc et pourcentages visibles
    fig.update_traces(
        textfont_color='white',
        textfont_size=14,
        textposition='inside',
        texttemplate='%{percent:.1%}',
        textinfo='percent+label'
    )
    
    return fig


@st.cache_data(ttl=3600)
def generer_nuage_points_streamlit():
    """Génère un nuage de points Score vs Followers - PLOTLY (style uniforme)"""
    
    if USE_POSTGRES:
        conn = psycopg2.connect(DB_URL)
    else:
        conn = sqlite3.connect(DB_NAME)
    
    # ✅ SOLUTION : 2 requêtes séparées + concat en Python
    query_spotify = """
        SELECT 
            nom_artiste,
            plateforme,
            score_potentiel,
            fans_followers,
            genre
        FROM metriques_historique
        WHERE score_potentiel > 0 
        AND fans_followers > 0
        AND plateforme = 'Spotify'
        ORDER BY score_potentiel DESC
        LIMIT 200
    """
    
    query_deezer = """
        SELECT 
            nom_artiste,
            plateforme,
            score_potentiel,
            fans_followers,
            genre
        FROM metriques_historique
        WHERE score_potentiel > 0 
        AND fans_followers > 0
        AND plateforme = 'Deezer'
        ORDER BY score_potentiel DESC
        LIMIT 200
    """
    
    # Exécuter les 2 requêtes
    df_spotify = pd.read_sql_query(query_spotify, conn)
    df_deezer = pd.read_sql_query(query_deezer, conn)
    
    # Combiner les résultats
    df = pd.concat([df_spotify, df_deezer], ignore_index=True)
    
    conn.close()
    
    if df.empty:
        return None
    
    # PLOTLY SCATTER
    fig = px.scatter(
        df,
        x='score_potentiel',
        y='fans_followers',
        color='plateforme',
        color_discrete_map={
            'Spotify': '#1DB954',
            'Deezer': '#4169E1'
        },
        labels={
            'score_potentiel': 'Score de Potentiel',
            'fans_followers': 'Nombre de Followers/Fans',
            'plateforme': 'Plateforme'
        },
        hover_data={
            'nom_artiste': True,
            'genre': True,
            'score_potentiel': ':.1f',
            'fans_followers': ':,',
            'plateforme': False
        }
    )
    
    fig.update_layout(
        plot_bgcolor=COLORS['bg_card'],
        paper_bgcolor=COLORS['bg_card'],
        font_color=COLORS['text'],
        height=350,
        margin=dict(l=25, r=25, t=25, b=25),
        showlegend=True,
        legend=dict(
            font=dict(color='white', size=12)
        ),
        xaxis=dict(
            title='Score de Potentiel',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        ),
        yaxis=dict(
            title='Nombre de Followers/Fans',
            gridcolor='rgba(255,255,255,0.1)',
            color='white'
        )
    )
    
    fig.update_traces(
        marker=dict(
            size=8,
            opacity=0.7,
            line=dict(width=0.5, color='white')
        )
    )
    
    return fig


@st.cache_data(ttl=3600)
def get_stats_plateformes():
    """Récupère les stats pour l'affichage sous les graphiques"""
    
    if USE_POSTGRES:
        conn = psycopg2.connect(DB_URL)
    else:
        conn = sqlite3.connect(DB_NAME)
    
    query = """
        SELECT 
            plateforme,
            COUNT(DISTINCT nom_artiste) as nb_artistes,
            ROUND(AVG(fans_followers), 0) as avg_followers,
            MAX(fans_followers) as max_followers,
            ROUND(AVG(score_potentiel), 1) as avg_score
        FROM metriques_historique
        GROUP BY plateforme
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    return df




if st.session_state.active_page == "Vue d'ensemble":
    with st.spinner(""):
        st.markdown("## 🏠 Vue d'ensemble")
        col1, col2, col3, col4 = st.columns(4)
        
    with col1:
        st.metric("🎤 ARTISTES", len(filtered_df))
    with col2:
        spotify_count = int((filtered_df['plateforme'] == 'Spotify').sum()) if 'plateforme' in filtered_df.columns else 0
        st.metric("🟢 SPOTIFY", spotify_count)
    with col3:
        deezer_count = int((filtered_df['plateforme'] == 'Deezer').sum()) if 'plateforme' in filtered_df.columns else 0
        st.metric("🔵 DEEZER", deezer_count)
    with col4:
        st.metric("🔔 ALERTES", len(alertes_df))
    

    
    st.markdown("---")
    col1, col2 = st.columns(2, gap="small") 

    with col1:
        st.markdown("### 📊 Distribution des scores")
        if len(filtered_df) > 0:
            fig = px.histogram(
                filtered_df, 
                x='score_potentiel',
                color='plateforme',
                color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']},
                labels={'count': "Nombre d'artistes", 'score_potentiel': 'Score'},
                barmode='group',
                nbins=20
            )
            fig.update_layout(
                plot_bgcolor=COLORS['bg_card'], 
                paper_bgcolor=COLORS['bg_card'], 
                font_color=COLORS['text'],
                yaxis_title="Nombre d'artistes",
                xaxis_title="Score",
                legend=dict(font=dict(color='white', size=12)),
                bargap=0.1,
                bargroupgap=0.05,
                height=350,
                margin=dict(l=40, r=20, t=20, b=40)  
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Ce graphique montre la répartition des scores de potentiel.Il permet d'identifier la concentration des artistes autour de certains niveaux de score, et de comparer les distributions entre Spotify et Deezer.")
        else:
            st.info("Aucune donnée avec ces filtres")

    with col2:
        st.markdown("### 🎵 Répartition par Genre")
        if 'genre' in filtered_df.columns and len(filtered_df) > 0:
            genre_counts = filtered_df['genre'].value_counts()
            
            fig = px.pie(
                values=genre_counts.values,
                names=genre_counts.index,
                hole=0.5,
                color_discrete_map={
                    'Country-Folk': '#FFA500',
                    'Pop': COLORS['primary'],
                    'Rap-HipHop-RnB': COLORS['accent3'],
                    'Jazz': COLORS['secondary'],
                    'Rock-Metal': '#dc2626',
                    'Afrobeat-Amapiano': '#21B178',
                    'Indie-Alternative': '#9333ea'
                }
            )
            fig.update_layout(
                plot_bgcolor=COLORS['bg_card'], 
                paper_bgcolor=COLORS['bg_card'], 
                font_color=COLORS['text'],
                legend=dict(font=dict(color='white', size=12)),
                height=350,  
                margin=dict(l=25, r=25, t=25, b=25)  # réduire marges
            )
            fig.update_traces(
                textfont_color='white',
                textfont_size=14,  
                textposition='inside',
                texttemplate='%{percent:.1%}',
                textinfo='percent',
                insidetextorientation='horizontal'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Répartition des artistes par genre musical. Cela permet d'identifier les genres les plus représentés dans notre base de talents émergents.")
        else:
            st.info("Aucune donnée de genre disponible")
            
    st.markdown("---")

    # Layout : 2 colonnes
    col_gauche, col_droite = st.columns(2)  

    # COLONNE GAUCHE : CAMEMBERT PLOTLY
    with col_gauche:
        st.markdown("### 🥧 Répartition des Plateformes")
        
        try:
            fig_cam = generer_camembert_streamlit()
            
            if fig_cam:
                st.plotly_chart(fig_cam, use_container_width=True)  
                # Stats détaillées
                stats_plat = get_stats_plateformes()
                
                st.caption("Ce graphique montre la répartition des artistes par plateforme")
            else:
                st.info(" Aucune donnée disponible")
        
        except Exception as e:
            st.error(f" Erreur : {e}")

    # COLONNE DROITE : NUAGE DE POINTS PLOTLY
    with col_droite:
        st.markdown("### ⭐👥 Score / Followers")
        
        try:
            fig_nuage = generer_nuage_points_streamlit()
            
            if fig_nuage:
                st.plotly_chart(fig_nuage, use_container_width=True) 
                
                st.caption("Ce graphique montre la relation entre score et audience par plateforme")
            else:
                st.info(" Aucune donnée disponible")
        
        except Exception as e:
            st.error(f" Erreur : {e}")

    st.markdown("---")
# ==================== TAB 2: LES TOP ====================
elif st.session_state.active_page == "Les Tops":
    with st.spinner(""):
        st.markdown("## 🏆 Les Tops")
        
    if len(top_df) > 0:
        st.markdown("### 🏆 Top 30 Meilleurs Scores")
        top30_score = top_df.head(30)
        
        fig = px.bar(
            top30_score.sort_values('score_potentiel'),
            y='nom_artiste',
            x='score_potentiel',
            orientation='h',
            text='score_potentiel',
            color='score_potentiel',
            color_continuous_scale=['#47559D', '#FF1B8D', '#21B178'],
            labels={'score_potentiel': 'Score', 'nom_artiste': 'Artiste'}
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig.update_layout(
            plot_bgcolor=COLORS['bg_card'],
            paper_bgcolor=COLORS['bg_card'],
            font_color=COLORS['text'],
            height=600,
            showlegend=False,
            yaxis={'categoryorder':'total ascending'}
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Le Top 30 des artistes avec les meilleurs scores de potentiel. Ces talents présentent le meilleur équilibre entre audience, engagement et croissance.")
        
        st.markdown("---")
        
        st.markdown("### 📈 Top 5 Meilleures Évolutions")
        
        evolution_data = []
        for artiste in top_df['nom_artiste'].unique()[:100]:
            artist_data = metriques_df[metriques_df['nom_artiste'] == artiste].copy()
            if len(artist_data) > 1:
                artist_data = artist_data.sort_values('date_collecte')
                first_score = artist_data.iloc[0]['score_potentiel']
                last_score = artist_data.iloc[-1]['score_potentiel']
                
                if first_score > 0:
                    evolution_pct = ((last_score - first_score) / first_score) * 100
                    evolution_data.append({
                        'nom_artiste': artiste,
                        'evolution': evolution_pct,
                        'score_actuel': last_score
                    })
        
        if evolution_data:
            evolution_df = pd.DataFrame(evolution_data)
            evolution_df_positive = evolution_df[evolution_df['evolution'] > 0]
            
            if len(evolution_df_positive) >= 5:
                top5_evolution = evolution_df_positive.nlargest(5, 'evolution')
            else:
                top5_evolution = evolution_df.nlargest(5, 'evolution')
            
            fig = px.scatter(
                top5_evolution,
                x='evolution',
                y='nom_artiste',
                color='evolution',
                color_continuous_scale=['#FFA500', '#FF1B8D', '#21B178'],
                labels={'evolution': 'Évolution (%)', 'nom_artiste': 'Artiste'}
            )

            fig.update_traces(marker=dict(size=14))

            for _, row in top5_evolution.iterrows():
                fig.add_shape(
                    type='line',
                    x0=0, x1=row['evolution'],
                    y0=row['nom_artiste'], y1=row['nom_artiste'],
                    line=dict(color='rgba(255,255,255,0.3)', width=2)
                )

            fig.update_layout(
                plot_bgcolor=COLORS['bg_card'],
                paper_bgcolor=COLORS['bg_card'],
                font_color=COLORS['text'],
                height=280,
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)
            st.caption("Le Top 5 des artistes avec la meilleure évolution de score. Ces artistes montrent une croissance rapide et un potentiel prometteur.")
                    
        st.markdown("---")
        
    st.markdown("---")
    col_top1, col_top2 = st.columns(2)
    
    with col_top1:
        st.markdown("### 🔵 Top 5 Deezer")
        if len(filtered_df) > 0:
            deezer_df = filtered_df[filtered_df['plateforme'] == 'Deezer']
            if len(deezer_df) > 0:
                top5_deezer = deezer_df.nlargest(min(5, len(deezer_df)), 'score_potentiel')
                fig = px.bar(
                    top5_deezer, 
                    x='score_potentiel', 
                    y='nom_artiste', 
                    orientation='h', 
                    text='score_potentiel',
                    color_discrete_sequence=[COLORS['secondary']]
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig.update_layout(
                    plot_bgcolor=COLORS['bg_card'], 
                    paper_bgcolor=COLORS['bg_card'], 
                    font_color=COLORS['text'], 
                    yaxis={'categoryorder':'total ascending'}, 
                    height=280,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Les 5 artistes Deezer avec les meilleurs scores de potentiel. Ces talents se démarquent par leur combinaison unique de fans, engagement et récence.")
            else:
                st.info("Aucun artiste Deezer avec ces filtres")

    with col_top2:
        st.markdown("### 🟢 Top 5 Spotify")
        if len(filtered_df) > 0:
            spotify_df = filtered_df[filtered_df['plateforme'] == 'Spotify']
            if len(spotify_df) > 0:
                top5_spotify = spotify_df.nlargest(min(5, len(spotify_df)), 'score_potentiel')
                fig = px.bar(
                    top5_spotify, 
                    x='score_potentiel', 
                    y='nom_artiste', 
                    orientation='h', 
                    text='score_potentiel',
                    color_discrete_sequence=[COLORS['accent3']]
                )
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig.update_layout(
                    plot_bgcolor=COLORS['bg_card'], 
                    paper_bgcolor=COLORS['bg_card'], 
                    font_color=COLORS['text'], 
                    yaxis={'categoryorder':'total ascending'}, 
                    height=280,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Les 5 artistes Spotify avec les meilleurs scores de potentiel. Ces artistes montrent une croissance prometteuse et un engagement fort de leur communauté.")
            else:
                st.info("Aucun artiste Spotify avec ces filtres")        

# ==================== TAB 3: LES ARTISTES ====================
elif st.session_state.active_page == "Les artistes":
    with st.spinner(""):
        st.markdown("## 🎤 Les Artistes")
    
    if len(filtered_df) > 0:
        artistes_list = sorted(filtered_df['nom_artiste'].dropna().unique())
        
        if len(artistes_list) == 0:
            st.info("Aucun artiste ne correspond à vos filtres")
        else:
            # Ligne de recherche + tri
            col_search, col_tri1, col_tri2 = st.columns([2, 1, 1])
            
            with col_search:
                selected_search = st.selectbox(
                    "Rechercher un artiste",
                    ["Tous"] + artistes_list,
                    key="search_artiste"
                )
            
            with col_tri1:
                tri_par = st.selectbox(
                    "Trier par",
                    ["Score", "Followers/Fans"],
                    key="tri_artistes"
                )
            
            with col_tri2:
                ordre = st.selectbox(
                    "Ordre",
                    ["Décroissant", "Croissant"],
                    key="ordre_artistes"
                )
            
            # Filtrage selon recherche
            if selected_search != "Tous":
                artistes_sorted = filtered_df[filtered_df['nom_artiste'] == selected_search].copy()
            else:
                artistes_sorted = filtered_df.copy()
            
            # Tri
            if tri_par == "Score":
                artistes_sorted = artistes_sorted.sort_values('score_potentiel', ascending=(ordre == "Croissant"))
            else:
                artistes_sorted = artistes_sorted.sort_values('followers_total', ascending=(ordre == "Croissant"))
                
            # ✅ CORRECTION : Réinitialiser la page si changement de filtres/tri
            if 'last_search' not in st.session_state:
                st.session_state.last_search = selected_search
                st.session_state.last_tri = tri_par
                st.session_state.last_ordre = ordre
            
            if (st.session_state.last_search != selected_search or 
                st.session_state.last_tri != tri_par or 
                st.session_state.last_ordre != ordre):
                st.session_state.page_artistes = 1
                st.session_state.last_search = selected_search
                st.session_state.last_tri = tri_par
                st.session_state.last_ordre = ordre
                
            # PAGINATION
            ITEMS_PER_PAGE = 10
            total_artistes = len(artistes_sorted)
            total_pages = math.ceil(total_artistes / ITEMS_PER_PAGE)
            
            # S'assurer que page_artistes est valide
            if st.session_state.page_artistes > total_pages:
                st.session_state.page_artistes = max(1, total_pages)
                
            start_idx = (st.session_state.page_artistes - 1) * ITEMS_PER_PAGE
            end_idx = start_idx + ITEMS_PER_PAGE
            page_artistes = artistes_sorted.iloc[start_idx:end_idx]
            
            # AFFICHAGE DES ARTISTES
            for i in range(0, len(page_artistes), 5):
                cols = st.columns(5)
                
                for col_idx, (_, artist) in enumerate(list(page_artistes.iloc[i:i+5].iterrows())):
                    with cols[col_idx]:
                        # Checkbox
                        is_checked = st.checkbox(
                            "Sélectionner",
                            value=artist['nom_artiste'] in st.session_state.temp_interesses_artistes,
                            key=f"check_artiste_{start_idx + i + col_idx}",
                            label_visibility="collapsed"
                        )
                        
                        if is_checked and artist['nom_artiste'] not in st.session_state.temp_interesses_artistes:
                            st.session_state.temp_interesses_artistes.append(artist['nom_artiste'])
                        elif not is_checked and artist['nom_artiste'] in st.session_state.temp_interesses_artistes:
                            st.session_state.temp_interesses_artistes.remove(artist['nom_artiste'])
                        
                        # Image
                        if 'image_url' in artist and pd.notna(artist['image_url']) and artist['image_url']:
                            st.markdown(f"""
                                <div style="width: 100%; 
                                            aspect-ratio: 1/1;
                                            overflow: hidden;
                                            border-radius: 10px;
                                            background: {COLORS['bg_card']};">
                                    <img src="{artist['image_url']}" 
                                        style="width: 100%; 
                                                height: 100%; 
                                                object-fit: cover;">
                                </div>
                            """, unsafe_allow_html=True)
                        else:
                            st.markdown(f"""
                                <div style="width: 100%; 
                                            aspect-ratio: 1/1;
                                            background: linear-gradient(135deg, {COLORS['accent1']}, {COLORS['accent2']}); 
                                            border-radius: 10px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 3rem;">
                                    🎵
                                </div>
                            """, unsafe_allow_html=True)
                        
                        # Info artiste
                        artist_name = artist['nom_artiste']
                        display_name = artist_name[:18] + '...' if len(artist_name) > 18 else artist_name
                        st.markdown(f"**{display_name}**")
                        st.caption(f"{artist['plateforme']} | {artist.get('genre', 'N/A')}")
                        st.caption(f"⭐ {artist['score_potentiel']:.1f} | 👥 {int(artist['followers_total']):,}")

                        # AFFICHER LES 2 BOUTONS CÔTE À CÔTE
                        col_ecouter, col_details = st.columns(2)

                        with col_ecouter:
                            # Récupérer l'URL
                            url_artiste = artist.get('url', '')
                            
                            # Si pas d'URL, essayer de reconstruire
                            if not url_artiste or pd.isna(url_artiste):
                                plateforme = artist.get('plateforme', '')
                                nom = artist.get('nom_artiste', '')
                                
                                if plateforme == 'Spotify':
                                    # Essayer de trouver l'URL dans artistes_df
                                    matching_artist = artistes_df[artistes_df['nom'] == nom]
                                    if len(matching_artist) > 0 and 'url_spotify' in matching_artist.columns:
                                        url_artiste = matching_artist.iloc[0].get('url_spotify', '')
                                
                                elif plateforme == 'Deezer':
                                    matching_artist = artistes_df[artistes_df['nom'] == nom]
                                    if len(matching_artist) > 0 and 'url_deezer' in matching_artist.columns:
                                        url_artiste = matching_artist.iloc[0].get('url_deezer', '')
                            
                            # Afficher le bouton
                            if url_artiste and pd.notna(url_artiste) and str(url_artiste).strip() != '':
                                st.link_button(
                                    "🎵",
                                    str(url_artiste),
                                    use_container_width=True
                                )
                            else:
                                st.button(
                                    "🎵",
                                    disabled=True,
                                    use_container_width=True,
                                    key=f"disabled_ecouter_{start_idx}_{i}_{col_idx}"
                                )

                        with col_details:
                            if st.button(
                                "ℹ️",
                                key=f"details_{start_idx}_{i}_{col_idx}",
                                use_container_width=True
                            ):
                                st.session_state.selected_artist_evolution = artist['nom_artiste']
                                st.session_state.previous_page = "Les artistes"
                                st.session_state.go_to_evolution = True


            

        
        st.markdown("---")
        
        col_left, col_center, col_right = st.columns([2, 1, 2])
        with col_center:
            if st.button("VALIDER", key="valider_artistes", use_container_width=True):
                for artiste in st.session_state.temp_interesses_artistes:
                    if artiste not in st.session_state.artistes_interesses:
                        st.session_state.artistes_interesses.append(artiste)
                
                st.success(f" {len(st.session_state.temp_interesses_artistes)} artiste(s) ajouté(s) !")
                st.session_state.temp_interesses_artistes = []
        
        st.markdown("---")
        
        st.caption(f" Page {st.session_state.page_artistes} sur {total_pages} ({total_artistes} artistes)")
        
        col_prev, col_pages, col_next = st.columns([1, 4, 1])
        
        with col_prev:
            if st.button("⬅️ Précédent", disabled=(st.session_state.page_artistes <= 1), key="prev_bottom"):
                st.session_state.page_artistes -= 1
                st.rerun()
                
        
        with col_pages:
            pages_to_show = []
            if total_pages <= 10:
                pages_to_show = list(range(1, total_pages + 1))
            else:
                if st.session_state.page_artistes <= 4:
                    pages_to_show = list(range(1, 8)) + ['...', total_pages]
                elif st.session_state.page_artistes >= total_pages - 3:
                    pages_to_show = [1, '...'] + list(range(total_pages - 6, total_pages + 1))
                else:
                    pages_to_show = [1, '...'] + list(range(st.session_state.page_artistes - 2, st.session_state.page_artistes + 3)) + ['...', total_pages]
            
            num_cols = len(pages_to_show)
            page_cols = st.columns([1] * num_cols)
            
            for idx, page_num in enumerate(pages_to_show):
                with page_cols[idx]:
                    if page_num == '...':
                        st.markdown("<div style='text-align: center; padding: 5px;'>...</div>", unsafe_allow_html=True)
                    else:
                        if st.button(
                            str(page_num),
                            key=f"page_bottom_{page_num}",
                            disabled=(page_num == st.session_state.page_artistes),
                            use_container_width=True
                        ):
                            st.session_state.page_artistes = page_num
                            st.rerun()
                            
        
        with col_next:
            if st.button("Suivant ➡️", disabled=(st.session_state.page_artistes >= total_pages), key="next_bottom"):
                st.session_state.page_artistes += 1
                st.rerun()
                
    else:
        st.info("Aucun artiste disponible")

# ==================== TAB 4: EVOLUTION ====================
elif st.session_state.active_page == "Évolution":
    with st.spinner(""):
        st.markdown("## 📈 Évolution")
        
        # BOUTON RETOUR
    if st.session_state.get('previous_page'):
        col_back, col_title = st.columns([1, 5])
        with col_back:
            if st.button("⬅️ Retour", use_container_width=True):
                st.session_state.active_page = st.session_state.previous_page
                st.session_state.previous_page = None
                
        with col_title:
            st.markdown("")
    else:
        st.markdown("")
        
    if len(metriques_df) > 0 and 'nom_artiste' in metriques_df.columns:
        filtered_artists = filtered_df.copy()
        artistes_list = sorted(filtered_artists['nom_artiste'].dropna().unique())
        
        if len(artistes_list) == 0:
            st.info("Aucun artiste ne correspond à vos filtres")
        else:
            #  Initialiser session_state pour navigation
            if 'selected_artist_evolution' not in st.session_state:
                st.session_state.selected_artist_evolution = artistes_list[0]

            if 'go_to_evolution' not in st.session_state:
                st.session_state.go_to_evolution = False

            #   Vérifier si on v0ient des alertes
            if st.session_state.go_to_evolution:
                # Message de confirmation
                st.success(f" Visualisation de l'artiste depuis les alertes : **{st.session_state.selected_artist_evolution}**")
                # Réinitialiser le flag
                st.session_state.go_to_evolution = False

            # Vérifier que l'artiste est dans la liste
            if st.session_state.selected_artist_evolution not in artistes_list:
                st.session_state.selected_artist_evolution = artistes_list[0]

            selected_artist = st.selectbox(
                " Artiste", 
                artistes_list,
                index=artistes_list.index(st.session_state.selected_artist_evolution)
            )
            
            st.session_state.selected_artist_evolution = selected_artist
            
            if selected_artist:
                artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
                
                if not artist_data.empty:
                    artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
                    artist_data['date_jour'] = artist_data['date_collecte'].dt.date
                    artist_data = artist_data.sort_values('date_collecte') # type: ignore
                    
                    if 'fans_followers' in artist_data.columns:
                        artist_data['followers_chart'] = artist_data['fans_followers'].fillna(0)
                    else:
                        artist_data['followers_chart'] = artist_data.apply(
                            lambda row: row.get('followers', 0) if pd.notna(row.get('followers')) else row.get('fans', 0), axis=1
                        )
                    
                    latest = artist_data.iloc[-1]
                    followers = latest['followers_chart']
                    
                    col_img, col_info = st.columns([1, 3])
                    
                    with col_img:
                        if 'image_url' in latest and pd.notna(latest['image_url']) and latest['image_url']:
                            st.image(latest['image_url'], width=200)
                        else:
                            st.markdown(f"""
                                <div style="width: 200px; 
                                            height: 200px; 
                                            background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}); 
                                            border-radius: 15px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            font-size: 4rem;">
                                    🎤
                                </div>
                            """, unsafe_allow_html=True)
                    
                    with col_info:
                        st.markdown(f"""
                            <h2 style="color: {COLORS['primary']};">{selected_artist}</h2>
                            <p style="font-size: 1.2rem;"><strong>Genre:</strong> {latest['genre']}</p>
                            <p style="font-size: 1.2rem;"><strong>Plateforme:</strong> {latest['plateforme']}</p>
                        """, unsafe_allow_html=True)
                        
                        if 'url' in latest and pd.notna(latest['url']):
                            if st.button("🎵 Écouter sur " + latest['plateforme'], key="listen_artist"):
                                st.markdown(f'<meta http-equiv="refresh" content="0; url={latest["url"]}">', unsafe_allow_html=True)
                        
                        col_check, col_btn = st.columns([3, 1])

                        with col_check:
                            is_interesse = st.checkbox(
                                f"⭐ Marquer {selected_artist} comme intéressé",
                                value=selected_artist in st.session_state.artistes_interesses,
                                key=f"check_evolution_{selected_artist}",
                                label_visibility="collapsed"
                            )
                            
                            if is_interesse:
                                st.session_state.temp_interesse_evolution = selected_artist
                            else:
                                st.session_state.temp_interesse_evolution = None

                        with col_btn:
                            if st.button("VALIDER", key="valider_evolution", use_container_width=True):
                                if st.session_state.temp_interesse_evolution:
                                    if st.session_state.temp_interesse_evolution not in st.session_state.artistes_interesses:
                                        st.session_state.artistes_interesses.append(st.session_state.temp_interesse_evolution)
                                        st.success(f"✅ {st.session_state.temp_interesse_evolution} ajouté !")
                                    else:
                                        st.info("Déjà dans vos artistes intéressés")
                                else:
                                    if selected_artist in st.session_state.artistes_interesses:
                                        st.session_state.artistes_interesses.remove(selected_artist)
                                        st.success(f"❌ {selected_artist} retiré")
                                


                        st.markdown("---")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("👥 Followers/Fans", f"{int(followers):,}")
                    with col2:
                        st.metric("⭐ Score Actuel", f"{latest['score_potentiel']:.1f}")
                    with col3:
                        if len(artist_data) > 1:
                            first_f = artist_data.iloc[0]['followers_chart']
                            if first_f > 0:
                                growth = ((followers - first_f) / first_f) * 100
                                st.metric("📈 Croissance", f"{growth:.1f}%")
                    
                    st.markdown("---")
                    
                    if len(artist_data) > 1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("#### 👥 Évolution des Followers/Fans")
                            chart_data = artist_data[artist_data['followers_chart'] > 0]
                            chart_data = chart_data.drop_duplicates(subset=['date_jour'], keep='last')
                            if len(chart_data) > 0:
                                fig = px.line(
                                    chart_data, 
                                    x='date_jour', 
                                    y='followers_chart',
                                    markers=True,
                                    labels={'date_jour': 'Date', 'followers_chart': 'Followers/Fans'}
                                )
                                fig.update_traces(
                                    line_color=COLORS['accent3'], 
                                    line_width=3, 
                                    marker=dict(size=10, color=COLORS['primary'])
                                )
                                fig.update_layout(
                                    plot_bgcolor=COLORS['bg_card'], 
                                    paper_bgcolor=COLORS['bg_card'], 
                                    font_color=COLORS['text'],
                                    xaxis_title="Date",
                                    yaxis_title="Followers/Fans",
                                    height=280
                                )
                                fig.update_xaxes(tickformat="%d/%m/%Y")

                                st.plotly_chart(fig, use_container_width=True)
                                st.caption("👥 L'évolution du nombre de followers/fans dans le temps. Une courbe ascendante indique une croissance régulière de l'audience.")
                            else:
                                st.info("Pas de données de pour afficher l'évolution de cet artiste.")
                                
                        with col2:
                            st.markdown("#### ⭐ Évolution du Score")
                            chart_data_score = artist_data.copy()
                            chart_data_score = chart_data_score.drop_duplicates(subset=['date_jour'], keep='last')
                            fig = px.line(
                                chart_data_score, 
                                x='date_jour', 
                                y='score_potentiel',
                                markers=True,
                                labels={'date_jour': 'Date', 'score_potentiel': 'Score'}
                            )
                            fig.update_traces(
                                line_color=COLORS['secondary'], 
                                line_width=3, 
                                marker=dict(size=10, color=COLORS['accent1'])
                            )
                            fig.update_layout(
                                plot_bgcolor=COLORS['bg_card'], 
                                paper_bgcolor=COLORS['bg_card'], 
                                font_color=COLORS['text'],
                                xaxis_title="Date",
                                yaxis_title="Score de Potentiel",
                                height=280
                            )
                            fig.update_xaxes(
                            tickformat="%d/%m/%Y"  # Format 19/01/2026
                            )

                            st.plotly_chart(fig, use_container_width=True)
                            st.caption("L'évolution du score de potentiel dans le temps. Un score en hausse traduit une amélioration globale de la performance (engagement, croissance, popularité).")
                    else:
                        st.info(" Pas assez de données historiques pour afficher l'évolution de cet artiste.")
                        
                    st.markdown("---")
                    st.markdown("### 🎵 Artistes Similaires")

                    candidates = filtered_df[
                        (filtered_df['nom_artiste'] != selected_artist) &
                        (filtered_df['genre'] == latest['genre']) &
                        (filtered_df['plateforme'] == latest['plateforme'])
                    ].copy()

                    if len(candidates) >= 2:
                        try:
                            from sklearn.neighbors import NearestNeighbors
                            
                            feature_cols = ['followers_total', 'score_potentiel']
                            
                            if 'popularity' in candidates.columns:
                                feature_cols.append('popularity')
                            
                            X = candidates[feature_cols].fillna(0)
                            
                            n_neighbors = min(6, len(candidates))
                            knn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
                            knn.fit(X) # type: ignore
                            
                            current_artist_data = filtered_df[filtered_df['nom_artiste'] == selected_artist]
                            current_features = current_artist_data[feature_cols].fillna(0).values[0]
                            
                            distances, indices = knn.kneighbors([current_features]) # type: ignore
                            
                            similar_indices = indices[0][:5]
                            similar_artists = candidates.iloc[similar_indices]
                            
                            if len(similar_artists) > 0:
                                cols = st.columns(min(5, len(similar_artists)))
                                
                                for idx, (col, (_, artist)) in enumerate(zip(cols, similar_artists.iterrows())):
                                    with col:
                                        #  CASE À COCHER
                                        is_checked_sim = st.checkbox(
                                            "⭐",
                                            value=artist['nom_artiste'] in st.session_state.temp_interesses_artistes,
                                            key=f"check_similar_{idx}_{artist['nom_artiste']}",
                                            label_visibility="collapsed"
                                        )
                                        
                                        if is_checked_sim and artist['nom_artiste'] not in st.session_state.temp_interesses_artistes:
                                            st.session_state.temp_interesses_artistes.append(artist['nom_artiste'])
                                        elif not is_checked_sim and artist['nom_artiste'] in st.session_state.temp_interesses_artistes:
                                            st.session_state.temp_interesses_artistes.remove(artist['nom_artiste'])
                                        
                                        # Photo
                                        if 'image_url' in artist and pd.notna(artist['image_url']) and artist['image_url']:
                                            st.markdown(f"""
                                                <div style="width: 100%; 
                                                            aspect-ratio: 1/1;
                                                            overflow: hidden;
                                                            border-radius: 10px;
                                                            background: {COLORS['bg_card']};">
                                                    <img src="{artist['image_url']}" 
                                                        style="width: 100%; 
                                                                height: 100%; 
                                                                object-fit: cover;">
                                                </div>
                                            """, unsafe_allow_html=True)
                                        else:
                                            st.markdown(f"""
                                                <div style="width: 100%; 
                                                            aspect-ratio: 1/1;
                                                            background: linear-gradient(135deg, {COLORS['accent1']}, {COLORS['accent2']}); 
                                                            border-radius: 10px;
                                                            display: flex;
                                                            align-items: center;
                                                            justify-content: center;
                                                            font-size: 3rem;">
                                                    🎵
                                                </div>
                                            """, unsafe_allow_html=True)
                                        
                                        artist_name = artist['nom_artiste'] or "Artiste Inconnu"
                                        display_name = artist_name[:15] + '...' if len(artist_name) > 15 else artist_name
                                        st.markdown(f"**{display_name}**")
                                        st.caption(f"⭐ {artist['score_potentiel']:.1f}")
                                        
                                        if 'url' in artist and pd.notna(artist['url']) and artist['url']:
                                            if st.button("🎵 Écouter", key=f"listen_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                                st.markdown(f'<a href="{artist["url"]}" target="_blank">Ouvrir</a>', unsafe_allow_html=True)
                                        
                                        if st.button("ℹ️ Infos", key=f"info_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                            st.session_state.selected_artist_evolution = artist['nom_artiste']
                                
                                # BOUTON VALIDATION (après les artistes similaires)
                                st.markdown("---")
                                
                                col_left_sim, col_center_sim, col_right_sim = st.columns([2, 1, 2])
                                with col_center_sim:
                                    if st.button("VALIDER", key="valider_similaires", use_container_width=True):
                                        for artiste in st.session_state.temp_interesses_artistes:
                                            if artiste not in st.session_state.artistes_interesses:
                                                st.session_state.artistes_interesses.append(artiste)
                                        
                                        st.success(f" {len(st.session_state.temp_interesses_artistes)} artiste(s) similaire(s) ajouté(s) !")
                                        st.session_state.temp_interesses_artistes = []
                            else:
                                st.info("Pas assez d'artistes similaires")
                        
                        except Exception as e:
                            # Fallback sans KNN (code identique avec checkboxes)
                            similar_artists = candidates.head(5)
                            
                            cols = st.columns(min(5, len(similar_artists)))
                            
                            for idx, (col, (_, artist)) in enumerate(zip(cols, similar_artists.iterrows())):
                                with col:
                                    #  CASE À COCHER
                                    is_checked_sim = st.checkbox(
                                        "⭐",
                                        value=artist['nom_artiste'] in st.session_state.temp_interesses_artistes,
                                        key=f"check_similar_fallback_{idx}_{artist['nom_artiste']}",
                                        label_visibility="collapsed"
                                    )
                                    
                                    if is_checked_sim and artist['nom_artiste'] not in st.session_state.temp_interesses_artistes:
                                        st.session_state.temp_interesses_artistes.append(artist['nom_artiste'])
                                    elif not is_checked_sim and artist['nom_artiste'] in st.session_state.temp_interesses_artistes:
                                        st.session_state.temp_interesses_artistes.remove(artist['nom_artiste'])
                                    
                                    # Photo + Info (même code que ci-dessus)
                                    if 'image_url' in artist and pd.notna(artist['image_url']):
                                        st.markdown(f"""
                                            <div style="width: 100%; aspect-ratio: 1/1; overflow: hidden; border-radius: 10px;">
                                                <img src="{artist['image_url']}" style="width: 100%; height: 100%; object-fit: cover;">
                                            </div>
                                        """, unsafe_allow_html=True)
                                    
                                    artist_name = artist['nom_artiste'] or "Artiste Inconnu"
                                    display_name = artist_name[:15] + '...' if len(artist_name) > 15 else artist_name
                                    st.markdown(f"**{display_name}**")
                                    st.caption(f"⭐ {artist['score_potentiel']:.1f}")
                                    
                                    if 'url' in artist and pd.notna(artist['url']):
                                        if st.button("🎵 Écouter", key=f"listen_fb_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                            st.markdown(f'<a href="{artist["url"]}" target="_blank">Ouvrir</a>', unsafe_allow_html=True)
                                    
                                    if st.button(" Infos", key=f"info_fb_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                        st.session_state.selected_artist_evolution = artist['nom_artiste']
                            
                            # Bouton validation fallback
                            st.markdown("---")
                            col_left_sim, col_center_sim, col_right_sim = st.columns([2, 1, 2])
                            with col_center_sim:
                                if st.button("VALIDER", key="valider_similaires_fb", use_container_width=True):
                                    for artiste in st.session_state.temp_interesses_artistes:
                                        if artiste not in st.session_state.artistes_interesses:
                                            st.session_state.artistes_interesses.append(artiste)
                                    
                                    st.success(f" {len(st.session_state.temp_interesses_artistes)} artiste(s) ajouté(s) !")
                                    st.session_state.temp_interesses_artistes = []
                    else:
                        st.info("Pas assez d'artistes similaires disponibles")
    else:
        st.info("Aucune donnée disponible")

# ==================== TAB 5: ALERTES ====================
elif st.session_state.active_page == "Alertes":
    with st.spinner(""):
        st.markdown("## 🔔 Alertes")
    
    if alertes_df.empty:
        st.success(" Aucune alerte pour le moment")
        st.info(" Lancez `python generer_alertes.py` pour détecter les évolutions significatives")
    else:
        # Convertir date_alerte en datetime
        alertes_df['date_alerte'] = pd.to_datetime(alertes_df['date_alerte'], errors='coerce')
        
        # Ajouter colonnes de tri
        alertes_df['date_format_fr'] = alertes_df['date_alerte'].dt.strftime('%d/%m/%Y') # type: ignore
        alertes_df['mois_annee'] = alertes_df['date_alerte'].dt.strftime('%m/%Y') # type: ignore
        
        # Extraire valeurs pour tri followers/score
        def extraire_variation_followers(message):
            """Extrait le % de variation des followers depuis le message"""
            import re
            # Recherche "Croissance de X%" ou "Baisse de X%"
            match = re.search(r'(?:Croissance|Baisse) de ([\d.]+)%', message)
            if match:
                variation = float(match.group(1))
                # Si c'est une baisse, mettre négatif
                if 'Baisse' in message:
                    return -variation
                return variation
            return 0
        
        def extraire_variation_score(message):
            """Extrait le % de variation du score depuis le message"""
            import re
            # Recherche "Score ... en hausse de X%"
            match = re.search(r'hausse de ([\d.]+)%', message)
            if match:
                return float(match.group(1))
            return 0
        
        alertes_df['variation_followers'] = alertes_df.apply(
            lambda row: extraire_variation_followers(row['message']) 
            if 'followers' in row['message'].lower() else 0, 
            axis=1
        )
        
        alertes_df['variation_score'] = alertes_df.apply(
            lambda row: extraire_variation_score(row['message']) 
            if 'score' in row['message'].lower() else 0, 
            axis=1
        )
        
        # Statistiques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Alertes", len(alertes_df))
        
        with col2:
            croissance_count = len(alertes_df[alertes_df['type_alerte'].str.contains('Croissance', na=False)])
            st.metric("Croissances", croissance_count)
        
        with col3:
            baisse_count = len(alertes_df[alertes_df['type_alerte'].str.contains('Baisse', na=False)])
            st.metric("Baisses", baisse_count)
        
        with col4:
            trending_count = len(alertes_df[alertes_df['type_alerte'].str.contains('TRENDING', na=False)])
            st.metric("Trending", trending_count)
        
        st.markdown("---")
        
        # Filtres de tri
        col_tri1, col_tri2, col_tri3 = st.columns(3)
        
        with col_tri1:
            tri_type = st.selectbox(
                " Trier par",
                ["Date (récent)", "Date (ancien)", "Variation Followers ↑", "Variation Followers ↓", 
                "Variation Score ↑", "Variation Score ↓", "Type d'alerte"],
                key="tri_alertes"
            )
        
        with col_tri2:
            filtre_type = st.selectbox(
                " Filtrer par type",
                ["Tous"] + sorted(alertes_df['type_alerte'].unique().tolist()),
                key="filtre_type_alerte"
            )
        
        with col_tri3:
            # Liste unique des mois/années
            mois_disponibles = sorted(alertes_df['mois_annee'].dropna().unique().tolist(), reverse=True)
            filtre_mois = st.selectbox(
                " Filtrer par mois",
                ["Tous"] + mois_disponibles,
                key="filtre_mois_alerte"
            )
        
        # Appliquer filtres
        alertes_filtrees = alertes_df.copy()
        
        if filtre_type != "Tous":
            alertes_filtrees = alertes_filtrees[alertes_filtrees['type_alerte'] == filtre_type]
        
        if filtre_mois != "Tous":
            alertes_filtrees = alertes_filtrees[alertes_filtrees['mois_annee'] == filtre_mois]
        
        # Appliquer tri
        if tri_type == "Date (récent)":
            alertes_filtrees = alertes_filtrees.sort_values('date_alerte', ascending=False)
        elif tri_type == "Date (ancien)":
            alertes_filtrees = alertes_filtrees.sort_values('date_alerte', ascending=True)
        elif tri_type == "Variation Followers ↑":
            alertes_filtrees = alertes_filtrees.sort_values('variation_followers', ascending=False)
        elif tri_type == "Variation Followers ↓":
            alertes_filtrees = alertes_filtrees.sort_values('variation_followers', ascending=True)
        elif tri_type == "Variation Score ↑":
            alertes_filtrees = alertes_filtrees.sort_values('variation_score', ascending=False)
        elif tri_type == "Variation Score ↓":
            alertes_filtrees = alertes_filtrees.sort_values('variation_score', ascending=True)
        elif tri_type == "Type d'alerte":
            alertes_filtrees = alertes_filtrees.sort_values('type_alerte')
        
        # Affichage des alertes
        st.markdown(f"### {len(alertes_filtrees)} alerte(s) affichée(s)")
        
        for idx, alerte in alertes_filtrees.iterrows():
            # Déterminer la couleur selon le type
            if '🚀' in alerte['type_alerte']:
                color = "#21B178"
                icon = ""
            elif '⚠️' in alerte['type_alerte']:
                color = "#FF6B6B"
                icon = ""
            elif '🔥' in alerte['type_alerte']:
                color = "#FF1B8D"
                icon = ""
            elif '⭐' in alerte['type_alerte']:
                color = "#FFD700"
                icon = ""
            else:
                color = "#47559D"
                icon = "📊"
            
            # Variation display
            variation_display = ""
            if alerte['variation_followers'] != 0:
                signe = "+" if alerte['variation_followers'] > 0 else ""
                variation_display = f" ({signe}{alerte['variation_followers']:.1f}%)"
            elif alerte['variation_score'] != 0:
                variation_display = f" (+{alerte['variation_score']:.1f}%)"
            
            # Layout avec bouton
            col_card, col_button = st.columns([4, 1])
            
            with col_card:
                st.markdown(f"""
                    <div style="background: linear-gradient(135deg, #1a0a2e 0%, #2a1a3e 100%);
                                padding: 1.5rem;
                                border-radius: 10px;
                                border-left: 4px solid {color};
                                margin: 1rem 0;">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div style="flex: 1;">
                                <div style="color: {color}; font-size: 1.2rem; font-weight: bold; margin-bottom: 0.5rem;">
                                    {icon} {alerte['type_alerte']}{variation_display}
                                </div>
                                <div style="color: #B18E57; font-size: 1.1rem; font-weight: 600; margin-bottom: 0.5rem;">
                                    {alerte['nom_artiste']}
                                </div>
                                <div style="color: #E0E0E0; font-size: 0.95rem; margin-bottom: 0.5rem;">
                                    {alerte['message']}
                                </div>
                                <div style="color: #888; font-size: 0.85rem;">
                                    {alerte['date_format_fr']}
                                </div>
                            </div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col_button:
                #  DEUX BOUTONS EMPILÉS
                # Récupérer URL
                url_artiste = ""
                matching = latest_metrics_df[latest_metrics_df['nom_artiste'] == alerte['nom_artiste']]
                if len(matching) > 0 and 'url' in matching.columns:
                    url_artiste = matching.iloc[0].get('url', '')
                
                # Bouton Écouter
                if url_artiste and pd.notna(url_artiste) and str(url_artiste).strip() != '':
                    st.link_button(
                        "🎵",
                        str(url_artiste),
                        use_container_width=True,
                    )
                else:
                    st.button(
                        "🎵",
                        disabled=True,
                        use_container_width=True,
                        key=f"disabled_alerte_ecouter_{idx}"
                    )
                
                # Bouton Détails
                if st.button(
                    "ℹ️",
                    key=f"alerte_details_{idx}",
                    use_container_width=True
                ):
                    st.session_state.selected_artist_evolution = alerte['nom_artiste']
                    st.session_state.previous_page = "Alertes"
                    st.session_state.go_to_evolution = True
                    
        
        # Bouton pour marquer comme lues 
        st.markdown("---")
        col_action1, col_action2, col_action3 = st.columns([2, 1, 2])
        
        with col_action2:
            if st.button(" Marquer toutes comme lues", key="marquer_lues"):
                try:
                    if USE_POSTGRES:
                        conn = psycopg2.connect(DB_URL)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE alertes SET vu = TRUE")
                        conn.commit()
                        conn.close()
                    else:
                        conn = sqlite3.connect(DB_NAME)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE alertes SET vu = 1")
                        conn.commit()
                        conn.close()
                    
                    st.success(" Toutes les alertes ont été marquées comme lues")
                except Exception as e:
                    st.error(f" Erreur : {e}")

# ==================== TAB 7: À PROPOS ====================
elif st.session_state.active_page == "A propos":
    with st.spinner(""):
        st.markdown("## ℹ️ À Propos")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: {COLORS['primary']};">QUI SOMMES-NOUS ?</h3>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        <strong>JEK2 Records</strong> est un label de musique français spécialisé dans 
        la découverte de nouveaux talents multi-genres.
        </p>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        Notre mission : identifier les artistes prometteurs <strong>avant</strong> qu'ils ne deviennent célèbres.
        </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card">
        <h3 style="color: {COLORS['secondary']}">MUSIC TALENT RADAR </h3>
        <p style="font-size: 1.1rem; line-height: 1.8;">
        Nous avons créé cet outil interne pour analyser des milliers d'artistes
        sur Spotify et Deezer, en utilisant des données publiques et des algorithmes nous permettant
        de repérer les talents émergents avant qu'ils n'explosent.
        </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="info-box">
        <h4 style="color: {COLORS['accent3']};">NOS GENRES</h4>
        <p><strong> - Pop française</strong></p>
        <p><strong> - Rap/Hip-Hop/RnB</strong></p>
        <p><strong> - Afrobeat/Amapiano</strong></p>
        <p><strong> - Rock-Metal</strong></p>
        <p><strong> - Jazz</strong></p>
        <p><strong> - Indie-Alternative</strong></p>
        <p><strong> - Country-Folk</strong></p>
        <p><strong> - Reggaeton-Latin</strong></p>
        <p><strong>📍 Localisation :</strong><br>France</p>
        </div>
        """, unsafe_allow_html=True)
    

    
    st.markdown("---")
    st.markdown(f"""
    <div class="metric-card">
    <h3 style="color: {COLORS['primary']};">👤 L'AUTEURE DU PROJET</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col_photo, col_bio = st.columns([1, 2])
    
    with col_photo:
        jenny_photo_path = os.path.join(BASE_DIR, "assets", "moipiano.png")
        if os.path.isfile(jenny_photo_path):
            st.image(jenny_photo_path, width=250)
        else:
            st.warning(f"Photo non trouvée: {jenny_photo_path}")
    
    with col_bio:
        st.markdown(f"""
        <div style="color: {COLORS['text']}; font-size: 1.05rem; line-height: 1.8;">
        <h4 style="color: {COLORS['accent3']}; font-weight: 700;">Jenny - Data Analyst & Musicienne</h4>
        <p>
        Passionnée par la data et la musique, j'ai développé cet outil dans le cadre 
        de mon projet final à la <strong>Wild Code School</strong>.
        </p>
        <p>
        🎹 <strong>Parolière - Interprète - Pianiste </strong><br>
        📊 <strong>Data Analyst</strong> en reconversion<br>
        🚀 <strong>Objectif</strong> : allier mes deux passions pour découvrir les talents de demain !
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""
    <h4 style="color: {COLORS['accent3']}; font-weight: 700;">🎹 MES OEUVRES MUSICALES</h4>
    <p style="color: {COLORS['text']}; font-size: 1.05rem;">
    En parallèle de mon parcours en data, j'écris et je chante mes propres chansons'. 
    Ayant peu de moyens, j'utilise un microphone basique, Audacity et Bandlab.
    Découvrez mes créations musicales :
    </p>
    """, unsafe_allow_html=True)
    
    audio_path = os.path.join(BASE_DIR, "assets", "Licorne.mp3")
    if os.path.isfile(audio_path):
        st.markdown(f"""
        <p style="color: {COLORS['text']}; font-weight: 700; margin-top: 1rem;">
        🎵 Princesse Licorne
        </p>
        """, unsafe_allow_html=True)
        
        audio_base64 = get_base64_image(audio_path)
        if audio_base64:
            st.markdown(f"""
                <audio controls style="width: 100%; margin-bottom: 1.5rem;">
                    <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
                    Votre navigateur ne supporte pas la lecture audio.
                </audio>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger le fichier audio")
    else:
        st.info(f" Fichier audio non trouvé : {audio_path}")
        st.caption("Ajoutez vos fichiers .m4a dans le dossier assets/")
    
    audio_path = os.path.join(BASE_DIR, "assets", "Humain.m4a")
    if os.path.isfile(audio_path):
        st.markdown(f"""
        <p style="color: {COLORS['text']}; font-weight: 700; margin-top: 1rem;">
        🎵 L'Humain
        </p>
        """, unsafe_allow_html=True)
        
        audio_base64 = get_base64_image(audio_path)
        if audio_base64:
            st.markdown(f"""
                <audio controls style="width: 100%; margin-bottom: 1.5rem;">
                    <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
                    Votre navigateur ne supporte pas la lecture audio.
                </audio>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger le fichier audio")
    else:
        st.info(f" Fichier audio non trouvé : {audio_path}")
        st.caption("Ajoutez vos fichiers .m4a dans le dossier assets/")    
    
    audio_path = os.path.join(BASE_DIR, "assets", "ma_famille.m4a")
    if os.path.isfile(audio_path):
        st.markdown(f"""
        <p style="color: {COLORS['text']}; font-weight: 700; margin-top: 1rem;">
        🎵 Ma Famille
        </p>
        """, unsafe_allow_html=True)
        
        audio_base64 = get_base64_image(audio_path)
        if audio_base64:
            st.markdown(f"""
                <audio controls style="width: 100%; margin-bottom: 1.5rem;">
                    <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
                    Votre navigateur ne supporte pas la lecture audio.
                </audio>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger le fichier audio")
    else:
        st.info(f" Fichier audio non trouvé : {audio_path}")
        st.caption("Ajoutez vos fichiers .m4a dans le dossier assets/")

    audio_path = os.path.join(BASE_DIR, "assets", "Personne_ne_voit.mp3")
    if os.path.isfile(audio_path):
        st.markdown(f"""
        <p style="color: {COLORS['text']}; font-weight: 700; margin-top: 1rem;">
        🎵 Personne ne voit
        </p>
        """, unsafe_allow_html=True)
        
        audio_base64 = get_base64_image(audio_path)
        if audio_base64:
            st.markdown(f"""
                <audio controls style="width: 100%; margin-bottom: 1.5rem;">
                    <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
                    Votre navigateur ne supporte pas la lecture audio.
                </audio>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger le fichier audio")
    else:
        st.info(f" Fichier audio non trouvé : {audio_path}")
        st.caption("Ajoutez vos fichiers .m4a dans le dossier assets/")


    audio_path = os.path.join(BASE_DIR, "assets", "je_suis.m4a")
    if os.path.isfile(audio_path):
        st.markdown(f"""
        <p style="color: {COLORS['text']}; font-weight: 700; margin-top: 1rem;">
        🎵 Je Suis
        </p>
        """, unsafe_allow_html=True)
        
        audio_base64 = get_base64_image(audio_path)
        if audio_base64:
            st.markdown(f"""
                <audio controls style="width: 100%; margin-bottom: 1.5rem;">
                    <source src="data:audio/mp4;base64,{audio_base64}" type="audio/mp4">
                    Votre navigateur ne supporte pas la lecture audio.
                </audio>
            """, unsafe_allow_html=True)
        else:
            st.warning("Impossible de charger le fichier audio")
    else:
        st.info(f"Fichier audio non trouvé : {audio_path}")
        st.caption("Ajoutez vos fichiers .m4a dans le dossier assets/")
# ==================== TAB 6: PRÉDICTIONS ====================
elif st.session_state.active_page == "Prédictions":
    with st.spinner(""):
        st.markdown("## 🔮 Prédictions")
    
    #  SI UN ARTISTE EST SÉLECTIONNÉ, AFFICHER SON ÉVOLUTION
    if 'selected_prediction_artist' in st.session_state and st.session_state.selected_prediction_artist:
        selected_artist = st.session_state.selected_prediction_artist
        
        # Bouton retour
        if st.button("⬅️ Retour aux prédictions", key="back_to_predictions"):
            st.session_state.selected_prediction_artist = None
        
        st.markdown(f"## 📈 Évolution de {selected_artist}")
        
        # Afficher l'évolution
        if len(metriques_df) > 0 and 'nom_artiste' in metriques_df.columns:
            artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
            
            if not artist_data.empty:
                artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
                artist_data['date_jour'] = artist_data['date_collecte'].dt.date
                artist_data = artist_data.sort_values('date_collecte')
                
                if 'fans_followers' in artist_data.columns:
                    artist_data['followers_chart'] = artist_data['fans_followers'].fillna(0)
                else:
                    artist_data['followers_chart'] = artist_data.apply(
                        lambda row: row.get('followers', 0) if pd.notna(row.get('followers')) else row.get('fans', 0), axis=1
                    )
                
                latest = artist_data.iloc[-1]
                followers = latest['followers_chart']
                
                col_img, col_info = st.columns([1, 3])
                
                with col_img:
                    if 'image_url' in latest and pd.notna(latest['image_url']) and latest['image_url']:
                        st.image(latest['image_url'], width=200)
                    else:
                        st.markdown(f"""
                            <div style="width: 200px; 
                                        height: 200px; 
                                        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['accent2']}); 
                                        border-radius: 15px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        font-size: 4rem;">
                                🎤
                            </div>
                        """, unsafe_allow_html=True)
                
                with col_info:
                    st.markdown(f"""
                        <h2 style="color: {COLORS['primary']};">{selected_artist}</h2>
                        <p style="font-size: 1.2rem;"><strong>Genre:</strong> {latest['genre']}</p>
                        <p style="font-size: 1.2rem;"><strong>Plateforme:</strong> {latest['plateforme']}</p>
                    """, unsafe_allow_html=True)
                    
                    if 'url' in latest and pd.notna(latest['url']):
                        if st.button("🎵 Écouter sur " + latest['plateforme'], key="listen_artist_pred"):
                            st.markdown(f'<meta http-equiv="refresh" content="0; url={latest["url"]}">', unsafe_allow_html=True)
                
                st.markdown("---")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("👥 Followers/Fans", f"{int(followers):,}")
                with col2:
                    st.metric("⭐ Score Actuel", f"{latest['score_potentiel']:.1f}")
                with col3:
                    if len(artist_data) > 1:
                        first_f = artist_data.iloc[0]['followers_chart']
                        if first_f > 0:
                            growth = ((followers - first_f) / first_f) * 100
                            st.metric("📈 Croissance", f"{growth:.1f}%")
                
                st.markdown("---")
                
                if len(artist_data) > 1:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 👥 Évolution des Followers/Fans")
                        chart_data = artist_data.copy()
                        chart_data['date_jour'] = chart_data['date_collecte'].dt.date
                        chart_data = chart_data.drop_duplicates(subset=['date_jour'], keep='last')
                        chart_data = chart_data[chart_data['followers_chart'] > 0]
                        if len(chart_data) > 0:
                            fig = px.line(
                                chart_data, 
                                x='date_jour', 
                                y='followers_chart',
                                markers=True,
                                labels={'date_collecte': 'Date', 'followers_chart': 'Followers/Fans'}
                            )
                            fig.update_traces(
                                line_color=COLORS['accent3'], 
                                line_width=3, 
                                marker=dict(size=10, color=COLORS['primary'])
                            )
                            fig.update_layout(
                                plot_bgcolor=COLORS['bg_card'], 
                                paper_bgcolor=COLORS['bg_card'], 
                                font_color=COLORS['text'],
                                xaxis_title="Date",
                                yaxis_title="Followers/Fans",
                                height=280
                            )
                            fig.update_xaxes(
                            tickformat="%d/%m/%Y"  
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### ⭐ Évolution du Score")
                        chart_data = artist_data.copy()
                        chart_data['date_jour'] = chart_data['date_collecte'].dt.date
                        chart_data = chart_data.drop_duplicates(subset=['date_jour'], keep='last')
                        fig = px.line(
                            chart_data, 
                            x='date_jour', 
                            y='score_potentiel',
                            markers=True,
                            labels={'date_jour': 'Date', 'score_potentiel': 'Score'}
                        )
                        fig.update_traces(
                            line_color=COLORS['secondary'], 
                            line_width=3, 
                            marker=dict(size=10, color=COLORS['accent1'])
                        )
                        fig.update_layout(
                            plot_bgcolor=COLORS['bg_card'], 
                            paper_bgcolor=COLORS['bg_card'], 
                            font_color=COLORS['text'],
                            xaxis_title="Date",
                            yaxis_title="Score de Potentiel",
                            height=280
                        )
                        fig.update_xaxes(
                            tickformat="%d/%m/%Y"  
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Aucune donnée trouvée pour {selected_artist}")
        
    else:
        #  AFFICHAGE DES PRÉDICTIONS
        st.markdown("")
        
        st.markdown(f"""
        <div class="info-box">
        <h4 style="color: {COLORS['accent3']};">💡 Comment ça marche ?</h4>
        <p style="font-size: 1.05rem; line-height: 1.6;">
        Notre modèle d'Intelligence Artificielle identifie les artistes émergents avec le plus fort potentiel.
        Cliquez sur "Voir évolution" pour voir les détails !
        </p>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            predictions_df = pd.read_csv('data/predictions_ml.csv')
            
            #  FILTRER les artistes VRAIMENT émergents
            original_count = len(predictions_df)
            
            if 'followers' in predictions_df.columns:
                predictions_df = predictions_df[predictions_df['followers'] < 80000]
                
            elif 'fans' in predictions_df.columns:
                predictions_df = predictions_df[predictions_df['fans'] < 80000]
                
            else:
                st.warning(" Impossible de filtrer les artistes connus (colonne followers manquante)")
            
            # Filtrer selon genre
            if selected_genre != 'Tous':
                predictions_df = predictions_df[predictions_df['genre'] == selected_genre]
            
            if len(predictions_df) == 0:
                st.warning(" Aucun artiste émergent avec ces filtres")
            else:
                st.markdown("### 🌟 Top 10 Artistes Émergents")
                
                top10 = predictions_df.nlargest(min(10, len(predictions_df)), 'proba_star')
                
                # Graphique
                fig = px.bar(
                    top10.sort_values('proba_star'),
                    y='nom',
                    x='proba_star',
                    orientation='h',
                    text='proba_star',
                    color='proba_star',
                    color_continuous_scale=['#47559D', '#FF1B8D'],
                    labels={'proba_star': 'Probabilité de Succès', 'nom': 'Artiste'}
                )
                fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
                fig.update_layout(
                    plot_bgcolor=COLORS['bg_card'],
                    paper_bgcolor=COLORS['bg_card'],
                    font_color=COLORS['text'],
                    height=600,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("### Cliquez pour voir l'évolution détaillée")
                
                # FONCTION DE NORMALISATION AMÉLIORÉE
                def normalize_name(name):
                    """Normalise un nom pour le matching - VERSION STRICTE"""
                    if pd.isna(name):
                        return ""
                    # Enlever accents, espaces, tirets, apostrophes, mettre en minuscules
                    import unicodedata
                    name = str(name).lower().strip()
                    name = unicodedata.normalize('NFD', name)
                    name = ''.join(c for c in name if unicodedata.category(c) != 'Mn')
                    name = name.replace('-', '').replace('_', '').replace("'", '').replace(' ', '')
                    return name

                # CRÉER COLONNES NORMALISÉES
                top10_with_images = top10.copy()
                top10_with_images['nom_normalized'] = top10_with_images['nom'].apply(normalize_name)

                # Merge 1: latest_metrics_df
                if 'nom_artiste' in latest_metrics_df.columns and 'image_url' in latest_metrics_df.columns:
                    temp_latest = latest_metrics_df[['nom_artiste', 'image_url', 'url']].copy()
                    temp_latest = temp_latest.dropna(subset=['image_url'])
                    temp_latest = temp_latest[temp_latest['image_url'] != '']
                    temp_latest['nom_normalized'] = temp_latest['nom_artiste'].apply(normalize_name)
                    temp_latest = temp_latest.drop_duplicates('nom_normalized', keep='first')
                    
                    top10_with_images = top10_with_images.merge(
                        temp_latest[['nom_normalized', 'image_url', 'url']],
                        on='nom_normalized',
                        how='left'
                    )

                # Merge 2: artistes_df (fallback)
                if 'image_url' not in top10_with_images.columns or top10_with_images['image_url'].isna().any():
                    if 'nom' in artistes_df.columns and 'image_url' in artistes_df.columns:
                        temp_artistes = artistes_df[['nom', 'image_url']].copy()
                        temp_artistes = temp_artistes.dropna(subset=['image_url'])
                        temp_artistes = temp_artistes[temp_artistes['image_url'] != '']
                        temp_artistes['nom_normalized'] = temp_artistes['nom'].apply(normalize_name)
                        temp_artistes = temp_artistes.drop_duplicates('nom_normalized', keep='first')
                        
                        # Merge avec suffixes
                        top10_with_images = top10_with_images.merge(
                            temp_artistes[['nom_normalized', 'image_url']],
                            on='nom_normalized',
                            how='left',
                            suffixes=('', '_fallback')
                        )
                        
                        # Remplir les images manquantes
                        if 'image_url_fallback' in top10_with_images.columns:
                            if 'image_url' not in top10_with_images.columns:
                                top10_with_images['image_url'] = top10_with_images['image_url_fallback']
                            else:
                                top10_with_images['image_url'].fillna(top10_with_images['image_url_fallback'], inplace=True)
                            top10_with_images.drop('image_url_fallback', axis=1, inplace=True)
                        
                
                # Grille 5 colonnes
                for row_idx in range(0, len(top10_with_images), 5):
                    cols = st.columns(5)
                    
                    for col_idx, (_, artist) in enumerate(list(top10_with_images.iloc[row_idx:row_idx+5].iterrows())):
                        with cols[col_idx]:
                            #  CASE À COCHER
                            is_checked = st.checkbox(
                                "⭐",
                                value=artist['nom'] in st.session_state.temp_interesses_artistes,
                                key=f"check_pred_{row_idx}_{col_idx}_{artist['nom']}",
                                label_visibility="collapsed"
                            )
                            
                            if is_checked and artist['nom'] not in st.session_state.temp_interesses_artistes:
                                st.session_state.temp_interesses_artistes.append(artist['nom'])
                            elif not is_checked and artist['nom'] in st.session_state.temp_interesses_artistes:
                                st.session_state.temp_interesses_artistes.remove(artist['nom'])
                            
                            # Photo
                            if 'image_url' in artist and pd.notna(artist['image_url']) and artist['image_url']:
                                st.markdown(f"""
                                    <div style="width: 100%; 
                                                aspect-ratio: 1/1;
                                                overflow: hidden;
                                                border-radius: 10px;
                                                background: {COLORS['bg_card']};
                                                margin-bottom: 10px;">
                                        <img src="{artist['image_url']}" 
                                            style="width: 100%; 
                                                    height: 100%; 
                                                    object-fit: cover;">
                                    </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.markdown(f"""
                                    <div style="width: 100%; 
                                                aspect-ratio: 1/1;
                                                background: linear-gradient(135deg, {COLORS['accent1']}, {COLORS['accent2']}); 
                                                border-radius: 10px;
                                                display: flex;
                                                align-items: center;
                                                justify-content: center;
                                                font-size: 3rem;
                                                margin-bottom: 10px;">
                                        🎵
                                    </div>
                                """, unsafe_allow_html=True)
                            
                            # Nom
                            artist_name = artist['nom'] or "Artiste Inconnu"
                            display_name = artist_name[:18] + '...' if len(artist_name) > 18 else artist_name
                            st.markdown(f"<div style='text-align: center;'><strong>{display_name}</strong></div>", unsafe_allow_html=True)
                            st.caption(f"⭐ {artist['proba_star']:.1%}")

                            # BOUTONS CÔTE À CÔTE
                            col_ecouter_pred, col_evo_pred = st.columns(2)

                            with col_ecouter_pred:
                                # Chercher URL dans latest_metrics_df
                                url_artiste = ""
                                matching = latest_metrics_df[latest_metrics_df['nom_artiste'] == artist['nom']]
                                if len(matching) > 0 and 'url' in matching.columns:
                                    url_artiste = matching.iloc[0].get('url', '')
                                
                                if url_artiste and pd.notna(url_artiste) and str(url_artiste).strip() != '':
                                    st.link_button(
                                        "🎵",
                                        str(url_artiste),
                                        use_container_width=True
                                    )
                                else:
                                    st.button(
                                        "🎵",
                                        disabled=True,
                                        use_container_width=True,
                                        key=f"disabled_pred_ecouter_{row_idx}_{col_idx}"
                                    )

                            with col_evo_pred:
                                if st.button(
                                    "ℹ️",
                                    key=f"pred_detail_{row_idx}_{col_idx}_{artist['nom']}",
                                    use_container_width=True
                                ):
                                    st.session_state.selected_prediction_artist = artist['nom']
                                    st.session_state.go_to_evolution = True
                                    st.session_state.active_tab = 3

                #  BOUTON VALIDATION (après la grille)
                st.markdown("---")

                col_left, col_center, col_right = st.columns([2, 1, 2])
                with col_center:
                    if st.button("VALIDER", key="valider_predictions", use_container_width=True):
                        for artiste in st.session_state.temp_interesses_artistes:
                            if artiste not in st.session_state.artistes_interesses:
                                st.session_state.artistes_interesses.append(artiste)
                        
                        st.success(f" {len(st.session_state.temp_interesses_artistes)} artiste(s) ajouté(s) !")
                        st.session_state.temp_interesses_artistes = []
                
                # Statistiques
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    stars_predicted = (predictions_df['proba_star'] > 0.5).sum()
                    st.metric("🌟 Stars Prédites (>50%)", stars_predicted)
                with col2:
                    avg_proba = predictions_df['proba_star'].mean()
                    st.metric("📊 Probabilité Moyenne", f"{avg_proba:.1%}")
                with col3:
                    high_potential = (predictions_df['proba_star'] > 0.3).sum()
                    st.metric("⚡ Haut Potentiel (>30%)", high_potential)

                st.markdown("---")
                st.markdown("### 📊 Performances du Modèle")

                try:
                    # Charger les métriques
                    with open('data/ml_metrics.json', 'r') as f:
                        metrics = json.load(f)
                    
                    cm = np.array(metrics['confusion_matrix'])
                    report = metrics['classification_report']
                    
                    col_cm, col_report = st.columns([1, 1])
                    
                    # ============================================================================
                    # COLONNE 1 : MATRICE DE CONFUSION AMÉLIORÉE
                    # ============================================================================
                    with col_cm:
                        st.markdown("####  Matrice de Confusion")
                        
                        # Créer heatmap avec TEXTE ADAPTATIF
                        fig_cm = go.Figure()
                        
                        # Ajouter la heatmap
                        fig_cm.add_trace(go.Heatmap(
                            z=cm,
                            x=['Non-Star', 'Star'],
                            y=['Non-Star', 'Star'],
                            colorscale='Blues',
                            showscale=False,
                            hovertemplate='Prédit: %{x}<br>Réel: %{y}<br>Valeur: %{z}<extra></extra>'
                        ))
                        
                        # ANNOTATIONS AVEC COULEUR ADAPTATIVE
                        for i in range(len(cm)):
                            for j in range(len(cm[i])):
                                value = cm[i][j]
                                
                                #  Texte BLANC pour cellules foncées, NOIR pour cellules claires
                                # Seuil : si valeur > 50% du max, texte blanc, sinon noir
                                text_color = 'white' if value > (cm.max() / 2) else 'black'
                                
                                fig_cm.add_annotation(
                                    x=j,
                                    y=i,
                                    text=f"<b>{value}</b>",
                                    font=dict(size=24, color=text_color),
                                    showarrow=False
                                )
                        
                        # Layout
                        fig_cm.update_layout(
                            xaxis_title="Prédiction",
                            yaxis_title="Réalité",
                            plot_bgcolor=COLORS['bg_card'],
                            paper_bgcolor=COLORS['bg_card'],
                            font=dict(color='white', size=12),
                            height=350,
                            margin=dict(l=80, r=20, t=20, b=80),
                            xaxis=dict(
                                side='bottom',
                                showgrid=False,
                                tickfont=dict(size=14)
                            ),
                            yaxis=dict(
                                showgrid=False,
                                tickfont=dict(size=14)
                            )
                        )
                        
                        st.plotly_chart(fig_cm, use_container_width=True)
                        
                        # Caption
                        total = metrics.get('total_samples', 0)
                        stars = metrics.get('stars_count', 0)
                        non_stars = metrics.get('non_stars_count', 0)
                        
                        st.caption(f" Total : {total} artistes |  Stars : {stars} |  Non-Stars : {non_stars}")
                    
                    # ============================================================================
                    # COLONNE 2 : RAPPORT DE CLASSIFICATION STYLISÉ
                    # ============================================================================
                    with col_report:
                        st.markdown("####  Rapport de Classification")
                        
                        # Extraire les données
                        non_star = report.get('0', {})
                        star = report.get('1', {})
                        
                        #  CRÉER DATAFRAME AVEC COULEURS
                        df_report = pd.DataFrame({
                            'Classe': [' Non-Star', ' Star'],
                            'Précision': [
                                f"{non_star.get('precision', 0)*100:.1f}%",
                                f"{star.get('precision', 0)*100:.1f}%"
                            ],
                            'Rappel': [
                                f"{non_star.get('recall', 0)*100:.1f}%",
                                f"{star.get('recall', 0)*100:.1f}%"
                            ],
                            'F1-Score': [
                                f"{non_star.get('f1-score', 0)*100:.1f}%",
                                f"{star.get('f1-score', 0)*100:.1f}%"
                            ],
                            'Support': [
                                int(non_star.get('support', 0)),
                                int(star.get('support', 0))
                            ]
                        })
                        
                        # STYLE PROFESSIONNEL AVEC COULEURS
                        def style_dataframe(df):
                            """Styliser le DataFrame"""
                            
                            def color_precision(val):
                                """Couleur basée sur la valeur"""
                                try:
                                    num = float(val.replace('%', ''))
                                    if num >= 90:
                                        return 'background-color: #2d5016; color: white'  # Vert foncé
                                    elif num >= 80:
                                        return 'background-color: #4a7c2c; color: white'  # Vert moyen
                                    elif num >= 70:
                                        return 'background-color: #7a9b5e; color: white'  # Vert clair
                                    else:
                                        return 'background-color: #9b6e4a; color: white'  # Orange
                                except:
                                    return ''
                            
                            # Appliquer le style
                            styled = df.style\
                                .applymap(color_precision, subset=['Précision', 'Rappel', 'F1-Score'])\
                                .set_properties(**{
                                    'text-align': 'center',
                                    'font-size': '14px',
                                    'padding': '10px'
                                })\
                                .set_table_styles([
                                    {'selector': 'th', 'props': [
                                        ('background-color', COLORS['accent2']),
                                        ('color', 'white'),
                                        ('font-weight', 'bold'),
                                        ('text-align', 'center'),
                                        ('padding', '12px')
                                    ]},
                                    {'selector': 'td', 'props': [
                                        ('border', '1px solid #444')
                                    ]}
                                ])
                            
                            return styled
                        
                        st.dataframe(
                            style_dataframe(df_report),
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Métriques globales
                        st.markdown("---")
                        
                        accuracy = metrics.get('accuracy', 0)
                        macro_f1 = report.get('macro avg', {}).get('f1-score', 0)
                        weighted_f1 = report.get('weighted avg', {}).get('f1-score', 0)
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(" Accuracy", f"{accuracy*100:.1f}%")
                        
                        with col2:
                            st.metric(" Macro F1", f"{macro_f1*100:.1f}%")
                        
                        with col3:
                            st.metric(" Weighted F1", f"{weighted_f1*100:.1f}%")
                        
                        # Explications
                        st.caption("""
                        ** Explications :**
                        - **Précision** : Sur 100 prédits "Star", combien le sont vraiment
                        - **Rappel** : Sur 100 vrais "Stars", combien sont détectés
                        - **F1-Score** : Équilibre entre précision et rappel
                        """)

                except FileNotFoundError:
                    st.warning(" Métriques ML non disponibles. Relancez `python ml_prediction.py`")
                except Exception as e:
                    st.warning(f" Erreur chargement métriques : {e}")
            
        except FileNotFoundError:
            st.error(" Fichier de prédictions non trouvé")
            st.info(" Lancez : `python ml_prediction.py`")
        except Exception as e:
            st.error(f" Erreur : {e}")
            import traceback
            st.error(traceback.format_exc())

# ==================== TAB 8: MON PROFIL ====================
elif st.session_state.active_page == "Mon Profil":
    with st.spinner("Chargement de votre profil..."):
        st.markdown("## 👤 Mon Profil")
    
    col_user, col_logout = st.columns([3, 1])
    with col_user:
        st.markdown(f"**Connecté :** {st.session_state.get('username', 'Utilisateur')}")
    with col_logout:
        if st.button("🚪 Se déconnecter", key="logout_profil", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()
    
    st.markdown("---")
    
    st.markdown("### ⭐ Mes Artistes")
    
    if len(st.session_state.artistes_interesses) == 0:
        st.info(" Aucun artiste ajouté pour le moment. Explorez les pages 'Les Tops', 'Les Artistes' ou 'Évolution' pour ajouter des artistes à votre sélection !")
    else:
        artistes_data = latest_metrics_df[latest_metrics_df['nom_artiste'].isin(st.session_state.artistes_interesses)]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("⭐ Artistes suivis", len(st.session_state.artistes_interesses))
        with col2:
            spotify_count = len(artistes_data[artistes_data['plateforme'] == 'Spotify'])
            st.metric("🟢 Sur Spotify", spotify_count)
        with col3:
            deezer_count = len(artistes_data[artistes_data['plateforme'] == 'Deezer'])
            st.metric("🔵 Sur Deezer", deezer_count)
        
        st.markdown("---")
        
        for idx, artiste_nom in enumerate(st.session_state.artistes_interesses):
            # CRÉER UNE CLÉ UNIQUE basée sur nom + index
            safe_nom = str(artiste_nom).replace(' ', '_').replace("'", '').replace('-', '_')[:30]
            unique_id = f"{safe_nom}_{idx}"
            
            artist_row = filtered_df[filtered_df['nom_artiste'] == artiste_nom]
            
            if len(artist_row) > 0:
                artist = artist_row.iloc[0]
                
                col_check, col_img, col_info, col_actions = st.columns([0.5, 1, 3, 1.5])
                
                with col_check:
                    st.write("")
                    st.write("")
                    st.markdown("")
                
                with col_img:
                    if 'image_url' in artist and pd.notna(artist['image_url']) and artist['image_url']:
                        st.image(artist['image_url'], width=80)
                    else:
                        st.markdown(f"""
                            <div style="width: 80px; 
                                        height: 80px; 
                                        background: linear-gradient(135deg, {COLORS['accent1']}, {COLORS['accent2']}); 
                                        border-radius: 10px;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        font-size: 2rem;">
                                🎵
                            </div>
                        """, unsafe_allow_html=True)
                
                with col_info:
                    st.markdown(f"### {artiste_nom}")
                    st.caption(f"{artist['plateforme']} | {artist['genre']}")
                    st.caption(f"⭐ Score: {artist['score_potentiel']:.1f} | 👥 {int(artist['followers_total']):,} followers/fans")
                
                with col_actions:
                    st.write("")
                    
                    # URL de l'artiste
                    url_artiste = artist.get('url', '')
                    
                    # Bouton Écouter
                    if url_artiste and pd.notna(url_artiste) and str(url_artiste).strip() != '':
                        st.link_button(
                            "🎵",
                            str(url_artiste),
                            use_container_width=True
                        )
                    else:
                        st.button(
                            "🎵",
                            disabled=True,
                            use_container_width=True,
                            key=f"profil_ecouter_disabled_{unique_id}"
                        )
                    
                    # Bouton Détails
                    if st.button(
                        "ℹ️",
                        key=f"profil_details_{unique_id}",
                        use_container_width=True
                    ):
                        st.session_state.selected_artist_evolution = artiste_nom
                        st.session_state.previous_page = "Mon Profil"
                        st.session_state.go_to_evolution = True
                    
                    # Bouton Retirer
                    if st.button(
                        "🗑️",
                        key=f"profil_del_{unique_id}",
                        use_container_width=True
                    ):
                        st.session_state.artistes_interesses.remove(artiste_nom)
                        
                
                st.markdown("---")
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"🎵 **{artiste_nom}**")
                    st.caption("(Non visible avec les filtres actuels)")
                with col2:
                    if st.button("🗑️ Retirer", key=f"profil_del_missing_{unique_id}", use_container_width=True):
                        st.session_state.artistes_interesses.remove(artiste_nom)
                        
                st.markdown("---")
                
# Footer
st.divider()
st.caption("JEK2 Records - MusicTalentRadar | La data au rythme du son | On capte les talents avant qu'ils n'explosent!")