import openai
import pandas as pd
import json
import time
import os
from bs4 import BeautifulSoup
from selenium import webdriver

# Chargement du fichier CSV
df = pd.read_csv("db_btc-touchpoint - db.csv", index_col=False)

# Initialisation du driver Selenium
driver = webdriver.Chrome()

# Filtrer les lignes correspondant aux vidéos YouTube
Type = 'youtu'
results = df[~df['links'].str.contains(Type, na=False)]

df['iframe_url'] = ''

# Traiter chaque URL
for index, row in results.iterrows():
    url = row['links']
    
    try:
        # Ouvrir l'URL avec Selenium
        driver.get(url)

        # Parser la page avec BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        iframes = soup.find_all('iframe')  # Trouver tous les iframes

        if iframes:
            # Extraire les 'src' de tous les iframes
            iframe_srcs = [iframe.get('src', '') for iframe in iframes if iframe.get('src')]
            # Stocker les sources comme une liste (ou une chaîne de caractères si nécessaire)
            df.at[index, 'iframe_url'] = ','.join(iframe_srcs)
        else:
            df.at[index, 'iframe_url'] = None

        time.sleep(2)

    except Exception as e:
        df.at[index, 'iframe_url'] = None

# Fermer le driver Selenium
driver.quit()

# Sauvegarder le DataFrame dans un fichier CSV
df.to_csv("iframes.csv", index=False)
