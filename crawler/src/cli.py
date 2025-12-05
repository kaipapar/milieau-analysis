'''
@File: cli.py
@Time: 05.12.2025 17:17:50
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''
import argparse

def argparser(args):
    parser = argparse.ArgumentParser(
                        prog='crawler',
                        description=' Crawls a property listing site for apartment listings, converts them into GDF for GIS usage.',
                        epilog='Text at the bottom of help')
    
    parser.add_argument('url')           # positional argument
    """ 
    parser.add_argument('-c',)      # option that takes a value
    parser.add_argument('-v', '--verbose',
                    action='store_true')  # on/off flag """
    
    args = parser.parse_args()
    print(args.url)
    return args