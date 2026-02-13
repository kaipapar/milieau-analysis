'''
@File: parser.py
@Time: 05.12.2025 17:17:47
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import json
from datahandler import IO
from warnings import warn
from bs4 import BeautifulSoup
import re
from propertycrawler.propertysite import PropertySite
from propertycrawler.remax import Remax

class HtmlParser:
    """ Logic parsing propertylisting html """
    def get_attributes(keys : list, list_value_tag : tuple, bs: BeautifulSoup) -> dict:
        new_dict = {}
        for item in keys:
            label = bs.find("div", string=re.compile(item))
            try:
                new_dict[label.get_text()] = label.parent.find_next(list_value_tag[0], list_value_tag[1]).get_text()
            except AttributeError: # the label hasn't been found -> add the key value pair as default
                # new_dict.setdefault(item)
                new_dict[item] = None
            finally:
                print('label: ', item)
                print('value: ', new_dict[item])
        return new_dict
    def parse(listing: PropertySite.Listing, bs):
        pass # unfinished
        match type(listing):
            case Remax.Listing:
                HtmlParser.get_attributes(keys = Remax.Listing.attr_keys, \
                                          list_value_tag = Remax.Listing.label_value_tag, \
                                          bs = bs )
            
    pass
class JsonParser:
    """ For parsing remax php search response """
    def __init__(self,json_list):
        self.json_list = json_list
    
    def _get_id(self, index, id = "identifier") -> int:
        return self.json_list[index][id]

    def gen_id_set(self) -> set:
        """ return set of property listing IDs from the php response json list.
            They are used to generate urls. """
        l = len(self.json_list)
        i = 0
        ids = set()
        while (i < l):
            n = self._get_id(i)
            # validation
            try:
                n = int(n)
            except ValueError:
                warn(f"Invalid id found in json list: {n}, skipping...")
            else:
                ids.add(n)
            i+=1
        return ids
