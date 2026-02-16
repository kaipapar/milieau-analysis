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
