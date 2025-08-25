from core.strategy.protocol import StrategyProtocol


class MockBreakoutStrategy(StrategyProtocol):
    name = "breakout"
    
    def execute(self, data: dict) -> dict:
        """Mock method to execute strategy."""
        return {"action": "buy", "confidence": 0.8}


class MockTrendFollowingStrategy(StrategyProtocol):
    name = "trend-following"
    
    def execute(self, data: dict) -> dict:
        """Mock method to execute strategy."""
        return {"action": "sell", "confidence": 0.6}


class MockStrategyService:
    def __init__(self):
        self._strategies = {
            "breakout": MockBreakoutStrategy(),
            "trend-following": MockTrendFollowingStrategy(),
        }
    
    def get(self, key):
        return self._strategies.get(key)
