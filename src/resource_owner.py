"""
Composant 4: EventHandler (Gestionnaire d'Événements)
Le moteur principal du simulateur événementiel
"""

import numpy as np
import heapq
from enum import Enum


class EventType(Enum):
    """
    Types d'événements dans le système
    
    Lien TP (PricingAndBidding.pdf, page 1):
    "The events that you need to simulate are the following:
    (1) Arrival and departures of players
    (2) Bidding action
    (3) Price adjustment"
    """
    ARRIVAL = 1      # Arrivée d'un joueur
    DEPARTURE = 2    # Départ d'un joueur
    BIDDING = 3      # Action d'enchère
    PRICE_ADJUST = 4 # Ajustement de prix


class Event:
    """
    Représente un événement dans le système
    """
    
    def __init__(self, event_time, event_type, player_id=None, data=None):
        """
        Args:
            event_time (float): Temps d'occurrence de l'événement
            event_type (EventType): Type d'événement
            player_id (int): ID du joueur concerné (si applicable)
            data (dict): Données supplémentaires
        """
        self.time = event_time
        self.type = event_type
        self.player_id = player_id
        self.data = data or {}
    
    def __lt__(self, other):
        """
        Comparaison pour la file de priorité (heap)
        Les événements sont triés par temps croissant
        """
        return self.time < other.time
    
    def __repr__(self):
        return f"Event(t={self.time:.2f}, type={self.type.name}, player={self.player_id})"


