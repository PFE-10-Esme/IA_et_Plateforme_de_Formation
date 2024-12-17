import openai
import pandas as pd
import json
import time
import os

# Load environment variable for API key
openai.api_key = "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"

# Load JSON data and CSV
with open("transcriptions_finales.json", "r", encoding='utf-8') as json_file:
    json_data = json.load(json_file)

df = pd.read_csv("description.csv", index_col=False)

# Filter the rows that correspond to YouTube videos
Type = 'Video Youtube'
results = df[(df['type'].str.contains(Type, na=False)) & (df['hash_id'].notna())]

df['titles_bis'] = ''

# Create a dictionary indexed by hash_id for faster lookup
json_indexed = {x["id"]: x["transcription"] for x in json_data}

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
    summary_bis = row['summary_bis']
    description_bis = row['description_bis']

    if not transcription:
        print(f"No transcription found for {title}")
        continue  # Skip if no transcription

    try:
        # Prepare the prompt for GPT-4 Chat model
        prompt_titles = f"""Résume en 3 ou 4 lignes le texte que je vais te fournir et qui provient d'un contenu {type}.
        Le {type} aborde le thème : {title}. Il a pour sous-thème : {subtitle}. 
        Il aborde une question : {quadrant}.
        Le titre du contenu est {titre}.
        L'auteur ou le groupe d'auteurs du contenu est {auteur}.
        Aide toi du résumé et des mots-clés pour donner un titre à mon contenu  {type}: {summary_bis} et {description_bis}
        Le dernier mot doit être complet et ne doit pas être une conjonction de coordination ou un adverbe."""

        # Call GPT-3.5 or GPT-4 Chat model using the 'chat/completions' endpoint
        response_title = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or use "gpt-4" if you're using GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_titles},
            ],
            max_tokens=50,  # limit for summary length
            temperature=0.7,
        )
        # Extract summary from the response
        title = response_title['choices'][0]['message']['content'].strip()
        df.at[index, 'titles_bis'] = title

        # Rate limiting: sleep for a short period to avoid overloading the API
        time.sleep(2)

    except Exception as e:
        # Handle any exceptions that may occur (e.g., network issues, API errors)
        pass

# Save the updated DataFrame to a new CSV file
df.to_csv("titles.csv", index=False)