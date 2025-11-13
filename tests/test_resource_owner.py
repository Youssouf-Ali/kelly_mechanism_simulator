"""
Tests unitaires pour le composant ResourceOwner
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.player import Player
from src.resource_owner import ResourceOwner
import numpy as np


def test_resource_owner_creation():
    """Test 1 : Création du propriétaire de ressources"""
    print("\n" + "="*60)
    print("TEST 1 : Création du ResourceOwner")
    print("="*60)
    
    owner = ResourceOwner(total_resource=1.0, price_lambda=1.5, delta=0.1)
    
    assert owner.total_resource == 1.0, "Ressource totale incorrecte"
    assert owner.price == 1.5, "Prix incorrect"
    assert owner.delta == 0.1, "Delta incorrect"
    
    print(f"✓ Propriétaire créé : {owner}")
    print("✓ Tous les attributs sont corrects")


def test_get_aggregate_bid():
    """Test 2 : Calcul enchère agrégée totale"""
    print("\n" + "="*60)
    print("TEST 2 : Enchère agrégée totale")
    print("="*60)
    
    owner = ResourceOwner()
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1),
        Player(3, 120, 40, alpha=1)
    ]
    
    # Définir les enchères
    players[0].current_bid = 10.0
    players[1].current_bid = 20.0
    players[2].current_bid = 30.0
    
    total = owner.get_aggregate_bid(players)
    expected = 10.0 + 20.0 + 30.0
    
    assert abs(total - expected) < 1e-6, f"Total incorrect : {total} != {expected}"
    
    print(f"✓ Enchères : {[p.current_bid for p in players]}")
    print(f"✓ Total : {total}€")


def test_get_aggregate_bid_excluding():
    """Test 3 : Enchère agrégée sans un joueur"""
    print("\n" + "="*60)
    print("TEST 3 : Enchère agrégée (excluant un joueur)")
    print("="*60)
    
    owner = ResourceOwner()
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1),
        Player(3, 120, 40, alpha=1)
    ]
    
    players[0].current_bid = 10.0
    players[1].current_bid = 20.0
    players[2].current_bid = 30.0
    
    # Exclure Player 2
    aggregate_without_2 = owner.get_aggregate_bid_excluding(players, exclude_id=2)
    expected = 10.0 + 30.0  # Player 1 + Player 3
    
    assert abs(aggregate_without_2 - expected) < 1e-6, f"Incorrect : {aggregate_without_2} != {expected}"
    
    print(f"✓ Total sans Player 2 : {aggregate_without_2}€")
    print(f"✓ Attendu : {expected}€")


def test_communicate_aggregate_to_players():
    """Test 4 : Communication des enchères agrégées"""
    print("\n" + "="*60)
    print("TEST 4 : Communication aux joueurs")
    print("="*60)
    
    owner = ResourceOwner()
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1),
        Player(3, 120, 40, alpha=1)
    ]
    
    players[0].current_bid = 10.0
    players[1].current_bid = 20.0
    players[2].current_bid = 30.0
    
    aggregates = owner.communicate_aggregate_to_players(players)
    
    # Vérifications
    assert 1 in aggregates, "Player 1 manquant"
    assert 2 in aggregates, "Player 2 manquant"
    assert 3 in aggregates, "Player 3 manquant"
    
    assert abs(aggregates[1] - 50.0) < 1e-6, "Agrégat Player 1 incorrect"  # 20+30
    assert abs(aggregates[2] - 40.0) < 1e-6, "Agrégat Player 2 incorrect"  # 10+30
    assert abs(aggregates[3] - 30.0) < 1e-6, "Agrégat Player 3 incorrect"  # 10+20
    
    print(f"✓ Agrégats communiqués : {aggregates}")


def test_compute_revenue():
    """Test 5 : Calcul du revenu"""
    print("\n" + "="*60)
    print("TEST 5 : Calcul du revenu")
    print("="*60)
    
    owner = ResourceOwner(price_lambda=2.0)
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1)
    ]
    
    players[0].current_bid = 15.0
    players[1].current_bid = 25.0
    
    revenue = owner.compute_revenue(players, time_step=0)
    expected = 2.0 * (15.0 + 25.0)  # prix × enchères
    
    assert abs(revenue - expected) < 1e-6, f"Revenu incorrect : {revenue} != {expected}"
    
    print(f"✓ Prix : {owner.price}€")
    print(f"✓ Enchères : {[p.current_bid for p in players]}")
    print(f"✓ Revenu : {revenue}€")


def test_inactive_players():
    """Test 6 : Gestion des joueurs inactifs"""
    print("\n" + "="*60)
    print("TEST 6 : Joueurs inactifs")
    print("="*60)
    
    owner = ResourceOwner()
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 80, 30, alpha=1),
        Player(3, 120, 40, alpha=1)
    ]
    
    players[0].current_bid = 10.0
    players[1].current_bid = 20.0
    players[2].current_bid = 30.0
    
    # Player 2 devient inactif
    players[1].active = False
    
    total = owner.get_aggregate_bid(players)
    expected = 10.0 + 30.0  # Seulement Player 1 et 3
    
    assert abs(total - expected) < 1e-6, f"Total incorrect : {total} != {expected}"
    
    print(f"✓ Player 2 inactif")
    print(f"✓ Total (actifs seulement) : {total}€")


def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*12 + "TESTS UNITAIRES RESOURCE OWNER" + " "*16 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        test_resource_owner_creation,
        test_get_aggregate_bid,
        test_get_aggregate_bid_excluding,
        test_communicate_aggregate_to_players,
        test_compute_revenue,
        test_inactive_players
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