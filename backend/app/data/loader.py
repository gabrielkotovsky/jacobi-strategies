import h5py
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Tuple, List
import logging

logger = logging.getLogger(__name__)

# Module-level cache for singleton data
RETURNS = None
ASSET_NAMES = None
ASSET_CATEGORIES = None
ASSET_INDEX_TO_CATEGORY = None

def load_data(hdf5_path: str = "../data/base_simulation.hdf5") -> Tuple[np.ndarray, List[str]]:
    """
    Load returns data from HDF5 file with memory-mapping to avoid copying.
    
    Args:
        hdf5_path: Path to the HDF5 file containing returns data
        
    Returns:
        Tuple of (returns_array, asset_names_list)
        - returns_array: numpy array of returns (float16) with shape (25, 20, 10000) - memory-mapped
        - asset_names_list: list of asset names (25-length, str)
        
    Raises:
        FileNotFoundError: If HDF5 file doesn't exist
        KeyError: If expected datasets are not found
        ValueError: If asset names are not unique or not 25 in length
    """
    hdf5_file = Path(hdf5_path)
    if not hdf5_file.exists():
        raise FileNotFoundError(f"HDF5 file not found: {hdf5_path}")
    
    try:
        with h5py.File(hdf5_file, 'r') as f:
            # Load returns with memory-mapping (read-only)
            if 'asset_class_projections' not in f:
                raise KeyError("Dataset 'asset_class_projections' not found in HDF5 file")
            
            if 'simulated_return' not in f['asset_class_projections']:
                raise KeyError("Dataset 'simulated_return' not found in asset_class_projections")
            
            # Load returns then promote to float32 for numeric stability
            returns = f['asset_class_projections']['simulated_return'][:].astype('float32')
            
            # Load asset names
            if 'asset_names' not in f:
                raise KeyError("Dataset 'asset_names' not found in HDF5 file")
            
            # Convert bytes to strings if necessary
            asset_names_raw = f['asset_names'][:]
            asset_names = []
            for name in asset_names_raw:
                if isinstance(name, bytes):
                    asset_names.append(name.decode('utf-8'))
                else:
                    asset_names.append(str(name))
            
            # Validate asset names
            if len(asset_names) != 25:
                raise ValueError(f"Expected 25 asset names, got {len(asset_names)}")
            
            # Check for uniqueness
            if len(set(asset_names)) != len(asset_names):
                raise ValueError("Asset names are not unique")
            
            # Validate returns shape matches asset names
            if returns.shape[0] != len(asset_names):
                raise ValueError(f"Returns shape {returns.shape} doesn't match asset count {len(asset_names)}")
            
            logger.info(f"Successfully loaded {returns.shape[1]} time periods for {len(asset_names)} assets")
            return returns, asset_names
            
    except Exception as e:
        logger.error(f"Error loading HDF5 data: {e}")
        raise

def load_asset_categories(csv_path: str = "../data/asset_categories.csv") -> Dict[str, str]:
    """
    Load asset categories from CSV file and build asset_name to category mapping.
    
    Args:
        csv_path: Path to the CSV file containing asset categories
        
    Returns:
        Dictionary mapping asset_name to category
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV format is invalid or missing required columns
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    try:
        # Read CSV file
        df = pd.read_csv(csv_file)
        
        # Validate required columns
        required_columns = ['asset_name', 'category']
        if not all(col in df.columns for col in required_columns):
            raise ValueError(f"CSV must contain columns: {required_columns}")
        
        # Convert to dictionary
        asset_categories = dict(zip(df['asset_name'], df['category']))
        
        # Validate no missing values
        if any(pd.isna(df['asset_name'])) or any(pd.isna(df['category'])):
            raise ValueError("CSV contains missing values in asset_name or category columns")
        
        # Check for duplicate asset names
        if len(asset_categories) != len(df):
            raise ValueError("Duplicate asset names found in CSV")
        
        logger.info(f"Successfully loaded categories for {len(asset_categories)} assets")
        return asset_categories
        
    except Exception as e:
        logger.error(f"Error loading asset categories: {e}")
        raise

def build_asset_index_to_category(asset_names: List[str], asset_categories: Dict[str, str]) -> Dict[int, str]:
    """
    Build mapping from asset index to category using asset_names and asset_categories.
    
    Args:
        asset_names: List of asset names in order
        asset_categories: Dictionary mapping asset_name to category
        
    Returns:
        Dictionary mapping asset index to category
        
    Raises:
        ValueError: If any asset name is missing from categories
    """
    asset_index_to_category = {}
    
    for idx, asset_name in enumerate(asset_names):
        if asset_name not in asset_categories:
            raise ValueError(f"Asset '{asset_name}' not found in categories")
        asset_index_to_category[idx] = asset_categories[asset_name]
    
    return asset_index_to_category

def initialize_cache(hdf5_path: str = "../data/base_simulation.hdf5", 
                    csv_path: str = "../data/asset_categories.csv") -> None:
    """
    Initialize module-level cache with data from HDF5 and CSV files.
    This should be called once at startup.
    
    Args:
        hdf5_path: Path to the HDF5 file
        csv_path: Path to the CSV file
        
    Raises:
        Various exceptions from load_data and load_asset_categories
    """
    global RETURNS, ASSET_NAMES, ASSET_CATEGORIES, ASSET_INDEX_TO_CATEGORY
    
    logger.info("Initializing data cache...")
    
    # Load returns and asset names
    RETURNS, ASSET_NAMES = load_data(hdf5_path)
    
    # Load asset categories
    asset_categories_dict = load_asset_categories(csv_path)
    
    # Build index to category mapping
    ASSET_INDEX_TO_CATEGORY = build_asset_index_to_category(ASSET_NAMES, asset_categories_dict)
    
    # Create list of categories aligned to asset index
    ASSET_CATEGORIES = [ASSET_INDEX_TO_CATEGORY[i] for i in range(len(ASSET_NAMES))]
    
    # Set the asset count in the BaseInputs schema for validation
    try:
        from app.schemas.inputs import BaseInputs
        BaseInputs.set_asset_count(len(ASSET_NAMES))
        logger.info(f"Set BaseInputs asset count to {len(ASSET_NAMES)}")
    except ImportError:
        logger.warning("Could not import BaseInputs schema to set asset count")
    
    logger.info(f"Cache initialized: {RETURNS.shape} returns, {len(ASSET_NAMES)} assets, {len(set(ASSET_CATEGORIES))} categories")

def get_cached_data() -> Tuple[np.ndarray, List[str], List[str], Dict[int, str]]:
    """
    Get cached data. Raises RuntimeError if cache not initialized.
    
    Returns:
        Tuple of (returns, asset_names, asset_categories, asset_index_to_category)
    """
    if RETURNS is None:
        raise RuntimeError("Data cache not initialized. Call initialize_cache() first.")
    
    return RETURNS, ASSET_NAMES, ASSET_CATEGORIES, ASSET_INDEX_TO_CATEGORY
