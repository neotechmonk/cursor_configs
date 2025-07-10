import pytest
import types

from util.fn_loader import function_loader


# ---- Setup: mock module and function ----
# We'll patch a dummy module into sys.modules for controlled testing

@pytest.fixture
def mock_module(monkeypatch):
    dummy_module = types.ModuleType("mockmod")
    dummy_module.some_function = lambda x: x * 2
    dummy_module.non_callable = 42

    monkeypatch.setitem(__import__("sys").modules, "mockmod", dummy_module)
    return dummy_module


# ---- Happy path ----
def test_function_loader_happy_path(mock_module):
    fn = function_loader("mockmod.some_function")
    assert callable(fn)
    assert fn(3) == 6


# ---- Error: invalid path format ----
def test_function_loader_invalid_path():
    with pytest.raises(ValueError, match="Invalid function path"):
        function_loader("invalidpath")


# ---- Error: module not found ----
def test_function_loader_module_not_found():
    with pytest.raises(ImportError, match="Could not import module"):
        function_loader("nonexistent.module.fn")


# ---- Error: function not found ----
def test_function_loader_function_not_found(mock_module):
    with pytest.raises(AttributeError, match="Function 'missing_fn' not found"):
        function_loader("mockmod.missing_fn")


# ---- Error: resolved attribute is not callable ----
def test_function_loader_not_callable(mock_module):
    with pytest.raises(TypeError, match="is not callable"):
        function_loader("mockmod.non_callable")