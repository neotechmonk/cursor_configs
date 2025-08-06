class MockBreakoutStrategy:
    name = "breakout"


class MockTrendFollowingStrategy:
    name = "trend-following"


class MockStrategyService:
    def __init__(self):
        self._strategies = {
            "breakout": MockBreakoutStrategy(),
            "trend-following": MockTrendFollowingStrategy(),
        }
    
    def get(self, key):
        return self._strategies.get(key)
