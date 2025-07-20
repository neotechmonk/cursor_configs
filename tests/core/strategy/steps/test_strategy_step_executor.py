

import pytest

from core.strategy.steps.executor import bind_params, execute, map_results
from core.strategy.steps.model import StrategyStepDefinition
from core.strategy.steps.protocol import ResultProtocol


# Mock functions for testing
def mock_callable_config_param_only(config1) -> ResultProtocol:
    return {"return_mapping": "return_value"}


def mock_callable_rt_param_only(rt1) -> ResultProtocol:
    return {"return_mapping": "return_value"}


def mock_callable(config1, rt1) -> ResultProtocol:
    return {"return_mapping": "return_value"}


def create_test_step(id: str, function_path: str, input_bindings: dict, output_bindings: dict):
    """Helper function to create StrategyStepDefinition for testing with validation disabled."""
    step = StrategyStepDefinition(
        id=id,
        function_path=function_path,
        input_bindings=input_bindings,
        output_bindings=output_bindings
    )
    # Disable validation for testing
    # step._skip_validation = True
    return step


def test_binding_only_config_params_with_return():
    mock_fn = mock_callable_config_param_only 
    step_def = create_test_step(
        id="mock",
        function_path=f"{mock_fn.__module__}.{mock_fn.__name__}",
        input_bindings={
            "config1": StrategyStepDefinition.InputBinding(source="config", mapping="config1_map")
        },
        output_bindings={
            "return_value": StrategyStepDefinition.OutputBinding(mapping="return_mapping")
        }
    )

    sample_config_data = {"config1_map": "config1_value"}

    bound_params = bind_params(step_def, config_data=sample_config_data)

    assert list(bound_params.keys()) == ["config1"]
    assert list(bound_params.values()) == ["config1_value"]
    assert bound_params["config1"] == "config1_value" 


def test_binding_only_runtime_params_with_return():
    mock_fn = mock_callable_rt_param_only 
    step_def = create_test_step(
        id="mock",
        function_path=f"{mock_fn.__module__}.{mock_fn.__name__}",
        input_bindings={
            "rt1": StrategyStepDefinition.InputBinding(source="runtime", mapping="rt1_map")
        },
        output_bindings={
            "return_value": StrategyStepDefinition.OutputBinding(mapping="return_mapping")
        }
    )

    sample_runtime_data = {"rt1_map": "rt1_value"}

    bound_params = bind_params(step_def, runtime_data=sample_runtime_data)

    assert list(bound_params.keys()) == ["rt1"]
    assert list(bound_params.values()) == ["rt1_value"]
    assert bound_params["rt1"] == "rt1_value" 
    

def test_binding_both_config_params_and_runtime_params_with_return():
    mock_fn = mock_callable    
    step_def = create_test_step(
        id="mock",
        function_path=f"{mock_fn.__module__}.{mock_fn.__name__}",
        input_bindings={
            "config1": StrategyStepDefinition.InputBinding(source="config", mapping="config1_map"),
            "rt1": StrategyStepDefinition.InputBinding(source="runtime", mapping="rt1_map")
        },
        output_bindings={
            "return_value": StrategyStepDefinition.OutputBinding(mapping="return_mapping")
        }
    )

    sample_config_data = {"config1_map": "config1_value"}
    sample_runtime_data = {"rt1_map": "rt1_value"}

    bound_params = bind_params(step_def, 
                              config_data=sample_config_data, 
                              runtime_data=sample_runtime_data)

    assert list(bound_params.keys()) == ["config1", "rt1"]
    assert list(bound_params.values()) == ["config1_value", "rt1_value"]
    assert bound_params["config1"] == "config1_value" 
    assert bound_params["rt1"] == "rt1_value" 
    

# Happy path tests for execute() function
def test_execute_with_keyword_arguments():
    """Test execute() with a function that accepts keyword arguments."""
    
    def test_function(a: int, b: str, c: bool = True) -> dict:
        return {"sum": a + len(b), "flag": c, "message": f"{a}_{b}"}
    
    params = {"a": 5, "b": "hello", "c": False}
    result = execute(test_function, params)
    
    expected = {"sum": 10, "flag": False, "message": "5_hello"}
    assert result == expected


def test_execute_with_positional_arguments():
    """Test execute() with a function that only accepts positional arguments."""
    
    def test_function(a, b, c):
        return {"sum": a + b + c, "product": a * b * c}
    
    params = {"a": 2, "b": 3, "c": 4}
    result = execute(test_function, params)
    
    expected = {"sum": 9, "product": 24}
    assert result == expected


def test_execute_with_mixed_argument_types():
    """Test execute() with a function that has both required and optional parameters."""
    
    def test_function(x, y, z=10, w="default"):
        return {"x": x, "y": y, "z": z, "w": w, "total": x + y + z}
    
    params = {"x": 1, "y": 2, "z": 5, "w": "custom"}
    result = execute(test_function, params)
    
    expected = {"x": 1, "y": 2, "z": 5, "w": "custom", "total": 8}
    assert result == expected


