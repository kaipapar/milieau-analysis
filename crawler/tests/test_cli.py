'''
@File: test_cli.py
@Time: 2026-04-20
@Author: Karri Korsu 
@Version : 2.0
@Contact : kkorsu@gmail.com
@Desc: Tests for backward compatibility with old CLI and new CLIArgs structure
'''

import pytest
import propertycrawler.cli as cli

class TestArgparser:
    well_formed_remax_url= "https://remax.fi/myytavat-asunnot/turku/"


    def test_no_input(self):
        """ Tests the edge case of no argument given as input. Should raise SystemExit """
        with pytest.raises(SystemExit) as excinfo:
            cli.argparser([])
        # argparse exits with code 1 on no command
        assert excinfo.value.code == 1

    def test_url_as_input(self):
        """ Tests backward compatibility: URL as first positional arg becomes 'full' command """
        result = cli.argparser([TestArgparser.well_formed_remax_url])
        assert result.url == TestArgparser.well_formed_remax_url
        assert result.command == 'full'

    def test_integer_as_input_typeerror(self):
        """ An integer should raise a type error at argparser level """
        with pytest.raises(TypeError):
            cli.argparser([0])
    
    def test_string_as_input_valueerror(self):
        """ All non well formed urls are not accepted """
        # With new CLI using subcommands, invalid input will cause SystemExit from argparse
        with pytest.raises(SystemExit):
            cli.argparser(["some string"])

    def test_output_type(self):
        """ The result type of argparser should be CLIArgs """
        result = cli.argparser([TestArgparser.well_formed_remax_url])
        assert type(result) == cli.CLIArgs
        assert hasattr(result, 'url')
        assert hasattr(result, 'command')

