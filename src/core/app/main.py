import os
from pathlib import Path

from core.app.container import AppContainer


def main():
    # Explicitly set the config path via environment variable
    os.environ["APP_SETTINGS_PATH"] = str(Path("configs/settings.json").resolve())

    # Initialise the container
    container = AppContainer()
    container.init_resources()  # Triggers logging setup, etc.

    # Access the logger (DI provided)
    logger = container.logger()
    logger.info("Application started")

    # Access config for further use
    settings = container.settings()
    logger.debug(f"Loaded config:\n{settings.model_dump_json(indent=2)}")

    # Example: use a subcontainer or resource
    # container.portfolio().load() or similar
    
    logger.info("Shutting down")

if __name__ == "__main__":
    main()