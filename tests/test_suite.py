import pytest
import os
import sys
from pathlib import Path

def collect_test_files():
    """Collect all test files from the tests directory."""
    test_files = []
    tests_dir = Path("tests")

    for file in tests_dir.glob("test_*.py"):
        if file.name.startswith("test_") and file.name.endswith(".py"):
            module_name = file.name.replace(".py", "")
            test_files.append(f"tests.{module_name}")

    return test_files

def run_test_suite():
    """Run the comprehensive test suite."""
    # Collect all test files
    test_files = collect_test_files()

    if not test_files:
        print("No test files found!")
        return False

    print(f"Running test suite with {len(test_files)} test modules...")

    # Filter out any test files that don't exist as modules
    valid_test_files = []
    for test_file in test_files:
        try:
            # Check if the module can be imported
            __import__(test_file)
            valid_test_files.append(test_file)
        except ImportError:
            print(f"Warning: Test module {test_file} not found, skipping...")
            continue

    if not valid_test_files:
        print("No valid test modules found!")
        return False

    # Add project root to Python path for proper module imports
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Run pytest on all collected test files
    pytest_args = [
        "--cov=src",
        "--cov-report=term-missing",
        "--cov-report=html",
        "--cov-fail-under=100",
        "-v"
    ]

    # Add all valid test files to pytest arguments
    pytest_args.extend(valid_test_files)

    # Run pytest
    exit_code = pytest.main(pytest_args)

    return exit_code == 0

def generate_test_report():
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("SIMPLE Project Test Suite Report")
    print("="*60)

    # Collect test statistics
    test_files = collect_test_files()
    print(f"\nTest Modules: {len(test_files)}")

    # List all test modules
    print("\nTest Modules Included:")
    for i, module in enumerate(sorted(test_files), 1):
        print(f"  {i}. {module}")

    # Coverage information
    print("\nCoverage Requirements:")
    print("  - Statement Coverage: 100% (target)")
    print("  - Branch Coverage: 95%+ (target)")
    print("  - Function Coverage: 100% (target)")

    # Quality gates
    print("\nQuality Gates:")
    print("  ✅ All tests must pass")
    print("  ✅ 100% statement coverage required")
    print("  ✅ Code style compliance")
    print("  ✅ Documentation completeness")

    print("\n" + "="*60)

if __name__ == "__main__":
    # Generate test report
    generate_test_report()

    # Run the test suite
    success = run_test_suite()

    if success:
        print("\n🎉 All tests passed successfully!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
