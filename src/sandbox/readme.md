# Strategy Sandbox

## Overview

The Strategy Sandbox provides a flexible, configuration-driven approach to executing trading strategy steps. It uses Pydantic models for configuration and direct evaluation via `StepEvaluator`.

## Key Components

- **StrategyStepTemplate:** A Pydantic model that defines a single strategy step, including its pure function, context inputs/outputs, and config mappings.
- **StrategyStepRegistry:** A registry of all available strategy step templates, loaded from a YAML configuration file.
- **StepEvaluator:** Evaluates a single strategy step using a pure function and configuration. It handles function signature validation, argument preparation, step execution, result mapping, and context updates.

## Flow Summary

### Step 1: Define Strategy Step Template

Define each step using `StrategyStepTemplate`:

```python
step_config = StrategyStepTemplate(
    pure_function="mock_get_trend",
    context_inputs={},
    context_outputs={"trend": "direction"},
    config_mapping={}
)
```

### Step 2: Create Step Evaluator

Create a `StepEvaluator` instance with the step template and pure function:

```python
evaluator = StepEvaluator(step_config, mock_get_trend)
```

### Step 3: Execute Step

Execute the step with a price feed and execution context:

```python
result = evaluator.evaluate(price_feed, context)
```

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
step_config = StrategyStepTemplate(
    pure_function="detect_trend",
    context_inputs={},
    context_outputs={
        "trend": "analysis.direction",
        "trend_strength": "analysis.strength"
    },
    config_mapping={}
)

# Create and execute step
evaluator = StepEvaluator(step_config, detect_trend)
result = evaluator.evaluate(price_feed, context)

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

### 1. StrategyStepTemplate Tests
- [x] `test_strategy_step_template_instantiation`: Basic instantiation with valid data
- [x] `test_strategy_step_template_with_complex_mappings`: Test complex context and config mappings
- [x] `test_strategy_step_template_empty_function`: Handle empty function names
- [x] `test_strategy_step_template_whitespace_function`: Handle whitespace in function names
- [x] `test_strategy_step_template_default_values`: Test default values for optional fields
- [x] `test_strategy_step_template_immutability`: Ensure templates are immutable

### 2. StrategyStepRegistry Tests
- [x] `test_load_valid_registry`: Load and validate correct YAML config
- [x] `test_load_invalid_registry_missing_field`: Handle missing required fields
- [x] `test_load_invalid_registry_empty_function`: Handle empty function names
- [x] `test_registry_properties`: Test registry properties (step names, templates)

### 3. StepEvaluator Tests
- [x] `test_step_evaluator_success`: Basic successful execution with context mapping
- [x] `test_step_evaluator_error`: Handle errors and return failure result
- [x] `test_step_evaluator_signature_validation`: Validate function signature on initialization
- [x] `test_step_evaluator_invalid_signature`: Handle function signature mismatches
- [x] `test_evaluate_success`: Test successful evaluation with nested outputs
- [x] `test_evaluate_with_empty_context`: Handle empty context inputs gracefully
- [x] `test_evaluate_with_missing_required_inputs`: Handle missing required context inputs
- [x] `test_evaluate_with_config_mapping`: Test config value mapping
- [x] `test_evaluate_with_pure_function_error`: Handle exceptions from the pure function

### 4. Integration Tests
- [x] `test_pipeline_step_integration`: Execute a single step with direct instantiation

### Additional Testing Scenarios (Not Yet Implemented)

1. **Complex Error Handling**
   - Test handling of nested exceptions in pure functions
   - Test recovery mechanisms after errors

2. **Advanced Integration Scenarios**
   - Test multi-step pipelines with complex data flow
   - Test parallel execution of steps

3. **Edge Cases**
   - Test with extremely large datasets
   - Test with empty or malformed inputs

4. **Performance Testing**
   - Benchmark execution time for large datasets
   - Test memory usage under load

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

### Running Tests

```bash
# Run all sandbox tests
pytest tests/sandbox/

# Run specific test file
pytest tests/sandbox/test_strategy_step_template.py

# Run with coverage
pytest --cov=src.sandbox tests/sandbox/
``` 