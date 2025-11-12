# Simulateur du Mécanisme de Kelly

## Description
Ce projet implémente un simulateur événementiel du mécanisme de Kelly pour l'allocation de ressources avec enchères.

## Installation
```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\Activate.ps1  # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Structure du projet
```
kelly_mechanism_simulator/
├── src/              # Code source des composants
├── tests/            # Tests unitaires
├── simulations/      # Scripts de simulation
├── results/          # Résultats et graphiques
└── docs/             # Documentation
```

## Utilisation
```bash
python simulations/run_simulation.py
```

## Auteurs
- Votre Nom

## Licence
MIT


```
📋 Commandes Git Essentielles - Aide-Mémoire
# Voir l'état actuel
git status

# Voir l'historique des commits
git log --oneline

# Ajouter des fichiers
git add fichier.py           # Un seul fichier
git add src/                 # Un dossier
git add .                    # Tout

# Créer un commit
git commit -m "Message descriptif"

# Envoyer sur GitHub
git push

# Récupérer depuis GitHub
git pull

# Voir les différences avant de commiter
git diff

# Annuler les modifications locales (⚠️ ATTENTION)
git checkout -- fichier.py

# Créer une nouvelle branche (pour tester sans casser)
git branch feature-test
git checkout feature-test
# Ou en une commande :
git checkout -b feature-test

# Revenir à la branche principale
git checkout main

# Fusionner une branche
git merge feature-test
```