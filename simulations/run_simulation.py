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
    print("\n INITIALISATION DES COMPOSANTS")
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
    
    print(f"\n STATISTIQUES GLOBALES:")
    print(f"  - Temps final : {results['final_time']:.2f}s")
    print(f"  - Nash Equilibrium atteint : {'✓ OUI' if results['is_nash_equilibrium'] else '✗ NON'}")
    
    kelly_stats = results['kelly_mechanism_stats']
    print(f"  - Bien-être social moyen : {kelly_stats['mean_social_welfare']:.2f}")
    print(f"  - Bien-être social final : {kelly_stats['final_social_welfare']:.2f}")
    
    if kelly_stats['convergence_time'] is not None:
        print(f"  - Temps de convergence : {kelly_stats['convergence_time']:.2f}s")
    
    print(f"\n STATISTIQUES DES JOUEURS:")
    for player_stats in results['players_stats']:
        print(f"\n  Player {player_stats['player_id']}:")
        print(f"    - Enchère moyenne : {player_stats['mean_bid']:.2f}€")
        print(f"    - Enchère finale : {player_stats['final_bid']:.2f}€")
        print(f"    - Allocation moyenne : {player_stats['mean_allocation']:.3f}")
        print(f"    - Gain total : {player_stats['total_payoff']:.2f}")
    
    owner_stats = results['resource_owner_stats']
    print(f"\n PROPRIÉTAIRE DE RESSOURCES:")
    print(f"  - Revenu total : {owner_stats['total_revenue']:.2f}€")
    print(f"  - Revenu moyen : {owner_stats['mean_revenue']:.2f}€/période")
    
    return results


def visualize_results(results):
    """Visualise les résultats de la simulation (VERSION ÉTENDUE)"""
    
    print("\n" + "="*70)
    print(" "*26 + "GÉNÉRATION DES GRAPHIQUES")
    print("="*70)
    
    history = results['history']
    
    # Créer une figure avec 6 sous-graphiques (2x3)
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Résultats de la Simulation du Mécanisme de Kelly', 
                 fontsize=16, fontweight='bold')
    
    # Couleurs pour chaque joueur
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    # ==================== GRAPHIQUE 1 : Enchère moyenne ====================
    ax1 = axes[0, 0]
    if len(history['time']) > 0:
        times = history['time']
        num_active = history['num_active_players']
        total_bids = history['total_bids']
        
        avg_bid_per_player = [total_bids[i] / max(num_active[i], 1) 
                              for i in range(len(times))]
        
        ax1.plot(times, avg_bid_per_player, 
                label='Enchère moyenne par joueur', 
                color='purple', linewidth=2)
        ax1.set_xlabel('Temps (s)', fontsize=10)
        ax1.set_ylabel('Enchère moyenne (€)', fontsize=10)
        ax1.set_title('Évolution de l\'Enchère Moyenne', fontsize=11, fontweight='bold')
        ax1.legend(fontsize=9)
        ax1.grid(True, alpha=0.3)
    
    # ==================== GRAPHIQUE 2 : Distance Nash ====================
    ax2 = axes[0, 1]
    if len(history['convergence_distance']) > 0:
        ax2.plot(history['time'], history['convergence_distance'], 
                color='red', linewidth=2)
        ax2.set_xlabel('Temps (s)', fontsize=10)
        ax2.set_ylabel('Distance', fontsize=10)
        ax2.set_title('Distance au Nash Equilibrium', fontsize=11, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.set_yscale('log')
    
    # ==================== GRAPHIQUE 3 : Bien-être social ====================
    ax3 = axes[0, 2]
    if len(history['social_welfare']) > 0:
        ax3.plot(history['time'], history['social_welfare'], 
                color='green', linewidth=2)
        ax3.set_xlabel('Temps (s)', fontsize=10)
        ax3.set_ylabel('Bien-être Social', fontsize=10)
        ax3.set_title('Évolution du Bien-être Social', fontsize=11, fontweight='bold')
        ax3.grid(True, alpha=0.3)
    
    # ==================== GRAPHIQUE 4 : Joueurs actifs ====================
    ax4 = axes[1, 0]
    if len(history['num_active_players']) > 0:
        ax4.plot(history['time'], history['num_active_players'], 
                color='blue', linewidth=2, drawstyle='steps-post')
        ax4.set_xlabel('Temps (s)', fontsize=10)
        ax4.set_ylabel('Nombre de joueurs actifs', fontsize=10)
        ax4.set_title('Joueurs Actifs dans le Système', fontsize=11, fontweight='bold')
        ax4.grid(True, alpha=0.3)
        ax4.set_ylim([0, config.NUM_PLAYERS + 0.5])
    
    # ==================== GRAPHIQUE 5 : Enchères individuelles (NOUVEAU) ====================
    ax5 = axes[1, 1]
    players_found = False
    if 'players' in results:
        for i, player in enumerate(results['players']):
            if hasattr(player, 'history') and len(player.history['time']) > 0:
                if 'bids' in player.history and len(player.history['bids']) > 0:
                    # S'assurer que les longueurs correspondent
                    min_len = min(len(player.history['time']), len(player.history['bids']))
                    if min_len > 0:
                        ax5.plot(player.history['time'][:min_len], 
                                player.history['bids'][:min_len],
                                label=f'Player {player.id}',
                                color=colors[i % len(colors)],
                                marker='o', markersize=3, linewidth=1.5)
                        players_found = True
    
    if players_found:
        ax5.set_xlabel('Temps (s)', fontsize=10)
        ax5.set_ylabel('Enchère (€)', fontsize=10)
        ax5.set_title('Enchères Individuelles', fontsize=11, fontweight='bold')
        ax5.legend(fontsize=8, loc='best')
        ax5.grid(True, alpha=0.3)
    else:
        ax5.text(0.5, 0.5, 'Données insuffisantes', 
                ha='center', va='center', transform=ax5.transAxes, fontsize=12)
        ax5.set_title('Enchères Individuelles', fontsize=11, fontweight='bold')
    
    # ==================== GRAPHIQUE 6 : Utilités individuelles (NOUVEAU) ====================
    ax6 = axes[1, 2]
    utilities_found = False
    if 'players' in results:
        for i, player in enumerate(results['players']):
            if hasattr(player, 'history') and len(player.history['time']) > 0:
                if 'utilities' in player.history and len(player.history['utilities']) > 0:
                    # S'assurer que les longueurs correspondent
                    min_len = min(len(player.history['time']), len(player.history['utilities']))
                    if min_len > 0:
                        ax6.plot(player.history['time'][:min_len], 
                                player.history['utilities'][:min_len],
                                label=f'Player {player.id} (a={player.valuation_weight})',
                                color=colors[i % len(colors)],
                                marker='^', markersize=3, linewidth=1.5)
                        utilities_found = True
    
    if utilities_found:
        ax6.set_xlabel('Temps (s)', fontsize=10)
        ax6.set_ylabel('Utilité', fontsize=10)
        ax6.set_title('Utilités Individuelles (α=1)', fontsize=11, fontweight='bold')
        ax6.legend(fontsize=8, loc='best')
        ax6.grid(True, alpha=0.3)
        ax6.axhline(y=0, color='black', linestyle='--', linewidth=0.8, alpha=0.5)
    else:
        ax6.text(0.5, 0.5, 'Données insuffisantes', 
                ha='center', va='center', transform=ax6.transAxes, fontsize=12)
        ax6.set_title('Utilités Individuelles', fontsize=11, fontweight='bold')
    
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
    print(" "*25 + " SIMULATION TERMINÉE ")
    print("="*70 + "\n")