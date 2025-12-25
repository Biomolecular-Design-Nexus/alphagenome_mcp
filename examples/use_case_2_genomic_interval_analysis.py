#!/usr/bin/env python3
"""
Use Case 2: Genomic Interval Analysis using AlphaGenome API

This script analyzes specific chromosomal regions for regulatory elements,
chromatin accessibility, and other genomic features.

Example usage:
    python examples/use_case_2_genomic_interval_analysis.py --chromosome chr1 --start 1000000 --end 1002048
    python examples/use_case_2_genomic_interval_analysis.py --interval chr1:1000000-1002048 --output-types atac cage
"""

import argparse
import json
import sys
import os
import re
from typing import List, Optional

# Add the repo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'repo', 'AlphaGenome-MCP-Server'))

try:
    from alphagenome_client import AlphaGenomeClient
except ImportError:
    print("Error: Could not import AlphaGenome client. Please ensure the environment is set up correctly.")
    sys.exit(1)


def parse_interval_string(interval_str: str) -> tuple:
    """
    Parse interval string in format chr:start-end.

    Example: "chr1:1000000-1002048" -> ("chr1", 1000000, 1002048)
    """
    pattern = r'^(\w+):(\d+)-(\d+)$'
    match = re.match(pattern, interval_str)
    if not match:
        raise ValueError(f"Invalid interval format: {interval_str}. Expected format: chr:start-end")

    chromosome = match.group(1)
    start = int(match.group(2))
    end = int(match.group(3))

    if start >= end:
        raise ValueError(f"Start position ({start}) must be less than end position ({end})")

    return chromosome, start, end


def predict_genomic_interval(chromosome: str, start: int, end: int,
                           organism: str = "human",
                           output_types: Optional[List[str]] = None,
                           api_key: Optional[str] = None) -> dict:
    """
    Predict genomic features for a chromosomal interval.

    Args:
        chromosome: Chromosome name (e.g., "chr1", "chrX")
        start: Start position (0-based)
        end: End position (exclusive)
        organism: Target organism (default: "human")
        output_types: List of output types to request (e.g., ["atac", "cage", "dnase"])
        api_key: AlphaGenome API key

    Returns:
        Dictionary with prediction results
    """
    if not api_key:
        # Try to get from environment
        api_key = os.getenv('ALPHAGENOME_API_KEY')
        if not api_key:
            raise ValueError("API key required. Set ALPHAGENOME_API_KEY environment variable or use --api-key")

    try:
        client = AlphaGenomeClient(api_key)
        result = client.predict_interval(
            chromosome=chromosome,
            start=start,
            end=end,
            organism=organism,
            output_types=output_types
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }


def main():
    parser = argparse.ArgumentParser(
        description="Analyze genomic intervals for regulatory elements using AlphaGenome API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a specific chromosomal region
  python %(prog)s --chromosome chr1 --start 1000000 --end 1002048

  # Use interval string format
  python %(prog)s --interval chr1:1000000-1002048 --output-types atac cage dnase

  # Analyze with specific organism
  python %(prog)s --interval chrX:100000-102048 --organism human

Note: The AlphaGenome API supports specific sequence lengths (2KB, 16KB, 131KB, 524KB, 1MB).
Common 2KB interval: end = start + 2048
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--interval',
                           help='Interval in format chr:start-end (e.g., chr1:1000000-1002048)')

    coord_group = parser.add_argument_group('coordinate specification')
    coord_group.add_argument('--chromosome',
                           help='Chromosome name (e.g., chr1, chrX)')
    coord_group.add_argument('--start', type=int,
                           help='Start position (0-based)')
    coord_group.add_argument('--end', type=int,
                           help='End position (exclusive)')

    # Analysis options
    parser.add_argument('--organism', default='human',
                       help='Target organism (default: human)')
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
        # Parse interval coordinates
        if args.interval:
            chromosome, start, end = parse_interval_string(args.interval)
        else:
            if not all([args.chromosome, args.start is not None, args.end is not None]):
                raise ValueError("Either --interval or all of --chromosome, --start, --end must be provided")
            chromosome, start, end = args.chromosome, args.start, args.end

        # Validate coordinates
        if start < 0:
            raise ValueError("Start position cannot be negative")
        if start >= end:
            raise ValueError("Start position must be less than end position")

        # Calculate interval size
        interval_size = end - start

        # Common AlphaGenome interval sizes
        supported_sizes = [2048, 16384, 131072, 524288, 1048576]  # 2KB, 16KB, 131KB, 524KB, 1MB
        if interval_size not in supported_sizes:
            print(f"Warning: Interval size {interval_size}bp may not be optimal.", file=sys.stderr)
            print(f"Recommended sizes: {', '.join(f'{s}bp' for s in supported_sizes)}", file=sys.stderr)

        # Set output types
        output_types = args.output_types if not args.all_outputs else None

        # Make prediction
        result = predict_genomic_interval(
            chromosome=chromosome,
            start=start,
            end=end,
            organism=args.organism,
            output_types=output_types,
            api_key=args.api_key
        )

        # Add analysis metadata
        result['metadata'] = {
            'chromosome': chromosome,
            'start': start,
            'end': end,
            'interval_size': interval_size,
            'organism': args.organism,
            'output_types_requested': output_types or 'all',
            'script': 'use_case_2_genomic_interval_analysis.py'
        }

        # Format output
        if args.pretty:
            output_str = json.dumps(result, indent=2)
        else:
            output_str = json.dumps(result)

        # Write output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_str)
            print(f"Results written to {args.output}")
        else:
            print(output_str)

        # Exit with error code if prediction failed
        if not result.get('success', False):
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "script": "use_case_2_genomic_interval_analysis.py"
        }

        output_str = json.dumps(error_result, indent=2 if args.pretty else None)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_str)
        else:
            print(output_str)

        sys.exit(1)


if __name__ == "__main__":
    main()