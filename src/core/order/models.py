from decimal import Decimal
from enum import StrEnum
from typing import Optional, Self

import pandas as pd
from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrderSide(StrEnum):
    BUY = "buy"
    SELL = "sell"


class OrderType(StrEnum):
    MARKET = "market"
    LIMIT = "limit"


class Order(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    symbol: str = Field(..., min_length=1)
    timeframe: str = Field(..., min_length=1)
    side: OrderSide
    order_type: OrderType
    quantity: Decimal = Field(..., gt=Decimal("0"))
    entry_price: Decimal = Field(..., ge=Decimal("0"))
    stop_price: Decimal = Field(..., ge=Decimal("0"))
    target_price: Decimal = Field(..., ge=Decimal("0"))
    tag: Optional[str] = Field(default=None, description="Custom tag for traceability")
    placement_bar_index: Optional[pd.Timestamp] = Field(
        default=None,
        description="Bar index when the order was placed"
    )
    # Bar-based expiration logic
    ttl_bars: Optional[int] = Field(
        default=None,
        ge=1,
        description="Bar-based TTL: order expires after N bars from placement"
    )

    @model_validator(mode="after")
    def validate_stop_target_prices(self) -> Self:
        error_messages = []

        if self.side == OrderSide.BUY:
            if self.stop_price >= self.entry_price:
                error_messages.append("Stop price must be less than entry price for buy orders")
            if self.target_price <= self.entry_price:
                error_messages.append("Target price must be greater than entry price for buy orders")

        elif self.side == OrderSide.SELL:
            if self.stop_price <= self.entry_price:
                error_messages.append("Stop price must be greater than entry price for sell orders")
            if self.target_price >= self.entry_price:
                error_messages.append("Target price must be less than entry price for sell orders")

        if error_messages:
            raise ValueError("; ".join(error_messages))

        return self