# IA et Plateforme de Formation

Ce projet est un projet ayant pour but d'améliorer la qualité de la donnée pour un ensemble de lignes de donnée et pouvoir l'automatiser, implémenter de textes générés par l'IA et de pouvoir déployer une base de données sur une solution cloud pour faire la gestion de cette BDD et l'utiliser pour la solution front-end que représente le site de BTC Touchpoint. 


## Collecte des données

Pour cela les ressources extraites seront des fichiers des liens qui amènent aux vidéos et textes en question. Les informations importantes de ces ressources seront extraites comme l'auteur du contenu, le titre du contenu, etc, ainsi que la transcription...
Plusieurs techniques et API sont appliquées pour recevoir les différentes informations comme web scrapping ou bien l'API Youtube. L'utilisation de ces techniques dépendra du type du contenu traité en question.
A partir de ces informations ainsi que d'un modèle de Chat GPT on va pouvoir implémenter des résumés et autres détails comme des titres de contenus pour la dite plateforme.


## Génération de données descriptives

A partir des informations pour chaque ligne on va pouvoir générer des résumés, des mots-clés et des titres pour chaque ligne de données. Pour se faire on va utiliser l'API openai qui va pouvoir faire des réponses aux prompts qu'on va lui donner qui contiennent la requete pour créer le résumé. Idem pour les mots-clés et des titres. Toutes les informations générées et précédentes vont ensuite être contenus dans Firestore.


## Déploiement de la solution Cloud



c
