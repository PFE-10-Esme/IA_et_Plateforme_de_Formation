import os
import pandas as pd
import requests

# Charger le fichier CSV
df = pd.read_csv("link_download.csv")
df = df.head(31)

# Filtrer uniquement les lignes non vides dans la colonne 'download_link'
results = df[df['download_link'].notna()]

# Créer un dossier pour les fichiers téléchargés
download_folder = os.path.join(os.getcwd(), "C:\\Users\\PC\\Downloads\\projet remodelé")
os.makedirs(download_folder, exist_ok=True)

# Définir l'agent utilisateur pour imiter un navigateur
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Parcourir chaque ligne des résultats filtrés
for index, row in results.iterrows():
    download_links = row['download_link']  # Récupérer les liens dans la cellule
    
    # Diviser les liens s'ils sont séparés par des virgules
    link_list = download_links.split(',')
    
    for url in link_list:
        url = url.strip()  # Supprimer les espaces superflus
        
        # Vérifier si le lien est valide et contient 'download=true'
        if url.startswith('https') and 'download=true' in url:
            print(f"Téléchargement depuis le lien : {url}")
            
            # Obtenir le nom de fichier à partir de l'URL
            file_name = url.split("/")[-1].split("?")[0]
            file_path = os.path.join(download_folder, file_name)
            
            try:
                # Télécharger le fichier avec l'agent utilisateur
                response = requests.get(url, headers=headers, stream=True)
                response.raise_for_status()  # Vérifier les erreurs HTTP
                
                # Enregistrer le fichier localement
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                print(f"Fichier téléchargé et enregistré sous : {file_path}")
            except requests.exceptions.RequestException as e:
                print(f"Erreur lors du téléchargement depuis {url} : {e}")
