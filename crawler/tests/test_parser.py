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
from bs4 import BeautifulSoup
from pathlib import Path
from propertycrawler.remax import Remax
import re


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
            with pytest.warns(UserWarning, match="kaka"): # check that kaka is causing the warning and not "143"
                ids = parser.gen_id_set()
            assert all(isinstance(item, int) for item in ids), "unexpected type found"
        
        def test_gen_id_set_handles_empty_list(self,parser):
            """ checks that gen_id_set works with empty list """
            parser.json_list = []
            ids = parser.gen_id_set()
            assert ids == set(), "expected empty set"

        def test_gen_id_set_converts_string_numbers(self,parser):
            """ checks that gen_id_set converts string numbers to integers """
            parser.json_list = [{"identifier":"123"},{"identifier":"125"},{"identifier":"143"}]
            ids = parser.gen_id_set()
            assert ids == {123,125,143}, "expected all string numbers to be converted to integers"
        
        
    class TestHtmlParser:
        @pytest.fixture
        def parser(self):
            html = "<html></html>"
            yield HtmlParser(html_content=html)

        @pytest.fixture
        def get_project_root(self):
            if Path(__file__).parent.parent.name == 'crawler':
                yield Path(__file__).parent.parent
            else:
                pytest.skip(f'HTML tests skipped : directory structure unknown, \
                            tried to look for project root at: {Path(__file__).parent.parent.name}')

        @pytest.fixture
        def fp_to_example_html(self, get_project_root):
            # add your own example file
            file_path = get_project_root/'data'/'Myydään _ Markulantie 119, Turku 20320 _ 1h+kk _ RE_MAX OmaanKotiin.html'
            if not file_path.exists():
                pytest.skip(f'HTML tests skipped : Example html file not found : {file_path}')
            with open(file_path) as fp:
                yield fp

        @pytest.fixture
        def default_attribute_dict(self, fp_to_example_html):
            # Yield an example table, so it doesn't have to be generated for every test.
            bs4 = BeautifulSoup(fp_to_example_html, 'html.parser')

            attr_dict = HtmlParser.get_attributes(Remax.Listing.attr_keys, Remax.Listing.label_value_tag, bs4)

            yield attr_dict

        def test_bs4_loads(self):
            """ beautiful soup initiates a bs instance correctly """
            bs4 = BeautifulSoup("<html></html>", 'html.parser')
            assert type(bs4) == BeautifulSoup

        def test_bs4_loads_full_page(self, fp_to_example_html):
            """ Check that the example file is found, it can be printed with pytest argument -s """
            bs4 = BeautifulSoup(fp_to_example_html, 'html.parser')

            for i,line in enumerate(bs4.prettify()):
                print(line)
                if i > 10:
                    break
            assert bs4 != None

        def test_extract_list_header(self, fp_to_example_html):
            """ Check that the remax style of header can be found in the bs object """
            bs4 = BeautifulSoup(fp_to_example_html, 'html.parser')
            listing = Remax().Listing(id=0, attr_dict={'kaka':'pupu'})
            header = bs4.find(string=listing.header_html[1]).parent
            print(header)
            assert set(header).issubset(listing.header_html)
            
        def test_extract_all_attributes_to_memory(self, fp_to_example_html):
            """ Check that the perustiedot list contents can be retrieved """
            bs4 = BeautifulSoup(fp_to_example_html, 'html.parser')
            # get the list keys
            keys = Remax.Listing.attr_keys
            # get all list keys from bs4
            all_keys = bs4.find_all("div", "col-12 col-md-5 list-label")
            attr_dict= {}
            new_dict = {}

            new_dict = HtmlParser.get_attributes(keys, ("div", "col-12 col-md-7 list-value"), bs4)
            listing = Remax.Listing(0, attr_dict)
            print(listing.attr_dict.values())
            assert len(keys) == len(new_dict.keys())
            assert keys == list(new_dict.keys())

        def test_htmlparser_interface(self, default_attribute_dict, get_project_root):
            correct_listing = Remax.Listing(0, default_attribute_dict)
            file_path = get_project_root/'data'/'Myydään _ Markulantie 119, Turku 20320 _ 1h+kk _ RE_MAX OmaanKotiin.html'

            test_listing = Remax.Listing(1)
            test_listing.filepath = str(file_path)
            HtmlParser.parse(test_listing)
            assert correct_listing.attr_dict == test_listing.attr_dict

        def test_attributes_not_found_from_html(self):
            """ test that attributes that default values are set for the attributest that aren't found """
            pass            

        def test_generate_multiple_listings(self):
            pass