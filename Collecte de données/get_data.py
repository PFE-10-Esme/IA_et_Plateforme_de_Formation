import os
import pandas as pd
import requests
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver

# Configuration des en-têtes User-Agent pour requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fonction pour corriger une URL si elle est invalide
def fix_url(url):
    if url.startswith('//'):
        return 'https:' + url
    elif not url.startswith('http'):
        return 'https://' + url
    return url

# Fonction pour extraire l'ID de la vidéo YouTube
def extraire_id_youtube(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_match = re.match(youtube_regex, url)
    return youtube_match.group(6) if youtube_match else None

# Fonction pour obtenir les informations de la vidéo YouTube via l'API
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
    return heures * 3600 + minutes * 60 + secondes

# Fonction pour convertir les secondes en format HH:MM:SS
def seconds_to_hh_mm_ss(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def extract_iframes(input_csv, output_csv, api_key):
    df = pd.read_csv(input_csv, index_col=False)
    driver = webdriver.Chrome()
    df['iframe_url'] = ''

    # Filtrer les lignes où 'hash_id' est vide ou NaN
    results = df[df['hash_id'].isna() | (df['hash_id'] == '')]

    for index, row in results.iterrows():
        url = row['links']
        str_youtu = 'youtu'

        if  str_youtu in url:   # Filtrer les lignes correspondant aux podcasts (pas YouTube)

            video_id = extraire_id_youtube(url)

            if video_id:
                try:
                    titre, auteur, duree = obtenir_infos_youtube(video_id, api_key)
                    if titre and auteur and duree:
                        duree_secondes = convertir_duree_en_secondes(duree)
                        df.at[index, 'titre'] = titre
                        df.at[index, 'auteur'] = auteur
                        df.at[index, 'duree'] = seconds_to_hh_mm_ss(duree_secondes)
                        df.at[index, 'type'] = 'Video Youtube'
                except Exception as e:
                    pass
        else:
            try:
                driver.get(url)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                iframes = soup.find_all('iframe')
                iframe_srcs = [iframe.get('src', '') for iframe in iframes if iframe.get('src')]
                df.at[index, 'iframe_url'] = ','.join(iframe_srcs) if iframe_srcs else None
                time.sleep(2)
            except Exception as e:
                df.at[index, 'iframe_url'] = None  


    driver.quit()
    df.to_csv(output_csv, index=False)

def extract_download_links(input_csv, output_csv):
    df = pd.read_csv(input_csv, index_col=False)
    df['download_link'] = ''

    results = df[df['hash_id'].isna() | (df['hash_id'] == '')]

    for index, row in results.iterrows():
        iframe_urls = row.get('iframe_url')
        if pd.notna(iframe_urls):
            url_list = iframe_urls.split(',')
            audio_links = []

            for url in url_list:
                try:
                    fixed_url = fix_url(url.strip())
                    response = requests.get(fixed_url, headers=headers)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.content, 'html.parser')

                    for tag in soup.find_all(href=True):
                        link = tag.get('href')
                        if 'mp3' in link:
                            audio_links.append(fix_url(link))

                    for tag in soup.find_all(src=True):
                        link = tag.get('src')
                        if 'mp3' in link:
                            audio_links.append(fix_url(link))

                except requests.exceptions.RequestException as e:
                    continue

            df.at[index, 'download_link'] = ','.join(audio_links) if audio_links else None
            time.sleep(2)

    df.to_csv(output_csv, index=False)

def download_files(input_csv):
    df = pd.read_csv(input_csv)
    results = df[df['download_link'].notna()]
    download_folder = os.getcwd()  # Répertoire actuel

    for index, row in results.iterrows():
        download_links = row['download_link']
        link_list = download_links.split(',')

        for url in link_list:
            url = url.strip()
            if url.startswith('https'):
                print(f"Téléchargement depuis le lien : {url}")
                file_name = url.split("/")[-1].split("?")[0]
                file_path = os.path.join(download_folder, file_name)

                try:
                    response = requests.get(url, headers=headers, stream=True)
                    response.raise_for_status()

                    with open(file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)

                    print(f"Fichier téléchargé et enregistré sous : {file_path}")
                except requests.exceptions.RequestException as e:
                    print(f"Erreur lors du téléchargement depuis {url} : {e}")

# Exécution
input_csv = "db_btc-touchpoint - db.csv"
output_csv = "output.csv"
download_link_output_csv = "link_download.csv"
api_key = ""

# Étape 1 : Extraction des iframes (podcasts)
extract_iframes(input_csv, output_csv, api_key)

# Étape 2 : Extraction des liens de téléchargement (podcasts)
extract_download_links(output_csv, download_link_output_csv)

# Étape 3 : Téléchargement des fichiers (podcasts)
download_files(download_link_output_csv)
