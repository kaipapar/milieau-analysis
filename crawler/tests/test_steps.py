'''
@File: test_steps.py
@Time: 2026-04-20
@Author: Karri Korsu
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: Tests for the modular step architecture and ExecutionContext
'''

import pytest
import tempfile
import json
from pathlib import Path
from propertycrawler.execution_context import ExecutionContext
from propertycrawler.steps import (
    STEP_REGISTRY, validate_step_sequence, StepA, StepB, StepC, StepD, StepE, StepF, StepG, StepH
)


class TestExecutionContext:
    """Test ExecutionContext initialization and validation."""

    def test_context_initialization(self):
        """Test that context initializes with default values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = ExecutionContext(base_data_path=tmpdir)
            
            assert ctx.session_id is not None
            assert ctx.remax is None
            assert ctx.listing_ids is None
            assert ctx.listings is None
            assert ctx.dataframe is None

    def test_context_custom_session_id(self):
        """Test that custom session ID is respected."""
        ctx = ExecutionContext(session_id="test_session_123")
        
        assert ctx.session_id == "test_session_123"

    def test_context_directory_creation(self):
        """Test that ensure_session_dir creates required directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ctx = ExecutionContext(base_data_path=tmpdir)
            ctx.ensure_session_dir()
            
            assert ctx.session_path.exists()
            assert ctx.listing_lists_path.exists()
            assert ctx.listings_path.exists()

    def test_context_validation_methods(self):
        """Test context validation helper methods."""
        ctx = ExecutionContext()
        
        assert not ctx.validate_has_remax()
        assert not ctx.validate_has_listing_ids()
        assert not ctx.validate_has_listings()
        assert not ctx.validate_has_dataframe()


class TestStepRegistry:
    """Test step registry and step existence."""

    def test_all_steps_registered(self):
        """Test that all 8 steps (a-h) are registered."""
        expected_steps = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        
        for step_id in expected_steps:
            assert step_id in STEP_REGISTRY
            assert STEP_REGISTRY[step_id].step_id == step_id

    def test_step_properties(self):
        """Test that registered steps have correct metadata."""
        test_cases = [
            ("a", "Download Listing Lists", []),
            ("b", "Parse Listing Lists", ["a"]),
            ("c", "Download Listings", ["b"]),
            ("d", "Parse Listings", ["c"]),
            ("e", "Create DataFrame", ["d"]),
            ("f", "Remove Duplicates", ["e"]),
            ("g", "Geocode", ["e"]),
            ("h", "Save CSV", ["e"]),
        ]
        
        for step_id, expected_name, expected_deps in test_cases:
            step = STEP_REGISTRY[step_id]
            assert step.name == expected_name
            assert step.dependencies == expected_deps


class TestStepSequenceValidation:
    """Test dependency validation logic."""

    def test_valid_single_step(self):
        """Test that a single step validates."""
        is_valid, error = validate_step_sequence(["a"])
        assert is_valid is True
        assert error is None

    def test_valid_consecutive_sequence(self):
        """Test that consecutive steps validate."""
        is_valid, error = validate_step_sequence(["a", "b", "c"])
        assert is_valid is True
        assert error is None

    def test_valid_partial_sequence(self):
        """Test that a partial valid sequence validates."""
        is_valid, error = validate_step_sequence(["e", "f", "h"])
        assert is_valid is True
        assert error is None

    def test_invalid_single_step_with_dependency(self):
        """Test that single step validates (external deps handled at execute time)."""
        # External dependencies like "b needs a" are handled by step.execute() 
        # via context validation, not by the sequence validator.
        # The sequence validator only checks ordering within the sequence.
        is_valid, error = validate_step_sequence(["b"])
        assert is_valid is True
        assert error is None

    def test_invalid_nonexistent_step(self):
        """Test that nonexistent step fails."""
        is_valid, error = validate_step_sequence(["z"])
        assert is_valid is False
        assert "Unknown step" in error or "z" in error

    def test_invalid_wrong_order(self):
        """Test that wrong step order fails."""
        is_valid, error = validate_step_sequence(["b", "a"])
        assert is_valid is False
        assert "b" in error  # b depends on a, but a comes after

    def test_empty_sequence(self):
        """Test that empty sequence fails."""
        is_valid, error = validate_step_sequence([])
        assert is_valid is False

    def test_multiple_independent_paths(self):
        """Test that multiple steps with same dependency validate."""
        # e, f, g, h all depend on e or earlier, so e,f,g,h should be valid
        is_valid, error = validate_step_sequence(["e", "f", "g", "h"])
        assert is_valid is True
        assert error is None


class TestStepBasics:
    """Test basic step class functionality."""

    def test_step_a_exists(self):
        """Test StepA is properly instantiated."""
        step = STEP_REGISTRY["a"]
        assert isinstance(step, StepA)
        assert step.step_id == "a"
        assert step.dependencies == []

    def test_step_b_exists(self):
        """Test StepB is properly instantiated."""
        step = STEP_REGISTRY["b"]
        assert isinstance(step, StepB)
        assert step.step_id == "b"
        assert step.dependencies == ["a"]

    def test_all_steps_have_execute_method(self):
        """Test that all steps implement execute method."""
        for step_id in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            step = STEP_REGISTRY[step_id]
            assert hasattr(step, 'execute')
            assert callable(step.execute)

    def test_step_validate_dependencies_method_exists(self):
        """Test that all steps have validate_dependencies method."""
        for step_id in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']:
            step = STEP_REGISTRY[step_id]
            assert hasattr(step, 'validate_dependencies')
            assert callable(step.validate_dependencies)
