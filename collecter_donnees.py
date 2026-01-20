import requests
import pandas as pd
from datetime import datetime
import os

# Configuration Spotify
SPOTIFY_CLIENT_ID = '521adaf36b6948bb82d6c6f398f9004e'
SPOTIFY_CLIENT_SECRET = '11fcdc06df214181bfa8e8580c86126d'

def get_spotify_token():
    """Obtenir token d'authentification Spotify"""
    auth_url = 'https://accounts.spotify.com/api/token'
    auth_response = requests.post(auth_url, {
        'grant_type': 'client_credentials',
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    })
    return auth_response.json()['access_token']

def collecter_spotify(artist_ids):
    """Collecter données depuis Spotify API"""
    token = get_spotify_token()
    headers = {'Authorization': f'Bearer {token}'}
    
    artists_data = []
    for artist_id in artist_ids:
        response = requests.get(
            f'https://api.spotify.com/v1/artists/{artist_id}',
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            artists_data.append({
                'nom': data['name'],
                'followers': data['followers']['total'],
                'popularity': data['popularity'],
                'genre': ', '.join(data['genres'][:3]),
                'image_url': data['images'][0]['url'] if data['images'] else '',
                'url_spotify': data['external_urls']['spotify'],
                'date_collecte': datetime.now().strftime('%Y-%m-%d')
            })
    
    return pd.DataFrame(artists_data)

def collecter_deezer(artist_ids):
    """Collecter données depuis Deezer API"""
    artists_data = []
    for artist_id in artist_ids:
        response = requests.get(f'https://api.deezer.com/artist/{artist_id}')
        if response.status_code == 200:
            data = response.json()
            artists_data.append({
                'nom': data['name'],
                'fans': data['nb_fan'],
                'genre': 'Pop',  # Deezer ne fournit pas toujours le genre
                'image_url': data['picture_medium'],
                'url_deezer': data['link'],
                'date_collecte': datetime.now().strftime('%Y-%m-%d')
            })
    
    return pd.DataFrame(artists_data)

if __name__ == "__main__":
    print(" Collecte des données en cours...")
    
    # Liste des IDs artistes à suivre (à définir)
    spotify_ids = ['id1', 'id2', 'id3']  # Tes artistes Spotify
    deezer_ids = ['id1', 'id2', 'id3']   # Tes artistes Deezer
    
    # Collecter
    spotify_df = collecter_spotify(spotify_ids)
    deezer_df = collecter_deezer(deezer_ids)
    
    # Sauvegarder
    date_str = datetime.now().strftime('%Y%m%d')
    spotify_df.to_csv(f'data/spotify_artists_{date_str}.csv', index=False)
    deezer_df.to_csv(f'data/deezer_artists_{date_str}.csv', index=False)
    
    print(" Collecte terminée !")