'''
@File: test_crawler.py
@Time: 11.12.2025 15:52:28
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
from propertycrawler.crawler import Crawler
from propertycrawler.datahandler import IO
from propertycrawler.parser import JsonParser
from pytest_httpserver import HTTPServer
from werkzeug.wrappers.response import Response
from collections.abc import Iterable
import json
import pytest
import os
import requests
import subprocess

class TestCrawler:

    @pytest.fixture
    def mock_json(self, tmp_path):
        """ make an example file """
        path = tmp_path / "test.json"
        example = '"21":{"identifier":"80440756","type":"Kiinteist"}'
        with open(path, "w") as f:
            f.write(example)
        yield path

    @pytest.fixture
    def mock_html(self,tmp_path): 
        """ make an example file """
        path = tmp_path / "out.html"
        # Create a file large enough (>100 bytes) to not be considered "empty"
        example : tuple = ('<!doctype html> ', \
                    '<html lang="fi"> ', \
                    '<body>', \
                    '<h1>Test Content</h1>' * 10, \
                    '</body>', \
                    '</html>')
        with open(path, "w") as f:
            f.writelines(example)
        yield path

    @pytest.fixture
    def outfile_json(self, tmp_path):
        """ make an example file """
        path = tmp_path / "out.json"
        example = ''
        with open(path, "w") as f:
            f.write(example)
        yield path

    @pytest.fixture
    def handler(self, mock_json, page=0):
        """ retrieves an example file according to the page num argument, if there's no file, it yields an empty string """
        data = ""
        with open(mock_json, 'r') as f:
            data = f.read()
        yield data
        
    def test_mock_server_is_reachable(self,httpserver):
        httpserver.expect_request('/index').respond_with_data("OK") # when a request for /index is made, it responds with whatever handler returns

        response = requests.get(httpserver.url_for('/index'))
        assert response.status_code == 200        

    def test_mock_server_returns_data(self, httpserver, handler):
        httpserver.expect_request('/index').respond_with_data(handler) # when a request for /index is made, it responds with whatever handler returns

        response = requests.get(httpserver.url_for('/index'))
        assert response.status_code == 200
        assert response.content.decode() == handler

    class TestGetListingPage:
        def test_subprocess_is_successfull(self, httpserver, tmp_path):
            base_url = "something"
            id = 9999
            data = 'OK'
            content = ''
            filepath = tmp_path / "temp.html"
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data(data)
            try:
                Crawler.get_listing_page(httpserver.url_for('/'+base_url+str(id)), id, filepath)
            except subprocess.CalledProcessError:
                pytest.fail("subprocess call failed")

        def test_subprocess_returns_data(self,httpserver,tmp_path):
            base_url = "something"
            id = 9999
            data = 'OK'
            content = ''
            filepath = tmp_path / "temp.html"
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data(data)
            Crawler.get_listing_page(httpserver.url_for('/'+base_url+str(id)), id, filepath)

            with open(filepath) as f:
                content = f.read()
            
            assert data == content

        def test_improper_custom_filepath(self, httpserver, tmp_path):
            base_url = "something"
            id = 9999
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data("OK")
            filepath = tmp_path / "**< > : | ? ***.html"
            try: 
                Crawler.get_listing_page(httpserver.url_for('/'+base_url+str(id)), id, filepath)
            except subprocess.CalledProcessError:
                pytest.fail("subprocess call failed")
            

        def test_default_filepath(self, httpserver):
            base_url = "something"
            id = 9999
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data("OK")
          
            with pytest.warns(UserWarning):
                Crawler.get_listing_page(httpserver.url_for('/'+base_url+str(id)), id)
                    
        def test_file_is_already_populated(self, httpserver, mock_html, tmp_path):
            base_url = "/something"
            id = 9999
            data = 'OK'
            content = ''
            filepath = mock_html
            url = base_url+str(id)
            httpserver.expect_request(url).respond_with_data(data)
            with pytest.warns(UserWarning):
                Crawler.get_listing_page(httpserver.url_for(url), id, filepath)
            newpath = mock_html.with_name(f"{mock_html.stem}(1){mock_html.suffix}")
            assert os.path.exists(newpath) 


        def test_proper_filepath_url_id(self, httpserver, mock_html, tmp_path):
            base_url = "index"
            id = 9999
            data = 'OK'
            content = IO.get_html(mock_html)
            filepath = tmp_path / "kaki.html"
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data(content)
            Crawler.get_listing_page(httpserver.url_for('/'+base_url+str(id)), id, filepath)
            result = IO.get_html(filepath)

            assert content == result

        def test_improper_html_format(self):
            """ Not implemented, because html format is not needed for parsing, yet """
            pass

        def test_improper_url(self, httpserver):
            """ TODO: Test that urls are validated at get_listing_page level. Should return a UserError. 
                It would make sure that the program is used correctly, and fail in a more verbose manner. """
            pytest.skip() # remove when implemented
            base_url = "something"
            id = 9999
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data("OK")

            try: 
                Crawler.get_listing_page(base_url, id)
            except subprocess.CalledProcessError:
                pytest.fail("subprocess call failed")             
        
        """ # what am I testing here?
        def test_improper_id(self, httpserver):
            base_url = "something"
            id = 9999
            httpserver.expect_request('/'+base_url+str(id)).respond_with_data("OK")

            try: 
                Crawler.get_listing_page(base_url, id)
            except subprocess.CalledProcessError:
                pytest.fail("subprocess call failed")"""

    class TestGetListingListPage:

        def test_listing_list_is_retrieved_wget(self, httpserver,handler, mock_json,outfile_json):
            httpserver.expect_request('/index').respond_with_data('{"21":{"identifier":"80440756","type":"Kiinteist"}}') # when a request for /index is made, it responds with whatever handler returns
            # handler is somehow funky! here if I do it through handler it fails, but with string literal is succeeds... go figure

            # now by using wget:
            print(Crawler.get_listing_list_page(httpserver.url_for('/index'), filepath= outfile_json))
            file = IO.get_json(outfile_json)
            
            assert file != "" # assert that file is not empty

        def test_listing_list_fails_non_valid_json(self,httpserver,outfile_json):
            httpserver.expect_request('/index').respond_with_data("kakihaise") # when a request for /index is made, it responds with whatever handler returns

            # now by using wget:
            print(Crawler.get_listing_list_page(httpserver.url_for('/index'), filepath= outfile_json))
            with pytest.raises(json.JSONDecodeError) as excinfo:
                file = IO.get_json(outfile_json)
            
            assert excinfo.type is json.JSONDecodeError

        def test_listing_list_succeeds_valid_json(self,httpserver,outfile_json):
            data= '{"kaki": "haise"}'
            httpserver.expect_request('/index').respond_with_data(data) # when a request for /index is made, it responds with whatever handler returns

            # now by using wget:
            print(Crawler.get_listing_list_page(httpserver.url_for('/index'), filepath= outfile_json))
            file = IO.get_json(outfile_json)

            assert file == json.loads(data) # this must convert file to string from bytestring

    class TestGetListingListFull:
        """ testing that multiple pages are retrieved until an empty page is found """



        def test_listing_list_next_page(self,httpserver,tmp_path):
            # checks that next page is retrieved

            httpserver.expect_request('/index', query_string={'page': '1'}).respond_with_data('{"21":{"identifier":"80440756","type":"Kiinteist"}}')
            httpserver.expect_request('/index', query_string={'page': '2'}).respond_with_data('{"22":{"identifier":"80440756","type":"Kiinteist"}}')

            Crawler.get_listing_list_full(httpserver.url_for('/index'), start_pg=1, filepath=tmp_path, separator="?")
            file1 = IO.get_json(tmp_path / "page_1.html")
            file2 = IO.get_json(tmp_path / "page_2.html")            
            assert '21' in file1
            assert '22' in file2        

        def test_listing_list_empty_page(self, httpserver, tmp_path):
            # if next page is empty, it stops and deletes the empty file
            httpserver.expect_request('/index', query_string={'page': '1'}).respond_with_data('{"21":{"identifier":"80440756","type":"Kiinteist"}}')
            httpserver.expect_request('/index', query_string={'page': '2'}).respond_with_data('') # empty page

            Crawler.get_listing_list_full(httpserver.url_for('/index'), start_pg=1, filepath=tmp_path, separator="?")
            file1 = IO.get_json(tmp_path / "page_1.html")
            assert '21' in file1

            with pytest.raises(FileNotFoundError) as excinfo:
                file2 = IO.get_json(tmp_path / "page_2.html")

    class TestGetListingIdsFromDisk:
        """ testing that all page IDs are retrieved and accumulated from disk """

        @pytest.fixture
        def parser(self):
            """ provides a reusable JsonParser instance """
            yield JsonParser([])

        def test_single_page_retrieval(self, tmp_path, parser):
            """ test that IDs are extracted from a single page_0.html file """
            # Create page_0.html with test data
            page_0_data = [
                {"identifier": "123"},
                {"identifier": "456"},
                {"identifier": "789"}
            ]
            page_0_file = tmp_path / "page_0.html"
            with open(page_0_file, 'w') as f:
                json.dump(page_0_data, f)

            # Call the method
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Verify all IDs were extracted
            assert ids == {123, 456, 789}

        def test_multiple_page_accumulation(self, tmp_path, parser):
            """ test that IDs are accumulated from multiple pages """
            # Create page_0.html (array format)
            page_0_data = [{"identifier": "100"}, {"identifier": "200"}]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html (object format with numeric string keys, matching real data)
            page_1_data = {"21": {"identifier": "300"}, "22": {"identifier": "400"}}
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)
            
            # Create page_2.html (object format with numeric string keys, matching real data)
            page_2_data = {"23": {"identifier": "500"}}
            with open(tmp_path / "page_2.html", 'w') as f:
                json.dump(page_2_data, f)

            # Call the method
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Verify all IDs from all pages are accumulated
            assert ids == {100, 200, 300, 400, 500}

        def test_stops_at_missing_page(self, tmp_path, parser):
            """ test that iteration stops when a page file is missing """
            # Create page_0.html (array format)
            page_0_data = [{"identifier": "111"}]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html (object format with numeric string keys, matching real data)
            page_1_data = {"21": {"identifier": "222"}}
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)

            # Call the method (page_2.html doesn't exist)
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Should only have IDs from page_0 and page_1
            assert ids == {111, 222}

        def test_parser_reuse(self, tmp_path, parser):
            """ test that the same parser instance is reused with updated json_list """
            # Create multiple pages
            page_0_data = [{"identifier": "10"}]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html with object format (matching real data)
            page_1_data = {"21": {"identifier": "20"}}
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)

            # Verify parser starts with empty list
            assert parser.json_list == []

            # Call the method
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # After the call, parser's json_list should be the last page's data
            assert parser.json_list == page_1_data
            assert ids == {10, 20}

        def test_handles_invalid_ids_per_page(self, tmp_path, parser):
            """ test that invalid IDs (non-integers) are skipped across pages """
            # Create page_0.html with mixed valid/invalid IDs (array format)
            page_0_data = [
                {"identifier": "100"},
                {"identifier": "not_a_number"},
                {"identifier": "200"}
            ]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html with object format and mixed data (matching real data)
            page_1_data = {
                "21": {"identifier": "invalid"},
                "22": {"identifier": "300"}
            }
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)

            # Call the method and expect warnings for invalid IDs
            with pytest.warns(UserWarning, match="Invalid id"):
                ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Should only have valid IDs
            assert ids == {100, 200, 300}

        def test_empty_page_file(self, tmp_path, parser):
            """ test that an empty page (empty list) is handled correctly """
            # Create page_0.html with data
            page_0_data = [{"identifier": "100"}]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html with empty list
            page_1_data = []
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)

            # Call the method
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Should have ID from page_0, and page_1 contributes nothing
            assert ids == {100}

        def test_no_pages_exist(self, tmp_path, parser):
            """ test that empty set is returned when no page_0.html exists """
            # Don't create any files
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Should return empty set
            assert ids == set()

        def test_duplicate_ids_across_pages(self, tmp_path, parser):
            """ test that duplicate IDs across pages are handled (set removes duplicates) """
            # Create page_0.html
            page_0_data = [{"identifier": "100"}, {"identifier": "200"}]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html with overlapping IDs
            page_1_data = [{"identifier": "200"}, {"identifier": "300"}]
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)

            # Call the method
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # Set should automatically deduplicate
            assert ids == {100, 200, 300}
            assert len(ids) == 3

        def test_string_number_conversion(self, tmp_path, parser):
            """ test that string numbers are converted to integers across pages """
            # Create page_0.html with string numbers
            page_0_data = [{"identifier": "100"}]
            with open(tmp_path / "page_0.html", 'w') as f:
                json.dump(page_0_data, f)
            
            # Create page_1.html with string numbers
            page_1_data = [{"identifier": "200"}]
            with open(tmp_path / "page_1.html", 'w') as f:
                json.dump(page_1_data, f)

            # Call the method
            ids = Crawler.get_listing_ids_from_disk(filepath=tmp_path, parser=parser)
            
            # All IDs should be integers
            assert all(isinstance(id, int) for id in ids)
            assert ids == {100, 200}
