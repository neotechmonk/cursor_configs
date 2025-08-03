#!/usr/bin/env python3
"""
File Execution Provider Demo

This demo shows how to use the File execution provider with real configuration
and order data using dependency injection patterns.
"""

from decimal import Decimal

from dependency_injector.wiring import Provide, inject

from core.app.container import AppContainer
from core.execution_provider.protocol import ExecutionProviderProtocol
from core.execution_provider.service import ExecutionProviderService
from core.order.models import Order, OrderSide, OrderType


@inject
def demo_basic(
    execution_service: ExecutionProviderService = Provide[AppContainer.execution_provider.service]
):
    """Demo: Using File execution provider through DI container."""
    print("\n" + "=" * 60)
    print("DEMO: File Execution Provider Usage")
    print("=" * 60)
    
    # Get all execution providers
    providers = execution_service.get_all()
    print(f"✓ Loaded {len(providers)} execution providers")
    
    # Get file provider specifically
    try:
        file_provider: ExecutionProviderProtocol = execution_service.get("file")
        print(f"✓ File provider: {file_provider.name}")
        print(f"  - File path: {file_provider.config.file_path}")
        
        return file_provider
    except Exception as e:
        print(f"❌ Error loading file provider: {e}")
        return None


@inject
def demo_submit_orders(
    execution_service: ExecutionProviderService = Provide[AppContainer.execution_provider.service]
):
    """Demo: Submit various orders to the file provider."""
    print("\n" + "=" * 60)
    print("DEMO: Order Submission")
    print("=" * 60)
    
    try:
        file_provider = execution_service.get("file")
        
        # Create sample orders
        orders = [
            Order(
                symbol="BTCUSD",
                timeframe="1m",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("0.01"),
                entry_price=Decimal("30000"),
                stop_price=Decimal("29000"),
                target_price=Decimal("31000"),
                tag="strategy_a",
                ttl_bars=10
            ),
            Order(
                symbol="ETHUSD",
                timeframe="5m",
                side=OrderSide.SELL,
                order_type=OrderType.LIMIT,
                quantity=Decimal("2"),
                entry_price=Decimal("2000"),
                stop_price=Decimal("2100"),
                target_price=Decimal("1900"),
                tag="strategy_b"
            ),
            Order(
                symbol="SPY",
                timeframe="1d",
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=Decimal("100"),
                entry_price=Decimal("450"),
                stop_price=Decimal("440"),
                target_price=Decimal("460"),
                tag="day_trading"
            )
        ]
        
        # Submit orders
        for i, order in enumerate(orders, 1):
            print(f"Submitting order {i}: {order.symbol} {order.side.value} {order.quantity}")
            result = file_provider.submit_order(order)
            print(f"  ✓ Order submitted successfully: {result}")
        
        print(f"\n✓ All {len(orders)} orders submitted to {file_provider.config.file_path}")
        
        return file_provider
        
    except Exception as e:
        print(f"❌ Error submitting orders: {e}")
        return None


@inject
def demo_read_orders(
    execution_service: ExecutionProviderService = Provide[AppContainer.execution_provider.service]
):
    """Demo: Read orders from the file."""
    print("\n" + "=" * 60)
    print("DEMO: Reading Orders from File")
    print("=" * 60)
    
    try:
        file_provider = execution_service.get("file")
        
        # Read all orders from file
        orders = file_provider.get_orders()
        
        print(f"✓ Read {len(orders)} orders from {file_provider.config.file_path}")
        
        # Display order details
        for i, order_data in enumerate(orders, 1):
            print(f"\nOrder {i}:")
            print(f"  - Symbol: {order_data.get('symbol')}")
            print(f"  - Side: {order_data.get('side')}")
            print(f"  - Quantity: {order_data.get('quantity')}")
            print(f"  - Entry Price: {order_data.get('entry_price')}")
            print(f"  - Tag: {order_data.get('tag', 'None')}")
            print(f"  - Timestamp: {order_data.get('timestamp')}")
        
        return orders
        
    except Exception as e:
        print(f"❌ Error reading orders: {e}")
        return []


@inject
def demo_clear_orders(
    execution_service: ExecutionProviderService = Provide[AppContainer.execution_provider.service]
):
    """Demo: Clear all orders from the file."""
    print("\n" + "=" * 60)
    print("DEMO: Clearing Orders")
    print("=" * 60)
    
    try:
        file_provider = execution_service.get("file")
        
        # Clear all orders
        result = file_provider.clear_orders()
        
        if result:
            print(f"✓ Cleared all orders from {file_provider.config.file_path}")
        else:
            print("❌ Failed to clear orders")
        
        return result
        
    except Exception as e:
        print(f"❌ Error clearing orders: {e}")
        return False


def main():
    """Run all demos."""
    print("File Execution Provider Demo")
    print("This demo shows how to use the File execution provider")
    print("with real configuration and order data using DI patterns.\n")

    try:
        # Use the root container
        container = AppContainer()
        container.init_resources()  # Important for logging etc.

        # Wire the container (so DI works in this module)
        container.wire(modules=[__name__])

        # Now `Provide[AppContainer.execution_provider.service]` works
        file_provider = None
        file_provider = demo_basic()

        if file_provider:
            print('')
            demo_submit_orders()
            # demo_read_orders()
            # demo_clear_orders()

        print("\n" + "=" * 60)
        print("✓ All demos completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main()) 