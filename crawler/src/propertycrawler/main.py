'''
@File: main.py
@Time: 2026-04-20
@Author: Karri Korsu 
@Version : 2.0
@Contact : kkorsu@gmail.com
@Desc: Main entry point for property crawler. Supports both legacy full-pipeline and new modular step execution.
'''

import sys
import warnings
from typing import List, Optional

from propertycrawler.cli import argparser, CLIArgs
from propertycrawler.execution_context import ExecutionContext
from propertycrawler.steps import STEP_REGISTRY, validate_step_sequence


class StepExecutionError(Exception):
    """Raised when a step fails to execute."""
    pass


class StepDependencyError(Exception):
    """Raised when step dependencies are not satisfied."""
    pass


def expand_step_range(starting_step: str) -> List[str]:
    """
    Expand a starting step to include all following steps.
    
    Args:
        starting_step: Single step ID (a-h)
        
    Returns:
        List of steps from starting_step to 'h'
    """
    all_steps = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    idx = all_steps.index(starting_step)
    return all_steps[idx:]


def execute_full_pipeline(url: str, context: ExecutionContext, verbose: bool = False) -> None:
    """
    Execute the full crawling pipeline (a → h).
    
    Args:
        url: PHP listing query URL
        context: ExecutionContext for state management
        verbose: Print results after each step
        
    Raises:
        StepExecutionError: If any step fails
    """
    print(f"\n{'='*70}")
    print(f"Starting FULL pipeline")
    print(f"{'='*70}\n")
    
    # Full pipeline: a → b → c → d → e → g → h (skipping f by default)
    steps_to_run = ['a', 'b', 'c', 'd', 'e', 'g', 'h']
    
    context.ensure_session_dir()
    
    try:
        for step_id in steps_to_run:
            step = STEP_REGISTRY[step_id]
            print(f"\n▶ Executing Step {step_id.upper()}: {step.name}")
            print(f"-{'-'*68}")
            
            try:
                # Execute step with appropriate arguments
                if step_id == 'a':
                    step.execute(context, url=url, verbose=verbose)
                elif step_id == 'b':
                    step.execute(context, listing_list_dir=None, verbose=verbose)
                elif step_id == 'c':
                    step.execute(context, verbose=verbose)
                elif step_id == 'd':
                    step.execute(context, listing_dir=None, verbose=verbose)
                else:  # e, g, h
                    step.execute(context, verbose=verbose)
                    
            except Exception as e:
                raise StepExecutionError(f"Step {step_id.upper()} failed: {e}")
        
        print(f"\n{'='*70}")
        print(f"✓ Full pipeline completed successfully!")
        print(f"Output: {context.get_csv_output_path()}")
        print(f"{'='*70}\n")
        
    except StepExecutionError as e:
        print(f"\n✗ Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)


def execute_step_pipeline(steps_to_run: List[str], cli_args: CLIArgs, 
                         context: ExecutionContext, verbose: bool = False) -> None:
    """
    Execute a specific sequence of steps with user-provided arguments.
    
    Args:
        steps_to_run: List of step IDs to execute (e.g., ['d', 'e', 'g'])
        cli_args: CLIArgs with step-specific options
        context: ExecutionContext for state management
        verbose: Print results after each step
        
    Raises:
        StepExecutionError: If any step fails
        StepDependencyError: If dependencies are not satisfied
    """
    print(f"\n{'='*70}")
    print(f"Starting STEP pipeline: {', '.join(steps_to_run).upper()}")
    print(f"{'='*70}\n")
    
    # Validate step sequence
    is_valid, error = validate_step_sequence(steps_to_run)
    if not is_valid:
        print(f"\n✗ Invalid step sequence: {error}", file=sys.stderr)
        print(f"Hint: Check that all dependencies are satisfied or provided explicitly.", file=sys.stderr)
        sys.exit(1)
    
    context.ensure_session_dir()
    
    try:
        for step_id in steps_to_run:
            step = STEP_REGISTRY[step_id]
            print(f"\n▶ Executing Step {step_id.upper()}: {step.name}")
            print(f"-{'-'*68}")
            
            try:
                # Check if dependencies are satisfied
                if not step.validate_dependencies(context):
                    missing = step.dependencies
                    raise StepDependencyError(
                        f"Step {step_id} requires input from step(s) {missing}. "
                        f"Either run those steps first or provide explicit input via flags."
                    )
                
                # Execute step with user-provided arguments
                if step_id == 'a':
                    if not cli_args.url:
                        raise ValueError("Step a requires --url argument")
                    step.execute(context, url=cli_args.url, verbose=verbose)
                    
                elif step_id == 'b':
                    step.execute(context, listing_list_dir=cli_args.listing_list_dir, verbose=verbose)
                    
                elif step_id == 'c':
                    step.execute(context, verbose=verbose)
                    
                elif step_id == 'd':
                    step.execute(context, listing_dir=cli_args.listing_dir, verbose=verbose)
                    
                elif step_id == 'e':
                    step.execute(context, verbose=verbose)
                    
                elif step_id == 'f':
                    step.execute(context, dedup_csv=cli_args.dedup_csv, verbose=verbose)
                    
                elif step_id == 'g':
                    step.execute(context, verbose=verbose)
                    
                elif step_id == 'h':
                    step.execute(context, output_path=cli_args.output_path, verbose=verbose)
                
                # Print result if verbose
                if verbose:
                    print(f"✓ Step {step_id.upper()} completed successfully")
                    
            except (StepDependencyError, ValueError) as e:
                raise StepExecutionError(str(e))
            except Exception as e:
                raise StepExecutionError(f"Step {step_id.upper()} failed: {e}")
        
        print(f"\n{'='*70}")
        print(f"✓ Step pipeline completed successfully!")
        if 'h' in steps_to_run:
            print(f"Output: {context.get_csv_output_path(cli_args.output_path)}")
        print(f"{'='*70}\n")
        
    except StepExecutionError as e:
        print(f"\n✗ Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the crawler application."""
    try:
        cli_args = argparser(sys.argv[1:])
    except SystemExit as e:
        if e.code != 0:
            raise
        sys.exit(0)
    
    # Initialize execution context
    context = ExecutionContext(
        session_id=cli_args.session_id,
        base_data_path=cli_args.base_dir
    )
    
    if cli_args.command == 'full':
        # Execute full pipeline (backward compatible)
        execute_full_pipeline(cli_args.url, context, verbose=cli_args.verbose)
    
    elif cli_args.command == 'step':
        # Expand step range if starting step given without -o
        steps_to_run = cli_args.steps
        if not cli_args.only and len(cli_args.steps) == 1:
            # Expand from starting step to end
            steps_to_run = expand_step_range(cli_args.steps[0])
        
        # Execute step pipeline
        execute_step_pipeline(steps_to_run, cli_args, context, verbose=cli_args.verbose)
    
    else:
        print("Error: Unknown command", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()







        

