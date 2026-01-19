import pytest
from src.simple.services.sanity_check import SanityCheck

class TestSanityCheck:
    """Test cases for the SanityCheck base class."""

    class ConcreteSanityCheck(SanityCheck):
        """Concrete implementation for testing."""

        def run(self) -> tuple[bool, str]:
            return True, "Test passed"

    @pytest.fixture
    def sanity_check(self):
        """Create a concrete SanityCheck instance for testing."""
        return self.ConcreteSanityCheck()

    def test_init(self, sanity_check):
        """Test SanityCheck initialization."""
        assert sanity_check.name == "Concrete Sanity Check"
        assert sanity_check.description == "Test sanity check"

    def test_run(self, sanity_check):
        """Test running the sanity check."""
        result, message = sanity_check.run()
        assert result is True
        assert message == "Test passed"

    def test_run_abstract(self):
        """Test that abstract run method raises NotImplementedError."""
        abstract_check = SanityCheck("Abstract", "Abstract check")
        with pytest.raises(NotImplementedError):
            abstract_check.run()
