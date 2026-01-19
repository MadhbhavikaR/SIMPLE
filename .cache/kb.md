# Knowledge Base

This file records resolved issues, solutions, and lessons learned to prevent rediscovering the same solutions.

## Format

Each entry should include:
- **File**: Path to the file
- **Location**: Line number or function name
- **Issue**: Description of the problem
- **Solution**: How it was resolved
- **References**: Links, commands, or related resources

## Entries

### Example Entry

**File**: `src/simple/engine.py`
**Location**: Line 42, `process_config()` function
**Issue**: Configuration validation was failing for nested objects
**Solution**: Added recursive validation with proper type checking
**References**:
- Related ADR: `docs/architecture/adr/003-config-validation.md`
- Test case: `tests/config_validation_test.py`
- Command: `uv run pytest tests/config_validation_test.py -v`

### Template for New Entries

**File**:
**Location**:
**Issue**:
**Solution**:
**References**:

### Actual Example Entry

File: src/simple/config/config_reader.py
Location: Line 42, validate_config() function
Issue: Configuration validation was failing for nested objects
Solution: Added recursive validation with proper type checking
References:
- Test: tests/config_validation_test.py
- Command: uv run pytest tests/config_validation_test.py -v
