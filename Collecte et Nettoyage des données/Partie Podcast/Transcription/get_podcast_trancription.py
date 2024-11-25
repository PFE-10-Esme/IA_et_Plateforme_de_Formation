import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\ffmpeg"
import whisper
import hashlib
import json
import time
import re
from pydub import AudioSegment

# Fonction pour générer un hash MD5 ou SHA256
def generer_hash(*args):
    args = [str(arg) if pd.notna(arg) else '' for arg in args]
    hash_object = hashlib.sha256()
    hash_object.update(' '.join(args).encode('utf-8'))
    return hash_object.hexdigest()

def transcrire_whisper(fichier_audio, model):
    # Charger le modèle Whisper et transcrire le fichier audio
    try:
        result = model.transcribe(fichier_audio)
        return(result["text"])
    except Exception as e:
        print(f"Erreur de transcription pour {fichier_audio}: {e}")
        return None

# Fonction pour convertir les secondes en format HH:MM:SS
def seconds_to_hh_mm_ss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

# Fonction pour récupérer la durée de l'audio en secondes
def obtenir_duree_audio(fichier_audio):
    try:
        audio = AudioSegment.from_file(fichier_audio)
        return len(audio) / 1000  # Durée en secondes
    except Exception as e:
        print(f"Erreur lors du calcul de la durée : {e}")
        return None

# Charger le fichier CSV
df = pd.read_csv("transcription_podcast_2.csv")

# Ajouter une colonne pour stocker les durées
#df['duree'] = None
# Ajouter une colonne vide 'hash_id' pour toutes les lignes
#df['hash_id'] = ''

# Charger les données JSON existantes
try:
    with open("transcription.json", "r", encoding='utf-8') as json_file:
        existing_data = json.load(json_file)
except FileNotFoundError:
    print("Le fichier transcription.json n'existe pas. Un nouveau fichier sera créé.")
    existing_data = []

# Convertir les données JSON existantes en un dictionnaire pour une recherche rapide
existing_hash_ids = {entry['id'] for entry in existing_data}
json_data = list(existing_data)  # Start with existing data if any

# Dictionnaire pour le cache des transcriptions
transcription_cache = {}

model = whisper.load_model("base")

# Filtrer uniquement les lignes non vides dans la colonne 'download_link'
results = df[(df['download_link'].notna()) & (df['hash_id'].isna())]

# Parcourir chaque ligne des résultats filtrés
for index, row in results.iterrows():
    download_links = row['download_link']  # Récupérer les liens dans la cellule
    
    # Diviser les liens s'ils sont séparés par des virgules
    link_list = download_links.split(',')
    
    for url in link_list:

        if 'download=true' in url:
            url = url.strip()  # Supprimer les espaces superflus
            
            # Obtenir le nom de fichier attendu à partir de l'URL
            expected_file_name = url.split("/")[-1].split("?")[0]
            
            # Vérifier si le fichier correspond au nom attendu
            if os.path.isfile(expected_file_name):
                print(f"Fichier trouvé : {expected_file_name}")
                
                # Vérifier si le fichier est déjà dans le cache
                if expected_file_name in transcription_cache:
                    print(f"Utilisation de la transcription en cache pour {expected_file_name}.")
                    transcription = transcription_cache[expected_file_name]
                else:
                    print(f"Transcription en cours pour {expected_file_name}...")
                    transcription = transcrire_whisper(expected_file_name, model)
                    transcription_cache[expected_file_name] = transcription  # Ajouter au cache
                
                duree_audio = obtenir_duree_audio(expected_file_name)
                duree_audio = seconds_to_hh_mm_ss(duree_audio)
                df.at[index, 'duree'] = duree_audio

                # Générer un identifiant de hashage basé sur les informations de la ligne
                hash_id = generer_hash(row['id'], row['title'], row['subtitle'], row['links'])
                df.at[index, 'hash_id'] = hash_id

                # Vérifier si la transcription existe déjà
                if hash_id in existing_hash_ids:
                    print(f"Transcription pour {hash_id} déjà présente, passage à la suivante.")
                    continue

                # Créer une entrée JSON pour cette ligne
                json_entry = {
                    "id": hash_id,
                    "transcription": transcription.strip() if transcription else ""
                }
                json_data.append(json_entry)

                # Marquer cette ligne comme traitée
                transcribed = True  # Empêche le traitement d'autres URLs de cette ligne
            
            if transcribed == True:
                break

# Sauvegarder les données dans un fichier JSON
with open("transcription.json", "w", encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("Les transcriptions ont été sauvegardées dans transcription.json.")

# Sauvegarder le DataFrame complet (avec toutes les données) dans un nouveau fichier CSV
df.to_csv("transcription_podcast_3.csv", index=False)
print("Le fichier CSV complet avec les nouvelles colonnes de hashage a été sauvegardé.")
