'''
@File: steps.py
@Time: 2026-04-20
@Author: Karri Korsu
@Version : 1.0
@Contact : kkorsu@gmail.com
@Desc: Step registry for modular workflow execution. Each step represents one phase of the crawling pipeline.
'''

from abc import ABC, abstractmethod
from typing import Set, Optional, List, Tuple
from pathlib import Path
import warnings
import pandas as pd

from propertycrawler.execution_context import ExecutionContext
from propertycrawler.propertysite import PropertySite
from propertycrawler.remax import Remax
from propertycrawler.crawler import Crawler
from propertycrawler.parser import JsonParser, HtmlParser
from propertycrawler.datahandler import IO, DF, GC
from propertycrawler.constants import REMAX_ATTR_KEYS


class Step(ABC):
    """
    Abstract base class for workflow steps.
    Each step encapsulates one phase of the property crawling pipeline.
    """

    def __init__(self, step_id: str, name: str, dependencies: List[str]):
        """
        Initialize a step.

        Args:
            step_id: Single letter identifier (a, b, c, ..., h)
            name: Human-readable step name
            dependencies: List of step IDs that must complete before this step
        """
        self.step_id = step_id
        self.name = name
        self.dependencies = dependencies

    @abstractmethod
    def execute(self, context: ExecutionContext) -> None:
        """
        Execute the step, updating the context with results.

        Args:
            context: ExecutionContext object to read from and update

        Raises:
            Various exceptions depending on step implementation
        """
        pass

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        """
        Check if all dependencies for this step are satisfied in the context.
        Override in subclasses for custom validation logic.

        Args:
            context: ExecutionContext to validate against

        Returns:
            True if all dependencies are satisfied
        """
        return True


# =============================================================================
# Step A: Download Listing Lists
# =============================================================================
class StepA(Step):
    """Step A: Download listing list pages from server."""

    def __init__(self):
        super().__init__(
            step_id="a",
            name="Download Listing Lists",
            dependencies=[]
        )

    def execute(self, context: ExecutionContext, url: str) -> None:
        """
        Download listing list pages using wget.

        Args:
            context: ExecutionContext for session info
            url: PHP listing query URL to crawl

        Raises:
            ValueError: If URL is invalid
        """
        if not isinstance(url, str) or not url.startswith("http"):
            raise ValueError(f"Invalid URL provided: {url}")

        context.ensure_session_dir()
        print(f"[Step A] Downloading listing lists from: {url}")

        Crawler.get_listing_list_full(
            url=url,
            start_pg=0,
            filepath=str(context.listing_lists_path),
            separator="&"
        )

        print(f"[Step A] ✓ Listing lists saved to: {context.listing_lists_path}")


# =============================================================================
# Step B: Parse Listing Lists to Extract IDs
# =============================================================================
class StepB(Step):
    """Step B: Parse listing list files and extract property IDs."""

    def __init__(self):
        super().__init__(
            step_id="b",
            name="Parse Listing Lists",
            dependencies=["a"]
        )

    def execute(self, context: ExecutionContext, listing_list_dir: Optional[str] = None) -> None:
        """
        Parse listing list files from disk and extract IDs.

        Args:
            context: ExecutionContext for session info
            listing_list_dir: Override path to listing_lists directory. If None, uses context path.

        Raises:
            FileNotFoundError: If listing_lists directory doesn't exist
        """
        list_dir = Path(listing_list_dir) if listing_list_dir else context.listing_lists_path

        if not list_dir.exists():
            raise FileNotFoundError(f"Listing lists directory not found: {list_dir}")

        print(f"[Step B] Parsing listing lists from: {list_dir}")

        # Create parser and extract IDs
        parser = JsonParser([])
        listing_ids = Crawler.get_listing_ids_from_disk(
            filepath=str(list_dir),
            parser=parser
        )

        # Create Remax instance and populate with extracted IDs
        remax = Remax()
        remax.populate_listing_list(listing_ids)

        # Update context
        context.remax = remax
        context.listing_ids = listing_ids

        print(f"[Step B] ✓ Extracted {len(listing_ids)} property IDs")
        print(f"[Step B] ✓ Created {len(remax.listings)} Listing objects")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        """Step B can run standalone if given an explicit directory."""
        return True  # No strict dependency for explicit input


# =============================================================================
# Step C: Download Individual Listings
# =============================================================================
class StepC(Step):
    """Step C: Download individual property listing HTML pages."""

    def __init__(self):
        super().__init__(
            step_id="c",
            name="Download Listings",
            dependencies=["b"]
        )

    def execute(self, context: ExecutionContext) -> None:
        """
        Download HTML pages for each property listing.

        Args:
            context: ExecutionContext containing Remax object with listings

        Raises:
            ValueError: If context doesn't have remax object
        """
        if not context.validate_has_remax():
            raise ValueError("Step C requires remax object from Step B. Run Step B first.")

        context.ensure_session_dir()
        print(f"[Step C] Downloading {len(context.remax.listings)} listing pages")

        Crawler.get_listings(
            context.remax,
            filepath=str(context.listings_path)
        )

        print(f"[Step C] ✓ Downloaded listings to: {context.listings_path}")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        return context.validate_has_remax()


