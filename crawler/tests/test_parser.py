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

class TestParser:
    @pytest.fixture
    def parser(self):
        jsonlist = [{"identifier":""}]
        yield JsonParser(json_list=jsonlist)

    def test_get_ids_outputs_ids(self,parser):
        parser.json_list = [{"identifier":123},{"identifier":125},{"identifier":143},]
        assert {123,125,143}.issubset(parser.get_ids()) 

    def test_get_ids_only_outputs_valid_ids(self,parser):
        parser.json_list = [{"identifier":123},{"identifier":125},{"identifier":143},{"identifier":"kaka"}, {"identifier":"143"}]
        ids = parser.get_ids()
        assert all(isinstance(item, int) for item in parser.get_ids()), "unexpected type found"
