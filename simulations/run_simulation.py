"""
Script principal de simulation du mécanisme de Kelly
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.player import Player
from src.resource_owner import ResourceOwner
from src.kelly_mechanism import KellyMechanism
from src.event_handler import EventHandler

import config
import numpy as np
import matplotlib.pyplot as plt


def create_players():
    """Crée les joueurs selon la configuration"""
    players = []
    for i in range(config.NUM_PLAYERS):
        player = Player(
            player_id=i+1,
            initial_budget=config.PLAYER_BUDGETS[i],
            valuation_weight=config.PLAYER_VALUATIONS[i],
            alpha=config.PLAYER_ALPHAS[i]
        )
        players.append(player)
    
    print(f"✓ {len(players)} joueurs créés")
    for p in players:
        print(f"  - Player {p.id}: budget={p.budget}€, a={p.valuation_weight}, α={p.alpha}")
    
    return players


def run_simulation():
    """Lance la simulation complète"""
    
    print("\n" + "="*70)
    print(" "*20 + "SIMULATION DU MÉCANISME DE KELLY")
    print("="*70)
    
    # 1. Créer les composants
    print("\n📦 INITIALISATION DES COMPOSANTS")
    print("-"*70)
    
    players = create_players()
    
    resource_owner = ResourceOwner(
        total_resource=1.0,
        price_lambda=config.PRICE_LAMBDA,
        delta=config.DELTA
    )
    print(f"✓ Propriétaire créé : λ={config.PRICE_LAMBDA}, δ={config.DELTA}")
    
    kelly_mechanism = KellyMechanism(delta=config.DELTA)
    print(f"✓ Mécanisme de Kelly créé")
    
    event_handler = EventHandler(
        players=players,
        resource_owner=resource_owner,
        kelly_mechanism=kelly_mechanism,
        arrival_rate=config.ARRIVAL_RATE,
        departure_rate=config.DEPARTURE_RATE,
        bidding_rate=config.BIDDING_RATE
    )
    event_handler.bidding_policy = config.BIDDING_POLICY
    print(f"✓ Gestionnaire d'événements créé")
    print(f"  - Politique : {config.BIDDING_POLICY}")
    print(f"  - Taux arrivées : {config.ARRIVAL_RATE}/s")
    print(f"  - Taux départs : {config.DEPARTURE_RATE}/s")
    print(f"  - Taux enchères : {config.BIDDING_RATE}/s")
    
    # 2. Lancer la simulation
    print("\n" + "="*70)
    print(" "*25 + "DÉBUT DE LA SIMULATION")
    print("="*70)
    
    results = event_handler.run_simulation(
        simulation_time=config.SIMULATION_TIME,
        record_interval=config.RECORD_INTERVAL,
        verbose=config.VERBOSE
    )
    
    # 3. Afficher les résultats
    print("\n" + "="*70)
    print(" "*28 + "RÉSULTATS FINAUX")
    print("="*70)
    
    print(f"\n📊 STATISTIQUES GLOBALES:")
    print(f"  - Temps final : {results['final_time']:.2f}s")
    print(f"  - Nash Equilibrium atteint : {'✓ OUI' if results['is_nash_equilibrium'] else '✗ NON'}")
    
    kelly_stats = results['kelly_mechanism_stats']
    print(f"  - Bien-être social moyen : {kelly_stats['mean_social_welfare']:.2f}")
    print(f"  - Bien-être social final : {kelly_stats['final_social_welfare']:.2f}")
    
    if kelly_stats['convergence_time'] is not None:
        print(f"  - Temps de convergence : {kelly_stats['convergence_time']:.2f}s")
    
    print(f"\n👥 STATISTIQUES DES JOUEURS:")
    for player_stats in results['players_stats']:
        print(f"\n  Player {player_stats['player_id']}:")
        print(f"    - Enchère moyenne : {player_stats['mean_bid']:.2f}€")
        print(f"    - Enchère finale : {player_stats['final_bid']:.2f}€")
        print(f"    - Allocation moyenne : {player_stats['mean_allocation']:.3f}")
        print(f"    - Gain total : {player_stats['total_payoff']:.2f}")
    
    owner_stats = results['resource_owner_stats']
    print(f"\n💰 PROPRIÉTAIRE DE RESSOURCES:")
    print(f"  - Revenu total : {owner_stats['total_revenue']:.2f}€")
    print(f"  - Revenu moyen : {owner_stats['mean_revenue']:.2f}€/période")
    
    return results


def visualize_results(results):
    """Visualise les résultats de la simulation"""
    
    print("\n" + "="*70)
    print(" "*26 + "GÉNÉRATION DES GRAPHIQUES")
    print("="*70)
    
    history = results['history']
    
    # Créer une figure avec 4 sous-graphiques
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    fig.suptitle('Résultats de la Simulation du Mécanisme de Kelly', fontsize=16, fontweight='bold')
    
    # 1. Évolution des enchères (CORRIGÉ)
    ax1 = axes[0, 0]
    
    # Récupérer les enchères depuis kelly_mechanism history
    kelly_history = results.get('kelly_mechanism_stats', {})
    
    # Alternative : tracer les enchères moyennes dans le temps
    if len(history['time']) > 0:
        # Créer des données synthétiques pour visualiser la convergence
        times = history['time']
        num_active = history['num_active_players']
        total_bids = history['total_bids']
        
        # Enchère moyenne par joueur actif
        avg_bid_per_player = [total_bids[i] / max(num_active[i], 1) 
                              for i in range(len(times))]
        
        ax1.plot(times, avg_bid_per_player, 
                label='Enchère moyenne par joueur', 
                color='purple', linewidth=2)
        ax1.set_xlabel('Temps (s)')
        ax1.set_ylabel('Enchère moyenne (€)')
        ax1.set_title('Évolution de l\'Enchère Moyenne')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    else:
        ax1.text(0.5, 0.5, 'Données insuffisantes', 
                ha='center', va='center', transform=ax1.transAxes)
    
    # 2. Distance de convergence
    ax2 = axes[0, 1]
    if len(history['convergence_distance']) > 0:
        ax2.plot(history['time'], history['convergence_distance'], 
                color='red', linewidth=2)
        ax2.set_xlabel('Temps (s)')
        ax2.set_ylabel('Distance')
        ax2.set_title('Distance au Nash Equilibrium')
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
    
    # 3. Bien-être social
    ax3 = axes[1, 0]
    if len(history['social_welfare']) > 0:
        ax3.plot(history['time'], history['social_welfare'], 
                color='green', linewidth=2)
        ax3.set_xlabel('Temps (s)')
        ax3.set_ylabel('Bien-être Social')
        ax3.set_title('Évolution du Bien-être Social')
        ax3.grid(True, alpha=0.3)
    
    # 4. Nombre de joueurs actifs
    ax4 = axes[1, 1]
    if len(history['num_active_players']) > 0:
        ax4.plot(history['time'], history['num_active_players'], 
                color='blue', linewidth=2, drawstyle='steps-post')
        ax4.set_xlabel('Temps (s)')
        ax4.set_ylabel('Nombre de joueurs actifs')
        ax4.set_title('Joueurs Actifs dans le Système')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim([0, config.NUM_PLAYERS + 0.5])
    
    plt.tight_layout()
    
    # Sauvegarder
    output_file = '../results/simulation_results.png'
    os.makedirs('../results', exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Graphiques sauvegardés : {output_file}")
    
    plt.show()


if __name__ == "__main__":
    # Lancer la simulation
    results = run_simulation()
    
    # Visualiser
    visualize_results(results)
    
    print("\n" + "="*70)
    print(" "*25 + "🎉 SIMULATION TERMINÉE 🎉")
    print("="*70 + "\n")