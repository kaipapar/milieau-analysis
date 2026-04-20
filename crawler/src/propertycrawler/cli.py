'''
@File: cli.py
@Time: 2026-04-20
@Author: Karri Korsu 
@Version : 2.0
@Contact : kkorsu@gmail.com
@Desc: Command-line interface supporting both legacy full-pipeline and new modular step execution
'''

import argparse
import sys
from typing import Optional, List, Dict, Any, Tuple


def validate_url(url: str) -> str:
    """Validate and return URL."""
    if not isinstance(url, str):
        raise TypeError("URL must be a string.")
    if not url.startswith("http"):
        raise ValueError(f"URL is not well formed: {url}")
    return url


def validate_steps(steps_str: str) -> List[str]:
    """
    Validate and parse step sequence string.
    
    Args:
        steps_str: Comma-separated step IDs (e.g., "a,b,c" or "d,e,g")
        
    Returns:
        List of validated step IDs
        
    Raises:
        ValueError: If steps string is malformed
    """
    if not steps_str:
        raise ValueError("Steps string cannot be empty")
    
    steps = [s.strip().lower() for s in steps_str.split(",")]
    valid_steps = set("abcdefgh")
    
    for step in steps:
        if step not in valid_steps:
            raise ValueError(f"Invalid step '{step}'. Valid steps: a-h")
    
    return steps


class CLIArgs:
    """Structured CLI arguments for readability."""
    
    def __init__(self):
        self.command: Optional[str] = None  # "full" or "step"
        self.url: Optional[str] = None
        self.steps: Optional[List[str]] = None
        self.only: bool = False  # If True, run ONLY the specified steps; else run X and all following
        self.verbose: bool = False
        self.session_id: Optional[str] = None
        self.base_dir: Optional[str] = None
        
        # Step-specific arguments
        self.listing_list_dir: Optional[str] = None
        self.listing_dir: Optional[str] = None
        self.dedup_csv: Optional[str] = None
        self.output_path: Optional[str] = None


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        prog='crawler',
        description='Crawls property listing sites for apartment data and converts to GIS-compatible format',
        epilog='Examples:\n'
               '  crawler full "https://remax.fi/..."\n'
               '  crawler step -o a,b --url "https://remax.fi/..."\n'
               '  crawler step d --listing-dir ./data/listings/',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # =========================================================================
    # FULL command (backward compatible)
    # =========================================================================
    full_parser = subparsers.add_parser(
        'full',
        help='Run full crawling pipeline (default mode)'
    )
    full_parser.add_argument('url', help='PHP listing query URL')
    full_parser.add_argument('--session-id', help='Override auto-generated session ID')
    full_parser.add_argument('--base-dir', help='Override base data directory (default: ./data/remax/)')
    full_parser.add_argument('-v', '--verbose', action='store_true', help='Print results after each step')
    
    # =========================================================================
    # STEP command (new modular interface)
    # =========================================================================
    step_parser = subparsers.add_parser(
        'step',
        help='Run specific workflow step(s) with fine-grained control'
    )
    
    # First positional is the starting step (optional with -o)
    step_parser.add_argument(
        'step',
        nargs='?',
        help='Starting step (a-h). Run this step and all following. Ignored if -o is specified.'
    )
    
    # Global step options
    step_parser.add_argument(
        '-o', '--only',
        metavar='STEPS',
        help='Run ONLY these consecutive steps (e.g., "a,b,c" or "d,e,g"). '
             'Non-consecutive steps fail upfront with dependency error.'
    )
    step_parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Print results after each step'
    )
    step_parser.add_argument(
        '--session-id',
        help='Override auto-generated session ID'
    )
    step_parser.add_argument(
        '--base-dir',
        help='Override base data directory (default: ./data/remax/)'
    )
    
    # Step-specific input options
    step_parser.add_argument(
        '--url',
        metavar='URL',
        help='[Step a] PHP listing query URL to crawl'
    )
    step_parser.add_argument(
        '--listing-list-dir',
        metavar='DIR',
        help='[Step b,d] Path to listing_lists/ directory (for parsing step b)'
    )
    step_parser.add_argument(
        '--listing-dir',
        metavar='DIR',
        help='[Step d] Path to listings/ directory containing HTML files'
    )
    step_parser.add_argument(
        '--dedup-csv',
        metavar='PATH',
        help='[Step f] CSV file to check for duplicate IDs'
    )
    step_parser.add_argument(
        '--output-path',
        metavar='PATH',
        help='[Step h] Custom CSV output path'
    )
    
    return parser


def argparser(args: List[str]) -> CLIArgs:
    """
    Parse command-line arguments and return structured CLIArgs.
    
    Args:
        args: Command-line arguments (usually sys.argv[1:])
        
    Returns:
        CLIArgs object with validated arguments
        
    Raises:
        SystemExit: If arguments are invalid (argparse handles this)
    """
    # Backward compatibility: if first arg is a URL (not a command), prepend 'full'
    if args and args[0].startswith('http'):
        args = ['full'] + args
    
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    cli_args = CLIArgs()
    cli_args.verbose = getattr(parsed, 'verbose', False)
    cli_args.session_id = getattr(parsed, 'session_id', None)
    cli_args.base_dir = getattr(parsed, 'base_dir', None)
    
    # Handle case where no command given - show help
    if parsed.command is None:
        parser.print_help()
        raise SystemExit(1)
    
    cli_args.command = parsed.command
    
    if parsed.command == 'full':
        cli_args.url = validate_url(parsed.url)
    
    elif parsed.command == 'step':
        # Parse steps: either from -o flag or positional argument
        if parsed.only:
            cli_args.steps = validate_steps(parsed.only)
            cli_args.only = True
        elif parsed.step:
            # Starting step provided
            starting_step = validate_steps(parsed.step)[0]
            # Generate list from starting step to end (will be expanded in main)
            cli_args.steps = [starting_step]
            cli_args.only = False
        else:
            parser.error('step command requires either a step name or --only option')
        
        # Collect step-specific arguments
        cli_args.url = parsed.url
        cli_args.listing_list_dir = parsed.listing_list_dir
        cli_args.listing_dir = parsed.listing_dir
        cli_args.dedup_csv = parsed.dedup_csv
        cli_args.output_path = parsed.output_path
    
    return cli_args


def print_cli_args(args: CLIArgs) -> None:
    """Pretty-print parsed arguments for debugging."""
    print(f"Command: {args.command}")
    print(f"Steps: {args.steps}")
    print(f"Only mode: {args.only}")
    print(f"Verbose: {args.verbose}")
    if args.url:
        print(f"URL: {args.url}")
    if args.listing_list_dir:
        print(f"Listing list dir: {args.listing_list_dir}")
    if args.listing_dir:
        print(f"Listing dir: {args.listing_dir}")
