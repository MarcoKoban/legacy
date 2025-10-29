#!/bin/bash
# Script pour préparer le déploiement Surge
# Copie index.html en 200.html pour le routing SPA

cp dist/front/browser/index.html dist/front/browser/200.html
echo "✅ Fichier 200.html créé pour le routing SPA Surge"
