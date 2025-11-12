"""
Tests unitaires pour le composant Player
"""

import sys
import os

# Ajouter le dossier parent au path pour importer src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.player import Player
import numpy as np


def test_player_creation():
    """Test 1 : Création d'un joueur"""
    print("\n" + "="*60)
    print("TEST 1 : Création d'un joueur")
    print("="*60)
    
    player = Player(player_id=1, initial_budget=100, valuation_weight=50, alpha=1)
    
    assert player.id == 1, "ID incorrect"
    assert player.budget == 100, "Budget incorrect"
    assert player.valuation_weight == 50, "Valorisation incorrecte"
    assert player.alpha == 1, "Alpha incorrect"
    assert player.active == True, "Joueur devrait être actif"
    assert player.current_bid == 0.001, "Enchère initiale incorrecte"
    
    print(f"✓ Joueur créé : {player}")
    print("✓ Tous les attributs sont corrects")


def test_compute_utility():
    """Test 2 : Calcul d'utilité pour différents α"""
    print("\n" + "="*60)
    print("TEST 2 : Calcul d'utilité")
    print("="*60)
    
    # Test α = 0 (efficacité maximale)
    player0 = Player(1, 100, 50, alpha=0)
    utility0 = player0.compute_utility(0.5)
    expected0 = 50 * 0.5  # U = a × x
    assert abs(utility0 - expected0) < 1e-6, f"Utilité α=0 incorrecte : {utility0} != {expected0}"
    print(f"✓ α=0 : U(0.5) = {utility0:.3f} (attendu: {expected0:.3f})")
    
    # Test α = 1 (proportional fairness)
    player1 = Player(1, 100, 50, alpha=1)
    utility1 = player1.compute_utility(0.5)
    expected1 = 50 * np.log(0.5)  # U = a × log(x)
    assert abs(utility1 - expected1) < 1e-6, f"Utilité α=1 incorrecte : {utility1} != {expected1}"
    print(f"✓ α=1 : U(0.5) = {utility1:.3f} (attendu: {expected1:.3f})")
    
    # Test α = 2 (minimum potential delay)
    player2 = Player(1, 100, 50, alpha=2)
    utility2 = player2.compute_utility(0.5)
    expected2 = 50 * (-1/0.5)  # U = a × (-1/x)
    assert abs(utility2 - expected2) < 1e-6, f"Utilité α=2 incorrecte : {utility2} != {expected2}"
    print(f"✓ α=2 : U(0.5) = {utility2:.3f} (attendu: {expected2:.3f})")
    
    # Test cas limite : share = 0
    utility_zero = player1.compute_utility(0)
    assert utility_zero == -np.inf, "Utilité pour share=0 devrait être -inf"
    print(f"✓ Cas limite : U(0) = -∞")


def test_compute_payoff():
    """Test 3 : Calcul du gain (payoff)"""
    print("\n" + "="*60)
    print("TEST 3 : Calcul du gain (payoff)")
    print("="*60)
    
    player = Player(1, 100, 50, alpha=1)
    player.current_bid = 25.0
    
    share = 0.25
    price = 1.0
    
    payoff = player.compute_payoff(share, price)
    
    # Vérification manuelle
    utility = 50 * np.log(0.25)
    cost = 1.0 * 25.0
    expected_payoff = utility - cost
    
    assert abs(payoff - expected_payoff) < 1e-6, f"Payoff incorrect : {payoff} != {expected_payoff}"
    
    print(f"✓ Part reçue : {share}")
    print(f"✓ Enchère : {player.current_bid}€")
    print(f"✓ Utilité : {utility:.3f}")
    print(f"✓ Coût : {cost:.3f}")
    print(f"✓ Gain net : {payoff:.3f}")


def test_best_response_bid():
    """Test 4 : Calcul Best Response"""
    print("\n" + "="*60)
    print("TEST 4 : Best Response")
    print("="*60)
    
    player = Player(1, 100, 50, alpha=1)
    
    aggregate_others = 50.0
    price = 1.0
    delta = 0.1
    
    best_bid = player.best_response_bid(aggregate_others, price, delta)
    
    # Vérification : doit être entre epsilon et budget
    assert best_bid >= 0.001, "Best Response trop petite"
    assert best_bid <= player.budget, "Best Response dépasse le budget"
    
    print(f"✓ Enchères des autres : {aggregate_others}€")
    print(f"✓ Prix : {price}€")
    print(f"✓ Delta : {delta}")
    print(f"✓ Best Response calculée : {best_bid:.3f}€")
    
    # Vérification de la formule pour α=1
    s_minus_i = aggregate_others + delta
    a = player.valuation_weight
    discriminant = s_minus_i**2 + 4 * a * s_minus_i / price
    expected_br = (-s_minus_i + np.sqrt(discriminant)) / 2
    
    assert abs(best_bid - expected_br) < 1e-6, "Formule BR incorrecte"
    print(f"✓ Formule vérifiée : BR = {expected_br:.3f}€")


