"""
Composant 1: Player (Joueur)
Représente un agent qui enchérit pour des ressources selon le mécanisme de Kelly
"""

import numpy as np


class Player:
    """
    Un joueur dans le système d'enchères Kelly
    """
    
    def __init__(self, player_id, initial_budget, valuation_weight, alpha=1):
        """
        Initialise un joueur
        
        Args:
            player_id (int): Identifiant unique du joueur
            initial_budget (float): Budget initial (ci)
            valuation_weight (float): Poids de valorisation (ai)
            alpha (float): Paramètre d'équité α-fair (0, 1, ou 2)
        """
        self.id = player_id
        self.budget = initial_budget
        self.valuation_weight = valuation_weight  # ai
        self.alpha = alpha  # α
        
        # État actuel
        self.current_bid = 0.001  # Enchère minimale au départ
        self.allocated_share = 0.0
        self.active = True
        
        # Historique
        self.history = {
            'time': [],
            'bids': [],
            'allocations': [],
            'utilities': [],
            'payoffs': []
        }
    
    def compute_utility(self, share_received):
        """
        Calcule l'utilité α-fair selon la part reçue
        
        Formules selon α:
        - α = 0: V(x) = x              (Efficacité maximale)
        - α = 1: V(x) = log(x)         (Proportional fairness)
        - α = 2: V(x) = -1/x           (Minimum potential delay)
        - α autre: V(x) = x^(1-α)/(1-α)
        
        Args:
            share_received (float): Part de ressource reçue (xi)
        
        Returns:
            float: Utilité calculée
        """
        if share_received <= 0:
            return -np.inf
        
        if self.alpha == 0:
            # Efficacité maximale
            utility = share_received
        elif self.alpha == 1:
            # Proportional fairness
            utility = np.log(share_received)
        elif self.alpha == 2:
            # Minimum potential delay
            utility = -1.0 / share_received
        else:
            # Cas général
            utility = (share_received ** (1 - self.alpha)) / (1 - self.alpha)
        
        # Pondération par ai
        return self.valuation_weight * utility
    
    def compute_payoff(self, share_received, price_lambda):
        """
        Calcule le gain net (utilité - coût)
        
        φi(z) = ai * Vi(z) - λ * zi
        
        Args:
            share_received (float): Part de ressource reçue
            price_lambda (float): Prix par unité (λ)
        
        Returns:
            float: Gain net
        """
        utility = self.compute_utility(share_received)
        cost = price_lambda * self.current_bid
        return utility - cost
    
    def best_response_bid(self, aggregate_bid_others, price_lambda, delta=0.1, epsilon=0.001):
        """
        Calcule l'enchère optimale (Best Response) selon Lemma 1
        
        Args:
            aggregate_bid_others (float): Somme des enchères des autres (Σz_j pour j≠i)
            price_lambda (float): Prix unitaire (λ)
            delta (float): Réservation système (δ)
            epsilon (float): Enchère minimale
        
        Returns:
            float: Enchère optimale
        """
        s_minus_i = aggregate_bid_others + delta
        a = self.valuation_weight
        
        # Calcul selon α (Lemma 1 du papier)
        if self.alpha == 0:
            # BRf_i(s_-i) = √(ai*s_-i/λ) - s_-i
            bid_unconstrained = np.sqrt(a * s_minus_i / price_lambda) - s_minus_i
            
        elif self.alpha == 1:
            # BRf_i(s_-i) = (-s_-i + √(s²_-i + 4ai*s_-i/λ)) / 2
            discriminant = s_minus_i**2 + 4 * a * s_minus_i / price_lambda
            if discriminant < 0:
                bid_unconstrained = epsilon
            else:
                bid_unconstrained = (-s_minus_i + np.sqrt(discriminant)) / 2
            
        elif self.alpha == 2:
            # BRf_i(s_-i) = √(ai*s_-i/λ)
            bid_unconstrained = np.sqrt(a * s_minus_i / price_lambda)
        
        else:
            # Cas général: approximation numérique
            bid_unconstrained = self._numerical_best_response(
                s_minus_i, price_lambda, epsilon
            )
        
        # Projection sur [epsilon, budget]
        bid_optimal = np.clip(bid_unconstrained, epsilon, self.budget)
        
        return bid_optimal
    
    def _numerical_best_response(self, s_minus_i, price_lambda, epsilon):
        """
        Calcule la meilleure réponse par recherche numérique
        (pour les cas α non standard)
        """
        # Recherche par dichotomie
        low, high = epsilon, self.budget
        
        for _ in range(50):  # 50 itérations suffisent
            mid = (low + high) / 2
            
            # Calcul de la dérivée approchée
            h = 1e-6
            share_mid = mid / (mid + s_minus_i)
            share_mid_plus = (mid + h) / (mid + h + s_minus_i)
            
            utility_mid = self.compute_utility(share_mid)
            utility_mid_plus = self.compute_utility(share_mid_plus)
            
            derivative = (utility_mid_plus - utility_mid) / h - price_lambda
            
            if abs(derivative) < 1e-6:
                break
            
            if derivative > 0:
                low = mid
            else:
                high = mid
        
        return mid
    
    def gradient_descent_update(self, aggregate_bid, learning_rate=0.1,  price_lambda=1.0, delta=0.1):
        """
        Mise à jour par descente de gradient (politique alternative)
        
        Args:
            learning_rate (float): Taux d'apprentissage (η)
            aggregate_bid (float): Enchère totale actuelle
            price_lambda (float): Prix
            delta (float): Réservation
        
        Returns:
            float: Nouvelle enchère
        """
        # Calcul du gradient numérique
        h = 1e-5
        current_share = self.current_bid / (aggregate_bid + delta)
        perturbed_share = (self.current_bid + h) / (aggregate_bid + h + delta)
        
        utility_current = self.compute_utility(current_share)
        utility_perturbed = self.compute_utility(perturbed_share)
        
        gradient = (utility_perturbed - utility_current) / h - price_lambda
        
        # Mise à jour
        new_bid = self.current_bid + learning_rate * gradient
        new_bid = np.clip(new_bid, 0.001, self.budget)
        
        return new_bid
    
    def update_bid(self, new_bid, time_step):
        """
        Met à jour l'enchère du joueur
        
        Args:
            new_bid (float): Nouvelle enchère
            time_step (int): Pas de temps actuel
        """
        self.current_bid = new_bid
        self.history['time'].append(time_step)
        self.history['bids'].append(new_bid)
    
    def receive_allocation(self, share, price_lambda):
        """
        Reçoit sa part de ressource et calcule les métriques
        
        Args:
            share (float): Part de ressource allouée
            price_lambda (float): Prix unitaire
        """
        self.allocated_share = share
        
        utility = self.compute_utility(share)
        payoff = self.compute_payoff(share, price_lambda)
        
        self.history['allocations'].append(share)
        self.history['utilities'].append(utility)
        self.history['payoffs'].append(payoff)
    
    def enter_system(self, time_step):
        """Entrée du joueur dans le système"""
        self.active = True
        print(f"[t={time_step}] Player {self.id} ARRIVED")
    
    def leave_system(self, time_step):
        """Sortie du joueur du système"""
        self.active = False
        print(f"[t={time_step}] Player {self.id} DEPARTED")
    
    def get_statistics(self):
        """
        Retourne les statistiques du joueur
        
        Returns:
            dict: Statistiques agrégées
        """
        if len(self.history['utilities']) == 0:
            return {
                'player_id': self.id,
                'mean_bid': 0,
                'mean_allocation': 0,
                'mean_utility': 0,
                'total_payoff': 0
            }
        
        return {
            'player_id': self.id,
            'mean_bid': np.mean(self.history['bids']),
            'std_bid': np.std(self.history['bids']),
            'mean_allocation': np.mean(self.history['allocations']),
            'mean_utility': np.mean(self.history['utilities']),
            'total_payoff': np.sum(self.history['payoffs']),
            'final_bid': self.history['bids'][-1] if self.history['bids'] else 0
        }
    
    def __repr__(self):
        return (f"Player(id={self.id}, α={self.alpha}, "
                f"bid={self.current_bid:.3f}, share={self.allocated_share:.3f})")