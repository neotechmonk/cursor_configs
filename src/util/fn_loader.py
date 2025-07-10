import importlib
from types import ModuleType
from typing import Callable


def function_loader(function_path: str) -> Callable:
    """
    Dynamically loads a function from a module given its dotted path.

    Example:
        function_loader("my_package.my_module.my_function")

    Args:
        function_path: Fully qualified path to the function.

    Returns:
        A callable function object.

    Raises:
        ImportError: If the module cannot be imported.
        AttributeError: If the function is not found in the module.
    """
    if not isinstance(function_path, str) or "." not in function_path:
        raise ValueError(f"Invalid function path: {function_path}")

    module_path, func_name = function_path.rsplit(".", 1)

    try:
        module: ModuleType = importlib.import_module(module_path)
    except ImportError as e:
        raise ImportError(f"Could not import module '{module_path}'") from e

    try:
        func = getattr(module, func_name)
    except AttributeError as e:
        raise AttributeError(f"Function '{func_name}' not found in '{module_path}'") from e

    if not callable(func):
        raise TypeError(f"Resolved attribute '{func_name}' is not callable")

    return func