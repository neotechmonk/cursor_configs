# Strategy Configuration

This directory contains configuration files for the trading strategy system.

## File Structure

- `strategy_steps.yaml`: Defines the sequence of steps and their configurations for strategy execution

## YAML Structure

The `strategy_steps.yaml` file follows this structure:

```yaml
steps:
  step_name:
    function: "path.to.function"  # Function to execute
    input_params_map:             # Map function parameters to context values
      param1: "context_value1"
      param2: "context_value2"
    return_map:                   # Map function return values
      result1: "_"               # "_" means use direct return value
      result2: "new_name"        # Otherwise, rename the return value
    config_mapping:              # Map configuration parameters
      config1: "config_value1"

config_mapping:                  # Global configuration parameters
  param1: "value1"
  param2: "value2"
```

### Field Descriptions

- **function**: The full path to the function to execute
- **input_params_map**: Maps function parameter names to their source values in the execution context
- **return_map**: Maps function return values:
  - Use `"_"` to use the direct return value
  - Use a new name to rename the return value
- **config_mapping**: Maps configuration parameter names to their source values

### Example

```yaml
steps:
  detect_trend:
    function: "src.utils.get_trend"
    input_params_map: {}  # No input parameters needed
    return_map:
      trend: "_"  # Direct value from function return

  find_extreme:
    function: "src.utils.is_extreme_bar"
    input_params_map:
      trend: "trend"  # Source determined by execution layer
    return_map:
      is_extreme: "_"  # Direct value from function return

config_mapping:
  frame_size: "frame_size"
  min_bars: "min_bars"
  max_bars: "max_bars"
```

## Best Practices

1. Keep function names consistent with their module paths
2. Use descriptive names for steps and parameters
3. Document any special requirements or dependencies in comments
4. Use `"_"` for direct return values to maintain clarity
5. Keep configuration mappings simple and avoid deep nesting 