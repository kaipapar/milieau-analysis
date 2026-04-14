'''
@File: test_datahandler.py
@Time: 10.12.2025 15:52:19
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import pytest
import tempfile
import os
import json
import pandas as pd
from pathlib import Path
from propertycrawler.datahandler import IO, DF
from propertycrawler.propertysite import PropertySite
from propertycrawler.remax import Remax

class TestDH:
    @pytest.fixture
    def filepath(self):
        yield "data/property_search_LINEAR.php.html"

    """ # why does the filepath end with .html and the test ask the json to be a list
    def test_json_loads_as_list_of_dicts(self, filepath):
        json = io.get_json(filepath)
        assert type(json) == list
        assert type(json[0]) == dict """

    def test_get_json_gives_filenotfounderror(self):
        with pytest.raises(OSError) as excinfo:
            IO.get_json('doesnt_exist')
        #assert excinfo == True # ? assert that excinfo exists -> OS error has been raised ?


class TestIOClass:
    """ Tests for IO class - file I/O operations """
    
    @pytest.fixture
    def temp_json_file(self):
        """ Create a temporary JSON file for testing """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            test_data = [{"id": 1, "name": "test1"}, {"id": 2, "name": "test2"}]
            json.dump(test_data, f)
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def temp_html_file(self):
        """ Create a temporary HTML file for testing """
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write("<html><body><p>Test content</p></body></html>")
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def empty_file(self):
        """ Create an empty file for testing """
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def small_file(self):
        """ Create a small file (under threshold) """
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("x" * 50)  # 50 bytes, below threshold of 100
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    @pytest.fixture
    def large_file(self):
        """ Create a large file (over threshold) """
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("x" * 500)  # 500 bytes, above threshold of 100
            temp_path = f.name
        yield temp_path
        os.unlink(temp_path)

    def test_get_json_loads_valid_file(self, temp_json_file):
        """ Test that get_json correctly loads a JSON file """
        data = IO.get_json(temp_json_file)
        assert type(data) == list
        assert len(data) == 2
        assert data[0]["id"] == 1

    def test_get_json_raises_error_for_missing_file(self):
        """ Test that get_json raises error for non-existent file """
        with pytest.raises(OSError):
            IO.get_json('/nonexistent/path/file.json')

    def test_get_html_loads_file_as_list(self, temp_html_file):
        """ Test that get_html reads file into list of lines """
        lines = IO.get_html(temp_html_file)
        assert type(lines) == list
        assert len(lines) > 0

    def test_get_file_returns_file_object(self, temp_html_file):
        """ Test that get_file returns a file object """
        file_obj = IO.get_file(temp_html_file)
        assert file_obj is not None
        content = file_obj.read()
        file_obj.close()
        assert len(content) > 0

    def test_get_file_returns_none_for_missing_file(self):
        """ Test that get_file returns None for missing file """
        result = IO.get_file('/nonexistent/path/file.html')
        assert result is None

    def test_is_empty_returns_true_for_small_file(self, small_file):
        """ Test that is_empty returns True for files under threshold """
        assert IO.is_empty(small_file) == True

    def test_is_empty_returns_false_for_large_file(self, large_file):
        """ Test that is_empty returns False for files over threshold """
        assert IO.is_empty(large_file) == False

    def test_is_empty_returns_true_for_nonexistent_file(self):
        """ Test that is_empty returns True for non-existent files """
        assert IO.is_empty('/nonexistent/path/file.html') == True


class TestDFClass:
    """ Tests for DF class - DataFrame operations """
    
    @pytest.fixture
    def sample_fields(self):
        """ Sample column fields """
        return ["id", "address", "price", "rooms"]

    @pytest.fixture
    def sample_dict(self):
        """ Sample dictionary with property data """
        return {"id": 1, "address": "Main St", "price": 250000, "rooms": 3}

    @pytest.fixture
    def sample_listings(self):
        """ Create sample Remax listings """
        listings = []
        for i in range(3):
            listing = Remax.Listing(i)
            listing.attr_dict = {
                "id": i,
                "address": f"Street {i}",
                "price": 200000 + (i * 10000),
                "rooms": 2 + i
            }
            listings.append(listing)
        return listings

    def test_convert_dict_df_creates_dataframe(self, sample_fields, sample_dict):
        """ Test that convert_dict_df creates a DataFrame with correct structure """
        df = DF.convert_dict_df(sample_fields, sample_dict)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == sample_fields
        assert len(df) == 1

    def test_convert_dict_df_populates_data_correctly(self, sample_fields, sample_dict):
        """ Test that convert_dict_df populates data correctly """
        df = DF.convert_dict_df(sample_fields, sample_dict)
        assert df.iloc[0]["id"] == 1
        assert df.iloc[0]["address"] == "Main St"
        assert df.iloc[0]["price"] == 250000

    def test_add_row_increases_dataframe_length(self, sample_fields, sample_dict):
        """ Test that add_row increases the DataFrame length """
        df = DF.convert_dict_df(sample_fields, sample_dict)
        initial_length = len(df)
        
        new_row = {"id": 2, "address": "Oak Ave", "price": 300000, "rooms": 4}
        df = DF.add_row(df, new_row)
        
        assert len(df) == initial_length + 1

    def test_add_row_adds_data_correctly(self, sample_fields, sample_dict):
        """ Test that add_row adds data correctly """
        df = DF.convert_dict_df(sample_fields, sample_dict)
        new_row = {"id": 2, "address": "Oak Ave", "price": 300000, "rooms": 4}
        df = DF.add_row(df, new_row)
        
        assert df.iloc[1]["id"] == 2
        assert df.iloc[1]["address"] == "Oak Ave"

    def test_add_rows_adds_multiple_rows(self, sample_fields, sample_listings):
        """ Test that add_rows adds multiple rows from listings """
        df = pd.DataFrame(columns=sample_fields)
        initial_length = len(df)
        
        df = DF.add_rows(df, sample_listings, session_id="2026-04-09_14-30-45")
        
        assert len(df) == initial_length + len(sample_listings)

    def test_add_rows_adds_all_listings_data(self, sample_fields, sample_listings):
        """ Test that add_rows correctly adds all listing data """
        df = pd.DataFrame(columns=sample_fields)
        session_id = "2026-04-09_14-30-45"
        df = DF.add_rows(df, sample_listings, session_id=session_id)
        
        # Check that all listings were added
        for i, listing in enumerate(sample_listings):
            assert df.iloc[i]["id"] == listing.attr_dict["id"]
            assert df.iloc[i]["address"] == listing.attr_dict["address"]

    def test_save_creates_csv_file(self, sample_fields, sample_dict):
        """ Test that save creates a CSV file """
        df = DF.convert_dict_df(sample_fields, sample_dict)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            DF.save(df, temp_path)
            assert os.path.exists(temp_path)
            assert os.path.getsize(temp_path) > 0
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_save_correct_format(self, sample_fields, sample_dict):
        """ Test that save produces valid CSV with correct format """
        df = DF.convert_dict_df(sample_fields, sample_dict)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = f.name
        
        try:
            DF.save(df, temp_path)
            # Read back and verify
            saved_df = pd.read_csv(temp_path, index_col=0)
            assert list(saved_df.columns) == sample_fields
            assert saved_df.iloc[0]["id"] == sample_dict["id"]
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_add_rows_with_set_of_listings(self, sample_fields):
        """ Test that add_rows works with a set of listings (as used in PropertySite) """
        df = pd.DataFrame(columns=sample_fields)
        session_id = "2026-04-09_14-30-45"
        
        # Create a set of listings (remax.listings is a set in actual code)
        listings_set = set()
        for i in range(3):
            listing = Remax.Listing(i)
            listing.attr_dict = {
                "id": i,
                "address": f"Street {i}",
                "price": 200000 + (i * 10000),
                "rooms": 2 + i
            }
            listings_set.add(listing)
        
        df = DF.add_rows(df, listings_set, session_id=session_id)
        assert len(df) == 3

    def test_add_rows_handles_missing_attr_dict(self, sample_fields):
        """ Test that add_rows skips listings with missing attr_dict """
        df = pd.DataFrame(columns=sample_fields)
        session_id = "2026-04-09_14-30-45"
        listings = []
        
        # Listing with valid attr_dict
        listing1 = Remax.Listing(1)
        listing1.attr_dict = {"id": 1, "address": "Street 1", "price": 200000, "rooms": 2}
        listings.append(listing1)
        
        # Listing with None attr_dict
        listing2 = Remax.Listing(2)
        listing2.attr_dict = None
        listings.append(listing2)
        
        # Listing without attr_dict attribute (edge case)
        listing3 = Remax.Listing(3)
        listing3.attr_dict = {"id": 3, "address": "Street 3", "price": 220000, "rooms": 3}
        listings.append(listing3)
        
        with pytest.warns(UserWarning, match="attr_dict"):
            df = DF.add_rows(df, listings, session_id=session_id)
        
        # Should only have 2 rows (listing2 should be skipped)
        assert len(df) == 2

    def test_add_rows_returns_dataframe(self, sample_fields, sample_listings):
        """ Test that add_rows returns a dataframe with correct data """
        df = pd.DataFrame(columns=sample_fields)
        result = DF.add_rows(df, sample_listings, session_id="2026-04-09_14-30-45")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == len(sample_listings)

    def test_add_rows_with_partial_dict_keys(self, sample_fields):
        """ Test that add_rows handles listings with incomplete attr_dict (missing some keys) """
        df = pd.DataFrame(columns=sample_fields)
        session_id = "2026-04-09_14-30-45"
        
        listings = []
        # Listing with all keys
        listing1 = Remax.Listing(1)
        listing1.attr_dict = {"id": 1, "address": "Street 1", "price": 200000, "rooms": 2}
        listings.append(listing1)
        
        # Listing with only some keys (pandas should fill NaN for missing keys)
        listing2 = Remax.Listing(2)
        listing2.attr_dict = {"id": 2, "address": "Street 2"}  # Missing price and rooms
        listings.append(listing2)
        
        df = DF.add_rows(df, listings, session_id=session_id)
        
        assert len(df) == 2
        assert df.iloc[0]["id"] == 1
        assert df.iloc[1]["id"] == 2
        # Check that missing values are NaN
        assert pd.isna(df.iloc[1]["price"])
        assert pd.isna(df.iloc[1]["rooms"])

    def test_add_rows_adds_site_id_from_class(self, sample_listings):
        """ Test that add_rows correctly extracts and adds siteID from listing class """
        df = pd.DataFrame()
        session_id = "2026-04-09_14-30-45"
        
        df = DF.add_rows(df, sample_listings, session_id=session_id)
        
        # All rows should have siteID extracted from Remax class
        assert "siteID" in df.columns
        for i in range(len(df)):
            assert df.iloc[i]["siteID"] == "remax"

    def test_add_rows_adds_session_id(self, sample_listings):
        """ Test that add_rows correctly adds sessionID to each row """
        df = pd.DataFrame()
        session_id = "2026-04-09_14-30-45"
        
        df = DF.add_rows(df, sample_listings, session_id=session_id)
        
        # All rows should have the provided sessionID
        assert "sessionID" in df.columns
        for i in range(len(df)):
            assert df.iloc[i]["sessionID"] == session_id

    def test_add_rows_adds_listing_id(self, sample_listings):
        """ Test that add_rows correctly adds listingID from each listing object """
        df = pd.DataFrame()
        session_id = "2026-04-09_14-30-45"
        
        df = DF.add_rows(df, sample_listings, session_id=session_id)
        
        # Each row should have the corresponding listing ID
        assert "listingID" in df.columns
        for i, listing in enumerate(sample_listings):
            assert df.iloc[i]["listingID"] == listing.id
