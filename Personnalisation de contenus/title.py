import openai
import re
import pandas as pd
import json
import time
import os
import tiktoken  # Library to estimate token count

# Initialize the tokenizer for the specific OpenAI model
tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Function to truncate text based on token limit
def truncate_text(text, max_tokens):
    tokens = tokenizer.encode(text)
    truncated_tokens = tokens[:max_tokens]
    return tokenizer.decode(truncated_tokens)

# Load environment variable for API key
openai.api_key = "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"

# Load JSON data and CSV
with open("nouveau_fichier.json", "r", encoding='utf-8') as json_file:
    json_data = json.load(json_file)

df = pd.read_csv("summary.csv", index_col=False)

df['keywords'] = None
df['Titre_BTC'] = None

# Create a dictionary indexed by hash_id and check transcription type dynamically
json_indexed = {}
for x in json_data:
    if x.get("transcription_video"):
        json_indexed[x["id"]] = x["transcription_video"]
    elif x.get("transcription_page_web"):
        json_indexed[x["id"]] = x["transcription_page_web"]
    elif x.get("transcription_podcast"):
        json_indexed[x["id"]] = x["transcription_podcast"]

def index_json(hash_id):
    return json_indexed.get(hash_id)  # Fast lookup in the dictionary

def clean_title(text):

    if not isinstance(text, str):  # Vérifie que le texte est une chaîne
        return ""
    
    # Expression régulière pour capturer uniquement le texte entre guillemets doubles
    matches = re.findall(r'"([^"]+)"', text)
    return " ".join(matches)

# Filter the rows that correspond to YouTube videos
results = df[df['summary'].notna()]
results = results.head(100)

# Process each YouTube video
for index, row in results.iterrows():
    title = row['title']
    subtitle = row['subtitle']
    quadrant = row['quadrant']
    type = row['type']
    titre = row['titre']
    auteur = row['auteur']
    hash_id = row['hash_id']
    transcription = index_json(hash_id)

    if not transcription:
        print(f"No transcription found for {title}")
        continue  # Skip if no transcription

    # Truncate the transcription to ensure it fits the token limit
    max_input_tokens = 12000  # Adjust this value to ensure space for the prompt and response
    truncated_transcription = truncate_text(transcription, max_input_tokens)

    try:

        prompt_keywords = f"""Donne un ensemble de mots-clés à partir du contenu suivant et des infos suivantes: {type}.
        Attention si la dernier mot n'est pas complet, coupe-le.
        Tu peux me prendre 8 et 10 mots-clés les pertinents et plus cohérents avec toutes les informations cités ci-dessus.
        Le {type} aborde le thème : {title}. Il a pour sous-thème : {subtitle}. 
        Il aborde une question : {quadrant}.
        Le titre du contenu est {titre}. Attention si le titre est nan ne prend pas le titre comme paramètre pour faire les mots-clés.
        Aide toi de la transcription du {type} pour trouver les différents mots-clés : {truncated_transcription}
        Sépare moi les différents mots-clés par des virgules."""

        response_keywords = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_keywords},
            ],
            max_tokens=150,
            temperature=0.7,
        )

        keywords = response_keywords['choices'][0]['message']['content'].strip()


        prompt_title = f"""Donne un titre en français et mets-le entre des guillements à partir de cette transcription: {truncated_transcription}.
        Les mots-clés reliés au contenus sont {keywords}
        On a comme thème pour ce contenu {title}. Il a pour sous-thème : {subtitle}. 
        Il aborde une question : {quadrant}.
        Si la dernier mot n'est pas complet, coupe-le."""

        response_title = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_title},
            ],
            max_tokens=40,
            temperature=0.7,
        )

        title = response_title['choices'][0]['message']['content'].strip()

        df.at[index, 'keywords'] = keywords
        df.at[index, 'Titre_BTC'] = title
        print(keywords)
        print(title)

        time.sleep(1)

    except Exception as e:
        # Handle any exceptions that may occur (e.g., network issues, API errors)
        print(f"Error processing {title}: {e}")
        pass

print("On applique la fonction de nettoyage pour les titres")
df['Titre_BTC'] = df['Titre_BTC'].apply(clean_title)

# Save the updated DataFrame to a new CSV file
df.to_csv("final_csv.csv", index=False)
