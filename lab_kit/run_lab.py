"""
run_lab.py
----------
INTEGRATION ARENA scoreboard.

Run this instead of pytest directly to see your score, level by level:

    python run_lab.py
"""

import pytest

LEVELS = [
    ("test_level1_basic_order", "Level 1 - Basic Sync Integration", 30),
    ("test_level2_idempotency", "Level 2 - Idempotency Key", 20),
    ("test_level2_retry_recovers", "Level 2 - Retry With Backoff", 10),
    ("test_level3_async_notification", "Level 3 - Async Notification", 20),
    ("test_level4_circuit_breaker", "Level 4 - Circuit Breaker (BOSS)", 20),
]

results = {}


class ScoreCollector:
    def pytest_runtest_logreport(self, report):
        if report.when == "call":
            name = report.nodeid.split("::")[-1]
            results[name] = report.outcome


def main():
    print("Running Integration Arena autograder...\n")
    pytest.main(["-q", "--no-header", "test_lab_autograder.py"], plugins=[ScoreCollector()])

    print("\n" + "=" * 54)
    print("           INTEGRATION ARENA — SCOREBOARD")
    print("=" * 54)

    total, max_total = 0, 0
    for test_name, label, points in LEVELS:
        max_total += points
        outcome = results.get(test_name)
        if outcome == "passed":
            total += points
            mark = f"+{points:>2} pts   [PASS]"
        else:
            mark = f"  0 pts   [FAIL]"
        print(f"{label:<38}{mark}")

    print("-" * 54)
    print(f"TOTAL SCORE: {total} / {max_total}")

    if total == max_total:
        rank = "SYSTEM ARCHITECT — every integration pattern implemented."
    elif total >= max_total * 0.7:
        rank = "INTEGRATION ENGINEER — solid work, a few gaps remain."
    elif total >= max_total * 0.4:
        rank = "JUNIOR DEVELOPER — the happy path works, reliability needs work."
    else:
        rank = "INTERN — start at Level 1 and work your way up."
    print(f"RANK: {rank}")
    print("=" * 54)


if __name__ == "__main__":
    main()
