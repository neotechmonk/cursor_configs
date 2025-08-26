**Context:**
- Files/Modules: src/loaders/ (risk_config_loader, step_registry_loader, strategy_config_loader, trading_config_loader_v2)
- Constraints: Python 3.12, pytest, uv, ruff

**Files to touch:**
- tests/core/loaders/test_risk_config_loader.py
- tests/core/loaders/test_step_registry_loader.py
- tests/core/loaders/test_strategy_config_loader.py
- tests/core/loaders/test_trading_config_loader_v2.py

- [x] Plan updated
- [x] Implemented code changes (test files)
- [x] Added/updated tests (all loader test files)
- [x] Ran `uv run pytest tests/core/loaders/` and captured results
- [x] Linted with `uv run ruff check --fix`
- [x] Summary & next steps updated

**Result:** mixed (62 passed, 2 skipped)
**Tests run:** `uv run pytest tests/core/loaders/` → 62 passed, 2 skipped
**Files changed:** 4 test files created, 1 __init__.py deleted
**New/updated mocks:** None needed - used unittest.mock directly
**Diff highlights:** 
- Converted all class-based tests to plain functions per revised rules
- Fixed import paths from `src.loaders` to `loaders` per pythonpath config
- Corrected Pydantic model instantiation and assertions
- Fixed patch statements and mock assertions
**Follow-ups/TODO:** 
- PriceFeedConfigLoader and TradingConfigLoader tests skipped due to import issues
- Investigate if these loaders should be deprecated in favor of v2 versions
**Next iteration proposal:** Fix import issues in skipped loaders or confirm deprecation strategy
