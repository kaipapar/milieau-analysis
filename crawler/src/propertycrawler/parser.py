'''
@File: parser.py
@Time: 05.12.2025 17:17:47
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import json
from .datahandler import IO
class HtmlParser:
    """ For parsing propertylisting html """
    pass
class JsonParser:
    """ For parsing remax php search response """
    def get_id(self, line) -> int:
        pass
    def get_ids(self,json) -> set:
        l = len(json)
        i = 0
        ids = set()
        while (i < l):
            ids.add(self.get_id(i))
        return ids
