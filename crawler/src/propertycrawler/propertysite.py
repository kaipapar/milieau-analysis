'''
@File: propertysite.py
@Time: 05.12.2025 17:17:43
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import abc

class PropertySite(abc.ABC):
    """ Abstract base class which houses an outline on how to implement a PropertySite class"""
    url = ""
    next_page = ""
    def __init__(self):
        self.listing_list = [] # houses a list of Listing type objects
        
    class Listing(abc.ABC):
        """ Information about specific listings """
        # the following are not instance specific
        url = ""
        list_header = ""
        header_html = ()
        attr_html = () # attribute list html element
        attr_keys = [] # attribute titles from html

        def __init__(self, id, attr_dict):
            self.id = id
            self.attr_dict = attr_dict # once they are retrieved they can be unordered because different sites may have different order of attributes

        def attr_key_html(self,index):
            return f"{type(self).attr_html[0]}{type(self).attr_keys[index]}{type(self).attr_html[1]}"



    def listing_append(self):
        raise NotImplementedError("listing_append() not implemented")


class Remax(PropertySite):
    def __init__(self):
        super().__init__()
        self.url="https://remax.fi/myytavat-asunnot/"
    
    class Listing(PropertySite.Listing):
        url = "https://remax.fi/kohde/"
        attr_html = ("<div>","</div>")
        attr_keys = ["Pinta-ala"]
        def __init__(self, id: int, attr_dict: dict):
            super().__init__(id=id, attr_dict=attr_dict)


    def listing_append(self, listing=None):
        if listing is None:
            listing = self.Listing()  # create a new listing if none provided
        self.listing_list.append(listing)


    
