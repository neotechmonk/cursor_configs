"""Technical analysis based strategy steps.

This package contains strategy steps that implement various technical analysis
methods such as trend detection, momentum indicators, and volatility measures.
"""

from .wrb import detect_wide_range_bar as wrb

__all__ = ['wrb']
