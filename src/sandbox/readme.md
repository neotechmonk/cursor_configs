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