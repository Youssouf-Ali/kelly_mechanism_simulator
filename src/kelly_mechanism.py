"""
Composant 3: KellyMechanism (Mécanisme d'Allocation)
Implémente l'allocation proportionnelle de Kelly et vérifie l'équilibre
"""

import numpy as np


class KellyMechanism:
    """
    Implémente le mécanisme d'allocation proportionnelle de Kelly
    """
    
    def __init__(self, delta=0.1):
        """
        Initialise le mécanisme de Kelly
        
        Args:
            delta (float): Paramètre de réservation système (δ)
        
        Lien avec équation (1) du CCWDN_2017.pdf:
        xi = zi / (Σzj + δ)
             Le δ apparaît ici ↑
        """
        self.delta = delta
        
        # Historique
        self.history = {
            'time': [],
            'social_welfare': [],
            'allocations': [],
            'is_nash': []
        }
    
    def allocate_resources(self, players):
        """
        Alloue les ressources selon le mécanisme de Kelly
        
        ÉQUATION (1) du CCWDN_2017.pdf, page 2:
        
                zi
        xi = --------
             Σzj + δ
        
        où:
        - xi : part de ressource pour le joueur i
        - zi : enchère du joueur i
        - Σzj : somme de TOUTES les enchères (y compris zi)
        - δ : réservation système
        
        Args:
            players (list): Liste des joueurs actifs
        
        Returns:
            dict: {player_id: allocated_share}
        
        Lien TP (PricingAndBidding.pdf, page 1):
        "Component 3: Bidding mechanism. Implements the Kelly mechanism."
        """
        # Calcul du dénominateur : Σzj + δ
        total_bid = sum(p.current_bid for p in players if p.active) + self.delta
        
        # Éviter la division par zéro
        if total_bid <= self.delta:  # Aucun joueur n'enchérit
            total_bid = self.delta
        
        allocations = {}
        
        for player in players:
            if not player.active:
                allocations[player.id] = 0.0
                continue
            
            # ÉQUATION (1) : Allocation proportionnelle
            share = player.current_bid / total_bid
            
            allocations[player.id] = share
            
            # Informer le joueur de sa part
            player.receive_allocation(share, self.get_price_from_owner(player))
        
        return allocations
    
    def get_price_from_owner(self, player):
        """
        Récupère le prix (en pratique, on le passera en paramètre)
        
        Note: Dans l'implémentation complète, on passera 
              resource_owner.get_current_price()
        """
        # Placeholder - sera remplacé dans l'event handler
        return 1.0
    
    def compute_social_welfare(self, players):
        """
        Calcule le bien-être social total
        
        Social Welfare = Σ Ui(xi)
        
        où Ui(xi) = ai · Vi(xi) est l'utilité du joueur i
        
        Args:
            players (list): Liste des joueurs
        
        Returns:
            float: Bien-être social total
        
        Lien avec le papier Best-Response, Section VI:
        Le bien-être social mesure l'efficacité globale du système.
        L'équilibre de Nash atteint au moins 3/4 de l'optimal (Johari & Tsitsiklis)
        """
        social_welfare = 0.0
        
        for player in players:
            if not player.active:
                continue
            
            if player.allocated_share > 0:
                utility = player.compute_utility(player.allocated_share)
                social_welfare += utility
        
        return social_welfare
    
    def compute_price_of_anarchy(self, players, optimal_welfare):
        """
        Calcule le Price of Anarchy (PoA)
        
        PoA = Optimal Social Welfare / Nash Equilibrium Welfare
        
        Args:
            players (list): Liste des joueurs
            optimal_welfare (float): Bien-être optimal (théorique)
        
        Returns:
            float: Price of Anarchy
        
        Interprétation:
        - PoA = 1 : L'équilibre est optimal
        - PoA > 1 : Il y a une perte d'efficacité due à l'égoïsme
        
        Référence: Johari & Tsitsiklis (2004) - PoA ≥ 3/4 pour Kelly
        """
        current_welfare = self.compute_social_welfare(players)
        
        if current_welfare <= 0:
            return np.inf
        
        return optimal_welfare / current_welfare
    
    def is_nash_equilibrium(self, players, resource_owner, tolerance=1e-3):
        """
        Vérifie si l'état actuel est un équilibre de Nash
        
        DÉFINITION (Best-Response paper, Def. 1, page 3):
        Un profil z* est un NE si, pour chaque joueur i:
        
        φi(z*i, z*-i) ≥ φi(zi, z*-i)  ∀zi ∈ Ri
        
        En pratique: on vérifie que personne ne peut améliorer 
        son gain en changeant unilatéralement son enchère.
        
        Args:
            players (list): Liste des joueurs
            resource_owner (ResourceOwner): Propriétaire de ressources
            tolerance (float): Tolérance numérique (ε)
        
        Returns:
            bool: True si équilibre de Nash, False sinon
        
        Lien TP (PricingAndBidding.pdf):
        Permet de vérifier la convergence du système.
        """
        for player in players:
            if not player.active:
                continue
            
            # Enchère actuelle du joueur
            current_bid = player.current_bid
            
            # Gain actuel
            current_payoff = player.compute_payoff(
                player.allocated_share,
                resource_owner.get_current_price()
            )
            
            # Calcul de la meilleure réponse
            aggregate_others = resource_owner.get_aggregate_bid_excluding(
                players, player.id
            )
            
            best_bid = player.best_response_bid(
                aggregate_others,
                resource_owner.get_current_price(),
                self.delta
            )
            
            # Vérification: Est-ce que la meilleure réponse est différente?
            if abs(best_bid - current_bid) > tolerance:
                # Le joueur peut améliorer → pas un NE
                return False
        
        # Aucun joueur ne peut améliorer → NE atteint
        return True
    
    def compute_convergence_distance(self, players, resource_owner):
        """
        Calcule la distance à l'équilibre
        
        Distance = Σ |zi - BR_i(s-i)|
        
        Args:
            players (list): Liste des joueurs
            resource_owner (ResourceOwner): Propriétaire
        
        Returns:
            float: Distance totale à l'équilibre
        
        Utilité:
        - Mesure la "proximité" de l'équilibre de Nash
        - = 0 ⟺ Équilibre de Nash atteint
        - Permet de tracer la convergence au fil du temps
        """
        total_distance = 0.0
        
        for player in players:
            if not player.active:
                continue
            
            aggregate_others = resource_owner.get_aggregate_bid_excluding(
                players, player.id
            )
            
            best_bid = player.best_response_bid(
                aggregate_others,
                resource_owner.get_current_price(),
                self.delta
            )
            
            distance = abs(player.current_bid - best_bid)
            total_distance += distance
        
        return total_distance
    
    def record_state(self, time_step, players, resource_owner):
        """
        Enregistre l'état actuel pour l'analyse
        
        Args:
            time_step (int): Temps actuel
            players (list): Joueurs
            resource_owner (ResourceOwner): Propriétaire
        """
        self.history['time'].append(time_step)
        
        sw = self.compute_social_welfare(players)
        self.history['social_welfare'].append(sw)
        
        is_ne = self.is_nash_equilibrium(players, resource_owner)
        self.history['is_nash'].append(is_ne)
        
        # Enregistrer les allocations
        allocations = {p.id: p.allocated_share for p in players if p.active}
        self.history['allocations'].append(allocations)
    
    def get_statistics(self):
        """
        Retourne les statistiques du mécanisme
        
        Returns:
            dict: Statistiques agrégées
        """
        if len(self.history['social_welfare']) == 0:
            return {
                'mean_social_welfare': 0,
                'convergence_time': None,
                'reached_nash': False
            }
        
        # Trouver le temps de convergence
        convergence_time = None
        for i, is_ne in enumerate(self.history['is_nash']):
            if is_ne:
                convergence_time = self.history['time'][i]
                break
        
        return {
            'mean_social_welfare': np.mean(self.history['social_welfare']),
            'final_social_welfare': self.history['social_welfare'][-1],
            'convergence_time': convergence_time,
            'reached_nash': any(self.history['is_nash'])
        }
    
    def __repr__(self):
        return f"KellyMechanism(δ={self.delta:.2f})"