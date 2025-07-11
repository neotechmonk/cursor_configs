import pytest

from core.strategy.steps.executor import StrategyStepExecutor
from core.strategy.steps.model import StrategyStepDefinition

# -------- Fixtures --------


@pytest.fixture
def runtime_context():
    return {
        "runtime_value1": 100,
        "runtime_value2": 200
    }


@pytest.fixture
def static_config():
    return {
        "config_value1": "threshold-A",
        "config_value2": "threshold-B"
    }


@pytest.fixture
def mock_loader():
    def loader(path: str):
        assert path == "mock_module.mock_step"
        def mock_step(runtime_param1, runtime_param2, config_param1, config_param2):
            assert runtime_param1 == 100
            assert runtime_param2 == 200
            assert config_param1 == "threshold-A"
            assert config_param2 == "threshold-B"
            return {"result_key": "SUCCESS"}
        return mock_step
    return loader


@pytest.fixture
def step_with_direct_return():
    return StrategyStepDefinition(
        id="direct_return_step",
        function_path="mock_module.mock_step",
        input_bindings={
            "runtime_param1": StrategyStepDefinition.InputBinding(source="runtime", mapping="runtime_value1"),
            "runtime_param2": StrategyStepDefinition.InputBinding(source="runtime", mapping="runtime_value2"),
            "config_param1": StrategyStepDefinition.InputBinding(source="config", mapping="config_value1"),
            "config_param2": StrategyStepDefinition.InputBinding(source="config", mapping="config_value2"),
        },
        output_bindings={
            "result_key": StrategyStepDefinition.OutputBinding(mapping="_")
        }
    )


@pytest.fixture
def step_with_explicit_output_mapping():
    return StrategyStepDefinition(
        id="mapped_output_step",
        function_path="mock_module.mock_step",
        input_bindings={
            "runtime_param1": StrategyStepDefinition.InputBinding(source="runtime", mapping="runtime_value1"),
            "runtime_param2": StrategyStepDefinition.InputBinding(source="runtime", mapping="runtime_value2"),
            "config_param1": StrategyStepDefinition.InputBinding(source="config", mapping="config_value1"),
            "config_param2": StrategyStepDefinition.InputBinding(source="config", mapping="config_value2"),
        },
        output_bindings={
            "result_key": StrategyStepDefinition.OutputBinding(mapping="result_mapped_key")
        }
    )

# -------- Tests --------


def test_strategy_step_executor_direct_return(
    step_with_direct_return,
    runtime_context,
    static_config,
    mock_loader
):
    executor = StrategyStepExecutor(
        step=step_with_direct_return,
        context=runtime_context,
        config=static_config,
        function_loader=mock_loader,
    )
    result = executor.execute()
    assert result == {"result_key": "SUCCESS"}


def test_strategy_step_executor_mapped_output(
    step_with_explicit_output_mapping,
    runtime_context,
    static_config,
    mock_loader
):
    executor = StrategyStepExecutor(
        step=step_with_explicit_output_mapping,
        context=runtime_context,
        config=static_config,
        function_loader=mock_loader,
    )
    result = executor.execute()
    assert result == {"result_mapped_key": "SUCCESS"}


# -------- Additional Tests for Error Handling --------

def test_strategy_step_executor_missing_input_key_raises_error(
    step_with_direct_return,
    mock_loader
):
    # Modify context and config to remove required key
    incomplete_context = {"runtime_value2": 200}  # missing runtime_value1
    incomplete_config = {"config_value2": "threshold-B"}  # missing config_value1

    executor = StrategyStepExecutor(
        step=step_with_direct_return,
        context=incomplete_context,
        config=incomplete_config,
        function_loader=mock_loader,
    )

    import pytest
    with pytest.raises(KeyError) as exc_info:
        executor.execute()

    assert "runtime_value1" in str(exc_info.value) or "config_value1" in str(exc_info.value)


def test_strategy_step_executor_conflicting_input_sources_raises_error(
    mock_loader
):

    with pytest.raises(ValueError) as exc_info:

        step_conflict = StrategyStepDefinition(
        id="conflict_step",
        function_path="mock_module.mock_step",
        input_bindings={
            "param1": StrategyStepDefinition.InputBinding(source="runtime", mapping="shared_key"),
            "param2": StrategyStepDefinition.InputBinding(source="config", mapping="shared_key"),
        },
        output_bindings={}
    )

        context = {"shared_key": 123}
        config = {"shared_key": 456}

        # NOTE Error caught at the StrategyStepDefinition level. Never makes it here
        StrategyStepExecutor(
            step=step_conflict,
            context=context,
            config=config,
            function_loader=mock_loader,
        ).execute()

    assert "Duplicate input mappings found" in str(exc_info.value)