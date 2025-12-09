'''
@File: test_propertysite.py
@Time: 08.12.2025 17:15:44
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import pytest
from propertycrawler.remax import Remax

class TestRemax:
    """ creation
     check that values are well formed
     check that url and next page button are correct

       """
    
    @pytest.fixture
    def remax(self):
        remax = Remax()
        yield remax

    @pytest.fixture
    def populate_remax(self,remax): 
        # create multiple Listings, insert them to listing_list
        list = [remax.Listing(id=123, attr_dict={'address':'Tuomiokirkontori 1'}), 
                remax.Listing(id=456, attr_dict={'address':'Linnanaukio 2b'})
                ]
        remax.listing_list = list
        yield remax

    def test_appending_is_implemented(self, remax):
        """ Checks that list append is implemented """
        remax.listing_append(listing=remax.Listing(id=1, attr_dict={'address':'kumputie'}))

    def test_listing_list_population(self, remax, populate_remax):
        """ expectation = [remax.Listing(id=123, attr_dict={'address':'Tuomiokirkontori 1'}), 
                remax.Listing(id=456, attr_dict={'address':'Linnanaukio 2b'})
                ]
        expectation """
        assert populate_remax.listing_list != None


    class TestListing:
        @pytest.fixture
        def listing(self):
            new_listing = Remax.Listing(id=1, attr_dict={'address':'kumputie 3'})
            yield new_listing

        def test_html_formatting(self, listing):
            html_tuple = ("<div>","</div>")
            attr = "Pinta-ala"
            expectation = f"{html_tuple[0]}{attr}{html_tuple[1]}"
            listing.attr_html = html_tuple
            listing.attr_keys = ["something", attr]

            result = listing.attr_key_html(0)
            assert result == expectation