class EventHandler:
    """
    Gestionnaire d'événements pour le simulateur
    
    Lien TP (PricingAndBidding.pdf, page 1):
    "Component 4: Event handler. This is the main engine 
     of the event-driven simulator."
    """
    
    def __init__(self, players, resource_owner, kelly_mechanism, 
                 arrival_rate=0.5, departure_rate=0.3, bidding_rate=1.0):
        """
        Initialise le gestionnaire d'événements
        
        Args:
            players (list): Liste des joueurs
            resource_owner (ResourceOwner): Propriétaire de ressources
            kelly_mechanism (KellyMechanism): Mécanisme d'allocation
            arrival_rate (float): Taux d'arrivée A (arrivées/sec)
            departure_rate (float): Taux de départ B (départs/sec)
            bidding_rate (float): Fréquence des enchères (enchères/sec)
        
        Lien TP (PricingAndBidding.pdf, page 1):
        "Players arrive into the system according to a random process 
         with intensity A arrivals per second and leave the system 
         according to a random process with mean B departures per second. 
         To start with, use exponential random variables."
        """
        self.players = players
        self.resource_owner = resource_owner
        self.kelly_mechanism = kelly_mechanism
        
        # Taux des processus
        self.arrival_rate = arrival_rate      # λ_arrival (A)
        self.departure_rate = departure_rate  # λ_departure (B)
        self.bidding_rate = bidding_rate      # λ_bidding
        
        # File d'événements (heap = priority queue)
        self.event_queue = []
        
        # Temps actuel de la simulation
        self.current_time = 0.0
        
        # Politique d'enchère
        self.bidding_policy = "best_response"  # ou "gradient_descent"
        
        # Historique global
        self.history = {
            'time': [],
            'num_active_players': [],
            'total_bids': [],
            'social_welfare': [],
            'convergence_distance': [],
            'events': []
        }
    
    def schedule_event(self, event):
        """
        Ajoute un événement à la file
        
        Args:
            event (Event): Événement à planifier
        
        Utilise heapq (tas min) pour maintenir les événements
        triés par temps croissant.
        """
        heapq.heappush(self.event_queue, event)
    
    def generate_exponential_time(self, rate):
        """
        Génère un temps d'inter-arrivée selon une loi exponentielle
        
        Formule: T ~ Exp(λ)
        
        P(T > t) = e^(-λt)
        E[T] = 1/λ
        
        Args:
            rate (float): Taux λ du processus de Poisson
        
        Returns:
            float: Temps d'inter-arrivée
        
        Lien TP (PricingAndBidding.pdf):
        "use exponential random variables for every such event"
        
        Pourquoi exponentielle ?
        Les processus d'arrivée/départ suivent souvent des 
        processus de Poisson → inter-arrivées exponentielles.
        """
        return np.random.exponential(1.0 / rate)
    
    def initialize_events(self, simulation_time):
        """
        Initialise les événements au début de la simulation
        
        Args:
            simulation_time (float): Durée totale de la simulation
        """
        # Planifier les premières arrivées
        for player in self.players:
            if np.random.random() < 0.5:  # 50% chance de démarrer actif
                player.active = True
                # Planifier une première enchère
                first_bid_time = self.generate_exponential_time(self.bidding_rate)
                self.schedule_event(Event(first_bid_time, EventType.BIDDING, player.id))
            else:
                player.active = False
                # Planifier une arrivée future
                arrival_time = self.generate_exponential_time(self.arrival_rate)
                if arrival_time < simulation_time:
                    self.schedule_event(Event(arrival_time, EventType.ARRIVAL, player.id))
    
    def handle_arrival(self, event):
        """
        Gère l'arrivée d'un joueur
        
        ÉVÉNEMENT (1) du TP: "Arrival and departures of players"
        
        Args:
            event (Event): Événement d'arrivée
        """
        player = self._get_player(event.player_id)
        
        if player is None or player.active:
            return  # Joueur déjà actif ou inexistant
        
        # Le joueur entre dans le système
        player.enter_system(self.current_time)
        
        # Planifier son prochain départ
        departure_time = self.current_time + self.generate_exponential_time(
            self.departure_rate
        )
        self.schedule_event(Event(departure_time, EventType.DEPARTURE, player.id))
        
        # Planifier sa première enchère
        first_bid_time = self.current_time + self.generate_exponential_time(
            self.bidding_rate
        )
        self.schedule_event(Event(first_bid_time, EventType.BIDDING, player.id))
        
        print(f"[t={self.current_time:.2f}] Player {player.id} ARRIVED")
    
    def handle_departure(self, event):
        """
        Gère le départ d'un joueur
        
        ÉVÉNEMENT (1) du TP: "Arrival and departures of players"
        
        Args:
            event (Event): Événement de départ
        """
        player = self._get_player(event.player_id)
        
        if player is None or not player.active:
            return  # Joueur déjà parti ou inexistant
        
        # Le joueur quitte le système
        player.leave_system(self.current_time)
        
        # Planifier une réarrivée future (optionnel)
        rearival_time = self.current_time + self.generate_exponential_time(
            self.arrival_rate
        )
        self.schedule_event(Event(rearival_time, EventType.ARRIVAL, player.id))
        
        print(f"[t={self.current_time:.2f}] Player {player.id} DEPARTED")
    
    def handle_bidding(self, event):
        """
        Gère une action d'enchère
        
        ÉVÉNEMENT (2) du TP: "Bidding action: players generate 
        the events of bidding repeatedly based on their utility 
        and the strategy of other players."
        
        Args:
            event (Event): Événement d'enchère
        """
        player = self._get_player(event.player_id)
        
        if player is None or not player.active:
            return  # Joueur inactif
        
        # 1. Obtenir l'enchère agrégée des autres joueurs
        aggregate_others = self.resource_owner.get_aggregate_bid_excluding(
            self.players, player.id
        )
        
        # 2. Calculer la nouvelle enchère selon la politique
        if self.bidding_policy == "best_response":
            # POLITIQUE: Best Response (Lemma 1)
            new_bid = player.best_response_bid(
                aggregate_others,
                self.resource_owner.get_current_price(),
                self.kelly_mechanism.delta
            )
        
        elif self.bidding_policy == "gradient_descent":
            # POLITIQUE: Gradient Descent
            total_aggregate = self.resource_owner.get_aggregate_bid(self.players)
            new_bid = player.gradient_descent_update(
                learning_rate=0.1,
                aggregate_bid=total_aggregate,
                price_lambda=self.resource_owner.get_current_price(),
                delta=self.kelly_mechanism.delta
            )
        
        else:
            raise ValueError(f"Unknown bidding policy: {self.bidding_policy}")
        
        # 3. Mettre à jour l'enchère du joueur
        player.update_bid(new_bid, int(self.current_time))
        
        # 4. Planifier la prochaine enchère
        next_bid_time = self.current_time + self.generate_exponential_time(
            self.bidding_rate
        )
        self.schedule_event(Event(next_bid_time, EventType.BIDDING, player.id))
    
    def handle_price_adjustment(self, event):
        """
        Gère l'ajustement de prix
        
        ÉVÉNEMENT (3) du TP: "Price adjustment: events when 
        the price maker revise the price of the assigned resource. 
        Start with static prices."
        
        Args:
            event (Event): Événement d'ajustement de prix
        
        VERSION SIMPLE: Prix statique (pas d'ajustement)
        VERSION AVANCÉE: Prix dynamique basé sur la demande
        """
        # VERSION SIMPLE: Rien à faire (prix fixe)
        pass
        
        # VERSION AVANCÉE (exemple):
        # total_bid = self.resource_owner.get_aggregate_bid(self.players)
        # if total_bid > 100:  # Demande élevée
        #     new_price = self.resource_owner.get_current_price() * 1.1
        #     self.resource_owner.set_price(new_price, self.current_time)
    
    def allocate_and_record(self):
        """
        Effectue l'allocation Kelly et enregistre l'état
        
        Appelée périodiquement pour:
        1. Allouer les ressources selon Kelly
        2. Calculer les métriques
        3. Enregistrer l'historique
        """
        # 1. Allocation Kelly
        allocations = self.kelly_mechanism.allocate_resources(self.players)
        
        # 2. Calculer les métriques
        num_active = sum(1 for p in self.players if p.active)
        total_bid = self.resource_owner.get_aggregate_bid(self.players)
        social_welfare = self.kelly_mechanism.compute_social_welfare(self.players)
        convergence_dist = self.kelly_mechanism.compute_convergence_distance(
            self.players, self.resource_owner
        )
        
        # 3. Enregistrer
        self.history['time'].append(self.current_time)
        self.history['num_active_players'].append(num_active)
        self.history['total_bids'].append(total_bid)
        self.history['social_welfare'].append(social_welfare)
        self.history['convergence_distance'].append(convergence_dist)
        
        # 4. Enregistrer dans Kelly Mechanism
        self.kelly_mechanism.record_state(
            int(self.current_time), self.players, self.resource_owner
        )
    
    def run_simulation(self, simulation_time, record_interval=1.0, verbose=True):
        """
        Lance la simulation événementielle
        
        Args:
            simulation_time (float): Durée totale (en secondes simulées)
            record_interval (float): Fréquence d'enregistrement des métriques
            verbose (bool): Afficher les logs détaillés
        
        Returns:
            dict: Résultats de la simulation
        
        ALGORITHME:
        1. Initialiser les événements
        2. Tant que temps < simulation_time:
            a. Extraire le prochain événement
            b. Avancer le temps
            c. Traiter l'événement
            d. Enregistrer l'état (périodiquement)
        3. Retourner les résultats
        """
        print(f"\n{'='*60}")
        print(f"  SIMULATION START - Duration: {simulation_time}s")
        print(f"{'='*60}\n")
        
        # 1. Initialisation
        self.initialize_events(simulation_time)
        next_record_time = 0.0
        
        # 2. Boucle principale
        while self.event_queue and self.current_time < simulation_time:
            # a. Extraire le prochain événement
            event = heapq.heappop(self.event_queue)
            
            # b. Avancer le temps
            self.current_time = event.time
            
            if self.current_time > simulation_time:
                break
            
            # c. Traiter l'événement selon son type
            if event.type == EventType.ARRIVAL:
                self.handle_arrival(event)
            
            elif event.type == EventType.DEPARTURE:
                self.handle_departure(event)
            
            elif event.type == EventType.BIDDING:
                self.handle_bidding(event)
            
            elif event.type == EventType.PRICE_ADJUST:
                self.handle_price_adjustment(event)
            
            # d. Enregistrer l'état périodiquement
            if self.current_time >= next_record_time:
                self.allocate_and_record()
                next_record_time += record_interval
                
                if verbose and int(self.current_time) % 10 == 0:
                    self._print_status()
        
        # 3. Allocation finale
        self.allocate_and_record()
        
        print(f"\n{'='*60}")
        print(f"  SIMULATION END - Final time: {self.current_time:.2f}s")
        print(f"{'='*60}\n")
        
        # 4. Vérifier si Nash Equilibrium atteint
        is_nash = self.kelly_mechanism.is_nash_equilibrium(
            self.players, self.resource_owner
        )
        
        if is_nash:
            print("✓ Nash Equilibrium REACHED!")
        else:
            print("✗ Nash Equilibrium NOT reached")
        
        return self.get_simulation_results()
    
    def get_simulation_results(self):
        """
        Retourne les résultats de la simulation
        
        Returns:
            dict: Résultats complets
        """
        results = {
            'history': self.history,
            'players_stats': [p.get_statistics() for p in self.players],
            'resource_owner_stats': self.resource_owner.get_statistics(),
            'kelly_mechanism_stats': self.kelly_mechanism.get_statistics(),
            'final_time': self.current_time,
            'is_nash_equilibrium': self.kelly_mechanism.is_nash_equilibrium(
                self.players, self.resource_owner
            )
        }
        
        return results
    
    def _get_player(self, player_id):
        """
        Récupère un joueur par son ID
        
        Args:
            player_id (int): ID du joueur
        
        Returns:
            Player ou None
        """
        for player in self.players:
            if player.id == player_id:
                return player
        return None
    
    def _print_status(self):
        """
        Affiche le statut actuel de la simulation
        """
        num_active = sum(1 for p in self.players if p.active)
        total_bid = self.resource_owner.get_aggregate_bid(self.players)
        
        print(f"[t={self.current_time:6.1f}] "
              f"Active: {num_active}/{len(self.players)} | "
              f"Total Bid: {total_bid:7.2f} | "
              f"Events in queue: {len(self.event_queue)}")
    
    def __repr__(self):
        return (f"EventHandler(players={len(self.players)}, "
                f"time={self.current_time:.2f})")   