from pathlib import Path

# Chemin vers ton logo depuis le script app/
logo_path = Path(__file__).parent.parent / "asset" / "logo.png"
print(logo_path)          # Affiche le chemin complet
print(logo_path.exists()) # True si le fichier existe
