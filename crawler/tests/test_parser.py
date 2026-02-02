'''
@File: test_parser.py
@Time: 10.12.2025 17:15:09
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import pytest
from propertycrawler.parser import JsonParser
from propertycrawler.parser import HtmlParser  

class TestParser:
    """ Tests for parsing both HTML and JSON content """
    class TestJsonParser:
        @pytest.fixture
        def parser(self):
            jsonlist = [{"identifier":""}]
            yield JsonParser(json_list=jsonlist)

        def test_gen_id_set_outputs_ids(self,parser):
            parser.json_list = [{"identifier":123},{"identifier":125},{"identifier":143},]
            assert {123,125,143}.issubset(parser.gen_id_set()) 

        def test_gen_id_set_only_outputs_valid_ids(self,parser):
            """ checks that gen_id_set only outputs integers """
            parser.json_list = [{"identifier":123},{"identifier":125},{"identifier":143},{"identifier":"kaka"}, {"identifier":"143"}]
            with pytest.warns(UserWarning):
                ids = parser.gen_id_set()
            assert all(isinstance(item, int) for item in ids), "unexpected type found"
        
        def test_gen_id_set_handles_empty_list(self,parser):
            """ checks that gen_id_set works with empty list """
            parser.json_list = []
            ids = parser.gen_id_set()
            assert ids == set(), "expected empty set"
        

    class TestHtmlParser:
        @pytest.fixture
        def parser(self):
            html = "<html></html>"
            yield HtmlParser(html_content=html)
