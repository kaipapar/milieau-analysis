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
    url = str
    next_page = str
    def __init__(self):
        self.listing_list = list
        
    class Listing(abc.ABC):
        """ Information about specific listings """
        # the following are not instance specific
        url = str
        list_header = str
        header_html = tuple
        attr_html = tuple
        attr_keys = list # keys are ordered because they are retrieved in a specific order

        def __init__(self):
            self.id = int
            self.attribute_dict = dict # once they are retrieved they can be unordered because different sites may have different order of attributes

        def attr_key_html(self,index):
            return f"{type(self).attr_html[0]}{type(self).attr_keys[index]}{type(self).attr_html[1]}"



    def listing_append():
        raise NotImplementedError("listing_append() not implemented")


class Remax(PropertySite):
    class Listing(PropertySite.Listing):
        url = "https://remax.fi/kohde/"

    def __init__(self):
        self.url="https://remax.fi/myytavat-asunnot/"

    def listing_append(self, listing=Listing()):
        self.listing_list.append(listing)

    
