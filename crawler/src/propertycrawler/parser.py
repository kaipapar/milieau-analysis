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
class HtmlParser:
    """ For parsing propertylisting html """
    pass
class JsonParser:
    """ For parsing remax php search response """
    def __init__(self,json_list):
        self.json_list = json_list
    
    def _get_id(self, index, id = "identifier") -> int:
        return self.json_list[index][id]

    def get_ids(self) -> set:
        l = len(self.json_list)
        i = 0
        ids = set()
        while (i < l):
            ids.add(self._get_id(i))
            i+=1
        return ids
