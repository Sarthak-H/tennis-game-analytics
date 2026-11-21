"""
Test runner script.
Executes test suites and prints a structured test execution report.
Works with both pytest and direct Python execution.
"""

import sys
import os
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

def run_all_tests():
    print("=" * 70)
    print("RUNNING TENNIS GAME ANALYTICS TEST SUITE")
    print("=" * 70)

    total_passed = 0
    total_failed = 0

    # 1. API tests
    print("\n--- 1. Testing API Client & Modules (test_api.py) ---")
    try:
        from tests.test_api import (
            test_client_init,
            test_missing_api_key_raises,
            test_successful_request,
            test_unauthorized_error,
            test_fetch_modules
        )
        test_client_init()
        print("  [PASS] test_client_init")
        test_missing_api_key_raises()
        print("  [PASS] test_missing_api_key_raises")
        test_successful_request()
        print("  [PASS] test_successful_request")
        test_unauthorized_error()
        print("  [PASS] test_unauthorized_error")
        test_fetch_modules()
        print("  [PASS] test_fetch_modules")
        total_passed += 5
    except Exception as exc:
        print(f"  [FAIL] API Tests failed: {exc}")
        total_failed += 1

    # 2. Processing tests
    print("\n--- 2. Testing Data Processing & Extraction (test_processing.py) ---")
    try:
        from tests.test_processing import (
            test_process_competitions_valid,
            test_process_competitions_empty_and_corrupt,
            test_process_complexes_valid,
            test_process_rankings_valid
        )
        test_process_competitions_valid()
        print("  [PASS] test_process_competitions_valid")
        test_process_competitions_empty_and_corrupt()
        print("  [PASS] test_process_competitions_empty_and_corrupt")
        test_process_complexes_valid()
        print("  [PASS] test_process_complexes_valid")
        test_process_rankings_valid()
        print("  [PASS] test_process_rankings_valid")
        total_passed += 4
    except Exception as exc:
        print(f"  [FAIL] Processing Tests failed: {exc}")
        total_failed += 1

    # 3. Database tests
    print("\n--- 3. Testing Database Relational CRUD & Analytics (test_database.py) ---")
    try:
        from tests.test_database import test_schema_and_upsert_operations
        test_schema_and_upsert_operations()
        print("  [PASS] test_schema_and_upsert_operations (Schema, Upserts, KPIs, Competitions, Rankings, Venues)")
        total_passed += 1
    except Exception as exc:
        print(f"  [FAIL] Database Tests failed: {exc}")
        total_failed += 1

    print("\n" + "=" * 70)
    print(f"TEST RESULTS: {total_passed} PASSED, {total_failed} FAILED")
    print("=" * 70)

    if total_failed > 0:
        sys.exit(1)
    else:
        print("ALL TESTS PASSED SUCCESSFULLY! Ready for deployment.\n")

if __name__ == "__main__":
    run_all_tests()

