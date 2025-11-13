"""
Tests unitaires pour le composant EventHandler
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.player import Player
from src.resource_owner import ResourceOwner
from src.kelly_mechanism import KellyMechanism
from src.event_handler import EventHandler, Event, EventType
import numpy as np


def test_event_creation():
    """Test 1 : Création d'un événement"""
    print("\n" + "="*60)
    print("TEST 1 : Création d'événement")
    print("="*60)
    
    event = Event(event_time=5.5, event_type=EventType.ARRIVAL, player_id=1)
    
    assert event.time == 5.5, "Temps incorrect"
    assert event.type == EventType.ARRIVAL, "Type incorrect"
    assert event.player_id == 1, "Player ID incorrect"
    
    print(f"✓ Événement créé : {event}")


def test_event_handler_creation():
    """Test 2 : Création du gestionnaire d'événements"""
    print("\n" + "="*60)
    print("TEST 2 : Création EventHandler")
    print("="*60)
    
    players = [Player(i, 100, 50, alpha=1) for i in range(1, 4)]
    owner = ResourceOwner()
    kelly = KellyMechanism()
    
    handler = EventHandler(players, owner, kelly)
    
    assert len(handler.players) == 3, "Nombre de joueurs incorrect"
    assert handler.current_time == 0.0, "Temps initial incorrect"
    
    print(f"✓ Handler créé : {handler}")
    print(f"✓ {len(handler.players)} joueurs")


def test_generate_exponential_time():
    """Test 3 : Génération temps exponentiel"""
    print("\n" + "="*60)
    print("TEST 3 : Temps exponentiels")
    print("="*60)
    
    players = [Player(1, 100, 50, alpha=1)]
    owner = ResourceOwner()
    kelly = KellyMechanism()
    handler = EventHandler(players, owner, kelly)
    
    # Générer plusieurs temps
    times = [handler.generate_exponential_time(rate=1.0) for _ in range(100)]
    
    # Vérifier que tous sont positifs
    assert all(t > 0 for t in times), "Temps négatifs générés"
    
    # Vérifier la moyenne (devrait être proche de 1/rate = 1.0)
    mean_time = np.mean(times)
    
    print(f"✓ 100 temps générés")
    print(f"✓ Moyenne : {mean_time:.3f} (attendu ≈ 1.0)")
    
    # Tolérance large car c'est aléatoire
    assert 0.7 < mean_time < 1.3, f"Moyenne incorrecte : {mean_time}"


def test_schedule_event():
    """Test 4 : Planification d'événements"""
    print("\n" + "="*60)
    print("TEST 4 : Planification événements")
    print("="*60)
    
    players = [Player(1, 100, 50, alpha=1)]
    owner = ResourceOwner()
    kelly = KellyMechanism()
    handler = EventHandler(players, owner, kelly)
    
    # Planifier plusieurs événements
    handler.schedule_event(Event(5.0, EventType.ARRIVAL, 1))
    handler.schedule_event(Event(2.0, EventType.BIDDING, 1))
    handler.schedule_event(Event(8.0, EventType.DEPARTURE, 1))
    
    assert len(handler.event_queue) == 3, "Nombre d'événements incorrect"
    
    # Vérifier l'ordre (heap → plus petit en premier)
    first_event = handler.event_queue[0]
    assert first_event.time == 2.0, "Ordre incorrect dans la heap"
    
    print(f"✓ {len(handler.event_queue)} événements planifiés")
    print(f"✓ Prochain événement : t={first_event.time}")


def test_simple_simulation():
    """Test 5 : Simulation simple"""
    print("\n" + "="*60)
    print("TEST 5 : Simulation simple (5 secondes)")
    print("="*60)
    
    # 2 joueurs, simulation courte
    players = [
        Player(1, 100, 50, alpha=1),
        Player(2, 100, 30, alpha=1)
    ]
    owner = ResourceOwner(price_lambda=1.0, delta=0.1)
    kelly = KellyMechanism(delta=0.1)
    
    handler = EventHandler(
        players, owner, kelly,
        arrival_rate=0.1,
        departure_rate=0.1,
        bidding_rate=2.0  # Enchères fréquentes
    )
    
    # Lancer simulation courte
    results = handler.run_simulation(
        simulation_time=5.0,
        record_interval=1.0,
        verbose=False
    )
    
    assert results is not None, "Résultats manquants"
    assert 'history' in results, "Historique manquant"
    assert len(results['history']['time']) > 0, "Aucun enregistrement"
    
    print(f"✓ Simulation terminée")
    print(f"✓ Temps final : {results['final_time']:.2f}s")
    print(f"✓ Points enregistrés : {len(results['history']['time'])}")


def run_all_tests():
    """Lance tous les tests"""
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + " "*13 + "TESTS UNITAIRES EVENT HANDLER" + " "*16 + "█")
    print("█" + " "*58 + "█")
    print("█"*60)
    
    tests = [
        test_event_creation,
        test_event_handler_creation,
        test_generate_exponential_time,
        test_schedule_event,
        test_simple_simulation
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