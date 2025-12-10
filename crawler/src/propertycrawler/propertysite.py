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
    """ Abstract base class which houses an outline on how to implement a PropertySite class """
    url = ""            # baseurl for the listinglist page
    next_page = ""      # next page button html
    php_query_url=""    # where the listinglist is accessed
    def __init__(self):
        self.listing_list = []
        
    class Listing(abc.ABC):
        """ Information about specific listings """
        url = ""            # baseurl for all listings
        list_header = ""    # list header name
        header_html = ()    # html list header element structure
        label_value_tag = ()      # attribute list html element structure
        attr_keys = []      # attribute titles from html

        def __init__(self, id, attr_dict):
            self.id = id        # url + id -> listing location on website
            self.attr_dict = attr_dict # listing attributes with title and value

        def attr_label_html(self,index):
            """ returns HTML element with list tag and list label  """
            return type(self).label_value_tag[0]+type(self).attr_keys[index]+"</"+type(self).label_value_tag[0][1:4]+">"

        def attr_value_html(self,index):
            """ returns HTML element with list tag and list value """
            pass

    def next_page(self):
        raise NotImplementedError("next page method not implemented")

    def listing_append(self):
        raise NotImplementedError("listing_append() not implemented")

    
