#!/usr/bin/env python3
"""
CSV Provider Usage Demo

This demo shows how to use the CSV price feed provider with real configuration
and data using dependency injection patterns.
"""

from pathlib import Path

# Add src to path for imports
from dependency_injector.wiring import Provide, inject

from core.container.price_provider import PriceFeedsContainer
from core.feed.providers.csv import CSVPriceFeedProvider
from core.time import CustomTimeframe


@inject
def demo_basic(
    providers: dict = Provide[PriceFeedsContainer.all_providers]
):
    """Demo: Using CSV provider through DI container with @inject decorator."""
    print("\n" + "=" * 60)
    print("DEMO 2: Container-based CSV Provider Usage (@inject Decorator)")
    print("=" * 60)
    
    # Get providers from the injected container
    providers_dict = providers
    print(f"✓ Loaded {len(providers_dict)} providers: {list(providers_dict.keys())}")
    
    # Get CSV provider specifically
    csv_provider:CSVPriceFeedProvider = providers_dict["csv"]
    print(f"✓ CSV provider: {csv_provider.name}")
    print(f"  - Supported symbols: {list(csv_provider.symbols)}")
    print(f"  - Supported timeframes: {[csv_provider.timeframes]}")
    
    return providers_dict


@inject
def demo_resampling(
    providers: dict = Provide[PriceFeedsContainer.all_providers]
):
    """Demo: Verify that resampling is working correctly."""
    print("\n" + "=" * 60)
    print("DEMO 3: Resampling Verification")
    print("=" * 60)
    
    # Get CSV provider using injected dependency
    csv_provider = providers["csv"]
    
    # Test data retrieval with different timeframes
    symbol = "CL"
    original_timeframe = CustomTimeframe("5m")  # Original timeframe
    resampled_timeframe = CustomTimeframe("15m")  # Resampled timeframe
    
    print(f"Fetching {symbol} data at {resampled_timeframe} timeframe (resampled)...")
    
    # Get both original and resampled data for comparison
    original_df = csv_provider.get_price_data(symbol, original_timeframe)
    resampled_df = csv_provider.get_price_data(symbol, resampled_timeframe)
    
    print(f"✓ Resampled data retrieved!")
    print(f"  - Original data shape: {original_df.shape}")
    print(f"  - Resampled data shape: {resampled_df.shape}")
    print(f"  - Resampling ratio: {len(original_df) / len(resampled_df):.1f}:1")
    print(f"  - Date range: {resampled_df.index.min()} to {resampled_df.index.max()}")
    
    # Show sample of original vs resampled data
    print(f"  - Sample original data (5m):")
    print(original_df.head(3).to_string())
    print(f"  - Sample resampled data (15m):")
    print(resampled_df.head(3).to_string())
    
    # Verify resampling logic - check that 15m data aggregates 5m data correctly
    print(f"\n  - Resampling verification:")
    print(f"    Original 5m periods in first 15m: {len(original_df.head(3))}")
    print(f"    First 15m open: {resampled_df.iloc[0]['open']:.2f}")
    print(f"    First 15m high: {resampled_df.iloc[0]['high']:.2f}")
    print(f"    First 15m low: {resampled_df.iloc[0]['low']:.2f}")
    print(f"    First 15m close: {resampled_df.iloc[0]['close']:.2f}")
    print(f"    First 15m volume: {resampled_df.iloc[0]['volume']:.0f}")
    
    # Manual verification of first 15m period
    first_three_5m = original_df.head(3)
    expected_open = first_three_5m.iloc[0]['open']
    expected_high = first_three_5m['high'].max()
    expected_low = first_three_5m['low'].min()
    expected_close = first_three_5m.iloc[-1]['close']
    expected_volume = first_three_5m['volume'].sum()
    
    print(f"\n  - Manual verification:")
    print(f"    Expected open: {expected_open:.2f} ✓" if abs(expected_open - resampled_df.iloc[0]['open']) < 0.01 else f"    Expected open: {expected_open:.2f} ✗")
    print(f"    Expected high: {expected_high:.2f} ✓" if abs(expected_high - resampled_df.iloc[0]['high']) < 0.01 else f"    Expected high: {expected_high:.2f} ✗")
    print(f"    Expected low: {expected_low:.2f} ✓" if abs(expected_low - resampled_df.iloc[0]['low']) < 0.01 else f"    Expected low: {expected_low:.2f} ✗")
    print(f"    Expected close: {expected_close:.2f} ✓" if abs(expected_close - resampled_df.iloc[0]['close']) < 0.01 else f"    Expected close: {expected_close:.2f} ✗")
    print(f"    Expected volume: {expected_volume:.0f} ✓" if abs(expected_volume - resampled_df.iloc[0]['volume']) < 1 else f"    Expected volume: {expected_volume:.0f} ✗")
    
    print("✓ Resampling verification completed!")


@inject
def demo_error_handling(
    providers: dict = Provide[PriceFeedsContainer.all_providers]
):
    """Demo: Error handling scenarios using dependency injection."""
    print("\n" + "=" * 60)
    print("DEMO 5: Error Handling")
    print("=" * 60)
    
    # Get CSV provider using injected dependency
    csv_provider = providers["csv"]
    
    # Test invalid symbol
    print("Testing invalid symbol...")
    try:
        csv_provider.get_price_data("INVALID_SYMBOL", CustomTimeframe("5m"))
    except Exception as e:
        print(f"✓ Expected error caught: {type(e).__name__}: {e}")
    
    # Test invalid timeframe
    print("\nTesting invalid timeframe...")
    try:
        csv_provider.get_price_data("CL", CustomTimeframe("2w"))
    except Exception as e:
        print(f"✓ Expected error caught: {type(e).__name__}: {e}")
    
    print("\n✓ Error handling working correctly!")


def main():
    """Run all demos."""
    print("CSV Provider Usage Demo")
    print("This demo shows how to use the CSV price feed provider")
    print("with real configuration and data files using DI patterns.\n")
    
    try:
        # Create and wire container for @inject decorator to work
        container = PriceFeedsContainer()
        container.providers_dir.override(Path("configs/providers"))
        
        # Wire the container with the current module - this is crucial for @inject to work
        container.wire(modules=[__name__])
        
        # Run demos

        demo_basic()

        demo_resampling()

        demo_error_handling()
        
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