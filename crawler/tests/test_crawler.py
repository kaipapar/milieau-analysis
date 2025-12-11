'''
@File: test_crawler.py
@Time: 11.12.2025 15:52:28
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import pytest
import os
import http.server
class TestCrawler:
    """ 
     atleast test everything that doesn't have to do with wget
     -> or mock wget

     - 
       """
    @pytest.fixture
    def mock_html(self):
        """ make a html file """
        file = "test.html"
        example = '"21":{"identifier":"80440756","type":"Kiinteist\u00f6","listingType":"DETACHEDHOUSE","listingTypeLocalized":"Omakotitalo","productGroup":"APARTMENTS","district":"Perno","image":"https:\/\/images.linear.fi\/3764a7f3-3002-496c-a615-299b4c9a1cbb.jpg","town":"Turku","street_address":"Kottaraisenkatu 13","living_area":"105","lot_area":"751","lot_area_in_sqm":"751","rooms":"4h+k+s","price":"199 000","rent":"","agent_id":"5166","publish_date":"2025-10-10 17:08:25","presentationDate":"","presentationStart":"","presentationEnd":"","presentation_info":"","presentation_info_class":" hidden"}'
        with open(file, "w+") as f:
            f.write(example)
        yield file
        os.remove(file)

    @pytest.fixture
    def mock_html_url(self,mock_html):
        """ make wget use a local html file """
        arg = ""
        http.server.HTTPServer() 

    