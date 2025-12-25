#!/usr/bin/env python3
"""
Script: variant_scoring.py
Description: Score genetic variants using multiple pathogenicity prediction algorithms

Original Use Case: examples/use_case_4_variant_scoring.py
Dependencies Removed: Direct repo imports, simplified client interface

Usage:
    python scripts/variant_scoring.py --variant <variant> --interval <interval> --output <output_file>

Example:
    python scripts/variant_scoring.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --output results/scores.json
    python scripts/variant_scoring.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --pretty
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any

# Add lib directory to path for our simplified modules
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from alphagenome_client import AlphaGenomeClient
from file_io import write_output
from parsers import parse_interval_string, parse_variant_string, validate_variant_in_interval
from utils import get_api_key, handle_error, add_metadata

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "organism": "human",
    "enable_mock_mode": True
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_variant_scoring(
    variant: str,
    interval: str,
    output_file: Optional[Union[str, Path]] = None,
    organism: str = "human",
    api_key: Optional[str] = None,
    pretty: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for variant scoring using multiple algorithms.

    Args:
        variant: Variant string in format "chr:posREF>ALT" (e.g., "chr1:1001000A>G")
        interval: Genomic interval string in format "chr:start-end"
        output_file: Path to save output (optional)
        organism: Target organism (default: human)
        api_key: AlphaGenome API key (optional, reads from env)
        pretty: Pretty print JSON output
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - success: Boolean indicating success/failure
            - result: Main scoring result (if successful)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata
            - error: Error message (if failed)

    Example:
        >>> result = run_variant_scoring(
        ...     variant="chr1:1001000A>G",
        ...     interval="chr1:1000000-1002048",
        ...     pretty=True
        ... )
        >>> print(result['result']['scores'])
    """
    script_name = "variant_scoring.py"

    try:
        # Parse and validate variant
        var_chromosome, var_position, ref, alt = parse_variant_string(variant)

        # Parse and validate interval
        interval_chromosome, interval_start, interval_end = parse_interval_string(interval)

        # Validate variant is within interval (with case-insensitive comparison)
        validate_variant_in_interval(
            var_chromosome, var_position,
            interval_chromosome, interval_start, interval_end
        )

        # Get API key
        client_api_key = get_api_key(api_key)

        # Initialize client
        client = AlphaGenomeClient(client_api_key)

        # Make scoring request
        scoring_result = client.score_variant(
            chromosome=var_chromosome,
            position=var_position,
            ref=ref,
            alt=alt,
            interval_start=interval_start,
            interval_end=interval_end,
            organism=organism
        )

        # Check if scoring was successful
        if not scoring_result.get('success', False):
            return scoring_result

        # Create enhanced result with metadata
        result = {
            "success": True,
            "result": scoring_result,
            "metadata": {
                "variant": variant,
                "variant_chromosome": var_chromosome,
                "variant_position": var_position,
                "reference_allele": ref,
                "alternate_allele": alt,
                "interval": interval,
                "interval_chromosome": interval_chromosome,
                "interval_start": interval_start,
                "interval_end": interval_end,
                "interval_length": interval_end - interval_start,
                "organism": organism,
                "analysis_type": "variant_scoring"
            },
            "output_file": None
        }

        # Add script metadata
        add_metadata(result, script_name,
                    pretty_output=pretty)

        # Save output if requested
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            write_output(result, output_path, pretty)
            result["output_file"] = str(output_path)

        return result

    except Exception as e:
        return handle_error(e, script_name)


# ==============================================================================
# CLI Interface
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a variant using all available algorithms
  python %(prog)s --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048"

  # Save results with pretty formatting
  python %(prog)s --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --output results/scores.json --pretty

  # Score a different type of variant
  python %(prog)s --variant "chr2:12345678T>C" --interval "chr2:12340000-12350000" --pretty
        """
    )

    # Input options
    parser.add_argument('--variant', '-v', required=True,
                       help='Genetic variant in format chr:posREF>ALT (e.g., chr1:1001000A>G)')
    parser.add_argument('--interval', '-i', required=True,
                       help='Genomic interval in format chr:start-end (e.g., chr1:1000000-2000000)')

    # Analysis options
    parser.add_argument('--organism', default=DEFAULT_CONFIG["organism"],
                       help=f'Target organism (default: {DEFAULT_CONFIG["organism"]})')

    # API options
    parser.add_argument('--api-key',
                       help='AlphaGenome API key (or set ALPHAGENOME_API_KEY env var)')

    # Output options
    parser.add_argument('--output', '-o',
                       help='Output file path (default: stdout)')
    parser.add_argument('--pretty', action='store_true',
                       help='Pretty print JSON output')

    args = parser.parse_args()

    try:
        # Run scoring
        result = run_variant_scoring(
            variant=args.variant,
            interval=args.interval,
            output_file=args.output,
            organism=args.organism,
            api_key=args.api_key,
            pretty=args.pretty
        )

        # Output results if not saved to file
        if not args.output:
            write_output(result, pretty=args.pretty)
        else:
            print(f"✅ Success: {result.get('output_file', 'Completed')}")

        # Exit with error code if scoring failed
        if not result.get('success', False):
            sys.exit(1)

        return result

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error_result = handle_error(e, "variant_scoring.py")
        write_output(error_result, pretty=args.pretty)
        sys.exit(1)


if __name__ == '__main__':
    main()