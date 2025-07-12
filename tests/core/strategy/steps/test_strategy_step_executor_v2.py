"""Atomic tests for the new pure function approach and StrategyFunctionResolver."""

from unittest.mock import Mock

import pytest

from core.strategy.steps.executor import (
    StrategyStepFunctionResolver,
    bind_params,
    execute,
    map_results,
)
from core.strategy.steps.model import StrategyStepDefinition

# -------- Fixtures --------


@pytest.fixture
def simple_step():
    """Simple step with basic bindings."""
    return StrategyStepDefinition(
        id="simple_step",
        function_path="mock_module.function",
        input_bindings={
            "x": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_x"),
            "y": StrategyStepDefinition.InputBinding(source="config", mapping="value_y")
        },
        output_bindings={
            "result": StrategyStepDefinition.OutputBinding(mapping="_")
        }
    )


@pytest.fixture
def simple_step_with_mapping():
    """Simple step with explicit output mapping."""
    return StrategyStepDefinition(
        id="simple_step_mapped",
        function_path="mock_module.function",
        input_bindings={
            "x": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_x"),
            "y": StrategyStepDefinition.InputBinding(source="config", mapping="value_y")
        },
        output_bindings={
            "result": StrategyStepDefinition.OutputBinding(mapping="mapped_result")
        }
    )


@pytest.fixture
def simple_config():
    """Simple config data."""
    return {"value_y": 5}


@pytest.fixture
def simple_runtime():
    """Simple runtime data."""
    return {"value_x": 3}


@pytest.fixture
def mock_function():
    """Simple mock function."""
    return Mock(return_value={"result": 8})


@pytest.fixture
def mock_function_loader():
    """Mock function loader."""
    return Mock()


# -------- Atomic Function Tests --------


def test_bind_params_happy_path(simple_step, simple_config, simple_runtime):
    """Test bind_params happy path - should resolve parameters correctly."""
    
    kwargs = bind_params(simple_step, simple_config, simple_runtime)
    
    assert kwargs == {"x": 3, "y": 5}


def test_execute_happy_path(mock_function):
    """Test execute happy path - should call function with params and return result."""

    params = {"x": 3, "y": 5}
    result = execute(mock_function, params)
    
    mock_function.assert_called_once_with(x=3, y=5)
    assert result == {"result": 8}


def test_map_results_direct_return(simple_step):
    """Test map_results with direct return (mapping='_')."""
    
    raw_results = {"result": 8}
    mapped = map_results(simple_step, raw_results)
    
    assert mapped == {"result": 8}


def test_map_results_explicit_mapping(simple_step_with_mapping):
    """Test map_results with explicit mapping (mapping='mapped_result')."""
    
    raw_results = {"result": 8}
    mapped = map_results(simple_step_with_mapping, raw_results)
    
    assert mapped == {"mapped_result": 8}


# -------- StrategyFunctionResolver Integration Tests --------


def test_strategy_function_resolver_direct_return(
    simple_step, 
    simple_config, 
    simple_runtime, 
    mock_function_loader,
    mock_function
):
    """Test StrategyFunctionResolver with direct return (mapping='_')."""
    
    # Setup mock function loader
    mock_function_loader.return_value = mock_function
    
    # Create resolver
    resolver = StrategyStepFunctionResolver(
        step_definition=simple_step,
        config_data=simple_config,
        runtime_data=simple_runtime,
        _function_loader=mock_function_loader
    )
    
    # Execute
    result = resolver()
    
    # Verify function loader was called correctly
    mock_function_loader.assert_called_once_with("mock_module.function")
    
    # Verify function was called with correct parameters
    mock_function.assert_called_once_with(x=3, y=5)
    
    # Verify final result (direct return)
    assert result == {"result": 8}


def test_strategy_function_resolver_explicit_mapping(
    simple_step_with_mapping,
    simple_config,
    simple_runtime,
    mock_function_loader,
    mock_function
):
    """Test StrategyFunctionResolver with explicit mapping (mapping='mapped_result')."""
    
    # Setup mock function loader
    mock_function_loader.return_value = mock_function
    
    # Create resolver
    resolver = StrategyStepFunctionResolver(
        step_definition=simple_step_with_mapping,
        config_data=simple_config,
        runtime_data=simple_runtime,
        _function_loader=mock_function_loader
    )
    
    # Execute
    result = resolver()
    
    # Verify function loader was called correctly
    mock_function_loader.assert_called_once_with("mock_module.function")
    
    # Verify function was called with correct parameters
    mock_function.assert_called_once_with(x=3, y=5)
    
    # Verify final result (explicit mapping)
    assert result == {"mapped_result": 8}


# -------- Additional Happy Path Tests --------


def test_bind_params_with_multiple_sources():
    """Test bind_params with multiple runtime and config sources."""
    
    step = StrategyStepDefinition(
        id="multi_source_step",
        function_path="mock_module.function",
        input_bindings={
            "runtime1": StrategyStepDefinition.InputBinding(source="runtime", mapping="rt1"),
            "runtime2": StrategyStepDefinition.InputBinding(source="runtime", mapping="rt2"),
            "config1": StrategyStepDefinition.InputBinding(source="config", mapping="cfg1"),
            "config2": StrategyStepDefinition.InputBinding(source="config", mapping="cfg2")
        },
        output_bindings={}
    )
    
    config_data = {"cfg1": "A", "cfg2": "B"}
    runtime_data = {"rt1": 100, "rt2": 200}
    
    kwargs = bind_params(step, config_data, runtime_data)
    
    assert kwargs == {
        "runtime1": 100,
        "runtime2": 200,
        "config1": "A",
        "config2": "B"
    }


