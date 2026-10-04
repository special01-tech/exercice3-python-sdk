# Exercice 3 : SDK Python RodiumAi

Script en ligne de commande qui utilise le SDK Python officiel `rodiumai` :
chat, génération d'image, génération de vidéo.
Après chaque étape : `p` (précédent), `r` (rester), `s` (suivant).

## Installation
pip install -r requirements.txt

## Configuration
Copier `.env.example` vers `.env` et y mettre votre clé :

RODIUMAI_API_KEY=rd_sk_votre_cle

Le fichier `.env` n'est jamais envoyé sur GitHub.

## Lancement
python main.py

## Fonctions du SDK utilisées
- client.model(...).chat(...) : chat
- client.images.generate(...) : image (fichier image.png)
- client.video(...) : vidéo (fichier video.mp4)