def test_gradient_descent_update():
    """Test 5 : Gradient Descent"""
    print("\n" + "="*60)
    print("TEST 5 : Gradient Descent")
    print("="*60)
    
    player = Player(1, 100, 50, alpha=1)
    player.current_bid = 25.0
    
    aggregate_bid = 75.0
    learning_rate = 0.1
    price = 1.0
    delta = 0.1
    
    new_bid = player.gradient_descent_update(
        aggregate_bid=aggregate_bid,
        learning_rate=learning_rate,
        price_lambda=price,
        delta=delta
    )
    
    # Vérification : doit être entre epsilon et budget
    assert new_bid >= 0.001, "Nouvelle enchère trop petite"
    assert new_bid <= player.budget, "Nouvelle enchère dépasse le budget"
    
    print(f"✓ Enchère actuelle : {player.current_bid}€")
    print(f"✓ Enchère totale : {aggregate_bid}€")
    print(f"✓ Learning rate : {learning_rate}")
    print(f"✓ Nouvelle enchère (GD) : {new_bid:.3f}€")
    print(f"✓ Variation : {new_bid - player.current_bid:+.3f}€")


def test_update_bid_and_allocation():
    """Test 6 : Mise à jour enchère et allocation"""
    print("\n" + "="*60)
    print("TEST 6 : Mise à jour et allocation")
    print("="*60)
    
    player = Player(1, 100, 50, alpha=1)
    
    # Mise à jour enchère
    player.update_bid(25.0, time_step=0)
    assert player.current_bid == 25.0, "Enchère non mise à jour"
    assert len(player.history['bids']) == 1, "Historique enchères incorrect"
    print(f"✓ Enchère mise à jour : {player.current_bid}€")
    
    # Réception allocation
    player.receive_allocation(share=0.25, price_lambda=1.0)
    assert player.allocated_share == 0.25, "Part non allouée"
    assert len(player.history['allocations']) == 1, "Historique allocations incorrect"
    assert len(player.history['utilities']) == 1, "Historique utilités incorrect"
    assert len(player.history['payoffs']) == 1, "Historique payoffs incorrect"
    print(f"✓ Part reçue : {player.allocated_share}")
    print(f"✓ Historiques mis à jour")


def test_enter_leave_system():
    """Test 7 : Entrée/Sortie du système"""
    print("\n" + "="*60)
    print("TEST 7 : Entrée/Sortie système")
    print("="*60)
    
    player = Player(1, 100, 50, alpha=1)
    
    # Sortie
    player.leave_system(time_step=5)
    assert player.active == False, "Joueur devrait être inactif"
    print(f"✓ Joueur sorti à t=5")
    
    # Entrée
    player.enter_system(time_step=10)
    assert player.active == True, "Joueur devrait être actif"
    print(f"✓ Joueur entré à t=10")


def test_get_statistics():
    """Test 8 : Statistiques du joueur"""
    print("\n" + "="*60)
    print("TEST 8 : Statistiques")
    print("="*60)
    
    player = Player(1, 100, 50, alpha=1)
    
    # Simuler quelques itérations
    player.update_bid(20.0, 0)
    player.receive_allocation(0.20, 1.0)
    
    player.update_bid(25.0, 1)
    player.receive_allocation(0.25, 1.0)
    
    player.update_bid(30.0, 2)
    player.receive_allocation(0.30, 1.0)
    
    stats = player.get_statistics()
    
    assert stats['player_id'] == 1, "ID incorrect dans stats"
    assert abs(stats['mean_bid'] - 25.0) < 1e-6, "Enchère moyenne incorrecte"
    assert abs(stats['mean_allocation'] - 0.25) < 1e-6, "Allocation moyenne incorrecte"
    assert stats['final_bid'] == 30.0, "Enchère finale incorrecte"
    
    print(f"✓ Enchère moyenne : {stats['mean_bid']:.2f}€")
    print(f"✓ Allocation moyenne : {stats['mean_allocation']:.3f}")
    print(f"✓ Gain total : {stats['total_payoff']:.2f}")
    print(f"✓ Enchère finale : {stats['final_bid']:.2f}€")


def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*15 + "TESTS UNITAIRES PLAYER" + " "*21 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        test_player_creation,
        test_compute_utility,
        test_compute_payoff,
        test_best_response_bid,
        test_gradient_descent_update,
        test_update_bid_and_allocation,
        test_enter_leave_system,
        test_get_statistics
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"\n❌ ÉCHEC : {test.__name__}")
            print(f"   Erreur : {e}")
            failed += 1
        except Exception as e:
            print(f"\n❌ ERREUR : {test.__name__}")
            print(f"   Exception : {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RÉSULTAT : {passed} tests réussis, {failed} tests échoués")
    print("="*60)
    
    if failed == 0:
        print("\n" + "🎉"*20)
        print("✅ TOUS LES TESTS PASSENT !")
        print("🎉"*20 + "\n")
    else:
        print("\n⚠️ Certains tests ont échoué. Vérifiez le code.\n")


if __name__ == "__main__":
    run_all_tests()