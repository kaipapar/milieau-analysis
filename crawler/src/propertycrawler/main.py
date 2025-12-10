'''
@File: main.py
@Time: 05.12.2025 17:16:41
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
from sys import argv
from remax import Remax
from cli import argparser
from datahandler import IO
from parser import JsonParser
if __name__ == "__main__":
    args = argparser(argv[1:])

    remax = Remax()
    remax.url = args.url
    io = IO()
    listings = io.get_json("data/property_search_LINEAR.php.html")
    print(listings)
    json = JsonParser(listings)
    print('getting ids')
    print(json.get_ids())





        

