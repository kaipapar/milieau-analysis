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
import os
import pathlib

class IO:
    """ save and retrieve from disk """
    def get_json(path) -> list | str:
        d = []
        with open(path,'r') as file:
            d = json.load(file) #not used so the file can be inspected in stdout before throwing an error.
            """ for line in file:
                d.append(line)             
                print(line)
                json.JSONDecoder().decode(s=d) """
        return d
    
    def get_html(path) -> list:
        d = []
        with open(path,'r') as file:
             for line in file:
                  d.append(line)
        return d
    
    def get_file(path: str):
        path = pathlib.Path(path) #TODO refactoring str literal paths to Path type...
        try:
            path.exists()
        except FileNotFoundError:
            return
        with open(path) as file:
            return file
                  

            
    
    def is_empty(filepath) -> bool:
        """ returns True if file is "empty" or doesn't exist. In use with crawler methods. """
        threshold = 100 #in bytes, it seems a empty file returned by wget is 2 bytes and a full one ~13k bytes
        if (os.path.exists(filepath)):
            if (os.path.getsize(filepath) > threshold):
                return False
        return True