# =============================================================================
# Step D: Parse Individual Listings
# =============================================================================
class StepD(Step):
    """Step D: Parse listing HTML pages to extract property attributes."""

    def __init__(self):
        super().__init__(
            step_id="d",
            name="Parse Listings",
            dependencies=["c"]
        )

    def execute(self, context: ExecutionContext, listing_dir: Optional[str] = None) -> None:
        """
        Parse listing HTML files and extract attributes.

        Args:
            context: ExecutionContext for session info
            listing_dir: Override path to listings directory. If None, uses context path.

        Raises:
            FileNotFoundError: If listings directory doesn't exist or is empty
        """
        list_path = Path(listing_dir) if listing_dir else context.listings_path

        if not list_path.exists():
            raise FileNotFoundError(f"Listings directory not found: {list_path}")

        # If no remax object in context, we need to load it from disk or create a temporary one
        # For now, assume remax is in context (from Step B or C)
        if not context.validate_has_remax():
            # Create a temporary Remax instance for parsing
            context.remax = Remax()
            # Reconstruct listings from HTML files in the directory
            for html_file in sorted(list_path.glob("*.html")):
                listing_id = html_file.stem
                try:
                    listing = context.remax.create_listing(int(listing_id))
                    listing.filepath = str(html_file)
                    context.remax.listings.add(listing)
                except (ValueError, AttributeError):
                    continue

        print(f"[Step D] Parsing {len(context.remax.listings)} listing pages")

        HtmlParser.parse_listings(context.remax.listings)

        # Update context
        context.listings = list(context.remax.listings)

        print(f"[Step D] ✓ Parsed all listings and extracted attributes")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        """Step D can run standalone if given an explicit directory."""
        return True  # No strict dependency for explicit input


# =============================================================================
# Step E: Create DataFrame
# =============================================================================
class StepE(Step):
    """Step E: Create DataFrame from parsed listing objects."""

    def __init__(self):
        super().__init__(
            step_id="e",
            name="Create DataFrame",
            dependencies=["d"]
        )

    def execute(self, context: ExecutionContext) -> None:
        """
        Create DataFrame from listing objects and geocode.

        Args:
            context: ExecutionContext containing parsed listings

        Raises:
            ValueError: If context doesn't have listings
        """
        if not context.validate_has_listings():
            raise ValueError("Step E requires parsed listings from Step D. Run Step D first.")

        print(f"[Step E] Creating DataFrame from {len(context.listings)} listings")

        # Create dataframe with proper column structure
        dataset = pd.DataFrame(columns=REMAX_ATTR_KEYS)

        # Add all listing rows to dataframe
        dataset = DF.add_rows(dataset, context.listings, context.session_id)

        # Geocode all addresses
        print(f"[Step E] Geocoding {len(dataset)} addresses...")
        dataset = GC.geocode_all(dataset, REMAX_ATTR_KEYS[0])  # [0] == "Osoite: "

        # Update context
        context.dataframe = dataset

        print(f"[Step E] ✓ Created DataFrame with {len(dataset)} rows and geocoding complete")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        return context.validate_has_listings()


# =============================================================================
# Step F: Remove Duplicates
# =============================================================================
class StepF(Step):
    """Step F: Remove duplicate listings based on listing IDs."""

    def __init__(self):
        super().__init__(
            step_id="f",
            name="Remove Duplicates",
            dependencies=["e"]
        )

    def execute(self, context: ExecutionContext, dedup_csv: Optional[str] = None) -> None:
        """
        Remove duplicate listings from DataFrame, optionally comparing with existing data.

        Args:
            context: ExecutionContext containing DataFrame
            dedup_csv: Optional CSV file path to load and compare duplicates against

        Raises:
            ValueError: If context doesn't have DataFrame
        """
        if not context.validate_has_dataframe():
            raise ValueError("Step F requires DataFrame from Step E. Run Step E first.")

        print(f"[Step F] Checking for duplicates in {len(context.dataframe)} rows")

        initial_count = len(context.dataframe)
        df = context.dataframe

        # Remove internal duplicates (same listingID appears multiple times)
        df = df.drop_duplicates(subset=["listingID"], keep="first")

        # If external CSV provided, compare and remove those already in the file
        if dedup_csv:
            try:
                existing_df = pd.read_csv(dedup_csv)
                existing_ids = set(existing_df["listingID"].astype(int))
                df = df[~df["listingID"].isin(existing_ids)]
                external_removed = initial_count - len(df)
                print(f"[Step F] Removed {external_removed} rows that exist in {dedup_csv}")
            except Exception as e:
                warnings.warn(f"Could not load dedup CSV: {e}")

        internal_removed = initial_count - len(df)
        context.dataframe = df

        print(f"[Step F] ✓ Removed {internal_removed} duplicate(s), {len(df)} rows remain")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        return context.validate_has_dataframe()


