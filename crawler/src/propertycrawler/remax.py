'''
@File: remax.py
@Time: 09.12.2025 18:30:08
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

from .propertysite import PropertySite
from .constants import REMAX_ATTR_KEYS as ATTR_KEYS

class Remax(PropertySite):
    url="https://remax.fi/myytavat-asunnot/"
    
    def __init__(self):
        super().__init__()
    
    class Listing(PropertySite.Listing):
        url = "https://remax.fi/kohde/"
        list_header = "<h5>Perustiedot</h5>"
        label_value_tag = ('<div class="col-12 col-md-5 list-label">',
                           '<div class="col-12 col-md-7 list-value">')
        attr_keys = ATTR_KEYS
        def __init__(self, id: int, attr_dict: dict):
            super().__init__(id=id, attr_dict=attr_dict)


    def listing_append(self, listing=None):
        if listing is None:
            listing = self.Listing()  # create a new listing if none provided
        self.listing_list.append(listing)