def test_execute_with_complex_function():
    """Test execute with a function that returns complex data."""
    
    def complex_function(a, b, c):
        return {
            "sum": a + b + c,
            "product": a * b * c,
            "list": [a, b, c],
            "nested": {"value": a + b}
        }
    
    params = {"a": 1, "b": 2, "c": 3}
    result = execute(complex_function, params)
    
    assert result == {
        "sum": 6,
        "product": 6,
        "list": [1, 2, 3],
        "nested": {"value": 3}
    }


def test_map_results_mixed_mappings():
    """Test map_results with both direct return and explicit mapping."""
    
    step = StrategyStepDefinition(
        id="mixed_mapping_step",
        function_path="mock_module.function",
        input_bindings={},
        output_bindings={
            "internal_result": StrategyStepDefinition.OutputBinding(mapping="public_result"),
            "debug_info": StrategyStepDefinition.OutputBinding(mapping="_"),
            "status": StrategyStepDefinition.OutputBinding(mapping="step_status")
        }
    )
    
    raw_results = {
        "internal_result": "success", 
        "debug_info": "step completed",
        "status": "ok"
    }
    mapped = map_results(step, raw_results)
    
    assert mapped == {
        "public_result": "success",
        "debug_info": "step completed",
        "step_status": "ok"
    }


def test_strategy_function_resolver_mixed_mappings(
    mock_function_loader,
    mock_function
):
    """Test StrategyFunctionResolver with mixed output mappings."""
    
    step = StrategyStepDefinition(
        id="mixed_mapping_step",
        function_path="mock_module.function",
        input_bindings={
            "input": StrategyStepDefinition.InputBinding(source="runtime", mapping="value")
        },
        output_bindings={
            "internal": StrategyStepDefinition.OutputBinding(mapping="external"),
            "debug": StrategyStepDefinition.OutputBinding(mapping="_"),
            "status": StrategyStepDefinition.OutputBinding(mapping="step_status")
        }
    )
    
    config_data = {}
    runtime_data = {"value": "test"}
    
    # Setup mock
    mock_function.return_value = {
        "internal": "processed_test",
        "debug": "debug_info",
        "status": "success"
    }
    mock_function_loader.return_value = mock_function
    
    resolver = StrategyStepFunctionResolver(
        step_definition=step,
        config_data=config_data,
        runtime_data=runtime_data,
        _function_loader=mock_function_loader
    )
    
    result = resolver()
    
    # Verify execution
    mock_function.assert_called_once_with(input="test")
    
    # Verify mapping
    assert result == {
        "external": "processed_test",
        "debug": "debug_info",
        "step_status": "success"
    }

# @pytest.mark.skip(reason="Default function loader is not implemented")
def test_strategy_function_resolver_default_loader():
    """Test StrategyFunctionResolver with default function loader."""
    from core.strategy.steps.executor import StrategyStepFunctionResolver

    # Use a function that accepts keyword arguments
    step = StrategyStepDefinition(
        id="default_loader_step",
        function_path="builtins.dict",  # dict() accepts keyword arguments
        input_bindings={
            "a": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_a"),
            "b": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_b")
        },

    )

    print ("step.output_bindings", step.output_bindings)
    
    config_data = {}
    runtime_data = {"value_a": 1, "value_b": 2}
    
    resolver = StrategyStepFunctionResolver(
        step_definition=step,
        config_data=config_data,
        runtime_data=runtime_data
        # Uses default function_loader
    )
    
    result = resolver()
    assert result ==  {"a": 1, "b": 2}


def test_strategy_function_resolver_no_output_bindings():
    """Test StrategyFunctionResolver with no output bindings - should return raw results."""
    from core.strategy.steps.executor import StrategyStepFunctionResolver

    # Step with no output bindings
    step = StrategyStepDefinition(
        id="no_output_bindings_step",
        function_path="builtins.dict",
        input_bindings={
            "a": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_a"),
            "b": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_b")
        },
        output_bindings={}  # No output bindings
    )
    
    config_data = {}
    runtime_data = {"value_a": 1, "value_b": 2}
    
    resolver = StrategyStepFunctionResolver(
        step_definition=step,
        config_data=config_data,
        runtime_data=runtime_data
    )
    
    result = resolver()
    # Should return raw results as-is
    assert result == {"a": 1, "b": 2}


def test_strategy_function_resolver_with_output_bindings():
    """Test StrategyFunctionResolver with output bindings - should apply mapping."""
    from core.strategy.steps.executor import StrategyStepFunctionResolver

    # Step with output bindings
    step = StrategyStepDefinition(
        id="with_output_bindings_step",
        function_path="builtins.dict",
        input_bindings={
            "a": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_a"),
            "b": StrategyStepDefinition.InputBinding(source="runtime", mapping="value_b")
        },
        output_bindings={
            "a": StrategyStepDefinition.OutputBinding(mapping="first"),
            "b": StrategyStepDefinition.OutputBinding(mapping="second")
        }
    )
    
    config_data = {}
    runtime_data = {"value_a": 1, "value_b": 2}
    
    resolver = StrategyStepFunctionResolver(
        step_definition=step,
        config_data=config_data,
        runtime_data=runtime_data
    )
    
    result = resolver()
    # Should apply output bindings
    assert result == {"first": 1, "second": 2}