# =============================================================================
# Step G: Geocode
# =============================================================================
class StepG(Step):
    """Step G: Geocode DataFrame addresses (latitude/longitude)."""

    def __init__(self):
        super().__init__(
            step_id="g",
            name="Geocode",
            dependencies=["e"]
        )

    def execute(self, context: ExecutionContext) -> None:
        """
        Geocode all addresses in DataFrame.

        Args:
            context: ExecutionContext containing DataFrame

        Raises:
            ValueError: If context doesn't have DataFrame
        """
        if not context.validate_has_dataframe():
            raise ValueError("Step G requires DataFrame from Step E. Run Step E first.")

        # Geocoding is already done in Step E, but this allows it to run independently
        # Re-geocode in case Step E was skipped
        if "latitude" not in context.dataframe.columns or context.dataframe["latitude"].isna().all():
            print(f"[Step G] Geocoding {len(context.dataframe)} addresses...")
            context.dataframe = GC.geocode_all(
                context.dataframe,
                REMAX_ATTR_KEYS[0]  # "Osoite: "
            )
            print(f"[Step G] ✓ Geocoding complete")
        else:
            print(f"[Step G] Addresses already geocoded, skipping")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        return context.validate_has_dataframe()


# =============================================================================
# Step H: Save DataFrame
# =============================================================================
class StepH(Step):
    """Step H: Save DataFrame to CSV file."""

    def __init__(self):
        super().__init__(
            step_id="h",
            name="Save CSV",
            dependencies=["e"]
        )

    def execute(self, context: ExecutionContext, output_path: Optional[str] = None) -> None:
        """
        Save DataFrame to CSV file.

        Args:
            context: ExecutionContext containing DataFrame
            output_path: Custom output CSV path. If None, uses default session path.

        Raises:
            ValueError: If context doesn't have DataFrame
        """
        if not context.validate_has_dataframe():
            raise ValueError("Step H requires DataFrame from Step E. Run Step E first.")

        csv_path = context.get_csv_output_path(output_path)
        print(f"[Step H] Saving {len(context.dataframe)} rows to CSV")

        DF.save(context.dataframe, str(csv_path))

        print(f"[Step H] ✓ Saved to: {csv_path}")

    def validate_dependencies(self, context: ExecutionContext) -> bool:
        return context.validate_has_dataframe()


# =============================================================================
# Step Registry and Utilities
# =============================================================================

# Central registry of all workflow steps
STEP_REGISTRY = {
    "a": StepA(),
    "b": StepB(),
    "c": StepC(),
    "d": StepD(),
    "e": StepE(),
    "f": StepF(),
    "g": StepG(),
    "h": StepH(),
}


def validate_step_sequence(step_ids: List[str], registry: dict = STEP_REGISTRY) -> Tuple[bool, Optional[str]]:
    """
    Validate that a sequence of steps forms a valid execution order.

    The steps must:
    1. All exist in the registry
    2. Be in valid sequential order (no circular dependencies)
    3. Have dependencies from WITHIN the sequence satisfied by earlier steps

    Dependencies outside the sequence are assumed to be satisfied by explicit input or context.
    For example, ["e", "f", "h"] is valid because f depends on e and e comes first,
    even though e depends on d (which would be provided explicitly or from context).

    Args:
        step_ids: List of step IDs to validate (e.g., ["a", "b", "c"])
        registry: Step registry dict (default: STEP_REGISTRY)

    Returns:
        Tuple of (is_valid: bool, error_message: str or None)
    """
    if not step_ids:
        return False, "No steps provided"

    # Check all steps exist
    for step_id in step_ids:
        if step_id not in registry:
            return False, f"Unknown step '{step_id}'. Valid steps: {', '.join(registry.keys())}"

    # Build set of steps that will be executed
    executed_steps = set(step_ids)

    # Check dependencies for each step
    for idx, step_id in enumerate(step_ids):
        step = registry[step_id]
        unsatisfied_deps = []

        for dep in step.dependencies:
            # Only check dependencies that are IN the sequence
            # External dependencies are handled by step.execute() via context validation
            if dep in executed_steps:
                # Dependency must come before current step
                if step_ids.index(dep) > idx:
                    unsatisfied_deps.append(f"{dep} (comes after {step_id})")

        if unsatisfied_deps:
            required_steps = ", ".join(unsatisfied_deps)
            missing_prefix = "Step " + step_id + " has ordering issue: " + required_steps
            return False, missing_prefix

    return True, None
