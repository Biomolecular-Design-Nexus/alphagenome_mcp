#!/usr/bin/env python3
"""
Script: genomic_interval_analysis.py
Description: Analyze genomic intervals for chromatin accessibility and regulatory features

Original Use Case: examples/use_case_2_genomic_interval_analysis.py
Dependencies Removed: Direct repo imports, simplified client interface

Usage:
    python scripts/genomic_interval_analysis.py --interval <interval> --output <output_file>

Example:
    python scripts/genomic_interval_analysis.py --interval "chr1:1000000-1002048" --output results/interval.json
    python scripts/genomic_interval_analysis.py --interval "chr1:1000000-1002048" --output-types atac --pretty
"""

# ==============================================================================
# Minimal Imports (only essential packages)
# ==============================================================================
import argparse
import sys
from pathlib import Path
from typing import Union, Optional, Dict, Any, List

# Add lib directory to path for our simplified modules
sys.path.insert(0, str(Path(__file__).parent / "lib"))

from alphagenome_client import AlphaGenomeClient
from file_io import write_output
from parsers import parse_interval_string, validate_genomic_coordinates
from utils import get_api_key, handle_error, add_metadata, validate_output_types

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "organism": "human",
    "default_output_types": ["atac"],
    "enable_mock_mode": True
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_genomic_interval_analysis(
    interval: str,
    output_file: Optional[Union[str, Path]] = None,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    all_outputs: bool = False,
    api_key: Optional[str] = None,
    pretty: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for genomic interval analysis.

    Args:
        interval: Genomic interval string in format "chr:start-end"
        output_file: Path to save output (optional)
        organism: Target organism (default: human)
        output_types: List of output types to request (e.g., ["atac", "cage", "dnase"])
        all_outputs: Request all available output types
        api_key: AlphaGenome API key (optional, reads from env)
        pretty: Pretty print JSON output
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - success: Boolean indicating success/failure
            - result: Main prediction result (if successful)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata
            - error: Error message (if failed)

    Example:
        >>> result = run_genomic_interval_analysis(interval="chr1:1000000-1002048", pretty=True)
        >>> print(result['result']['predictions']['atac_accessibility_scores'])
    """
    script_name = "genomic_interval_analysis.py"

    try:
        # Parse and validate interval
        chromosome, start, end = parse_interval_string(interval)
        validate_genomic_coordinates(chromosome, start, end)

        # Set output types
        if all_outputs:
            requested_output_types = None
        else:
            requested_output_types = validate_output_types(output_types)

        # Get API key
        client_api_key = get_api_key(api_key)

        # Initialize client
        client = AlphaGenomeClient(client_api_key)

        # Make prediction
        prediction_result = client.predict_interval(
            chromosome=chromosome,
            start=start,
            end=end,
            organism=organism,
            output_types=requested_output_types
        )

        # Check if prediction was successful
        if not prediction_result.get('success', False):
            return prediction_result

        # Create enhanced result with metadata
        result = {
            "success": True,
            "result": prediction_result,
            "metadata": {
                "interval": interval,
                "chromosome": chromosome,
                "start": start,
                "end": end,
                "length": end - start,
                "organism": organism,
                "output_types_requested": requested_output_types or 'all'
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
  # Analyze a genomic interval with default ATAC output
  python %(prog)s --interval "chr1:1000000-1002048"

  # Analyze interval with specific output types
  python %(prog)s --interval "chr1:1000000-1002048" --output-types atac cage dnase

  # Generate all available outputs with pretty formatting
  python %(prog)s --interval "chr1:1000000-1002048" --all-outputs --pretty

  # Save results to file
  python %(prog)s --interval "chr1:1000000-1002048" --output results/interval.json
        """
    )

    # Input options
    parser.add_argument('--interval', '-i', required=True,
                       help='Genomic interval in format chr:start-end (e.g., chr1:1000000-2000000)')

    # Analysis options
    parser.add_argument('--organism', default=DEFAULT_CONFIG["organism"],
                       help=f'Target organism (default: {DEFAULT_CONFIG["organism"]})')
    parser.add_argument('--output-types', nargs='*',
                       help='Specific output types to request (e.g., atac cage dnase)')
    parser.add_argument('--all-outputs', action='store_true',
                       help='Request all available output types')

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
        # Run analysis
        result = run_genomic_interval_analysis(
            interval=args.interval,
            output_file=args.output,
            organism=args.organism,
            output_types=args.output_types,
            all_outputs=args.all_outputs,
            api_key=args.api_key,
            pretty=args.pretty
        )

        # Output results if not saved to file
        if not args.output:
            write_output(result, pretty=args.pretty)
        else:
            print(f"✅ Success: {result.get('output_file', 'Completed')}")

        # Exit with error code if analysis failed
        if not result.get('success', False):
            sys.exit(1)

        return result

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error_result = handle_error(e, "genomic_interval_analysis.py")
        write_output(error_result, pretty=args.pretty)
        sys.exit(1)


if __name__ == '__main__':
    main()