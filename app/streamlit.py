import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time
import sys
import os
from PIL import Image
import math
import base64

import auth  

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

# Initialiser les artistes intéressés dans session_state
if 'artistes_interesses' not in st.session_state:
    st.session_state.artistes_interesses = []

if 'temp_interesses_artistes' not in st.session_state:
    st.session_state.temp_interesses_artistes = []

if 'temp_interesse_evolution' not in st.session_state:
    st.session_state.temp_interesse_evolution = None

if 'page_artistes' not in st.session_state:
    st.session_state.page_artistes = 1
    
# ============= AUTHENTIFICATION =============
if not auth.require_authentication(): # type: ignore
    if st.session_state.get('show_login', False):
        auth.login_form() # type: ignore
    else:
        auth.public_page_about() # type: ignore
    st.stop()

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
    /* Fond principal avec image */
    .stApp {{
        {bg_style}
    }}
    
    /* Overlay semi-transparent pour lisibilité */
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
    
    /* Assurer que le contenu est au-dessus de l'overlay */
    .main > div {{
        position: relative;
        z-index: 1;
    }}
    
    /* Header principal */
    .main-header {{
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['secondary']}, {COLORS['accent1']});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 1rem 0;
        text-transform: uppercase;
        letter-spacing: 3px;
    }}
    
    .subtitle {{
        color: {COLORS['accent3']};
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }}
    
    /* Sidebar sans espace en haut */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['bg_card']} 0%, #1a0a2e 100%);
        padding-top: 0 !important;
    }}
    
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0 !important;
        margin-top: 0 !important;
    }}
    
    /* Boutons en GRAS */
    .stButton button {{
        background: linear-gradient(90deg, {COLORS['primary']}, {COLORS['accent2']});
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold !important;
    }}
    
    /* Titres des pages en GRAS et plus GRANDS */
    .stTabs [data-baseweb="tab-list"] button {{
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }}
    
    /* Titres h1, h2, h3 en gras */
    h1, h2, h3 {{
        color: {COLORS['accent3']} !important;
        font-weight: 900 !important;
        font-size: 1.8rem !important;
    }}
    
    h2 {{
        font-size: 1.6rem !important;
    }}
    
    h3 {{
        font-size: 1.4rem !important;
    }}
    
    /* Métriques - Chiffres en BLANC */
    [data-testid="stMetricValue"] {{
        color: white !important;
        font-size: 2rem !important;
        font-weight: bold !important;
    }}
    
    /* Labels des métriques */
    [data-testid="stMetricLabel"] {{
        color: {COLORS['text']} !important;
        font-weight: 600 !important;
    }}
    
    /* RESPONSIVE MOBILE */
    @media (max-width: 768px) {{
        .main-header {{
            font-size: 1.8rem !important;
            letter-spacing: 1px !important;
        }}
        
        .subtitle {{
            font-size: 0.9rem !important;
        }}
        
        .metric-card {{
            padding: 1rem !important;
            margin: 0.5rem 0 !important;
        }}
        
        [data-testid="stSidebar"] {{
            width: 80% !important;
        }}
    }}
    
    /* Cartes métriques */
    .metric-card {{
        background: linear-gradient(135deg, {COLORS['bg_card']} 0%, #2a1a3e 100%);
        padding: 2rem;
        border-radius: 15px;
        border-left: 4px solid {COLORS['primary']};
        box-shadow: 0 8px 16px rgba(255, 27, 141, 0.2);
        margin: 1rem 0;
    }}
    
    .stMarkdown, p, li {{
        color: {COLORS['text']} !important;
    }}
    
    .info-box {{
        background: linear-gradient(135deg, #1a0a2e 0%, #2a1a3e 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid {COLORS['accent1']};
        margin: 1rem 0;
    }}
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)
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

def get_latest_metrics(metriques_df):
    """Récupère les dernières métriques par artiste/plateforme"""
    if metriques_df.empty:
        return pd.DataFrame().reset_index(drop=True)
    
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
    if fans < 10000:
        return "Micro (1k-10k)"
    elif fans < 30000:
        return "Petit (10k-30k)"
    elif fans < 60000:
        return "Moyen (30k-60k)"
    else:
        return "Large (60k-100k)"

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
    
    latest_metrics_df = get_latest_metrics(metriques_df)
    latest_metrics_df = latest_metrics_df.reset_index(drop=True)
    
    if latest_metrics_df.empty:
        st.error(" Aucune métrique trouvée")
        st.stop()
    
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
        latest_metrics_df['followers_total'] = latest_metrics_df.get('followers', 0).fillna(0) + latest_metrics_df.get('fans', 0).fillna(0) # type: ignore
    
    # Catégorie fans
    latest_metrics_df['categorie_fans'] = latest_metrics_df['followers_total'].apply(get_fan_category)
    
except Exception as e:
    st.error(f" Erreur critique: {e}")
    st.stop()

# ==================== HEADER ====================
col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    st.markdown('<div class="main-header">JEK2 RECORDS</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">⭐ MUSIC TALENT RADAR ⭐</div>', unsafe_allow_html=True)

# ==================== SIDEBAR ====================
with st.sidebar:
    # Logo sans espace
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
    if os.path.isfile(logo_path):
        st.image(logo_path, width=200)

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
    
    categories_fans = ['Tous', 'Micro (1k-10k)', 'Petit (10k-30k)', 'Moyen (30k-60k)', 'Large (60k-100k)']
    selected_fans = st.selectbox("👥 Nombre de fans", categories_fans)
    
    min_score = st.slider("⭐ Score minimum", 0, 100, 0, 5)

# ==================== FILTRES ====================
filtered_df = latest_metrics_df.copy().reset_index(drop=True)

# Exclure Electro-EDM
if 'genre' in filtered_df.columns and len(filtered_df) > 0:
    try:
        filtered_df = filtered_df.query('genre != "Electro-EDM"').reset_index(drop=True)
    except:
        mask = (filtered_df['genre'] != 'Electro-EDM').values
        filtered_df = filtered_df[mask].copy().reset_index(drop=True)

# Filtre Plateforme
if selected_plateforme != 'Tous':
    filtered_df = filtered_df[filtered_df['plateforme'] == selected_plateforme].reset_index(drop=True)

# Filtre Genre
if selected_genre != 'Tous':
    filtered_df = filtered_df[filtered_df['genre'] == selected_genre].reset_index(drop=True)

# Filtre Fans
if selected_fans != 'Tous':
    filtered_df = filtered_df[filtered_df['categorie_fans'] == selected_fans].reset_index(drop=True)

# Filtre Score
filtered_df = filtered_df[filtered_df['score_potentiel'] >= min_score].reset_index(drop=True)

# Top artistes
top_df = filtered_df.sort_values('score_potentiel', ascending=False).reset_index(drop=True)

# ✅ SUPPRIMER COLONNES DUPLIQUÉES + RESET INDEX
filtered_df = filtered_df.loc[:, ~filtered_df.columns.duplicated()]
top_df = top_df.loc[:, ~top_df.columns.duplicated()]
filtered_df = filtered_df.reset_index(drop=True)
top_df = top_df.reset_index(drop=True)

# ==================== TABS CLASSIQUES ====================
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "**📊 VUE D'ENSEMBLE**", 
    "**🌟 LES TOP**", 
    "**🎤 LES ARTISTES**", 
    "**📈 ÉVOLUTION**", 
    "**🔔 ALERTES**",
    "**🔮 PRÉDICTIONS**",
    "**ℹ️ À PROPOS DE JEK2**",
    "**👤 MON PROFIL**"
])

