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
    def __init__(self):
        self.url=""

class Remax(PropertySite):
    def __init__(self):
        self.url=""

