#!/usr/bin/env python3
"""
Script pour corriger music_talent_radar.py
Commente automatiquement les DELETE FROM metriques_historique
"""

import shutil
from datetime import datetime

print("🔧 CORRECTION AUTOMATIQUE de music_talent_radar.py")
print("=" * 70)

# 1. Faire une sauvegarde
backup_name = f'music_talent_radar_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.py'
shutil.copy('music_talent_radar.py', backup_name)
print(f"✅ Sauvegarde créée : {backup_name}")

# 2. Lire le fichier
with open('music_talent_radar.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 3. Corriger les lignes avec DELETE
corrections = 0
new_lines = []

for i, line in enumerate(lines, 1):
    # Si la ligne contient DELETE FROM metriques_historique ET n'est pas déjà commentée
    if 'DELETE FROM metriques_historique' in line and not line.strip().startswith('#'):
        print(f"\n📍 Ligne {i} trouvée :")
        print(f"   AVANT : {line.rstrip()}")
        
        # Commenter la ligne
        indent = len(line) - len(line.lstrip())
        commented_line = ' ' * indent + '# ' + line.lstrip()
        new_lines.append(commented_line)
        
        print(f"   APRÈS : {commented_line.rstrip()}")
        corrections += 1
    else:
        new_lines.append(line)

# 4. Écrire le fichier corrigé
if corrections > 0:
    with open('music_talent_radar.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("\n" + "=" * 70)
    print(f"✅ {corrections} ligne(s) corrigée(s) !")
    print("=" * 70)
    print("""
PROCHAINES ÉTAPES :

1. Lance une nouvelle collecte :
   python music_talent_radar.py --all

2. Vérifie que tu as maintenant 2 dates :
   python verifier_collecte.py

3. Génère les alertes :
   python generer_alertes.py

4. Vérifie dans Streamlit :
   streamlit run app/streamlit.py
""")
else:
    print("\n⚠️  Aucune ligne DELETE non-commentée trouvée")
    print("   Le fichier était peut-être déjà corrigé ?")

print(f"\n💾 Sauvegarde disponible dans : {backup_name}")
