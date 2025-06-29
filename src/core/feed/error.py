
class PriceFeedError(Exception):
    """Base class for price feed errors."""
    pass


class SymbolError(PriceFeedError):
    """Error raised when a symbol is invalid or not supported."""
    pass


class TimeframeError(PriceFeedError):
    """Error raised when a timeframe is not supported."""
    pass


class RateLimitError(PriceFeedError):
    """Error raised when rate limits are exceeded."""
    pass


class AuthError(PriceFeedError):
    """Error raised when authentication fails."""
    pass