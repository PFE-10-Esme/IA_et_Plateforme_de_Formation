# IA et Plateforme de Formation

Ce projet est un projet ayant pour but d'automatiser l'implémentation de textes générés par l'IA et de pouvoir le déployer sur une plateforme de formation. 


## Collecte des données

Pour cela les ressources extraites seront des fichiers des liens qui amènent aux vidéos et textes en question. Les informations importantes de ces ressources seront extraites comme l'auteur du contenu, le titre du contenu, etc, ainsi que la transcription... A partir de ces informations ainsi que d'un modèle de Chat GPT on va pouvoir implémenter des résumés et autres détails comme des titres de contenus pour la dite plateforme.


## Génération de données descriptives

A partir des informations pour chaque ligne on va pouvoir générer des résumés, des mots-clés et des titres pour chaque ligne de données. Pour se faire on va utiliser l'API openai qui va pouvoir faire des réponses aux prompts qu'on va lui donner qui contiennent la requete pour créer le résumé. Idem pour les mots-clés et des titres. Toutes les informations générées et précédentes vont ensuite être contenus dans Firebase.


c
