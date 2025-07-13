from unittest.mock import Mock, patch
import pytest

from core.strategy.executor import StrategyExecutor
from core.strategy.model import StrategyStepDefinition, StrategyStepInstance


@pytest.fixture
def example_step_definition():
    return StrategyStepDefinition(
        id="step_1",
        function_path="my.module.dummy_func",
        input_bindings={
            "arg1": StrategyStepDefinition.InputBinding(source="config", mapping="foo"),
            "arg2": StrategyStepDefinition.InputBinding(source="runtime", mapping="bar")
        },
        output_bindings={
            "result": StrategyStepDefinition.OutputBinding(mapping="step_output")
        }
    )

@pytest.fixture
def reevaluated_step_definition():
    return StrategyStepDefinition(
        id="step_2",
        function_path="my.module.another_func",
        input_bindings={},
        output_bindings={
            "result": StrategyStepDefinition.OutputBinding(mapping="second_output")
        }
    )

@pytest.fixture
def mock_step_instance(example_step_definition, reevaluated_step_definition):
    reevaluated = StrategyStepInstance(
        step_definition=reevaluated_step_definition,
        config_bindings={},
        runtime_bindings={},
        description="Reevaluated step"
    )

    return StrategyStepInstance(
        step_definition=example_step_definition,
        config_bindings={"foo": "value_from_config"},
        runtime_bindings={"bar": "value_from_runtime"},
        description="Sample step",
        reevaluates=[reevaluated]
    )

@pytest.fixture
def mock_strategy_config(mock_step_instance):
    from core.strategy.model import StrategyConfig
    return StrategyConfig(name="test_strategy", steps=[mock_step_instance])

@pytest.fixture
def mock_context():
    mock = Mock()
    mock._data = {}

    def mock_get(key):
        return mock._data.get(key)

    def mock_set(key, value):
        mock._data[key] = value

    def mock_has(key):
        return key in mock._data

    mock.get = mock_get
    mock.set = mock_set
    mock.has = mock_has

    return mock


def test_run_step_executes_and_reevaluates(
    mock_strategy_config, mock_step_instance, mock_context,
):
    executor = StrategyExecutor(config=mock_strategy_config, context=mock_context)
    executed_steps = []

    with patch('core.strategy.executor.StrategyStepFunctionResolver') as mock_resolver_class:
        mock_resolver_1 = Mock(return_value={"step_output": 42})
        mock_resolver_2 = Mock(return_value={"second_output": 99})
        
        # Return different resolvers depending on which step_definition is passed
        def side_effect_resolver(*, step_definition, config_data, runtime_data):
            if step_definition.id == "step_1":
                return mock_resolver_1
            elif step_definition.id == "step_2":
                return mock_resolver_2
            raise ValueError("Unexpected step")

        mock_resolver_class.side_effect = side_effect_resolver

        result = executor._run_step(mock_step_instance, executed_steps)

    # Check results of both original and reevaluated steps
    assert result == {"step_output": 42}
    assert mock_context.get("step_1") == {"step_output": 42}
    assert mock_context.get("step_2") == {"second_output": 99}

    # Confirm both resolvers were used
    assert mock_resolver_1.called
    assert mock_resolver_2.called

    # Confirm resolver instantiation called for both steps
    assert mock_resolver_class.call_count == 2
    step_ids = [call.kwargs["step_definition"].id for call in mock_resolver_class.call_args_list]
    assert sorted(step_ids) == ["step_1", "step_2"]