"""Trading sessions module - clean public API."""

# Public API - what users actually need
from .container import TradingSessionContainer
from .protocols import TradingSessionProtocol, TradingSessionServiceProtocol
from .session import TradingSession, TradingSessionService

__all__ = [
    # Service Layer - main entry point
    "TradingSessionService",
    "TradingSessionServiceProtocol",
    
    # Runtime Objects - what users work with
    "TradingSession", 
    "TradingSessionProtocol",
    
    # Container - for DI setup
    "TradingSessionContainer",
]
