'''
@File: test_cli.py
@Time: 08.12.2025 15:19:02
@Author: Karri Korsu 
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: None
'''

import pytest
import propertycrawler.cli as cli

class TestArgparser:
    well_formed_remax_url= "https://remax.fi/myytavat-asunnot/turku/"


    def test_no_input(self):
        """ Tests the edge case of no argument given as input. The argparse library should be handling this as SystemExit """
        with pytest.raises(SystemExit) as excinfo:
                cli.argparser(None)  # the function ignores its args parameter anyway

            # argparse exits with code 2 on parsing errors
        assert excinfo.value.code == 2

    def test_url_as_input(self):
        """ Tests the proper usage of the function, an url should be passed through the function unscathed  """
        assert cli.argparser([TestArgparser.well_formed_remax_url]).url == TestArgparser.well_formed_remax_url
    
    def test_integer_as_input_typeerror(self):
        """ An integer should raise a type error at argparser level. exit value 2 -> cli usage error """
        arg = 0
        with pytest.raises(TypeError) as excinfo:
            cli.argparser([int(arg)])
        assert excinfo.value.code == 2 
    
    def test_string_as_input_valueerror(self):
        """ All non well formed urls are not accepted, which extends to all strings other than urls """
        arg = "some string"
        with pytest.raises(ValueError) as excinfo:
            cli.argparser([arg])
        #assert excinfo.value == 2 

    def test_output_type(self):
        """ The result type of argparser should be argparse.Namespace """
        assert type(cli.argparser([TestArgparser.well_formed_remax_url])) == cli.argparse.Namespace
        
