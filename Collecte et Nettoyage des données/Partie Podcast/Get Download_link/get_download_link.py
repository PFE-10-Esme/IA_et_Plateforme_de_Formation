import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Exemple d'en-têtes User-Agent pour simuler un navigateur
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Fonction pour corriger une URL si elle est invalide
def fix_url(url):
    if url.startswith('//'):  # Si l'URL commence par //
        return 'https:' + url
    elif not url.startswith('http'):  # Si l'URL ne contient pas http ou https
        return 'https://' + url
    return url  # Retourne l'URL telle quelle si elle est valide

# Chargement du fichier CSV
df = pd.read_csv("iframes.csv", index_col=False)


# Ajouter une colonne pour les liens de téléchargement
df['download_link'] = ''

# Filtrer les lignes avec des URLs valides dans la colonne 'podcast_url'
results = df[df['iframe_url'].notna()]

# Parcourir chaque ligne du DataFrame
for index, row in results.iterrows():
    try:
        iframe_urls = row['iframe_url']  # Colonne contenant les URLs
        url_list = iframe_urls.split(',')  # Diviser en liste si plusieurs URLs
        audio_links = []  # Liste pour stocker les liens audio trouvés

        # Traiter chaque URL
        for url in url_list:
            fixed_url = fix_url(url.strip())  # Corriger l'URL si nécessaire
            response = requests.get(fixed_url, headers=headers)  # Requête HTTP
            response.raise_for_status()  # Vérifie les erreurs HTTP
            soup = BeautifulSoup(response.content, 'html.parser')

            # Rechercher les balises avec href
            for tag in soup.find_all(href=True):
                link = tag.get('href')
                if 'mp3' in link or 'mp4' in link:
                    audio_links.append(fix_url(link))  # Corriger si nécessaire

            # Rechercher les balises avec src
            for tag in soup.find_all(src=True):
                link = tag.get('src')
                if 'mp3' in link or 'mp4' in link:
                    audio_links.append(fix_url(link))  # Corriger si nécessaire


        # Enregistrer les liens trouvés dans la colonne
        if audio_links:
            df.at[index, 'download_link'] = ','.join(audio_links)
        else:
            df.at[index, 'download_link'] = None

        time.sleep(2)  # Pause pour éviter de surcharger le serveur

    except requests.exceptions.RequestException as e:
        #print(f"Erreur pour l'index {index}: {e}")
        df.at[index, 'download_link'] = None

# Sauvegarder le DataFrame dans un nouveau fichier CSV
df.to_csv("link_download.csv", index=False)
