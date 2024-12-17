import pandas as pd

df = pd.read_csv("db_btc-touchpoint - db.csv",index_col=False)
#df=df.drop(["time_min","AUTEUR (TODO)","TYPE (vidéo, podcast, article ou combinés de plusieurs)"], axis=1) # Supprimer les colonnes non-necessaires

import requests
import pandas as pd
import re
import time

# Fonction pour extraire l'ID de la vidéo YouTube à partir de l'URL
def extraire_id_youtube(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_match = re.match(youtube_regex, url)
    return youtube_match.group(6) if youtube_match else None

# Fonction pour obtenir les informations de la vidéo à partir de l'API YouTube
def obtenir_infos_youtube(video_id, api_key):
    url = f'https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=snippet,contentDetails&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        video_info = data['items'][0]
        titre = video_info['snippet']['title']
        auteur = video_info['snippet']['channelTitle']
        duree = video_info['contentDetails']['duration']
        return titre, auteur, duree
    return None, None, None

# Fonction pour convertir la durée ISO 8601 en secondes
def convertir_duree_en_secondes(duree):
    match = re.match(r'PT(\d+H)?(\d+M)?(\d+S)?', duree)
    heures = int(match.group(1)[:-1]) if match.group(1) else 0
    minutes = int(match.group(2)[:-1]) if match.group(2) else 0
    secondes = int(match.group(3)[:-1]) if match.group(3) else 0

    # Calculer le total en secondes
    total_secondes = heures * 3600 + minutes * 60 + secondes
    return total_secondes

# Fonction pour convertir les secondes en format HH:MM:SS
def seconds_to_hh_mm_ss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# Ajouter les nouvelles colonnes pour les résultats
#df['titre'] = ''
#df['auteur'] = ''
#df['duree'] = None  # Initialiser à None
#df['type'] = ''  # Nouvelle colonne pour le type

# Filtrer uniquement les lignes avec des liens YouTube
sous_chaine_Youtube = 'youtu'
results = df[(df['links'].str.contains(sous_chaine_Youtube, na=False))]

# Parametrer ici sa propre clé pour récupérer la data à l'aide de l'API
API_KEY = '' 

# Parcourir chaque URL YouTube dans les résultats filtrés
for index, row in results.iterrows():
    url_youtube = row['links']
    
    # Extraire l'ID de la vidéo YouTube
    video_id = extraire_id_youtube(url_youtube)
    
    if video_id:
        try:
            # Obtenir les informations de la vidéo via l'API YouTube
            titre, auteur, duree = obtenir_infos_youtube(video_id, API_KEY)
            
            if titre and auteur and duree:
                # Convertir la durée en secondes
                duree_secondes = convertir_duree_en_secondes(duree)
                
                # Mettre à jour le DataFrame avec les nouvelles informations
                df.at[index, 'titre'] = titre
                df.at[index, 'auteur'] = auteur
                df.at[index, 'duree'] = seconds_to_hh_mm_ss(duree_secondes)  # Convertir en HH:MM:SS
                df.at[index, 'type'] = 'Video Youtube'  # Marquer le type comme vidéo
                
                # Délai pour éviter de dépasser les limites de l'API (ajuster si nécessaire)
                time.sleep(1)
            else:
                # Si les informations ne sont pas valides, laisser les colonnes vides
                df.at[index, 'duree'] = None
                df.at[index, 'type'] = 'Video Youtube'
                
        except Exception as e:
            print(f"Erreur lors de la récupération des infos pour la vidéo {video_id}: {e}")
            # Si une exception est levée, laisser les colonnes vides
            df.at[index, 'duree'] = None
            df.at[index, 'type'] = 'Video Youtube'

# Sauvegarder le DataFrame modifié dans un nouveau fichier CSV

df.to_csv("output.csv",index=False)
print("Le fichier CSV avec les informations YouTube a été sauvegardé.")
