'''
@File: test_propertysite.py
@Time: 08.12.2025 17:15:44
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import pytest
from propertycrawler.propertysite import Remax

class TestRemax:
    """ creation
     check that values are well formed
     check that url and next page button are correct

       """
    def test_appending_is_implemented(self):
        """ Checks that list append is implemented """
        remax = Remax()
        
        with pytest.raises(NotImplementedError) as excinfo:
                remax.listing_append(listing=remax.Listing())  # the function ignores its args parameter anyway   

    class TestListing:
        def test_html_formatting(self):
            html_tuple = ("<div>","</div>")
            attr = "Pinta-ala"
            expectation = f"{html_tuple[0]}{attr}{html_tuple[1]}"
            object = Remax.Listing()
            object.attr_html = html_tuple
            object.attr_keys = ["something", attr]

            result = object.attr_key_html(1)
            assert result == expectation