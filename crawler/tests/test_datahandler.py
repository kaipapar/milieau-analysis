'''
@File: test_datahandler.py
@Time: 10.12.2025 15:52:19
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import pytest
from propertycrawler.datahandler import IO

class TestDH:
    @pytest.fixture
    def filepath(self):
        yield "data/property_search_LINEAR.php.html"

    def test_json_loads_as_list_of_dicts(self,filepath):
        io = IO()
        json = io.get_json(filepath)
        assert type(json) == list
        assert type(json[0]) == dict