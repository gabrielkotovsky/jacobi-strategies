"""
Portfolio Analysis Data Module

This module handles data loading, caching, and management for Monte Carlo simulation data.
"""

from .loader import (
    load_data,
    load_asset_categories,
    build_asset_index_to_category,
    initialize_cache,
    get_cached_data
)

# Cache module is currently empty but exists for future expansion

__all__ = [
    # Data loading
    "load_data",
    "load_asset_categories", 
    "build_asset_index_to_category",
    "initialize_cache",
    "get_cached_data"
]
