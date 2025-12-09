'''
@File: main.py
@Time: 05.12.2025 17:16:41
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
from sys import argv
from propertysite import Remax
from cli import argparser

if __name__ == "__main__":
    args = argparser(argv[1:])

    if 1:
        remax = Remax()
        remax.url = args.url
        remax.listing_append(remax.Listing())

        

