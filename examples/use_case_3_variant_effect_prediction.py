#!/usr/bin/env python3
"""
Use Case 3: Variant Effect Prediction using AlphaGenome API

This script predicts the functional effects of genetic variants (SNPs, indels)
on genomic features and regulatory elements.

Example usage:
    python examples/use_case_3_variant_effect_prediction.py --variant chr1:1001000A>G --interval chr1:1000000-1002048
    python examples/use_case_3_variant_effect_prediction.py --chromosome chr1 --position 1001000 --ref A --alt G --interval-start 1000000 --interval-end 1002048
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


def parse_variant_string(variant_str: str) -> tuple:
    """
    Parse variant string in format chr:posREF>ALT.

    Example: "chr1:1001000A>G" -> ("chr1", 1001000, "A", "G")
    """
    pattern = r'^(\w+):(\d+)([ATGC]+)>([ATGC]+)$'
    match = re.match(pattern, variant_str.upper())
    if not match:
        raise ValueError(f"Invalid variant format: {variant_str}. Expected format: chr:posREF>ALT")

    chromosome = match.group(1)
    position = int(match.group(2))
    ref = match.group(3)
    alt = match.group(4)

    return chromosome, position, ref, alt


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


def predict_variant_effect(chromosome: str, position: int, ref: str, alt: str,
                         interval_start: int, interval_end: int,
                         organism: str = "human",
                         output_types: Optional[List[str]] = None,
                         api_key: Optional[str] = None) -> dict:
    """
    Predict the effect of a genetic variant.

    Args:
        chromosome: Chromosome name (e.g., "chr1", "chrX")
        position: Variant position (1-based)
        ref: Reference allele
        alt: Alternative allele
        interval_start: Start position of analysis interval (0-based)
        interval_end: End position of analysis interval (exclusive)
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
        result = client.predict_variant(
            chromosome=chromosome,
            position=position,
            ref=ref,
            alt=alt,
            interval_start=interval_start,
            interval_end=interval_end,
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
        description="Predict functional effects of genetic variants using AlphaGenome API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a variant using string format
  python %(prog)s --variant chr1:1001000A>G --interval chr1:1000000-1002048

  # Analyze using individual parameters
  python %(prog)s --chromosome chr1 --position 1001000 --ref A --alt G \\
                   --interval-start 1000000 --interval-end 1002048

  # Request specific output types
  python %(prog)s --variant chr1:1001000A>G --interval chr1:1000000-1002048 \\
                   --output-types atac cage dnase

Note: The variant position must fall within the analysis interval.
      Typical interval size is 2KB (2048bp) around the variant.
        """
    )

    # Variant input options
    variant_group = parser.add_mutually_exclusive_group()
    variant_group.add_argument('--variant',
                             help='Variant in format chr:posREF>ALT (e.g., chr1:1001000A>G)')

    # Individual variant parameters
    var_param_group = parser.add_argument_group('variant specification')
    var_param_group.add_argument('--chromosome',
                                help='Chromosome name (e.g., chr1, chrX)')
    var_param_group.add_argument('--position', type=int,
                                help='Variant position (1-based)')
    var_param_group.add_argument('--ref',
                                help='Reference allele (e.g., A, T, G, C)')
    var_param_group.add_argument('--alt',
                                help='Alternative allele (e.g., A, T, G, C)')

    # Interval input options
    interval_group = parser.add_mutually_exclusive_group()
    interval_group.add_argument('--interval',
                              help='Analysis interval in format chr:start-end')

    # Individual interval parameters
    interval_param_group = parser.add_argument_group('interval specification')
    interval_param_group.add_argument('--interval-start', type=int,
                                    help='Interval start position (0-based)')
    interval_param_group.add_argument('--interval-end', type=int,
                                    help='Interval end position (exclusive)')

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
        # Parse variant information
        if args.variant:
            chromosome, position, ref, alt = parse_variant_string(args.variant)
        else:
            if not all([args.chromosome, args.position is not None, args.ref, args.alt]):
                raise ValueError("Either --variant or all of --chromosome, --position, --ref, --alt must be provided")
            chromosome, position, ref, alt = args.chromosome, args.position, args.ref, args.alt

        # Parse interval information
        if args.interval:
            interval_chr, interval_start, interval_end = parse_interval_string(args.interval)
            # Ensure variant and interval are on the same chromosome (case-insensitive)
            if chromosome.lower() != interval_chr.lower():
                raise ValueError(f"Variant chromosome ({chromosome}) must match interval chromosome ({interval_chr})")
        else:
            if not all([args.interval_start is not None, args.interval_end is not None]):
                raise ValueError("Either --interval or both --interval-start and --interval-end must be provided")
            interval_start, interval_end = args.interval_start, args.interval_end

        # Validate inputs
        if position <= 0:
            raise ValueError("Position must be positive (1-based)")
        if interval_start < 0:
            raise ValueError("Interval start cannot be negative")
        if interval_start >= interval_end:
            raise ValueError("Interval start must be less than end")

        # Check if variant position falls within interval
        # Note: position is 1-based, interval coordinates are 0-based
        if not (interval_start < position <= interval_end):
            raise ValueError(f"Variant position {position} must fall within interval [{interval_start}, {interval_end}]")

        # Validate alleles
        valid_bases = set('ATGC')
        if not (set(ref.upper()).issubset(valid_bases) and set(alt.upper()).issubset(valid_bases)):
            raise ValueError("Reference and alternative alleles must contain only A, T, G, C")

        # Set output types
        output_types = args.output_types if not args.all_outputs else None

        # Make prediction
        result = predict_variant_effect(
            chromosome=chromosome,
            position=position,
            ref=ref.upper(),
            alt=alt.upper(),
            interval_start=interval_start,
            interval_end=interval_end,
            organism=args.organism,
            output_types=output_types,
            api_key=args.api_key
        )

        # Add analysis metadata
        result['metadata'] = {
            'variant': f"{chromosome}:{position}{ref}>{alt}",
            'chromosome': chromosome,
            'position': position,
            'ref_allele': ref.upper(),
            'alt_allele': alt.upper(),
            'interval': f"{chromosome}:{interval_start}-{interval_end}",
            'interval_size': interval_end - interval_start,
            'organism': args.organism,
            'output_types_requested': output_types or 'all',
            'script': 'use_case_3_variant_effect_prediction.py'
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
            "script": "use_case_3_variant_effect_prediction.py"
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