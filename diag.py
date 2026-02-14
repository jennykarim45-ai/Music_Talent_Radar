import requests

artist_id = "13"  # Eminem

# 1. Récupérer les albums de l'artiste
albums_url = f"https://api.deezer.com/artist/{artist_id}/albums"
albums_response = requests.get(albums_url)
albums_data = albums_response.json()

print("📀 ALBUMS:")
print(f"Nombre d'albums: {len(albums_data.get('data', []))}")

if albums_data.get('data'):
    # Prendre le premier album
    first_album_id = albums_data['data'][0]['id']
    print(f"\n🎵 Premier album ID: {first_album_id}")
    
    # 2. Récupérer les détails de l'album
    album_url = f"https://api.deezer.com/album/{first_album_id}"
    album_response = requests.get(album_url)
    album_data = album_response.json()
    
    print("\n📊 DÉTAILS ALBUM:")
    print(f"Titre: {album_data.get('title')}")
    print(f"Champs disponibles: {album_data.keys()}")
    
    # 3. Chercher les genres
    if 'genres' in album_data:
        genres = album_data['genres'].get('data', [])
        print(f"\n✅ GENRES TROUVÉS:")
        for genre in genres:
            print(f"  - {genre.get('name')} (ID: {genre.get('id')})")
    else:
        print("\n❌ Pas de genres dans l'album")