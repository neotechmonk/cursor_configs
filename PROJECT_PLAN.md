# Project Plan: Strategy Configuration System

## Goal

Develop a flexible and robust system for defining and loading trading strategy configurations from YAML files, including support for step dependencies and reevaluation logic.

## Completed Tasks

- [x] **Core Data Structures:** Defined `StrategyStep` and `StrategyConfig` dataclasses (`src/strategy.py`).
- [x] **YAML Loading:** Implemented `load_strategy_config` using `PyYAML` for safe parsing.
- [x] **Basic Validation:** Added checks for required fields (`name`, `steps`).
- [x] **Path Handling:** Used `pathlib.Path` for robust file path management.
- [x] **Configurable Directory:** Made `config_dir` a parameter in `load_strategy_config`.
- [x] **Dynamic Function Loading:** Implemented loading of `evaluation_fn` from modules or globals using `importlib`.
- [x] **Reevaluation Logic (using stable IDs):**
    - [x] Added unique `id` field to `StrategyStep`.
    - [x] Updated YAML to use step `id` for `reevaluates` references.
    - [x] Implemented 2-pass loading in `load_strategy_config` to resolve `id` references to `StrategyStep` objects.
    - [x] Added validation for missing/duplicate IDs and invalid references.
- [x] **Testing Setup:**
    - [x] Configured `pytest` and `pythonpath`.
    - [x] Created `sample_strategy_config` fixture (`tests/conftest.py`).
    - [x] Added `test_load_strategy_config_basic` verifying core loading, configs, function refs, and ID-based reevaluation.
    - [x] Added mock evaluation functions.
- [x] **Sample Configuration:** Created and updated `configs/strategies/trend_following.yaml` using stable IDs.

## Next Steps

- [x] **Strategy Execution Engine:** Implement logic to run the strategy based on `StrategyConfig` and handle reevaluations. (Basic sequential execution implemented)
- [ ] **Advanced Validation:** Add schema validation and circular dependency checks for `reevaluates`.
- [ ] **Expanded Testing:** Add tests for errors (missing files, invalid YAML/IDs/functions) and edge cases.
- [ ] **Visualization:** Develop tools to visualize step dependencies/reevaluations.

## Backlog 
- [ ] **Advanced Validation:** Add schema validation and circular dependency checks for `reevaluates`.
- [ ] **Expanded Testing:** Add tests for errors (missing files, invalid YAML/IDs/functions) and edge cases.
- [ ] **Visualization:** Develop tools to visualize step dependencies/reevaluations. 

