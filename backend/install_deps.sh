#!/bin/bash

# Script d'installation des dépendances essentielles pour Django

source venv/bin/activate

echo "Installation des dépendances essentielles Django..."

pip install \
    djangorestframework==3.16.0 \
    django-cors-headers==4.7.0 \
    djangorestframework-simplejwt==5.5.0 \
    django-environ==0.11.2 \
    django-filter==23.5 \
    pillow \
    python-dateutil \
    --quiet

echo "Dépendances installées avec succès!"