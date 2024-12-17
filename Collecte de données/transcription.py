import os
import pandas as pd
import requests
import re
import time
import hashlib
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from youtube_transcript_api import YouTubeTranscriptApi
from pydub import AudioSegment
import whisper
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Configuration des en-têtes User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def convertir_duree_en_secondes(duree):
    """Convertit une durée ISO 8601 en secondes."""
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duree)
    heures = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    secondes = int(match.group(3)[:-1]) if match.group(3) else 0
    return heures * 3600 + minutes * 60 + secondes

def seconds_to_hh_mm_ss(seconds):
    """Convertit des secondes en format HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def verifier_presence(url, sous_chaine1, sous_chaine2):

    if sous_chaine1 in url:

        # Extraire l'ID de la vidéo
        video_id = url.split('youtu.be/')[1].split('?')[0]

        if '?t=' in url :
            param_t = url.split('?t=')[1]
            complete_id =video_id+"&t="+param_t
            
        else :
            complete_id = video_id
        
    elif sous_chaine2 in url :
        complete_id = url.replace('https://www.youtube.com/watch?v=', '') 

    return(complete_id)

def generer_hash(*args):
    """Génère un hash unique."""
    args = [str(arg) if pd.notna(arg) else '' for arg in args]
    hash_object = hashlib.sha256()
    hash_object.update(' '.join(args).encode('utf-8'))
    return hash_object.hexdigest()

def obtenir_duree_audio(fichier_audio):
    """Obtient la durée d'un fichier audio en secondes."""
    try:
        audio = AudioSegment.from_file(fichier_audio)
        return len(audio) / 1000
    except Exception as e:
        print(f"Erreur lors du calcul de la durée : {e}")
        return None

def transcrire_whisper(fichier_audio, model):
    """Transcrit un fichier audio avec Whisper."""
    try:
        result = model.transcribe(fichier_audio)
        return result["text"]
    except Exception as e:
        print(f"Erreur de transcription pour {fichier_audio}: {e}")
        return None

# Étape 1 : Téléchargement et transcription
def process_audio_and_transcriptions(input_csv, transcription_json, api_key):
    model = whisper.load_model("base")
    df = pd.read_csv(input_csv)
    json_data = []
    # Dictionnaire pour le cache des transcriptions
    transcription_cache = {}
    sous_chaine_Youtube_1 = "youtu.be"
    sous_chaine_Youtube_2 = "youtube"

    results = df[df['hash_id'].isna() | (df['hash_id'] == '')]

    for index, row in results.iterrows():

        if 'youtu' in row['links']:
            video_id = verifier_presence(row['links'], sous_chaine_Youtube_1, sous_chaine_Youtube_2)

            try:
                # Essayer d'obtenir la transcription de la vidéo
                transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])

                # Construire la transcription en un seul texte
                output = ' '.join([x['text'] for x in transcript])

                # Générer un identifiant de hashage basé sur les informations de la ligne
                hash_id = generer_hash(row['id'], row['title'], row['subtitle'], row['links'])
                df.at[index, 'hash_id'] = hash_id
                transcription_page_web = ""
                transcription_podcast = ""
                

                # Créer une entrée JSON pour cette ligne
                json_entry = {
                    "id": hash_id,
                    "transcription_page_web": transcription_page_web,
                    "transcription_video": output.strip(),
                    "transcription_podcast": transcription_podcast
                }
                json_data.append(json_entry)

                # Délai de 2 secondes entre les requêtes
                time.sleep(6)

            except Exception as e:
                # En cas d'erreur (ex. transcription non disponible), ignorer la vidéo
                pass

        elif isinstance(row['links'], str) and 'btctouchpoint' in row['links'] and \
            isinstance(row['download_link'], str) and 'download=true' in row['download_link']:


            url = row['download_link'].strip()  # Supprimer les espaces superflus
            
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
                transcription_page_web = ""
                transcription_video = ""

                # Créer une entrée JSON pour cette ligne
                json_entry = {
                    "id": hash_id,
                    "transcription_page_web": transcription_page_web,
                    "transcription_video": transcription_video,
                    "transcription_podcast": transcription.strip() if transcription else ""
                }
                json_data.append(json_entry)
                
            if not os.path.isfile(expected_file_name):
                print(f"Fichier manquant : {expected_file_name}. Téléchargement nécessaire ou fichier incorrect.")
                continue

    colonnes = ['iframe_url', 'download_link']  # Remplacez par les noms des colonnes à supprimer
    input_csv = input_csv.drop(columns=colonnes)



    with open(transcription_json, "w", encoding='utf-8') as json_file:
        json.dump(json_data, json_file, ensure_ascii=False, indent=4)

    df.to_csv("processed_data.csv", index=False)

# Exécution
api_key = ""
output_csv = "link_download.csv"
transcription_json = "transcriptions.json"

process_audio_and_transcriptions(output_csv, transcription_json, api_key)
