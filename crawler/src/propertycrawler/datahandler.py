'''
@File: datahandler.py
@Time: 05.12.2025 17:17:45
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import json
class IO:
    """ save and retrieve from disk """
    def get_json(self, path):
        with open(path,'r') as file:
            d = json.load(file) 
        return d[0]