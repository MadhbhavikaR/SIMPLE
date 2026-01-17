#!/usr/bin/env python3
"""
Sanity Check Runner
===================

This module implements the SanityCheckRunner class that runs a chain of sanity checks.
"""

from typing import List
from .sanity_check import SanityCheck

class SanityCheckRunner:
    """
    Runs a chain of sanity checks and reports results.

    This class implements an extensible chain-of-responsibility pattern
    for running multiple sanity checks in sequence.
    """

    def __init__(self):
        self.checks: List[SanityCheck] = []

    def add_check(self, check: SanityCheck) -> 'SanityCheckRunner':
        """
        Add a sanity check to the chain.

        Args:
            check: SanityCheck instance to add

        Returns:
            self for method chaining
        """
        self.checks.append(check)
        return self

    def run_all_checks(self) -> tuple[bool, List[tuple[bool, str]]]:
        """
        Run all registered sanity checks.

        Returns:
            Tuple of (overall_success, individual_results) where
            overall_success is True only if all checks passed,
            and individual_results contains (success, message) for each check
        """
        if not self.checks:
            return (True, [])

        results = []
        overall_success = True

        print("🔍 Running Sanity Checks")
        print("=" * 50)

        for check in self.checks:
            print(f"📋 {check.name}: {check.description}")
            success, message = check.run()
            results.append((success, message))

            if success:
                print(f"   ✅ PASS: {message}")
            else:
                print(f"   ❌ FAIL: {message}")
                overall_success = False

            print()

        return (overall_success, results)
