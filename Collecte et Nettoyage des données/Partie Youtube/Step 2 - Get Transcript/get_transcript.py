import pandas as pd
import hashlib
import json
import time
from youtube_transcript_api import YouTubeTranscriptApi

# Fonction pour générer un hash MD5 ou SHA256
def generer_hash(*args):
    args = [str(arg) if pd.notna(arg) else '' for arg in args]
    hash_object = hashlib.sha256()
    hash_object.update(' '.join(args).encode('utf-8'))
    return hash_object.hexdigest()

# Charger le fichier CSV avec gestion des erreurs
try:
    df = pd.read_csv('output.csv', on_bad_lines='skip', quoting=1, encoding='utf-8')
except Exception as e:
    print(f"Erreur lors de la lecture du CSV: {e}")

# Ajouter une colonne vide 'hash_id' pour toutes les lignes
#df['hash_id'] = ''

sous_chaine_Youtube_1 = "youtu.be"
sous_chaine_Youtube_2 = "youtube"

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
    

# Créer une liste pour stocker les données JSON
json_data = []

# Filtrer uniquement les lignes avec des liens YouTube
YoutubeLink = 'youtu'
results = df[df['links'].str.contains(YoutubeLink, na=False)]

# Parcourir chaque URL YouTube dans les résultats filtrés
for index, row in results.iterrows():

    url_Youtube = row['links']

    video_id = verifier_presence(url_Youtube, sous_chaine_Youtube_1, sous_chaine_Youtube_2)
    
    try:
        # Essayer d'obtenir la transcription de la vidéo
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['fr', 'en'])

        # Construire la transcription en un seul texte
        output = ' '.join([x['text'] for x in transcript])

        # Générer un identifiant de hashage basé sur les informations de la ligne
        hash_id = generer_hash(row['id'], row['title'], row['subtitle'], row['links'])
        df.at[index, 'hash_id'] = hash_id

        # Créer une entrée JSON pour cette ligne
        json_entry = {
            "id": hash_id,
            "transcription": output.strip()
        }
        json_data.append(json_entry)

        # Délai de 2 secondes entre les requêtes
        time.sleep(6)

    except Exception as e:
        # En cas d'erreur (ex. transcription non disponible), ignorer la vidéo
        pass

# Sauvegarder les données dans un fichier JSON
with open("transcriptions_finales.json", "w", encoding='utf-8') as json_file:
    json.dump(json_data, json_file, ensure_ascii=False, indent=4)

print("Les transcriptions ont été sauvegardées dans transcriptions_finale.json.")

# Sauvegarder le DataFrame complet (avec toutes les données) dans un nouveau fichier CSV
df.to_csv("csv_final.csv", index=False)

print("Le fichier CSV complet avec les nouvelles colonnes de hashage a été sauvegardé.")
