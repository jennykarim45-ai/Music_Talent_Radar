import streamlit as st
import os
import base64

def get_base64_image(image_path):
    """Convertit une image en base64"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

def public_page_about():
    """Page d'accueil publique avant connexion"""
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Charger l'image de fond
    background_path = os.path.join(BASE_DIR, "assets", "back.png")
    bg_image = get_base64_image(background_path)
    
    if bg_image:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(7, 7, 7, 0.85);
                z-index: 0;
            }}
            
            .main > div {{
                position: relative;
                z-index: 1;
            }}
            </style>
        """, unsafe_allow_html=True)
    
    # Logo en haut à gauche SEUL
    logo_path = os.path.join(BASE_DIR, "assets", "logo.png")
    
    col_logo, col_description,col3 = st.columns([1, 4, 1])
    with col_logo:
        if os.path.exists(logo_path):
            st.image(logo_path, width=300)
    
    # Titres CENTRÉS : JEK2 AU-DESSUS de MUSIC TALENT RADAR
    with col_description:
        st.markdown("""
            <div style="text-align: center; margin: 1rem 0 1.5rem 0;">
                <h1 style="
                    background: linear-gradient(90deg, 
                        #ff0000 0%, 
                        #ff7f00 16.67%, 
                        #ffff00 33.33%, 
                        #00ff00 50%, 
                        #0000ff 66.67%, 
                        #4b0082 83.33%, 
                        #9400d3 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-size: 3rem; 
                    font-weight: 900; 
                    margin: 0 0 0.5rem 0;
                    text-transform: uppercase;
                    letter-spacing: 5px;
                    line-height: 1;
                ">JEK2 RECORDS</h1>
                <h2 style="
                    background: linear-gradient(90deg, 
                        #ff0000 0%, 
                        #ff7f00 16.67%, 
                        #ffff00 33.33%, 
                        #00ff00 50%, 
                        #0000ff 66.67%, 
                        #4b0082 83.33%, 
                        #9400d3 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                    font-size: 3rem; 
                    font-weight: 900; 
                    margin: 0;
                    text-transform: uppercase;
                    letter-spacing: 5px;
                    line-height: 1;
                ">MUSIC TALENT RADAR</h2>
            </div>
        """, unsafe_allow_html=True)
    
    # NOTRE MISSION ET NOTRE APPROCHE CÔTE À CÔTE (2 colonnes)
    col_mission,col2, col_approche = st.columns([1, 0.7, 1])
    
    with col_mission:
        st.markdown("""
            <div style="color: #21B178; font-size: 1.5rem; font-weight: 700; margin: 1rem 0 1rem 0;">
                Notre Mission
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="color: #B18E57; font-size: 1.05rem; line-height: 1.8;">
                Découvrir les talents émergents français qui pourraient devenir les prochains leaders de la scène urbaine selon les genres musicaux suivant :
                <ul style="margin-top: 1rem;">
                    <li> Identifier l'analyse de données pour détecter les artistes à fort potentiel</li>
                    <li> Rendre les artistes plus visible grâce aux recommandations</li>
                    <li> Anticiper les tendances musivales avec le Machine Learning</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    with col_approche:
        st.markdown("""
            <div style="color: #21B178; font-size: 1.5rem; font-weight: 700; margin: 1rem 0 1rem 0;">
                Notre Approche
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
            <div style="color: #B18E57; font-size: 1.05rem; line-height: 1.8;">
                Collecte de données depuis les plateformes de streaming :
                <ul style="margin-top: 1rem;">
                    <li><strong>🟢 Spotify</strong></li>
                    <li><strong>🔵 Deezer</strong></li>
                </ul>
                Création d'un dashboard interactif pour visualiser :
                <ul style="margin-top: 1rem;">
                    <li><strong> Les Tops </strong></li>
                    <li><strong> Evolution des artistes</strong></li>
                    <li><strong> Prédiction des stars de demain</strong></li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
    
    # Section Le Score de Potentiel (en pleine largeur)
    st.markdown("""
        <div style="color: #21B178; font-size: 1.5rem; font-weight: 700; margin: 2rem 0 1rem 0;">
            Le Score de Potentiel
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="color: #B18E57; font-size: 1.05rem; line-height: 1.8; margin-bottom: 1rem;">
            Notre algorithme attribue un score sur <strong>100</strong> pour évaluer le potentiel de chaque artiste en fonction de ces critères :
        </div>
    """, unsafe_allow_html=True)
    
    # Tableau TRÈS COLORÉ
    st.markdown("""
        <p style='margin-top: 15px; color: #B18E57; font-style: italic;'>
        Note : Le score varie de 0 à 100 selon la position de l'artiste dans la fourchette cible.
        </p>        
        <table style="width: 100%; border-collapse: collapse; background: rgba(30, 41, 59, 0.95); border-radius: 15px; overflow: hidden; margin: 1rem 0; box-shadow: 0 8px 20px rgba(0,0,0,0.3);">
            <thead>
                <tr style="background: linear-gradient(135deg, #dc2626 0%, #9333ea 50%, #2563eb 100%);">
                    <th style="color: white; padding: 1.2rem; text-align: left; font-weight: 900; font-size: 1.1rem;">Critère</th>
                    <th style="color: white; padding: 1.2rem; text-align: left; font-weight: 900; font-size: 1.1rem;">Poids</th>
                    <th style="color: white; padding: 1.2rem; text-align: left; font-weight: 900; font-size: 1.1rem;">Description</th>
                </tr>
            </thead>
            <tbody>
                <tr style="background: linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(239, 68, 68, 0.05)); border-bottom: 2px solid rgba(239, 68, 68, 0.3);">
                    <td style="color: #fca5a5; padding: 1rem; font-weight: 700; font-size: 1.05rem;"> Audience</td>
                    <td style="color: #fca5a5; padding: 1rem; font-weight: 700; font-size: 1.05rem;">35%</td>
                    <td style="color: #e5e7eb; padding: 1rem;">Taille de la communauté (100 - 40 000 followers/fans)</td>
                </tr>
                <tr style="background: linear-gradient(135deg, rgba(251, 146, 60, 0.15), rgba(251, 146, 60, 0.05)); border-bottom: 2px solid rgba(251, 146, 60, 0.3);">
                    <td style="color: #fdba74; padding: 1rem; font-weight: 700; font-size: 1.05rem;"> Engagement</td>
                    <td style="color: #fdba74; padding: 1rem; font-weight: 700; font-size: 1.05rem;">30%</td>
                    <td style="color: #e5e7eb; padding: 1rem;">Interactions avec les fans</td>
                </tr>
                <tr style="background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(34, 197, 94, 0.05)); border-bottom: 2px solid rgba(34, 197, 94, 0.3);">
                    <td style="color: #86efac; padding: 1rem; font-weight: 700; font-size: 1.05rem;"> Récurrance</td>
                    <td style="color: #86efac; padding: 1rem; font-weight: 700; font-size: 1.05rem;">25%</td>
                    <td style="color: #e5e7eb; padding: 1rem;">Régularité des sorties</td>
                </tr>
                <tr style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.05));">
                    <td style="color: #93c5fd; padding: 1rem; font-weight: 700; font-size: 1.05rem;"> Influence</td>
                    <td style="color: #93c5fd; padding: 1rem; font-weight: 700; font-size: 1.05rem;">10%</td>
                    <td style="color: #e5e7eb; padding: 1rem;">Présence multi-plateforme</td>
                </tr>
            </tbody>
        </table>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div style="color: #B18E57; font-size: 1.05rem; line-height: 1.8; margin-top: 1.5rem;">
            Ce score élevé implique un fort potentiel de croissance et des meilleures chances de devenir une future star !
        </div>
    """, unsafe_allow_html=True)
    
    # Bouton de connexion ROUGE
    st.markdown("""
        <style>
        .stButton > button {
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
            color: white !important;
            font-weight: 700 !important;
            font-size: 1.2rem !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 0.75rem 2rem !important;
            transition: all 0.3s ease !important;
        }
        .stButton > button:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(220, 38, 38, 0.5) !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='margin: 3rem 0 2rem 0;'></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("CONNEXION", key="btn_connexion", use_container_width=True):
            st.session_state.show_login = True
            st.rerun()

def login_form():
    """Formulaire de connexion"""
    
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    
    # Fond
    background_path = os.path.join(BASE_DIR, "assets", "back.png")
    bg_image = get_base64_image(background_path)
    
    if bg_image:
        st.markdown(f"""
            <style>
            .stApp {{
                background-image: url("data:image/png;base64,{bg_image}");
                background-size: cover;
                background-position: center;
                background-repeat: no-repeat;
                background-attachment: fixed;
            }}
            
            .stApp::before {{
                content: "";
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(7, 7, 7, 0.85);
                z-index: 0;
            }}
            
            /* Labels en GRAS et BLANCS */
            label {{
                color: white !important;
                font-weight: 700 !important;
                font-size: 1.1rem !important;
            }}
            
            /* Inputs avec bordure ROUGE */
            .stTextInput > div > div > input {{
                border: 2px solid #dc2626 !important;
                border-radius: 8px !important;
                background: rgba(255, 255, 255, 0.95) !important;
                color: black !important;
                font-size: 1rem !important;
                padding: 0.75rem !important;
            }}
            
            .stTextInput > div > div > input:focus {{
                border-color: #991b1b !important;
                box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.2) !important;
            }}
            
            /* TOUS les Boutons ROUGES */
            .stButton > button {{
                background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
                color: white !important;
                font-weight: 700 !important;
                border: none !important;
                border-radius: 10px !important;
                padding: 0.75rem 2rem !important;
            }}
            
            .stButton > button:hover {{
                transform: translateY(-2px) !important;
                box-shadow: 0 8px 20px rgba(220, 38, 38, 0.5) !important;
            }}
            
            /* Bouton submit du form ROUGE aussi */
            .stForm button[type="submit"] {{
                background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
                color: white !important;
                font-weight: 700 !important;
                border: none !important;
            }}
            </style>
        """, unsafe_allow_html=True)
    
    # Titre arc-en-ciel
    st.markdown("""
        <div style="text-align: center; margin: 3rem 0 2rem 0;">
            <h1 style="
                background: linear-gradient(90deg, 
                    #ff0000 0%, 
                    #ff7f00 16.67%, 
                    #ffff00 33.33%, 
                    #00ff00 50%, 
                    #0000ff 66.67%, 
                    #4b0082 83.33%, 
                    #9400d3 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                font-size: 2.5rem; 
                font-weight: 900;
                text-transform: uppercase;
            ">CONNEXION</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("login_form"):
            username = st.text_input("👤 Nom d'utilisateur")
            password = st.text_input("🔒 Mot de passe", type="password")
            submit = st.form_submit_button("Se connecter", use_container_width=True)
            
            if submit:
                if username == "admin" and password == "admin123":
                    st.session_state.logged_in = True
                    st.session_state.username = username
                    st.session_state.show_login = False
                    st.success(" Connexion réussie !")
                    st.rerun()
                else:
                    st.error(" Identifiants incorrects")
        
        if st.button("← Retour", key="back_to_about"):
            st.session_state.show_login = False
            st.rerun()

def require_authentication():
    """Vérifie si l'utilisateur est connecté"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if 'show_login' not in st.session_state:
        st.session_state.show_login = False
    
    return st.session_state.logged_in