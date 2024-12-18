import openai
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

df = pd.read_csv("output.csv", index_col=False)

# Filter the rows that correspond to YouTube videos
results = df[df['hash_id'].notna()]
results = results.head(100)

df['summary'] = None

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
        # Prepare the prompt for GPT-4 Chat model
        prompt_summary = f"""Résume en 3 ou 4 lignes et en français la transcription que je vais te fournir et qui provient d'un contenu {type}.
        Attention Ne mentionne pas dans le résumé que c'est une transcription et varie les mots et les verbes d'introduction pour les premières phrases. 
        On veut éviter de tout le temps générer : "le contenu vidéo aborde". Le problème est que ce genre de phrase est trop générique.
        Attention si la dernière phrase n'a pas comme dernier caractère un signe de ponctuation alors supprime cette phrase et ne mets pas mes consignes suivantes et précédentes dans le résumé comme 'Il a pour sous-thème'.
        Le {type} aborde le thème : {title}. Il a pour sous-thème : {subtitle}. 
        Il aborde une question : {quadrant}.
        Le titre du contenu est {titre}. Attention s'il n'y a pas de titre pour le contenu alors ne mentionne pas ceci dans le résumé.
        L'auteur ou le groupe d'auteurs du contenu est {auteur}.
        Voici la transcription en entier que je te demande de résumer : {truncated_transcription}"""

        # Call GPT-3.5 or GPT-4 Chat model using the 'chat/completions' endpoint
        response_summary = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or use "gpt-4" if you're using GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_summary},
            ],
            max_tokens=150,  # limit for summary length
            temperature=0.7,
        )

        # Extract summary from the response
        summary = response_summary['choices'][0]['message']['content'].strip()
        df.at[index, 'summary'] = summary
        print(summary)

        # Rate limiting: sleep for a short period to avoid overloading the API
        time.sleep(2)

    except Exception as e:
        # Handle any exceptions that may occur (e.g., network issues, API errors)
        print(f"Error processing {title}: {e}")
        pass

def clean_summary(summary):
    if pd.isna(summary):
        return summary
        
    sentences = re.split(r'(?<=[.!?])\s+', summary.strip())

    if sentences and not sentences[-1].endswith('.'):
        sentences.pop()

    return " ".join(sentences)

print("On applique la fonction de nettoyage pour les résumés")
df['summary'] = df['summary'].apply(clean_summary)

# Save the updated DataFrame to a new CSV file
df.to_csv("summary.csv", index=False)
