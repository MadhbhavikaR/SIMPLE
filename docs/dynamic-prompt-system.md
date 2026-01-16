# Dynamic Prompt System Documentation

## Overview

The SIMPLE project now features a dynamic prompt system that eliminates hard-coded field definitions and makes prompt collection fully driven by service configuration files. This system provides:

1. **Template-Based Prompt Extraction**: Prompts are extracted from Jinja2 templates based on variable usage
2. **Dynamic Validation**: Required prompts are validated against template requirements
3. **Secret Detection**: Automatic detection of secret variables from `/run/secrets/` references
4. **Alternative-Specific Prompts**: Different prompts for different service configuration alternatives

## Key Changes

### 1. Deprecated PASSWORD Type

The `PASSWORD` prompt type has been deprecated and replaced with `SECRET`. All existing `PASSWORD` types should be migrated to `SECRET`.

**Before:**
```yaml
prompts:
  - name: SOME_PASSWORD
    type:
      enum:
        - PASSWORD  # Deprecated
    required: true
```

**After:**
```yaml
prompts:
  - name: SOME_SECRET
    type:
      enum:
        - SECRET  # Use SECRET instead
    required: true
```

### 2. Dynamic Prompt Extraction

The system now scans service templates to determine which prompts are actually needed, rather than prompting for all defined prompts.

**How it works:**
1. Load the selected alternative template (e.g., `default.yaml.jinja`)
2. Extract variable names from:
   - Jinja2 variables: `{{ VAR_NAME }}`
   - Environment variables: `{{ ${VAR_NAME} }}`
   - Secret file references: `/run/secrets/VAR_NAME`
3. Filter the `about.yaml` prompts to only those used in the template
4. Prompt the user only for the required variables

### 3. Required Prompt Validation

A new sanity check validates that all prompts marked as `required: true` in `about.yaml` are actually used in the corresponding template.

**Example:**
```yaml
# about.yaml
prompts:
  - name: REQUIRED_VAR
    description: "This variable is required"
    type:
      enum: ["STRING"]
    required: true  # Must be used in template

# default.yaml.jinja
service:
  environment:
    - REQUIRED_VAR={{ REQUIRED_VAR }}  # ✅ Used - validation passes
```

## Implementation Details

### Core Components

1. **`UnifiedServiceStrategy.get_required_prompts_for_alternative()`**
   - Extracts prompts based on template variable usage
   - Supports Jinja2 variables, environment variables, and secret references

2. **`RequiredPromptsSanityCheck`**
   - Validates that required prompts are present in templates
   - Runs during service initialization
   - Provides clear error messages for missing prompts

3. **`DockerEngine._get_service_secrets()`**
   - Updated to use only `SECRET` type (no longer checks for `PASSWORD`)
   - Dynamically detects secrets from `about.yaml`

### File Changes

**Modified Files:**
- `src/simple/core/prompt.py`: Deprecated `PASSWORD` enum
- `src/simple/engine.py`: Updated secret handling and prompt extraction
- `src/simple/services/unified_service.py`: Enhanced prompt extraction logic
- `src/simple/services/sanity_checks.py`: Added required prompt validation

**New Files:**
- `tests/test_dynamic_prompts.py`: Comprehensive test suite

## Migration Guide

### For Service Developers

1. **Update `about.yaml` files:**
   - Replace all `PASSWORD` types with `SECRET`
   - Ensure `required: true` is set appropriately

2. **Review templates:**
   - Ensure all required prompts are used in templates
   - Use consistent variable naming
   - For secrets, use `/run/secrets/VAR_NAME` pattern

3. **Test the changes:**
   - Run the new test suite: `pytest tests/test_dynamic_prompts.py`
   - Verify prompt extraction works for all alternatives

### Example Migration

**Before:**
```yaml
# templates/services/example/about.yaml
prompts:
  - name: API_KEY
    description: "API key for service"
    type:
      enum: ["PASSWORD"]  # Old type
    required: true

# templates/services/example/default.yaml.jinja
service:
  environment:
    - API_KEY={{ API_KEY }}  # Direct usage
```

**After:**
```yaml
# templates/services/example/about.yaml
prompts:
  - name: API_KEY
    description: "API key for service"
    type:
      enum: ["SECRET"]  # New type
    required: true

# templates/services/example/default.yaml.jinja
service:
  environment:
    - API_KEY_FILE=/run/secrets/API_KEY  # Better: use Docker secrets
```

## Benefits

1. **Reduced User Prompts**: Users only see prompts relevant to their selected configuration
2. **Improved Security**: Secrets are consistently handled via Docker secrets
3. **Better Validation**: Early detection of configuration errors
4. **Maintainability**: Centralized prompt definitions in `about.yaml`
5. **Flexibility**: Different alternatives can have different prompt requirements

## Testing

The system includes comprehensive tests covering:

- Prompt extraction from various template patterns
- Secret variable detection
- Required prompt validation
- Multiple alternative scenarios
- Edge cases and error conditions

Run tests with:
```bash
PYTHONPATH=/mnt/Storage/Projects/SIMPLE/src python -m pytest tests/test_dynamic_prompts.py -v
```

## Troubleshooting

**Issue: Missing required prompts**
- **Symptom**: Sanity check fails with "Missing required prompts"
- **Solution**: Ensure all `required: true` prompts are used in the template

**Issue: Prompts not appearing**
- **Symptom**: Expected prompts don't appear during service selection
- **Solution**: Check that the variable is used in the selected template

**Issue: Secret detection failing**
- **Symptom**: Secrets not being handled as secrets
- **Solution**: Use `/run/secrets/VAR_NAME` pattern in templates

## Future Enhancements

1. **Conditional Prompts**: Support for prompts that appear based on other selections
2. **Prompt Groups**: Logical grouping of related prompts
3. **Default Values**: Support for default values in prompt definitions
4. **Validation Patterns**: Enhanced validation for different prompt types

## Conclusion

The dynamic prompt system represents a significant improvement in the SIMPLE project's configuration management. By making prompts fully dynamic and template-driven, we've eliminated hard-coded field definitions and created a more flexible, maintainable, and user-friendly configuration system.
