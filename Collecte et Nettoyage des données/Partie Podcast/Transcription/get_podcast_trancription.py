import pandas as pd
import os
os.environ["PATH"] += os.pathsep + r"C:\Program Files\ffmpeg"
import whisper
import hashlib
import json
import time

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
        pass

# Charger le fichier CSV
df = pd.read_csv("link_download.csv")
df = df.head(31)

# Ajouter une colonne vide 'hash_id' pour toutes les lignes
df['hash_id'] = ''

# Créer une liste pour stocker les données JSON
json_data = []

model = whisper.load_model("base")

# Filtrer uniquement les lignes non vides dans la colonne 'download_link'
results = df[df['download_link'].notna()]

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
                print(f"Fichier trouvé : {expected_file_name}. Lancement de la transcription...")
                #print(f"Ligne trouvée : {index}")  # Afficher l'index de la ligne
                transcription = transcrire_whisper(expected_file_name,model)
            output = ' '.join([transcription])

            # Générer un identifiant de hashage basé sur les informations de la ligne
            hash_id = generer_hash(row['id'], row['title'], row['subtitle'], row['links'])
            df.at[index, 'hash_id'] = hash_id

            # Créer une entrée JSON pour cette ligne
            json_entry = {
                "id": hash_id,
                "transcription": output.strip()
            }
            json_data.append(json_entry)

# Sauvegarder les données dans un fichier JSON
with open("transcription_podcast.json", "w", encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("Les transcriptions ont été sauvegardées dans transcription_podcast.json.")

# Sauvegarder le DataFrame complet (avec toutes les données) dans un nouveau fichier CSV
df.to_csv("transcription_podcast.csv", index=False)

print("Le fichier CSV complet avec les nouvelles colonnes de hashage a été sauvegardé.")