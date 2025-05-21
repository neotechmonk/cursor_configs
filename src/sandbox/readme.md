# Pipeline Configuration Pattern

## Overview

The Pipeline Configuration Pattern is a flexible, configuration-driven approach to executing trading strategy steps. It allows you to define each step in a YAML configuration file, including its pure function, context inputs/outputs, and config mappings.

## Key Components

- **YAML Configuration:** Defines each step (e.g., `detect_trend`, `find_extreme`, `validate_pullback`, `check_fib`) with its pure function, context inputs/outputs, and config mappings.
- **Pipeline Config Loader:** Loads and validates the YAML configuration.
- **Strategy Step:** Executes a pure function, maps inputs from context/config, and stores outputs in the context.
- **Strategy Step Factory:** Creates strategy steps from configuration and validates function signatures.
- **Example Usage:** Demonstrates how to load the config, create steps, and execute them in order.

## Flow Summary

### Step 1: Load Configuration

The YAML file (`strategy_steps.yaml`) defines each step:

```yaml
steps:
  detect_trend:
    pure_function: "src.utils.get_trend"
    context_inputs: {}
    context_outputs:
      trend: "result.trend"
    config_mapping: {}

  find_extreme:
    pure_function: "src.utils.is_extreme_bar"
    context_inputs:
      trend: "context.trend"
    context_outputs:
      is_extreme: "result.is_extreme"
      extreme_bar_index: "result.extreme_bar_index"
    config_mapping:
      frame_size: "config.extreme.frame_size"

  validate_pullback:
    pure_function: "src.utils.is_bars_since_extreme_pivot_valid"
    context_inputs:
      major_swing_high_idx: "context.extreme_bar_index"
    context_outputs:
      bars_valid: "result.bars_valid"
    config_mapping:
      min_bars: "config.pullback.min_bars"
      max_bars: "config.pullback.max_bars"

  check_fib:
    pure_function: "src.utils.is_within_fib_extension"
    context_inputs:
      trend: "context.trend"
      ref_swing_start_idx: "context.extreme_bar_index"
      ref_swing_end_idx: "context.current_bar_index"
    context_outputs:
      fib_valid: "result.fib_valid"
    config_mapping:
      min_fib_extension: "config.fib.min_extension"
      max_fib_extension: "config.fib.max_extension"
```

### Step 2: Create Strategy Steps

The factory loads each step's configuration and creates a `StrategyStep` instance. It validates that the pure function's signature matches the required inputs.

### Step 3: Execute Steps

Each step is executed in order:

1. **`detect_trend`:**  
   Calls `get_trend(price_feed)` and stores the result as `trend` in the context.

2. **`find_extreme`:**  
   Calls `is_extreme_bar(price_feed, trend, frame_size)` and stores `is_extreme` and `extreme_bar_index` in the context.

3. **`validate_pullback`:**  
   Calls `is_bars_since_extreme_pivot_valid(price_feed, major_swing_high_idx, min_bars, max_bars)` and stores `bars_valid` in the context.

4. **`check_fib`:**  
   Calls `is_within_fib_extension(price_feed, trend, ref_swing_start_idx, ref_swing_end_idx, min_fib_extension, max_fib_extension)` and stores `fib_valid` in the context.

### Step 4: Handle Non-Dict Returns

If a pure function returns a non-dict (e.g., just a value), it is wrapped as `{"result": value}`. The `context_outputs` mapping in the YAML determines how this value is stored in the context.

## Current Issues and Next Steps

- **Issue:**  
  The factory expects the pure function to have a parameter named `extreme_bar_index`, but the function in `utils.py` uses `major_swing_high_idx`.

- **Solution:**  
  Add a mapping layer in the `StrategyStep` to rename context keys to function parameters when calling the pure function.

- **Next Steps:**
  1. Update `StrategyStep._execute_pure_function` to map context keys to function parameters.
  2. Re-run the example to verify everything works.

## Example Output (Expected)

When you run the example, you should see:

```
Executing step: detect_trend
Step detect_trend succeeded: Step completed successfully
Step output: {"trend": Direction.UP}

Executing step: find_extreme
Step find_extreme succeeded: Step completed successfully
Step output: {"is_extreme": True, "extreme_bar_index": <timestamp>}

Executing step: validate_pullback
Step validate_pullback succeeded: Step completed successfully
Step output: {"bars_valid": True}

Executing step: check_fib
Step check_fib succeeded: Step completed successfully
Step output: {"fib_valid": True}
```

## Tomorrow's Tasks

- Implement the mapping layer in `StrategyStep` to handle context key renaming.
- Re-run the example to verify the fix.
- Consider adding more error handling, validation, or tests.

# Strategy Sandbox

The sandbox provides a flexible way to execute strategy steps using pure functions and pipeline configuration.

## Context Mapping

The sandbox uses a mapping system to extract values from pure function results and store them in the strategy context. This allows for flexible data flow between steps.

### How Context Mapping Works

1. **Pure Function Returns Complex Data**
   ```python
   {
       "analysis": {
           "direction": "UP",
           "strength": "strong",
           "confidence": 0.95
       }
   }
   ```

