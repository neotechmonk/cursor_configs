from pathlib import Path

import pytest
import yaml

from core.strategy.steps.model import StrategyStepDefinition
from util.yaml_config_loader import load_yaml_config

CONFIG_PATH = Path("configs/strategies/_steps/strategy_steps.yaml")


# -------- Integration Test --------
def test_strategy_step_definition_sample(tmp_path):
    # Sample YAML content simulating a user-defined strategy file
    yaml_content = """
    - id: detect_trend
      function_path: src.utils.get_trend
      input_bindings:
        price_feed:
          source: runtime
          mapping: price_feed
      output_bindings:
        trend:
          mapping: "_"

    - id: find_extreme
      function_path: src.utils.is_extreme_bar
      input_bindings:
        trend:
          source: runtime
          mapping: trend
      output_bindings:
        is_extreme:
          mapping: "_"
    """

    # Write the YAML content to a temporary file
    yaml_file = tmp_path / "strategy_steps.yaml"
    yaml_file.write_text(yaml_content)

    # Load and parse the YAML file
    with open(yaml_file) as f:
        raw_steps = yaml.safe_load(f)

    # Convert to list of StrategyStepDefinition
    steps = [StrategyStepDefinition(**step) for step in raw_steps]

    assert len(steps) == 2

    assert steps[0].id == "detect_trend"
    assert steps[0].function_path == "src.utils.get_trend"
    assert steps[0].output_bindings["trend"].mapping is None

    assert steps[1].id == "find_extreme"
    assert steps[1].input_bindings["trend"].source == StrategyStepDefinition.ParamSource.RUNTIME
    assert steps[1].input_bindings["trend"].mapping == "trend"
    assert steps[1].output_bindings["is_extreme"].mapping is None

# @pytest.mark.xfail(reason="This test is not working as expected")
def test_strategy_step_yaml_parses_all_entries():
    """
    Integration test to ensure that all entries in the strategy_steps.yaml
    file are valid StrategyStepDefinition instances.
    """
    assert CONFIG_PATH.exists(), f"YAML file not found: {CONFIG_PATH}"
    strategy_steps_yaml = load_yaml_config(CONFIG_PATH, StrategyStepDefinition)

    assert isinstance(strategy_steps_yaml, list), "YAML must contain a list of step definitions"

    for idx, step in enumerate(strategy_steps_yaml):
        assert isinstance(step, StrategyStepDefinition), f"Invalid StrategyStepDefinition at index {idx}"