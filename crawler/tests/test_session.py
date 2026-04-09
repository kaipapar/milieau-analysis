'''
@File: test_session.py
@Time: 09.04.2026
@Author: Karri Korsu
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: Tests for site ID and session ID functionality
'''

import pytest
import tempfile
import os
from datetime import datetime
from pathlib import Path
from propertycrawler.remax import Remax
from propertycrawler.crawler import Crawler
from propertycrawler.datahandler import DF, IO
import pandas as pd


class TestSessionIDGeneration:
    """Tests for site ID and session ID generation"""

    def test_site_id_extraction_from_class_name(self):
        """Test that site_id is correctly extracted from PropertySite class name"""
        remax = Remax()
        site_id = remax.__class__.__name__.lower()
        assert site_id == "remax"

    def test_session_id_format(self):
        """Test that session_id follows ISO datetime format YYYY-MM-DD_HH-MM-SS"""
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # Verify format with regex
        import re
        pattern = r"^\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$"
        assert re.match(pattern, session_id), f"Session ID {session_id} doesn't match pattern"

    def test_base_data_path_structure(self):
        """Test that base_data_path is constructed correctly"""
        site_id = "remax"
        session_id = "2026-04-09_14-30-45"
        base_data_path = f"./data/{site_id}/{session_id}/"
        assert base_data_path == "./data/remax/2026-04-09_14-30-45/"


class TestDirectoryCreation:
    """Tests for automatic directory creation during operations"""

    def test_get_listing_list_full_creates_directory(self, tmp_path):
        """Test that get_listing_list_full creates the directory structure"""
        # Use a nested path structure
        test_dir = tmp_path / "data" / "remax" / "2026-04-09_14-30-45" / "listing_lists"
        
        # Mock subprocess to avoid actual network calls and hanging
        import unittest.mock as mock
        
        # Create mock page file to simulate successful page_0.html creation
        # Then second call returns False to stop iteration
        mock_get_page = mock.MagicMock(side_effect=[True, False])
        
        with mock.patch('propertycrawler.crawler.Crawler.get_listing_list_page', mock_get_page):
            Crawler.get_listing_list_full(
                url="http://test.local/index",
                start_pg=0,
                filepath=str(test_dir),
                separator="?"
            )
        
        # Verify directory was created
        assert test_dir.exists()

    def test_get_listings_creates_directory(self, tmp_path):
        """Test that get_listings creates the listings directory"""
        remax = Remax()
        # Create a listing
        listing = Remax.Listing(123)
        remax.listings.append(listing)
        
        # Use a nested path structure
        listings_dir = tmp_path / "data" / "remax" / "2026-04-09_14-30-45" / "listings"
        
        # Mock wget to avoid actual network calls
        import unittest.mock as mock
        with mock.patch('subprocess.run'):
            Crawler.get_listings(remax, filepath=str(listings_dir))
        
        # Verify directory was created
        assert listings_dir.exists()
        # Verify listing filepath was updated to the new directory
        expected_filepath = str(listings_dir / "123.html")
        assert listing.filepath == expected_filepath

    def test_csv_save_creates_directory(self, tmp_path):
        """Test that DF.save() creates parent directories before saving"""
        # Use a nested path structure
        csv_path = tmp_path / "data" / "remax" / "2026-04-09_14-30-45" / "output.csv"
        
        # Create a simple dataframe
        df = pd.DataFrame({"id": [1, 2], "name": ["test1", "test2"]})
        
        # Save to nested path
        DF.save(df, str(csv_path))
        
        # Verify file was created
        assert csv_path.exists()
        # Verify content
        loaded_df = pd.read_csv(csv_path, index_col=0)
        assert len(loaded_df) == 2
        assert list(loaded_df.columns) == ["id", "name"]

    def test_get_listing_list_full_with_multiple_pages(self, tmp_path):
        """Test that get_listing_list_full creates multiple page files"""
        test_dir = tmp_path / "listing_lists"
        
        # Mock to create 3 pages, then stop
        import unittest.mock as mock
        mock_get_page = mock.MagicMock(side_effect=[True, True, True, False])
        
        with mock.patch('propertycrawler.crawler.Crawler.get_listing_list_page', mock_get_page):
            Crawler.get_listing_list_full(
                url="http://test.local/",
                start_pg=0,
                filepath=str(test_dir),
                separator="?"
            )
        
        # Verify directory was created and method was called 4 times (pages 0,1,2 success, page 3 fails)
        assert test_dir.exists()
        assert mock_get_page.call_count == 4


class TestSessionConsistency:
    """Tests to verify session ID remains consistent throughout a program call"""

    def test_same_session_id_used_throughout(self):
        """Test that the same session_id is used for all operations in a single call"""
        # Generate session_id once
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        # Create paths using the same session_id
        listing_list_path = f"./data/remax/{session_id}/listing_lists"
        listings_path = f"./data/remax/{session_id}/listings"
        csv_path = f"./data/remax/{session_id}/remax_{session_id}.csv"
        
        # All should use the same session_id
        assert session_id in listing_list_path
        assert session_id in listings_path
        assert session_id in csv_path
        
        # Extract session_ids to verify they're identical
        import re
        pattern = r"(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"
        extracted_ids = re.findall(pattern, listing_list_path + listings_path + csv_path)
        # Should find 3 identical session_ids
        assert len(set(extracted_ids)) == 1, "Session IDs should be identical across all paths"
