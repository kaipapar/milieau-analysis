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
from propertysite import PropertySite
from datahandler import IO

# need this more verbose import for checking whether listing is instance Remax.Listing
from propertycrawler.remax import Remax 

class HtmlParser:
    """ Logic parsing propertylisting html """
    @staticmethod
    def get_attributes(keys: list, list_value_tag: tuple, bs: BeautifulSoup) -> dict:
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
        print("new_dict***",new_dict, "\n")
        return new_dict
    @staticmethod
    def parse(listing: PropertySite.Listing):
        """ Interface for HTMLparser. Parses one listing page """
        #IO.get_file()
        with open(listing.filepath) as file:
        #file = open(listing.filepath) # leaves file open...
        #bs = BeautifulSoup(IO.get_file(listing.filepath), 'html.parser') #needs a pointer to the html file.
        #bs = BeautifulSoup(listing.filepath, 'html.parser') #needs a pointer to the html file.
            bs = BeautifulSoup(file, 'html.parser') #needs a pointer to the html file.
            print("*****type:", type(listing))
            print("**another type:", type(Remax.Listing))

            match type(listing):
                case Remax.Listing:
                    print("\nsuccess****")        
                    listing.attr_dict = HtmlParser.get_attributes(
                        keys=Remax.Listing.attr_keys,
                        list_value_tag=Remax.Listing.label_value_tag,
                        bs=bs
                    )
                case _:
                    print("Not found ***")
                    warn(f"listing variable type handling is unknown: type: {type(listing)}")
        #file.close()
    
    @staticmethod
    def parse_listings(listings: set[PropertySite.Listing]):
        """ cycle through listings and parse them all """
        for listing in listings:
            HtmlParser.parse(listing)
            
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
