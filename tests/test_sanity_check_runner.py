import pytest
from unittest.mock import MagicMock
from src.simple.services.sanity_check_runner import SanityCheckRunner
from src.simple.services.sanity_check import SanityCheck

class TestSanityCheckRunner:
    """Test cases for the SanityCheckRunner class."""

    @pytest.fixture
    def sanity_check_runner(self):
        """Create a SanityCheckRunner instance for testing."""
        return SanityCheckRunner()

    def test_init(self, sanity_check_runner):
        """Test SanityCheckRunner initialization."""
        assert sanity_check_runner.checks == []

    def test_add_check(self, sanity_check_runner):
        """Test adding a sanity check."""
        mock_check = MagicMock(spec=SanityCheck)
        result = sanity_check_runner.add_check(mock_check)
        assert result is sanity_check_runner
        assert len(sanity_check_runner.checks) == 1
        assert sanity_check_runner.checks[0] == mock_check

    def test_run_all_checks(self, sanity_check_runner):
        """Test running all sanity checks."""
        # Add mock checks
        mock_check1 = MagicMock(spec=SanityCheck)
        mock_check1.run.return_value = (True, "Check 1 passed")

        mock_check2 = MagicMock(spec=SanityCheck)
        mock_check2.run.return_value = (False, "Check 2 failed")

        sanity_check_runner.add_check(mock_check1)
        sanity_check_runner.add_check(mock_check2)

        # Run all checks
        result, messages = sanity_check_runner.run_all_checks()
        assert result is False  # Overall result should be False if any check fails
        assert len(messages) == 2
        assert messages[0][0] is True
        assert messages[0][1] == "Check 1 passed"
        assert messages[1][0] is False
        assert messages[1][1] == "Check 2 failed"

    def test_run_all_checks_all_pass(self, sanity_check_runner):
        """Test running all sanity checks when all pass."""
        # Add mock checks that all pass
        mock_check1 = MagicMock(spec=SanityCheck)
        mock_check1.run.return_value = (True, "Check 1 passed")

        mock_check2 = MagicMock(spec=SanityCheck)
        mock_check2.run.return_value = (True, "Check 2 passed")

        sanity_check_runner.add_check(mock_check1)
        sanity_check_runner.add_check(mock_check2)

        # Run all checks
        result, messages = sanity_check_runner.run_all_checks()
        assert result is True  # Overall result should be True if all checks pass
        assert len(messages) == 2
        assert all(msg[0] is True for msg in messages)
