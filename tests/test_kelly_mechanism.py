"""
Tests unitaires pour le composant KellyMechanism
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.player import Player
from src.resource_owner import ResourceOwner
from src.kelly_mechanism import KellyMechanism
import numpy as np


def test_kelly_mechanism_creation():
    """Test 1 : Création du mécanisme de Kelly"""
    print("\n" + "="*60)
    print("TEST 1 : Création du KellyMechanism")
    print("="*60)
    
    kelly = KellyMechanism(delta=0.15)
    
    assert kelly.delta == 0.15, "Delta incorrect"
    
    print(f"✓ Mécanisme créé : {kelly}")
    print("✓ Tous les attributs sont corrects")


def test_allocate_resources():
    """Test 2 : Allocation proportionnelle de Kelly"""
    print("\n" + "="*60)
    print("TEST 2 : Allocation Kelly")
    print("="*60)
    
    kelly = KellyMechanism(delta=0.1)
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1),
        Player(3, 120, 40, alpha=1)
    ]
    
    # Définir les enchères
    players[0].current_bid = 10.0
    players[1].current_bid = 20.0
    players[2].current_bid = 30.0
    
    allocations = kelly.allocate_resources(players)
    
    # Vérifier la formule : xi = zi / (Σzj + δ)
    total = 10.0 + 20.0 + 30.0 + 0.1
    expected = {
        1: 10.0 / total,
        2: 20.0 / total,
        3: 30.0 / total
    }
    
    for player_id in [1, 2, 3]:
        assert abs(allocations[player_id] - expected[player_id]) < 1e-6, \
            f"Allocation Player {player_id} incorrecte"
    
    print(f"✓ Enchères : [10, 20, 30]€")
    print(f"✓ Total : {total}€")
    print(f"✓ Allocations : {[f'{allocations[i]:.3f}' for i in [1,2,3]]}")
    
    # Vérifier que la somme est proche de 1
    total_allocated = sum(allocations.values())
    print(f"✓ Total alloué : {total_allocated:.3f}")


def test_compute_social_welfare():
    """Test 3 : Calcul du bien-être social"""
    print("\n" + "="*60)
    print("TEST 3 : Bien-être social")
    print("="*60)
    
    kelly = KellyMechanism(delta=0.1)
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1)
    ]
    
    players[0].current_bid = 20.0
    players[1].current_bid = 30.0
    
    # Allouer d'abord
    kelly.allocate_resources(players)
    
    # Calculer le bien-être
    sw = kelly.compute_social_welfare(players)
    
    # Vérification manuelle
    x1 = players[0].allocated_share
    x2 = players[1].allocated_share
    
    u1 = 50 * np.log(x1)
    u2 = 30 * np.log(x2)
    expected_sw = u1 + u2
    
    assert abs(sw - expected_sw) < 1e-6, f"SW incorrect : {sw} != {expected_sw}"
    
    print(f"✓ Allocations : {[p.allocated_share for p in players]}")
    print(f"✓ Bien-être social : {sw:.3f}")


def test_convergence_distance():
    """Test 4 : Distance à l'équilibre"""
    print("\n" + "="*60)
    print("TEST 4 : Distance de convergence")
    print("="*60)
    
    kelly = KellyMechanism(delta=0.1)
    owner = ResourceOwner(price_lambda=1.0, delta=0.1)
    
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1)
    ]
    
    # État initial loin de l'équilibre
    players[0].current_bid = 10.0
    players[1].current_bid = 15.0
    
    kelly.allocate_resources(players)
    
    distance = kelly.compute_convergence_distance(players, owner)
    
    print(f"✓ Enchères actuelles : {[p.current_bid for p in players]}")
    print(f"✓ Distance à l'équilibre : {distance:.3f}")
    
    # La distance doit être positive (pas à l'équilibre)
    assert distance > 0, "Distance devrait être positive"


def test_is_nash_equilibrium_false():
    """Test 5 : Vérifier qu'on n'est PAS à l'équilibre"""
    print("\n" + "="*60)
    print("TEST 5 : Nash Equilibrium (PAS atteint)")
    print("="*60)
    
    kelly = KellyMechanism(delta=0.1)
    owner = ResourceOwner(price_lambda=1.0, delta=0.1)
    
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1)
    ]
    
    # Enchères arbitraires
    players[0].current_bid = 10.0
    players[1].current_bid = 15.0
    
    kelly.allocate_resources(players)
    
    is_nash = kelly.is_nash_equilibrium(players, owner, tolerance=1e-3)
    
    assert is_nash == False, "Ne devrait PAS être un Nash Equilibrium"
    
    print(f"✓ Enchères : {[p.current_bid for p in players]}")
    print(f"✓ Nash atteint : {is_nash} (correct)")


def test_is_nash_equilibrium_true():
    """Test 6 : Forcer un équilibre et vérifier"""
    print("\n" + "="*60)
    print("TEST 6 : Nash Equilibrium (forcé)")
    print("="*60)
    
    kelly = KellyMechanism(delta=0.1)
    owner = ResourceOwner(price_lambda=1.0, delta=0.1)
    
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1)
    ]
    
    # Calculer directement les Best Responses mutuelles
    # (itération pour converger)
    for _ in range(20):
        for player in players:
            aggregate_others = owner.get_aggregate_bid_excluding(players, player.id)
            br = player.best_response_bid(aggregate_others, owner.price, kelly.delta)
            player.current_bid = br
    
    kelly.allocate_resources(players)
    
    is_nash = kelly.is_nash_equilibrium(players, owner, tolerance=1e-2)
    
    print(f"✓ Enchères convergées : {[f'{p.current_bid:.2f}' for p in players]}")
    print(f"✓ Nash atteint : {is_nash}")
    
    assert is_nash == True, "Devrait être un Nash Equilibrium"


def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*12 + "TESTS UNITAIRES KELLY MECHANISM" + " "*15 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        test_kelly_mechanism_creation,
        test_allocate_resources,
        test_compute_social_welfare,
        test_convergence_distance,
        test_is_nash_equilibrium_false,
        test_is_nash_equilibrium_true
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


if __name__ == "__main__":
    run_all_tests()