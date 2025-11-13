"""
Configuration de la simulation
"""

# PARAMÈTRES DES JOUEURS
NUM_PLAYERS = 4
PLAYER_BUDGETS = [100, 80, 120, 90]  # Budgets individuels
PLAYER_VALUATIONS = [50, 30, 40, 35]  # Valorisations (ai)
PLAYER_ALPHAS = [1, 1, 1, 1]  # Tous proportional fairness

# PARAMÈTRES DU SYSTÈME
DELTA = 0.1  # Réservation système
PRICE_LAMBDA = 1.0  # Prix par unité

# PARAMÈTRES DE SIMULATION
SIMULATION_TIME = 200.0  # Durée totale (secondes simulées)
RECORD_INTERVAL = 1.0  # Fréquence d'enregistrement

# TAUX D'ÉVÉNEMENTS
ARRIVAL_RATE = 0.1  # Arrivées par seconde
DEPARTURE_RATE = 0.05  # Départs par seconde
BIDDING_RATE = 1.0  # Enchères par seconde

# POLITIQUE D'ENCHÈRE
BIDDING_POLICY = "gradient_descent"  # ou "gradient_descent"

# AFFICHAGE
VERBOSE = True  # Afficher les logs détaillés