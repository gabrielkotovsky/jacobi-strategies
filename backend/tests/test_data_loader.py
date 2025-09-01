import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data.loader import (
    load_data, 
    load_asset_categories, 
    build_asset_index_to_category,
    initialize_cache,
    get_cached_data
)

class TestDataLoader:
    """Test suite for data loading functions with real data."""
    
    def setup_method(self):
        """Setup test data paths."""
        self.hdf5_path = "../data/base_simulation.hdf5"
        self.csv_path = "../data/asset_categories.csv"
        
        # Verify test data exists
        assert Path(self.hdf5_path).exists(), f"HDF5 file not found: {self.hdf5_path}"
        assert Path(self.csv_path).exists(), f"CSV file not found: {self.csv_path}"
    
    def test_load_data_structure(self):
        """Test that load_data returns correct data structure."""
        returns, asset_names = load_data(self.hdf5_path)
        
        # Test returns array
        assert isinstance(returns, np.ndarray), "Returns should be numpy array"
        assert returns.shape == (25, 20, 10000), f"Expected shape (25, 20, 10000), got {returns.shape}"
        assert returns.dtype == np.float16, f"Expected float16 dtype, got {returns.dtype}"
        
        # Test asset names
        assert isinstance(asset_names, list), "Asset names should be list"
        assert len(asset_names) == 25, f"Expected 25 asset names, got {len(asset_names)}"
        assert all(isinstance(name, str) for name in asset_names), "All asset names should be strings"
        
        # Test uniqueness
        assert len(set(asset_names)) == len(asset_names), "Asset names should be unique"
        
        # Test specific asset names we know exist
        expected_names = ['Inflation-Protected Bond', 'EM Debt', 'Cash', 'US Small Cap', 'US Equity']
        for name in expected_names:
            assert name in asset_names, f"Expected asset name '{name}' not found"
    
    def test_load_data_values(self):
        """Test that load_data returns reasonable values."""
        returns, asset_names = load_data(self.hdf5_path)
        
        # Test that returns are finite
        assert np.all(np.isfinite(returns)), "All returns should be finite"
        
        # Test reasonable range (returns should typically be between -1 and 1.1 for extreme cases)
        assert np.all(returns >= -1.0), "Returns should not be less than -100%"
        assert np.all(returns <= 1.1), "Returns should not be greater than 110%"
        
        # Test that we have some non-zero values
        assert np.any(returns != 0), "Should have some non-zero returns"
    
    def test_load_asset_categories_structure(self):
        """Test that load_asset_categories returns correct structure."""
        asset_categories = load_asset_categories(self.csv_path)
        
        # Test return type
        assert isinstance(asset_categories, dict), "Should return dictionary"
        
        # Test that we have categories for all assets
        assert len(asset_categories) >= 25, f"Expected at least 25 assets, got {len(asset_categories)}"
        
        # Test that all values are strings
        assert all(isinstance(category, str) for category in asset_categories.values()), \
            "All categories should be strings"
        
        # Test that we have the expected categories
        expected_categories = ['Fixed Income', 'Equity', 'Cash', 'Commodities', 'Real Assets', 'Alternatives', 'Private Markets']
        actual_categories = set(asset_categories.values())
        for category in expected_categories:
            assert category in actual_categories, f"Expected category '{category}' not found"
    
    def test_load_asset_categories_content(self):
        """Test specific asset-category mappings."""
        asset_categories = load_asset_categories(self.csv_path)
        
        # Test specific known mappings
        expected_mappings = {
            'Inflation-Protected Bond': 'Fixed Income',
            'EM Debt': 'Fixed Income',
            'Cash': 'Cash',
            'US Small Cap': 'Equity',
            'US Equity': 'Equity'
        }
        
        for asset_name, expected_category in expected_mappings.items():
            assert asset_name in asset_categories, f"Asset '{asset_name}' not found in categories"
            assert asset_categories[asset_name] == expected_category, \
                f"Asset '{asset_name}' should be '{expected_category}', got '{asset_categories[asset_name]}'"
    
    def test_build_asset_index_to_category(self):
        """Test building index to category mapping."""
        returns, asset_names = load_data(self.hdf5_path)
        asset_categories = load_asset_categories(self.csv_path)
        
        index_to_category = build_asset_index_to_category(asset_names, asset_categories)
        
        # Test structure
        assert isinstance(index_to_category, dict), "Should return dictionary"
        assert len(index_to_category) == 25, f"Expected 25 mappings, got {len(index_to_category)}"
        
        # Test that all indices are covered
        for i in range(25):
            assert i in index_to_category, f"Index {i} not found in mapping"
            assert isinstance(index_to_category[i], str), f"Category for index {i} should be string"
        
        # Test specific mappings
        assert index_to_category[0] == 'Fixed Income', "Index 0 should be Fixed Income (Inflation-Protected Bond)"
        assert index_to_category[2] == 'Cash', "Index 2 should be Cash"
    
    def test_cache_functionality(self):
        """Test the caching mechanism."""
        # Clear any existing cache by reimporting
        import importlib
        import app.data.loader as loader_module
        importlib.reload(loader_module)
        
        # Initialize cache
        loader_module.initialize_cache(self.hdf5_path, self.csv_path)
        
        # Get cached data multiple times
        returns1, names1, categories1, index_to_cat1 = loader_module.get_cached_data()
        returns2, names2, categories2, index_to_cat2 = loader_module.get_cached_data()
        
        # Test that we get the same objects (singleton behavior)
        assert returns1 is returns2, "Returns should be the same object"
        assert names1 is names2, "Asset names should be the same object"
        assert categories1 is categories2, "Categories should be the same object"
        assert index_to_cat1 is index_to_cat2, "Index to category should be the same object"
        
        # Test data integrity
        assert returns1.shape == (25, 20, 10000), "Cached returns should have correct shape"
        assert len(names1) == 25, "Cached asset names should have correct length"
        assert len(categories1) == 25, "Cached categories should have correct length"
        assert len(index_to_cat1) == 25, "Cached index mapping should have correct length"
    
    def test_cache_without_initialization(self):
        """Test that get_cached_data raises error when cache not initialized."""
        # Clear cache by reimporting
        import importlib
        import app.data.loader as loader_module
        importlib.reload(loader_module)
        
        # Should raise RuntimeError
        with pytest.raises(RuntimeError, match="Data cache not initialized"):
            loader_module.get_cached_data()
    
    def test_data_consistency(self):
        """Test that all data is consistent across different loading methods."""
        # Load data directly
        returns_direct, names_direct = load_data(self.hdf5_path)
        categories_dict = load_asset_categories(self.csv_path)
        index_to_cat_direct = build_asset_index_to_category(names_direct, categories_dict)
        
        # Load data through cache
        initialize_cache(self.hdf5_path, self.csv_path)
        returns_cache, names_cache, categories_cache, index_to_cat_cache = get_cached_data()
        
        # Test consistency
        np.testing.assert_array_equal(returns_direct, returns_cache, "Returns should be identical")
        assert names_direct == names_cache, "Asset names should be identical"
        assert index_to_cat_direct == index_to_cat_cache, "Index mappings should be identical"
        
        # Test categories list consistency
        categories_list_direct = [index_to_cat_direct[i] for i in range(len(names_direct))]
        assert categories_list_direct == categories_cache, "Category lists should be identical"
    
    def test_error_handling_invalid_paths(self):
        """Test error handling for invalid file paths."""
        # Test invalid HDF5 path
        with pytest.raises(FileNotFoundError):
            load_data("nonexistent_file.hdf5")
        
        # Test invalid CSV path
        with pytest.raises(FileNotFoundError):
            load_asset_categories("nonexistent_file.csv")
    
    def test_error_handling_missing_asset_in_categories(self):
        """Test error handling when asset is missing from categories."""
        returns, asset_names = load_data(self.hdf5_path)
        
        # Create incomplete categories dict
        incomplete_categories = {'Inflation-Protected Bond': 'Fixed Income'}  # Missing other assets
        
        with pytest.raises(ValueError, match="Asset 'EM Debt' not found in categories"):
            build_asset_index_to_category(asset_names, incomplete_categories)

if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
