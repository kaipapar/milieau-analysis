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

class HtmlParser:
    """ For parsing propertylisting html """
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
