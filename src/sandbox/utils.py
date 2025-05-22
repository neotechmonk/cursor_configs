import importlib
import importlib.util
import os
from typing import Any, Callable


def import_function_from_path(module_path: str, function_name: str) -> Callable[..., Any]:
    """
    Dynamically import a function from a module specified by its file path.

    Args:
        module_path (str): The file path to the module.
        function_name (str): The name of the function to import.

    Returns:
        Callable[..., Any]: The imported function.

    Raises:
        ImportError: If the module cannot be loaded or the function is not found.
    """
    if not os.path.exists(module_path):
        raise ImportError(f"Module file not found: {module_path}")

    spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {module_path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, function_name):
        raise ImportError(f"Function '{function_name}' not found in module {module_path}")

    return getattr(module, function_name)


def import_function_from_dotted_path(dotted_path: str):
    """
    Import a function from a dotted Python path, e.g. 'src.sandbox.utils.get_trend'.
    """
    module_path, func_name = dotted_path.rsplit('.', 1)
    module = importlib.import_module(module_path)
    return getattr(module, func_name) 