def test_execute_with_no_parameters():
    """Test execute() with a function that takes no parameters."""
    
    def test_function():
        return {"status": "success", "message": "no params"}
    
    params = {}
    result = execute(test_function, params)
    
    expected = {"status": "success", "message": "no params"}
    assert result == expected


def test_execute_with_complex_return_value():
    """Test execute() with a function that returns complex data structures."""
    
    def test_function(items, multiplier):
        return {
            "processed_items": [item * multiplier for item in items],
            "count": len(items),
            "total": sum(items) * multiplier,
            "metadata": {
                "multiplier": multiplier,
                "original_items": items
            }
        }
    
    params = {"items": [1, 2, 3, 4], "multiplier": 2}
    result = execute(test_function, params)
    
    expected = {
        "processed_items": [2, 4, 6, 8],
        "count": 4,
        "total": 20,
        "metadata": {
            "multiplier": 2,
            "original_items": [1, 2, 3, 4]
        }
    }
    assert result == expected


def test_execute_with_string_parameters():
    """Test execute() with string parameters."""
    
    def test_function(name, greeting="Hello"):
        return {"message": f"{greeting}, {name}!", "name_length": len(name)}
    
    params = {"name": "Alice", "greeting": "Hi"}
    result = execute(test_function, params)
    
    expected = {"message": "Hi, Alice!", "name_length": 5}
    assert result == expected


def test_execute_with_boolean_parameters():
    """Test execute() with boolean parameters."""
    
    def test_function(enabled, verbose=False, debug=False):
        return {
            "enabled": enabled,
            "verbose": verbose,
            "debug": debug,
            "status": "active" if enabled else "disabled"
        }
    
    params = {"enabled": True, "verbose": True, "debug": False}
    result = execute(test_function, params)
    
    expected = {
        "enabled": True,
        "verbose": True,
        "debug": False,
        "status": "active"
    }
    assert result == expected


def test_execute_with_list_parameters():
    """Test execute() with list parameters."""
    
    def test_function(numbers, operations):
        results = []
        for op in operations:
            if op == "sum":
                results.append(sum(numbers))
            elif op == "max":
                results.append(max(numbers))
            elif op == "min":
                results.append(min(numbers))
        
        return {
            "numbers": numbers,
            "operations": operations,
            "results": results
        }
    
    params = {"numbers": [10, 20, 30, 40], "operations": ["sum", "max", "min"]}
    result = execute(test_function, params)
    
    expected = {
        "numbers": [10, 20, 30, 40],
        "operations": ["sum", "max", "min"],
        "results": [100, 40, 10]
    }
    assert result == expected
    
# test_map_resultsv2.py
def test_map_resultsv2_no_output_bindings():
    raw_results = {"a": 1, "b": 2}
    mapped = map_results(output_bindings={}, raw_results=raw_results)
    assert mapped == raw_results


def test_map_resultsv2_explicit_mappings():
    raw_results = {"a": "X", "b": "Y"}
    output_bindings = {"a": "x", "b": "y"}

    mapped = map_results(output_bindings=output_bindings, raw_results=raw_results)
    assert mapped == {"x": "X", "y": "Y"}


def test_map_resultsv2_none_mapping_keeps_key():
    raw_results = {"res": 42, "info": "something"}
    output_bindings = {"res": None}

    mapped = map_results(output_bindings=output_bindings, raw_results=raw_results)
    assert mapped == {"res": 42, "info": "something"}


def test_map_resultsv2_mixed_mappings():
    raw_results = {"a": "X", "b": "Y", "c": "Z"}
    output_bindings = {"a": "x", "b": None}

    mapped = map_results(output_bindings=output_bindings, raw_results=raw_results)
    assert mapped == {"x": "X", "b": "Y", "c": "Z"}


def test_map_resultsv2_raises_on_collision():
    raw_results = {"a": 1, "x": 999}
    output_bindings = {"a": "x"}  # This would overwrite existing key

    with pytest.raises(ValueError, match="would overwrite existing key 'x'"):
        map_results(output_bindings=output_bindings, raw_results=raw_results)


def test_map_resultsv2_missing_keys_become_none():
    raw_results = {"a": 10}
    output_bindings = {"a": "x", "b": "y"}  # 'b' is missing in raw_results

    mapped = map_results(output_bindings=output_bindings, raw_results=raw_results)
    assert mapped == {"x": 10, "y": None}


def test_map_resultsv2_preserves_extra_keys():
    raw_results = {"a": 1, "b": 2, "extra": 3}
    output_bindings = {"a": "x"}

    mapped = map_results(output_bindings=output_bindings, raw_results=raw_results)
    assert mapped == {"x": 1, "b": 2, "extra": 3}


def test_map_resultsv2_empty_raw_results():
    raw_results = {}
    output_bindings = {"x": "y"}

    mapped = map_results(output_bindings=output_bindings, raw_results=raw_results)
    assert mapped == {"y": None}