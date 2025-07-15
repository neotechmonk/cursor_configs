

import pytest

from core.strategy.steps.executor import bind_params
from core.strategy.steps.model import StrategyStepDefinition
from core.strategy.steps.protocol import ResultProtocol


# @pytest.fixture
def mock_callable_config_param_only(config1)-> ResultProtocol:
    return {"return_mapping":"return_value"}

def mock_callable_rt_param_only(rt1)-> ResultProtocol:
    return {"return_mapping":"return_value"}

def mock_callable(config1,rt1)-> ResultProtocol:
    return {"return_mapping":"return_value"}

# @pytest.fixture
# def mock_step_definition():
#     return StrategyStepDefinition(
#             id="mock",
#             function_path=f"{mock_callable.__module__}.mock_callable",
#             input_bindings={"config1": 
#                                 {"source": "config", "mapping": "config1_map"}},
#             output_bindings={"return_value": 
#                                 {"mapping": "return_mapping"}
#                                 }
#         )
                                
# @pytest.mark.skip()
def test_binding_only_config_params_with_return():
    mock_fn = mock_callable_config_param_only 
    step_def =  StrategyStepDefinition(
                                    id="mock",
                                    function_path=f"{mock_fn.__module__}.{mock_fn.__name__}",
                                    input_bindings={"config1": 
                                                        {"source": "config", "mapping": "config1_map"}},
                                    output_bindings={"return_value": 
                                                        {"mapping": "return_mapping"}
                                                        }
                                )

    # print(mock_step_definition)
    sample_cofig_data = {"config1_map" :"config1_value"}

    bound_params =  bind_params(step_def, config_data=sample_cofig_data)

    assert list(bound_params.keys()) == ["config1"]
    assert list(bound_params.values()) == ["config1_value"]

    assert bound_params["config1"] == "config1_value" 

def test_binding_only_runtime_params_with_return():
    mock_fn = mock_callable_rt_param_only 
    step_def =  StrategyStepDefinition(
                                    id="mock",
                                    function_path=f"{mock_fn.__module__}.{mock_fn.__name__}",
                                    input_bindings={"rt1": 
                                                        {"source": "runtime", "mapping": "rt1_map"}},
                                    output_bindings={"return_value": 
                                                        {"mapping": "return_mapping"}
                                                        }
                                )

    # print(mock_step_definition)
    sample_runtime_data = {"rt1_map" :"rt1_value"}

    bound_params =  bind_params(step_def, runtime_data=sample_runtime_data)

    assert list(bound_params.keys()) == ["rt1"]
    assert list(bound_params.values()) == ["rt1_value"]

    assert bound_params["rt1"] == "rt1_value" 
    

# @pytest.mark.skip()
def test_binding_both_config_params_and_runtime_params_with_return():
    mock_fn = mock_callable    
    step_def =  StrategyStepDefinition(
                                    id="mock",
                                    function_path=f"{mock_fn.__module__}.{mock_fn.__name__}",
                                    input_bindings={"config1": 
                                                        {"source": "config", "mapping": "config1_map"},
                                                    "rt1": 
                                                        {"source": "runtime", "mapping": "rt1_map"}
                                                    },
                                                        
                                    output_bindings={"return_value": 
                                                        {"mapping": "return_mapping"}
                                                        }
                                )

    # print(mock_step_definition)
    sample_cofig_data = {"config1_map" :"config1_value"}
    sample_runtime_data = {"rt1_map" :"rt1_value"}

    bound_params =  bind_params(step_def, 
                                config_data=sample_cofig_data, 
                                runtime_data=sample_runtime_data)

    assert list(bound_params.keys()) == ["config1", "rt1"]
    assert list(bound_params.values()) == ["config1_value", "rt1_value"]

    assert bound_params["config1"] == "config1_value" 
    assert bound_params["rt1"] == "rt1_value" 
    

