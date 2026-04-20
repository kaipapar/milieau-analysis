'''
@File: execution_context.py
@Time: 2026-04-20
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: Execution context for workflow steps. Holds shared state across all steps in the pipeline.
'''

import pathlib
from datetime import datetime
from typing import Optional, Set, List
import pandas as pd
from propertycrawler.propertysite import PropertySite


class ExecutionContext:
    """
    Shared execution context passed between workflow steps.
    Maintains state to enable steps to run independently or sequentially
    without repeated disk I/O or redundant initialization.
    """

    def __init__(self, session_id: Optional[str] = None, base_data_path: Optional[str] = None, 
                 site_type: str = "remax"):
        """
        Initialize execution context.

        Args:
            session_id: Custom session ID. If None, auto-generates from current timestamp
            base_data_path: Base directory for output. If None, defaults to ./data/{site_type}/
            site_type: Type of property site (default: "remax")
        """
        self.site_type = site_type
        self.session_id = session_id or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.base_data_path = pathlib.Path(base_data_path or f"./data/{site_type}")
        
        # Initialize workflow state (None until steps populate them)
        self.remax: Optional[PropertySite] = None
        self.listing_ids: Optional[Set[int]] = None
        self.listings: Optional[List[PropertySite.Listing]] = None
        self.dataframe: Optional[pd.DataFrame] = None
        
        # Output paths for current session
        self.session_path = self.base_data_path / self.session_id
        self.listing_lists_path = self.session_path / "listing_lists"
        self.listings_path = self.session_path / "listings"
        
    def ensure_session_dir(self):
        """Create session directory structure if it doesn't exist."""
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.listing_lists_path.mkdir(parents=True, exist_ok=True)
        self.listings_path.mkdir(parents=True, exist_ok=True)
        
    def get_csv_output_path(self, custom_path: Optional[str] = None) -> pathlib.Path:
        """
        Get the CSV output path for the current session.
        
        Args:
            custom_path: Optional custom output path. If provided, returns it as Path
            
        Returns:
            Path to CSV file
        """
        if custom_path:
            return pathlib.Path(custom_path)
        return self.session_path / f"{self.site_type}_{self.session_id}.csv"

    def validate_has_remax(self) -> bool:
        """Check if PropertySite object is initialized."""
        return self.remax is not None

    def validate_has_listing_ids(self) -> bool:
        """Check if listing IDs have been extracted."""
        return self.listing_ids is not None and len(self.listing_ids) > 0

    def validate_has_listings(self) -> bool:
        """Check if Listing objects have been created."""
        return self.listings is not None and len(self.listings) > 0

    def validate_has_dataframe(self) -> bool:
        """Check if DataFrame has been created."""
        return self.dataframe is not None and len(self.dataframe) > 0
