'''
@File: test_cli.py (Phase 2)
@Time: 2026-04-20
@Author: Karri Korsu
@Version : 2.0
@Contact : kkorsu@gmail.com
@Desc: Tests for the new modular CLI interface
'''

import pytest
from propertycrawler.cli import argparser, validate_url, validate_steps, CLIArgs


class TestValidateFunctions:
    """Test validation helper functions."""

    def test_validate_url_valid(self):
        """Test that valid URL passes."""
        url = "https://remax.fi/wp-content/themes/blocksy-child/property_search_LINEAR.php"
        result = validate_url(url)
        assert result == url

    def test_validate_url_invalid_no_http(self):
        """Test that non-http URL fails."""
        with pytest.raises(ValueError):
            validate_url("ftp://example.com")

    def test_validate_url_invalid_type(self):
        """Test that non-string URL fails."""
        with pytest.raises(TypeError):
            validate_url(123)

    def test_validate_steps_valid_single(self):
        """Test that single step validates."""
        steps = validate_steps("a")
        assert steps == ["a"]

    def test_validate_steps_valid_multiple(self):
        """Test that multiple steps validate."""
        steps = validate_steps("a,b,c")
        assert steps == ["a", "b", "c"]

    def test_validate_steps_valid_with_spaces(self):
        """Test that steps with spaces validate."""
        steps = validate_steps("d, e, g")
        assert steps == ["d", "e", "g"]

    def test_validate_steps_invalid_step(self):
        """Test that invalid step fails."""
        with pytest.raises(ValueError):
            validate_steps("a,z,c")

    def test_validate_steps_empty(self):
        """Test that empty string fails."""
        with pytest.raises(ValueError):
            validate_steps("")


class TestCLIArgsParsing:
    """Test CLI argument parsing."""

    def test_full_command_basic(self):
        """Test parsing 'full' command with URL."""
        args = argparser(['full', 'https://example.com/api'])
        
        assert args.command == 'full'
        assert args.url == 'https://example.com/api'
        assert args.verbose is False

    def test_full_command_with_verbose(self):
        """Test parsing 'full' command with verbose flag."""
        args = argparser(['full', 'https://example.com/api', '--verbose'])
        
        assert args.command == 'full'
        assert args.verbose is True

    def test_step_command_only_mode(self):
        """Test parsing 'step' command with --only."""
        args = argparser(['step', '--only', 'a,b,c'])
        
        assert args.command == 'step'
        assert args.steps == ['a', 'b', 'c']
        assert args.only is True

    def test_step_command_range_mode(self):
        """Test parsing 'step' command with starting step."""
        args = argparser(['step', 'd'])
        
        assert args.command == 'step'
        assert args.steps == ['d']
        assert args.only is False

    def test_step_command_with_url(self):
        """Test parsing 'step' command with --url."""
        args = argparser(['step', '--only', 'a,b', '--url', 'https://example.com/api'])
        
        assert args.command == 'step'
        assert args.url == 'https://example.com/api'

    def test_step_command_with_directories(self):
        """Test parsing 'step' command with directory arguments."""
        args = argparser([
            'step', 'd',
            '--listing-dir', '/path/to/listings',
            '--listing-list-dir', '/path/to/lists'
        ])
        
        assert args.listing_dir == '/path/to/listings'
        assert args.listing_list_dir == '/path/to/lists'

    def test_step_command_with_dedup(self):
        """Test parsing 'step' command with dedup CSV."""
        args = argparser(['step', '--only', 'f,h', '--dedup-csv', 'existing.csv', '--output-path', 'new.csv'])
        
        assert args.dedup_csv == 'existing.csv'
        assert args.output_path == 'new.csv'

    def test_backward_compat_full_url_only(self):
        """Test backward compatibility: URL as first positional argument (legacy mode)."""
        # Legacy: crawler <url>
        args = argparser(['https://example.com/api'])
        
        # Should auto-detect as 'full' command
        assert args.command == 'full'
        assert args.url == 'https://example.com/api'

    def test_step_with_session_id(self):
        """Test parsing with custom session ID."""
        args = argparser(['step', 'd', '--session-id', 'my_session_123'])
        
        assert args.session_id == 'my_session_123'

    def test_step_with_base_dir(self):
        """Test parsing with custom base directory."""
        args = argparser(['step', 'd', '--base-dir', '/custom/data/path'])
        
        assert args.base_dir == '/custom/data/path'


class TestCLIArgsStructure:
    """Test CLIArgs data structure."""

    def test_cli_args_initialization(self):
        """Test that CLIArgs initializes with None values."""
        args = CLIArgs()
        
        assert args.command is None
        assert args.url is None
        assert args.steps is None
        assert args.only is False
        assert args.verbose is False
        assert args.session_id is None
        assert args.listing_dir is None

    def test_cli_args_setters(self):
        """Test that CLIArgs values can be set."""
        args = CLIArgs()
        args.command = 'step'
        args.steps = ['a', 'b']
        args.verbose = True
        
        assert args.command == 'step'
        assert args.steps == ['a', 'b']
        assert args.verbose is True