# ==================== TAB 1: VUE D'ENSEMBLE ====================
with tab1:
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
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Distribution des scores")
        if len(filtered_df) > 0:
            fig = px.histogram(
                filtered_df, 
                x='score_potentiel', 
                nbins=20, 
                color='plateforme',
                color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']},
                labels={'count': "Nombre d'artistes", 'score_potentiel': 'Score'}
            )
            fig.update_layout(
                plot_bgcolor=COLORS['bg_card'], 
                paper_bgcolor=COLORS['bg_card'], 
                font_color=COLORS['text'],
                yaxis_title="Nombre d'artistes",
                xaxis_title="Score",
                legend=dict(font=dict(color='white'))
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Ce graphique montre la répartition des scores de potentiel. La plupart des artistes se situent entre 40 et 70 points, avec quelques talents exceptionnels au-delà de 80.")
        else:
            st.info("Aucune donnée avec ces filtres")

    with col2:
        st.markdown("### 🎵 Répartition par Genre")
        if 'genre' in filtered_df.columns and len(filtered_df) > 0:
            genre_counts = filtered_df['genre'].value_counts()
            
            fig = px.pie(
                values=genre_counts.values,
                names=genre_counts.index,
                hole=0.4,
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
                legend=dict(font=dict(color='white'))
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
                    height=400,
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
                    height=400,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Les 5 artistes Spotify avec les meilleurs scores de potentiel. Ces artistes montrent une croissance prometteuse et un engagement fort de leur communauté.")
            else:
                st.info("Aucun artiste Spotify avec ces filtres")

# ==================== TAB 2: LES TOP ====================
with tab2:
    st.markdown("## 🌟 Les Top")
    
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
            height=900,
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
            
            fig = px.bar(
                top5_evolution.sort_values('evolution'),
                y='nom_artiste',
                x='evolution',
                orientation='h',
                text='evolution',
                color='evolution',
                color_continuous_scale=['#FFA500', '#FF1B8D', '#21B178'],
                labels={'evolution': 'Évolution (%)', 'nom_artiste': 'Artiste'}
            )
            fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig.update_layout(
                plot_bgcolor=COLORS['bg_card'],
                paper_bgcolor=COLORS['bg_card'],
                font_color=COLORS['text'],
                height=400,
                showlegend=False,
                yaxis={'categoryorder':'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Les 5 artistes ayant connu la plus forte progression de score. Cette croissance indique une dynamique positive et un potentiel de percée prochaine.")
        else:
            st.info("Pas assez de données historiques pour calculer les évolutions")
        
        st.markdown("---")
        
        st.markdown("### 🌐 Répartition Plateforme (Top 50)")
        top50 = top_df.head(50)
        platform_counts = top50['plateforme'].value_counts()
        
        fig = px.pie(
            values=platform_counts.values,
            names=platform_counts.index,
            color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']},
            hole=0.4
        )
        fig.update_layout(
            plot_bgcolor=COLORS['bg_card'],
            paper_bgcolor=COLORS['bg_card'],
            font_color=COLORS['text'],
            legend=dict(font=dict(color='white'))
        )
        fig.update_traces(textfont_color='white', textfont_size=16)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Répartition Spotify vs Deezer parmi les 50 meilleurs. Cela montre quelle plateforme domine dans le Top.")
        
        st.markdown("---")
        
        st.markdown("### 👥 Distribution Followers (Top 50)")
        
        fig = px.histogram(
            top50,
            x='followers_total',
            nbins=15,
            color='plateforme',
            color_discrete_map={'Spotify': COLORS['accent3'], 'Deezer': COLORS['secondary']},
            labels={'followers_total': 'Followers/Fans', 'count': 'Nombre d\'artistes'}
        )
        fig.update_layout(
            plot_bgcolor=COLORS['bg_card'],
            paper_bgcolor=COLORS['bg_card'],
            font_color=COLORS['text'],
            height=400,
            legend=dict(font=dict(color='white'))
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Distribution du nombre de followers/fans parmi les 50 meilleurs. La plupart ont entre 10k et 60k followers, zone idéale pour la détection de talents.")
    else:
        st.info("Aucun artiste disponible")

# ==================== TAB 3: LES ARTISTES ====================
with tab3:
    st.markdown("## 🎤 Les Artistes")
    
    if len(filtered_df) > 0:
        col_tri1, col_tri2 = st.columns(2)
        
        with col_tri1:
            tri_par = st.selectbox(
                "📊 Trier par",
                ["Score", "Followers/Fans"],
                key="tri_artistes"
            )
        
        with col_tri2:
            ordre = st.selectbox(
                "📈 Ordre",
                ["Décroissant", "Croissant"],
                key="ordre_artistes"
            )
        
        if tri_par == "Score":
            artistes_sorted = filtered_df.sort_values('score_potentiel', ascending=(ordre == "Croissant"))
        else:
            artistes_sorted = filtered_df.sort_values('followers_total', ascending=(ordre == "Croissant"))
        
        ITEMS_PER_PAGE = 50
        total_artistes = len(artistes_sorted)
        total_pages = math.ceil(total_artistes / ITEMS_PER_PAGE)
        
        start_idx = (st.session_state.page_artistes - 1) * ITEMS_PER_PAGE
        end_idx = start_idx + ITEMS_PER_PAGE
        page_artistes = artistes_sorted.iloc[start_idx:end_idx]
        
        for i in range(0, len(page_artistes), 5):
            cols = st.columns(5)
            
            for col_idx, (_, artist) in enumerate(list(page_artistes.iloc[i:i+5].iterrows())):
                with cols[col_idx]:
                    is_checked = st.checkbox(
                        "",
                        value=artist['nom_artiste'] in st.session_state.temp_interesses_artistes,
                        key=f"check_artiste_{start_idx + i + col_idx}_{artist['nom_artiste']}"
                    )
                    
                    if is_checked and artist['nom_artiste'] not in st.session_state.temp_interesses_artistes:
                        st.session_state.temp_interesses_artistes.append(artist['nom_artiste'])
                    elif not is_checked and artist['nom_artiste'] in st.session_state.temp_interesses_artistes:
                        st.session_state.temp_interesses_artistes.remove(artist['nom_artiste'])
                    
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
                    
                    artist_name = artist['nom_artiste']
                    display_name = artist_name[:18] + '...' if len(artist_name) > 18 else artist_name
                    st.markdown(f"**{display_name}**")
                    st.caption(f"{artist['plateforme']} | {artist['genre']}")
                    st.caption(f"⭐ {artist['score_potentiel']:.1f} | 👥 {int(artist['followers_total']):,}")
                    
                    if 'url' in artist and pd.notna(artist['url']):
                        if st.button("🎵 Écouter", key=f"listen_artiste_{start_idx + i + col_idx}", use_container_width=True):
                            st.markdown(f'<a href="{artist["url"]}" target="_blank">Ouvrir</a>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        col_left, col_center, col_right = st.columns([2, 1, 2])
        with col_center:
            if st.button("VALIDER MES SELECTIONS", key="valider_artistes", use_container_width=True):
                for artiste in st.session_state.temp_interesses_artistes:
                    if artiste not in st.session_state.artistes_interesses:
                        st.session_state.artistes_interesses.append(artiste)
                
                st.success(f" {len(st.session_state.temp_interesses_artistes)} artiste(s) ajouté(s) !")
                st.session_state.temp_interesses_artistes = []
                time.sleep(1)
                st.rerun()
        
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
with tab4:
    st.markdown("### 📈 Évolution Temporelle")
    
    if len(metriques_df) > 0 and 'nom_artiste' in metriques_df.columns:
        filtered_artists = filtered_df.copy()
        artistes_list = sorted(filtered_artists['nom_artiste'].dropna().unique())
        
        if len(artistes_list) == 0:
            st.info("Aucun artiste ne correspond à vos filtres")
        else:
            if 'selected_artist_evolution' not in st.session_state:
                st.session_state.selected_artist_evolution = artistes_list[0]
            
            if st.session_state.selected_artist_evolution not in artistes_list:
                st.session_state.selected_artist_evolution = artistes_list[0]
            
            selected_artist = st.selectbox(
                "🎤 Artiste", 
                artistes_list,
                index=artistes_list.index(st.session_state.selected_artist_evolution)
            )
            
            st.session_state.selected_artist_evolution = selected_artist
            
            if selected_artist:
                artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
                
                if not artist_data.empty:
                    artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
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
                                key=f"check_evolution_{selected_artist}"
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
                                
                                time.sleep(1)
                                st.rerun()

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
                            if len(chart_data) > 0:
                                fig = px.line(
                                    chart_data, 
                                    x='date_collecte', 
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
                                    height=400
                                )
                                st.plotly_chart(fig, use_container_width=True)
                                st.caption("👥 L'évolution du nombre de followers/fans dans le temps. Une courbe ascendante indique une croissance régulière de l'audience.")
                        
                        with col2:
                            st.markdown("#### ⭐ Évolution du Score")
                            fig = px.line(
                                artist_data, 
                                x='date_collecte', 
                                y='score_potentiel',
                                markers=True,
                                labels={'date_collecte': 'Date', 'score_potentiel': 'Score'}
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
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                            st.caption("L'évolution du score de potentiel dans le temps. Un score en hausse traduit une amélioration globale de la performance (engagement, croissance, popularité).")
                    
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
                                        
                                        artist_name = artist['nom_artiste']
                                        display_name = artist_name[:15] + '...' if len(artist_name) > 15 else artist_name
                                        st.markdown(f"**{display_name}**")
                                        st.caption(f"⭐ {artist['score_potentiel']:.1f}")
                                        
                                        if 'url' in artist and pd.notna(artist['url']) and artist['url']:
                                            if st.button("🎵 Écouter", key=f"listen_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                                st.markdown(f'<a href="{artist["url"]}" target="_blank">Ouvrir</a>', unsafe_allow_html=True)
                                        
                                        if st.button("ℹ️ Infos", key=f"info_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                            st.session_state.selected_artist_evolution = artist['nom_artiste']
                                            st.rerun()
                            else:
                                st.info("Pas assez d'artistes similaires")
                        
                        except Exception as e:
                            similar_artists = candidates.head(5)
                            
                            cols = st.columns(min(5, len(similar_artists)))
                            
                            for idx, (col, (_, artist)) in enumerate(zip(cols, similar_artists.iterrows())):
                                with col:
                                    if 'image_url' in artist and pd.notna(artist['image_url']) and artist['image_url']:
                                        st.markdown(f"""
                                            <div style="width: 100%; 
                                                        aspect-ratio: 1/1;
                                                        overflow: hidden;
                                                        border-radius: 10px;">
                                                <img src="{artist['image_url']}" 
                                                    style="width: 100%; 
                                                            height: 100%; 
                                                            object-fit: cover;">
                                            </div>
                                        """, unsafe_allow_html=True)
                                    
                                    artist_name = artist['nom_artiste']
                                    display_name = artist_name[:15] + '...' if len(artist_name) > 15 else artist_name
                                    st.markdown(f"**{display_name}**")
                                    st.caption(f"⭐ {artist['score_potentiel']:.1f}")
                                    
                                    if 'url' in artist and pd.notna(artist['url']):
                                        if st.button("🎵 Écouter", key=f"listen_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                            st.markdown(f'<a href="{artist["url"]}" target="_blank">Ouvrir</a>', unsafe_allow_html=True)
                                    
                                    if st.button("ℹ️ Infos", key=f"info_{idx}_{artist['nom_artiste']}", use_container_width=True):
                                        st.session_state.selected_artist_evolution = artist['nom_artiste']
                                        st.rerun()
                    else:
                        st.info("Pas assez d'artistes similaires disponibles")
    else:
        st.info("Aucune donnée disponible")

# ==================== TAB 5: ALERTES ====================
with tab5:
    st.markdown("### 🔔 Alertes")
    if len(alertes_df) == 0:
        st.info("✅ Aucune alerte pour le moment")
    else:
        for _, alert in alertes_df.iterrows():
            st.markdown(f"""
                <div class="metric-card">
                    <h4>{alert['type_alerte']}</h4>
                    <p><strong>{alert['nom_artiste']}</strong></p>
                    <p>{alert['message']}</p>
                </div>
            """, unsafe_allow_html=True)

# ==================== TAB 7: À PROPOS ====================
with tab7:
    st.markdown("## 🎵 À PROPOS DE JEK2 RECORDS")
    
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
        🎹 <strong>Musicienne</strong> depuis l'enfance<br>
        📊 <strong>Data Analyst</strong> en reconversion<br>
        💻 <strong>Python, SQL, Machine Learning</strong>
        </p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown(f"""
    <h4 style="color: {COLORS['accent3']}; font-weight: 700;">🎹 MES COMPOSITIONS</h4>
    <p style="color: {COLORS['text']}; font-size: 1.05rem;">
    En parallèle de mon parcours en data, je compose et joue du piano. 
    Découvrez mes créations musicales :
    </p>
    """, unsafe_allow_html=True)
    
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
        st.info(f"📁 Fichier audio non trouvé : {audio_path}")
        st.caption("Ajoutez vos fichiers .m4a dans le dossier assets/")


# ==================== TAB 6: PRÉDICTIONS ====================
with tab6:
    #  SI UN ARTISTE EST SÉLECTIONNÉ, AFFICHER SON ÉVOLUTION
    if 'selected_prediction_artist' in st.session_state and st.session_state.selected_prediction_artist:
        selected_artist = st.session_state.selected_prediction_artist
        
        # Bouton retour
        if st.button("⬅️ Retour aux prédictions", key="back_to_predictions"):
            st.session_state.selected_prediction_artist = None
            st.rerun()
        
        st.markdown(f"## 📈 Évolution de {selected_artist}")
        
        # Afficher l'évolution
        if len(metriques_df) > 0 and 'nom_artiste' in metriques_df.columns:
            artist_data = metriques_df[metriques_df['nom_artiste'] == selected_artist].copy()
            
            if not artist_data.empty:
                artist_data['date_collecte'] = pd.to_datetime(artist_data['date_collecte'])
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
                        chart_data = artist_data[artist_data['followers_chart'] > 0]
                        if len(chart_data) > 0:
                            fig = px.line(
                                chart_data, 
                                x='date_collecte', 
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
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### ⭐ Évolution du Score")
                        fig = px.line(
                            artist_data, 
                            x='date_collecte', 
                            y='score_potentiel',
                            markers=True,
                            labels={'date_collecte': 'Date', 'score_potentiel': 'Score'}
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
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning(f"Aucune donnée trouvée pour {selected_artist}")
        
    else:
        #  AFFICHAGE DES PRÉDICTIONS
        st.markdown("## 🔮 Prédictions")
        
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
                
                #  FONCTION DE NORMALISATION
                def normalize_name(name):
                    """Normalise un nom pour le matching"""
                    if pd.isna(name):
                        return ""
                    return str(name).lower().strip().replace('-', ' ').replace('_', ' ')
                
                #  CRÉER COLONNES NORMALISÉES
                top10_with_images = top10.copy()
                top10_with_images['nom_normalized'] = top10_with_images['nom'].apply(normalize_name)
                
                
                
                # Merge 1: latest_metrics_df
                if 'nom_artiste' in latest_metrics_df.columns and 'image_url' in latest_metrics_df.columns:
                    temp_latest = latest_metrics_df[['nom_artiste', 'image_url']].copy()
                    temp_latest = temp_latest.dropna(subset=['image_url'])
                    temp_latest = temp_latest[temp_latest['image_url'] != '']
                    temp_latest['nom_normalized'] = temp_latest['nom_artiste'].apply(normalize_name)
                    temp_latest = temp_latest.drop_duplicates('nom_normalized', keep='first')
                    
                                        
                    top10_with_images = top10_with_images.merge(
                        temp_latest[['nom_normalized', 'image_url']],
                        on='nom_normalized',
                        how='left'
                    )
                    
                    matched = top10_with_images['image_url'].notna().sum()
                    
                
                # Merge 2: artistes_df (fallback)
                if 'image_url' not in top10_with_images.columns or top10_with_images['image_url'].isna().sum() > 0:
                    if 'nom' in artistes_df.columns and 'image_url' in artistes_df.columns:
                        temp_artistes = artistes_df[['nom', 'image_url']].copy()
                        temp_artistes = temp_artistes.dropna(subset=['image_url'])
                        temp_artistes = temp_artistes[temp_artistes['image_url'] != '']
                        temp_artistes['nom_normalized'] = temp_artistes['nom'].apply(normalize_name)
                        temp_artistes = temp_artistes.drop_duplicates('nom_normalized', keep='first')
                        
                        
                        
                        top10_with_images = top10_with_images.merge(
                            temp_artistes[['nom_normalized', 'image_url']],
                            on='nom_normalized',
                            how='left',
                            suffixes=('', '_artistes')
                        )
                        
                        if 'image_url_artistes' in top10_with_images.columns:
                            if 'image_url' not in top10_with_images.columns:
                                top10_with_images['image_url'] = top10_with_images['image_url_artistes']
                            else:
                                top10_with_images['image_url'] = top10_with_images['image_url'].fillna(top10_with_images['image_url_artistes'])
                            top10_with_images = top10_with_images.drop('image_url_artistes', axis=1)
                        
                        matched = top10_with_images['image_url'].notna().sum()
                        
                

                
                # Grille 5 colonnes
                for row_idx in range(0, len(top10_with_images), 5):
                    cols = st.columns(5)
                    
                    for col_idx, (_, artist) in enumerate(list(top10_with_images.iloc[row_idx:row_idx+5].iterrows())):
                        with cols[col_idx]:
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
                            artist_name = artist['nom']
                            display_name = artist_name[:18] + '...' if len(artist_name) > 18 else artist_name
                            st.markdown(f"<div style='text-align: center;'><strong>{display_name}</strong></div>", unsafe_allow_html=True)
                            st.caption(f"⭐ {artist['proba_star']:.1%}")
                            
                            # Bouton
                            if st.button(
                                " Détails",
                                key=f"pred_detail_{row_idx}_{col_idx}_{artist['nom']}",
                                use_container_width=True
                            ):
                                st.session_state.selected_prediction_artist = artist['nom']
                                st.rerun()
                
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
            
        except FileNotFoundError:
            st.error(" Fichier de prédictions non trouvé")
            st.info(" Lancez : `python ml_prediction.py`")
        except Exception as e:
            st.error(f" Erreur : {e}")
            import traceback
            st.error(traceback.format_exc())

# ==================== TAB 8: MON PROFIL ====================
with tab8:
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
    
    st.markdown("### ⭐ Mes Artistes Intéressés")
    
    if len(st.session_state.artistes_interesses) == 0:
        st.info(" Aucun artiste ajouté pour le moment. Explorez les pages 'Les Top', 'Les Artistes' ou 'Évolution' pour ajouter des artistes à votre sélection !")
    else:
        artistes_data = filtered_df[filtered_df['nom_artiste'].isin(st.session_state.artistes_interesses)]
        
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
            artist_row = filtered_df[filtered_df['nom_artiste'] == artiste_nom]
            
            if len(artist_row) > 0:
                artist = artist_row.iloc[0]
                
                col_check, col_img, col_info, col_actions = st.columns([0.5, 1, 3, 1.5])
                
                with col_check:
                    st.write("")
                    st.write("")
                    st.markdown("✅")
                
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
                    if st.button("Détails", key=f"profil_voir_{idx}", use_container_width=True):
                        st.session_state.selected_artist_evolution = artiste_nom
                        st.session_state.redirect_to_evolution = True
                        st.rerun()
                    
                    if st.button("🗑️ Retirer", key=f"profil_del_{idx}", use_container_width=True):
                        st.session_state.artistes_interesses.remove(artiste_nom)
                        st.rerun()
                
                st.markdown("---")
            else:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"🎵 **{artiste_nom}**")
                    st.caption("(Non visible avec les filtres actuels)")
                with col2:
                    if st.button("🗑️ Retirer", key=f"profil_del_missing_{idx}", use_container_width=True):
                        st.session_state.artistes_interesses.remove(artiste_nom)
                        st.rerun()
                st.markdown("---")

# Footer
st.divider()
st.caption("JEK2 Records - MusicTalentRadar | La data au rythme du son | On capte les talents avant qu'ils n'explosent!")