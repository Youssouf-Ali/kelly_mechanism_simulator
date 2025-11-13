"""
Composant 2: ResourceOwner (Propriétaire de Ressources)
Gère les prix et communique l'enchère agrégée aux joueurs
"""

import numpy as np


class ResourceOwner:
    """
    Le propriétaire de ressources qui fixe les prix et gère l'allocation
    """
    
    def __init__(self, total_resource=1.0, price_lambda=1.0, delta=0.1):
        """
        Initialise le propriétaire de ressources
        
        Args:
            total_resource (float): Quantité totale de ressource (normalisée à 1)
            price_lambda (float): Prix par unité de caching (λ)
            delta (float): Réservation système (δ ≥ 0)
        """
        self.total_resource = total_resource
        self.price = price_lambda
        self.delta = delta
        
        # Historique pour analyse
        self.history = {
            'time': [],
            'prices': [],
            'total_bids': [],
            'revenues': []
        }
    
    def get_current_price(self):
        """
        Retourne le prix actuel
        
        Returns:
            float: Prix λ
        """
        return self.price
    
    def set_price(self, new_price, time_step):
        """
        Ajuste le prix (pour versions avancées du TP)
        
        Args:
            new_price (float): Nouveau prix λ
            time_step (int): Temps actuel
        
        Lien TP (PricingAndBidding.pdf, page 1):
        "(3) Price adjustment: events when the price maker revise 
             the price of the assigned resource. Start with static prices."
        """
        self.price = new_price
        self.history['time'].append(time_step)
        self.history['prices'].append(new_price)
        print(f"[t={time_step}] Price updated: λ = {new_price:.3f}")
    
    def get_aggregate_bid(self, players):
        """
        Calcule la somme totale des enchères de tous les joueurs actifs
        
        Args:
            players (list): Liste des joueurs
        
        Returns:
            float: Σzi (somme des enchères)
        
        Lien avec équation (1) du CCWDN_2017.pdf:
        Le dénominateur de xi = zi / (Σzj + δ)
        """
        total_bid = sum(p.current_bid for p in players if p.active)
        return total_bid
    
    def get_aggregate_bid_excluding(self, players, exclude_id):
        """
        Calcule Σzj pour j≠i (enchère agrégée sans le joueur i)
        
        Args:
            players (list): Liste des joueurs
            exclude_id (int): ID du joueur à exclure
        
        Returns:
            float: s-i = Σ(zj pour j≠i)
        
        Pourquoi cette méthode ?
        Utilisée pour calculer le Best Response du joueur i.
        Il a besoin de connaître ce que les AUTRES enchérissent.
        
        Formule Lemma 1: BRi(s-i) où s-i = Σ(zj pour j≠i) + δ
        """
        aggregate = sum(p.current_bid for p in players 
                       if p.active and p.id != exclude_id)
        return aggregate
    
    def communicate_aggregate_to_players(self, players):
        """
        Communique l'enchère agrégée à chaque joueur
        
        Lien TP (PricingAndBidding.pdf, page 1):
        "Assume that players know what the others bid at the previous step 
         (the resource owner will communicate the aggregated bid)"
        
        Args:
            players (list): Liste des joueurs
        
        Returns:
            dict: {player_id: aggregate_bid_others}
        """
        aggregates = {}
        
        for player in players:
            if not player.active:
                continue
            
            # Calcul de s-i pour chaque joueur
            aggregate_others = self.get_aggregate_bid_excluding(
                players, player.id
            )
            aggregates[player.id] = aggregate_others
        
        return aggregates
    
    def compute_revenue(self, players, time_step):
        """
        Calcule le revenu du propriétaire
        
        Revenue = Σ(λ · zi) pour tous les joueurs actifs
        
        Args:
            players (list): Liste des joueurs
            time_step (int): Temps actuel
        
        Returns:
            float: Revenu total
        
        Lien avec équation (4):
        Le coût pour le joueur i est : λ · zi
        Donc le revenu du propriétaire est la somme de ces coûts
        """
        revenue = sum(self.price * p.current_bid 
                     for p in players if p.active)
        
        self.history['revenues'].append(revenue)
        return revenue
    
    def get_statistics(self):
        """
        Retourne les statistiques du propriétaire
        
        Returns:
            dict: Statistiques agrégées
        """
        if len(self.history['revenues']) == 0:
            return {
                'mean_revenue': 0,
                'total_revenue': 0,
                'mean_price': self.price
            }
        
        return {
            'mean_revenue': np.mean(self.history['revenues']),
            'total_revenue': np.sum(self.history['revenues']),
            'mean_price': np.mean(self.history['prices']) if self.history['prices'] else self.price,
            'final_price': self.price
        }
    
    def __repr__(self):
        return f"ResourceOwner(λ={self.price:.2f}, δ={self.delta:.2f})"