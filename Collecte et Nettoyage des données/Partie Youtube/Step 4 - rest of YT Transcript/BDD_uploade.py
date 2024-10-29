import pandas as pd
import hashlib
import json
from youtube_transcript_api import YouTubeTranscriptApi

# Fonction pour générer un hash MD5 ou SHA256
def generer_hash(*args):
    args = [str(arg) if pd.notna(arg) else '' for arg in args]
    hash_object = hashlib.sha256()
    hash_object.update(' '.join(args).encode('utf-8'))
    return hash_object.hexdigest()

# Charger le fichier CSV avec gestion des erreurs
try:
    df = pd.read_csv('csv_final.csv', on_bad_lines='skip', quoting=1, encoding='utf-8')
except Exception as e:
    print(f"Erreur lors de la lecture du CSV: {e}")

# Filtrer uniquement les lignes avec des liens YouTube et un hash_id vide
sous_chaine_Youtube = 'youtu'
results = df[(df['links'].str.contains(sous_chaine_Youtube, na=False)) & (df['hash_id'].isna())]

# Charger l'ancien fichier JSON s'il existe, sinon créer une liste vide
json_filename = "output.json"
with open(json_filename, "r", encoding='utf-8') as json_file:
        json_data = json.load(json_file)


# Parcourir chaque URL YouTube dans les résultats filtrés
for index, row in results.iterrows():
    url_Youtube = row['links']
    
    video_id = url_Youtube.replace('https://www.youtube.com/watch?v=', '')
    
    try:
        # Essayer d'obtenir la transcription de la vidéo
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])

        # Construire la transcription en un seul texte
        output = ' '.join([x['text'] for x in transcript])

        # Générer un identifiant de hashage basé sur les informations de la ligne
        hash_id = generer_hash(row['id'], row['title'], row['links'], row['titre'], row['auteur'], str(row['duree_hh_mm_ss']))
        df.at[index, 'hash_id'] = hash_id  # Mise à jour du DataFrame avec le nouveau hash_id

        # Créer une entrée JSON pour cette ligne
        json_entry = {
            "id": hash_id,
            "transcription": output.strip()
        }
        json_data.append(json_entry)


    except Exception as e:
        # En cas d'erreur (ex. transcription non disponible), ignorer la vidéo
        pass

# Sauvegarder les données complètes (anciennes + nouvelles) dans le même fichier JSON
with open(json_filename, "w", encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

# Sauvegarder le DataFrame complet (avec toutes les données) dans un nouveau fichier CSV
df.to_csv("output.csv", index=False)

print("Le fichier CSV complet avec les nouvelles colonnes de hashage a été sauvegardé.")
