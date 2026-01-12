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

class TestCrawler:
    """ 
     atleast test everything that doesn't have to do with wget
     -> or mock wget

     - 
       """


    '''this is already a functionality in httpserver, this fixture is just overwriting it...
    @pytest.fixture
    def httpserver(self) -> Iterable[HTTPServer]:
        """ launch a mock http server """
        httpserver = HTTPServer(port = 8080) # default -> localhost -> random port
        yield httpserver
        httpserver.check_assertions()  # this will raise AssertionError and make the test failing'''
    @pytest.fixture
    def mock_json(self, tmp_path):
        """ make an example file """
        path = tmp_path / "test.json"
        example = '"21":{"identifier":"80440756","type":"Kiinteist"}'
        with open(path, "w") as f:
            f.write(example)
        yield path

    @pytest.fixture
    def outfile(self, tmp_path):
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

    def test_listing_list_is_retrieved(self, httpserver, handler):
        httpserver.expect_request('/index').respond_with_data(handler) # when a request for /index is made, it responds with whatever handler returns

        response = requests.get(httpserver.url_for('/index'))
        assert response.status_code == 200
        assert response.content.decode() == handler

    def test_listing_list_is_retrieved_wget(self, httpserver,handler, mock_json,outfile):
        httpserver.expect_request('/index').respond_with_data('{"21":{"identifier":"80440756","type":"Kiinteist"}}') # when a request for /index is made, it responds with whatever handler returns
        # handler is somehow funky! here if I do it through handler it fails, but with string literal is succeeds... go figure

        # now by using wget:
        print(Crawler.get_listing_list_page(httpserver.url_for('/index'), filepath= outfile))
        file = IO.get_json(outfile)
        
        assert file != "" # assert that file is not empty

    def test_listing_list_fails_non_valid_json(self,httpserver,outfile):
        httpserver.expect_request('/index').respond_with_data("kakihaise") # when a request for /index is made, it responds with whatever handler returns

        # now by using wget:
        print(Crawler.get_listing_list_page(httpserver.url_for('/index'), filepath= outfile))
        with pytest.raises(json.JSONDecodeError) as excinfo:
            file = IO.get_json(outfile)
        
        assert excinfo.type is json.JSONDecodeError

    def test_listing_list_succeeds_valid_json(self,httpserver,outfile):
        data= '{"kaki": "haise"}'
        httpserver.expect_request('/index').respond_with_data(data) # when a request for /index is made, it responds with whatever handler returns

        # now by using wget:
        print(Crawler.get_listing_list_page(httpserver.url_for('/index'), filepath= outfile))
        file = IO.get_json(outfile)

        assert file == data # this must convert file to string from bytestring

    def test_listing_list_next_page(self,httpserver,handler):
        pass
        #httpserver.expect_request('/index', query_string={'page': '1'}).respond_with_handler(handler(1))

    def test_listing_list_empty_page(self,httpserver,handler):
        pass
        #httpserver.expect_request('/index', query_string={'page': '2'}).respond_with_handler(handler(2))