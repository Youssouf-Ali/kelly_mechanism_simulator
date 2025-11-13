"""
Script pour lancer tous les tests unitaires
"""

import subprocess
import sys

tests = [
    "tests/test_player.py",
    "tests/test_resource_owner.py",
    "tests/test_kelly_mechanism.py",
    "tests/test_event_handler.py"
]

print("="*70)
print(" "*20 + "LANCEMENT DE TOUS LES TESTS")
print("="*70)

total_passed = 0
total_failed = 0

for test in tests:
    print(f"\n🧪 Lancement de {test}...")
    result = subprocess.run([sys.executable, test], capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {test} - RÉUSSI")
        # Compter les tests passés dans la sortie
        if "tests réussis" in result.stdout:
            import re
            match = re.search(r'(\d+) tests réussis', result.stdout)
            if match:
                total_passed += int(match.group(1))
    else:
        print(f"❌ {test} - ÉCHEC")
        total_failed += 1

print("\n" + "="*70)
print(f"RÉSULTAT GLOBAL : {total_passed} tests réussis, {total_failed} fichiers échoués")
print("="*70)

if total_failed == 0:
    print("\n🎉 TOUS LES TESTS PASSENT ! 🎉\n")
    sys.exit(0)
else:
    print("\n⚠️ Certains tests ont échoué.\n")
    sys.exit(1)
