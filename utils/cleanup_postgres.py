import streamlit as st
import psycopg2

st.title("🧹 Nettoyage de la base PostgreSQL")

if st.button("🗑️ SUPPRIMER LES DOUBLONS"):
    try:
        DB_URL = st.secrets["DATABASE_URL"]
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        # Compter avant
        cursor.execute("""
            SELECT COUNT(*) FROM (
                SELECT 1
                FROM metriques_historique
                GROUP BY DATE(date_collecte), id_unique
                HAVING COUNT(*) > 1
            ) AS doublons
        """)
        nb_avant = cursor.fetchone()[0]
        st.info(f"📊 {nb_avant} artistes avec doublons détectés")
        
        # Supprimer
        cursor.execute("""
            DELETE FROM metriques_historique
            WHERE id NOT IN (
                SELECT MAX(id)
                FROM metriques_historique
                GROUP BY DATE(date_collecte), id_unique
            )
        """)
        
        nb_supprimes = cursor.rowcount
        conn.commit()
        conn.close()
        
        st.success(f"✅ {nb_supprimes} doublons supprimés !")
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Erreur : {e}")