2. **Context Outputs Mapping**
   ```python
   "context_outputs": {
       "trend": "analysis.direction",      # Stores "UP" as "trend"
       "trend_strength": "analysis.strength",  # Stores "strong" as "trend_strength"
       "confidence": "analysis.confidence"     # Stores 0.95 as "confidence"
   }
   ```

3. **What Happens**
   - The pure function returns a complex object with multiple values
   - The context_outputs mapping tells the sandbox:
     - Which values to extract from the result
     - What names to store them under in the context
   - Any values not mapped are ignored
   - The context can then be used by subsequent steps

### Example

```python
# Pure function returns complex data
def detect_trend(price_feed):
    return {
        "analysis": {
            "direction": "UP",
            "strength": "strong",
            "confidence": 0.95
        }
    }

# Step configuration maps specific values to context
step_config = {
    "context_inputs": {},
    "context_outputs": {
        "trend": "analysis.direction",
        "trend_strength": "analysis.strength"
    },
    "config_mapping": {}
}

# Create and execute step
step = StrategyStep(step_config, detect_trend)
result = step.evaluate(price_feed, context)

# Context now has:
# - context.get_latest_strategey_step_output_result("trend") == "UP"
# - context.get_latest_strategey_step_output_result("trend_strength") == "strong"
# Note: "confidence" is not stored in context as it wasn't mapped
```

### Benefits

1. **Flexibility**: Pure functions can return any structure, and the mapping system extracts what's needed
2. **Clarity**: The mapping makes it explicit what data is being passed between steps
3. **Decoupling**: Pure functions don't need to know about context structure
4. **Selective Storage**: Only map the values you need in the context

### Best Practices

1. Use clear, descriptive names in the context_outputs mapping
2. Document the structure of your pure function's return value
3. Only map values that will be used by subsequent steps
4. Consider using nested paths for complex data structures 

## Test Plan

### 1. StrategyStep Tests
- [x] `test_evaluate_success`: Basic successful execution with context mapping
- [x] `test_evaluate_with_empty_context`: Handle empty context gracefully
- [x] `test_evaluate_with_invalid_mapping`: Handle invalid context mappings
- [x] `test_evaluate_with_nested_paths`: Test deep nested path access
- [x] `test_evaluate_with_non_dict_result`: Handle non-dictionary return values
- [x] `test_evaluate_with_missing_required_inputs`: Handle missing required context inputs
- [x] `test_evaluate_with_config_mapping`: Test config value mapping
- [ ] `test_evaluate_with_pure_function_error`: Handle pure function exceptions

### 2. PipelineConfig Tests
- [ ] `test_load_valid_config`: Load and validate correct YAML config
- [ ] `test_load_invalid_config`: Handle invalid YAML format
- [ ] `test_load_missing_required_fields`: Handle missing required fields
- [ ] `test_load_invalid_step_config`: Handle invalid step configurations
- [ ] `test_load_duplicate_step_names`: Handle duplicate step names
- [ ] `test_load_invalid_function_paths`: Handle invalid function paths

### 3. StrategyStepFactory Tests
- [ ] `test_create_step_success`: Create step from valid config
- [ ] `test_create_step_invalid_function`: Handle invalid function paths
- [ ] `test_create_step_missing_function`: Handle missing function
- [ ] `test_create_step_signature_mismatch`: Handle function signature mismatches
- [ ] `test_create_step_invalid_mapping`: Handle invalid context/config mappings

### 4. Integration Tests
- [ ] `test_pipeline_execution`: Execute full pipeline with multiple steps
- [ ] `test_pipeline_context_flow`: Verify context values flow correctly between steps
- [ ] `test_pipeline_error_handling`: Handle errors in pipeline execution
- [ ] `test_pipeline_with_config`: Execute pipeline with configuration values
- [ ] `test_pipeline_with_complex_mappings`: Test complex context and config mappings

### Test Implementation Guidelines

1. **Test Organization**
   - Place all tests in `tests/sandbox/`
   - Use descriptive test names
   - Group related tests in test classes/functions

2. **Test Data**
   - Use fixtures for common test data
   - Create mock functions in `tests/mocks/`
   - Use realistic test scenarios

3. **Test Coverage**
   - Test happy paths
   - Test error cases
   - Test edge cases
   - Test configuration variations

4. **Best Practices**
   - Use pytest fixtures
   - Mock external dependencies
   - Clean up test resources
   - Document test scenarios

### Example Test Structure

```python
# tests/sandbox/test_pipeline_config.py
import pytest
from src.sandbox.pipeline_config import PipelineConfig

def test_load_valid_config():
    """Test loading a valid pipeline configuration."""
    config = PipelineConfig("path/to/valid_config.yaml")
    assert config.steps is not None
    assert "detect_trend" in config.steps

def test_load_invalid_config():
    """Test handling of invalid YAML configuration."""
    with pytest.raises(ValueError):
        PipelineConfig("path/to/invalid_config.yaml")
```

### Running Tests

```bash
# Run all sandbox tests
pytest tests/sandbox/

# Run specific test file
pytest tests/sandbox/test_strategy_step.py

# Run with coverage
pytest --cov=src.sandbox tests/sandbox/
``` 