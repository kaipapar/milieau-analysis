'''
@File: datahandler.py
@Time: 05.12.2025 17:17:45
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import json
import warnings
import io

class IO:
    """ save and retrieve from disk """
    def get_json(path):
        with open(path,'r') as file:
            #d = json.load(file) 
            d = file.read()
            print(d)
            json.JSONDecoder().decode(s=d)
        return d