#!/usr/bin/env python3
"""
Use Case 4: Variant Scoring using AlphaGenome API

This script scores genetic variants using 19 different algorithms to assess
their potential functional impact and pathogenicity.

Example usage:
    python examples/use_case_4_variant_scoring.py --variant chr1:1001000A>G --interval chr1:1000000-1002048
    python examples/use_case_4_variant_scoring.py --chromosome chr1 --position 1001000 --ref A --alt G --interval-start 1000000 --interval-end 1002048
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


def score_variant(chromosome: str, position: int, ref: str, alt: str,
                 interval_start: int, interval_end: int,
                 organism: str = "human",
                 api_key: Optional[str] = None) -> dict:
    """
    Score a genetic variant using 19 scoring algorithms.

    Args:
        chromosome: Chromosome name (e.g., "chr1", "chrX")
        position: Variant position (1-based)
        ref: Reference allele
        alt: Alternative allele
        interval_start: Start position of analysis interval (0-based)
        interval_end: End position of analysis interval (exclusive)
        organism: Target organism (default: "human")
        api_key: AlphaGenome API key

    Returns:
        Dictionary with scoring results
    """
    # Check if using mock mode first
    use_mock = os.getenv('ALPHAGENOME_USE_MOCK', '').lower() == 'true'

    if not use_mock:
        if not api_key:
            # Try to get from environment
            api_key = os.getenv('ALPHAGENOME_API_KEY')
            if not api_key:
                raise ValueError("API key required. Set ALPHAGENOME_API_KEY environment variable or use --api-key")

    try:
        # Use dummy key for mock mode
        client_api_key = api_key if not use_mock else "mock_key"
        client = AlphaGenomeClient(client_api_key)
        result = client.score_variant(
            chromosome=chromosome,
            position=position,
            ref=ref,
            alt=alt,
            interval_start=interval_start,
            interval_end=interval_end,
            organism=organism
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }


def interpret_scores(scores: dict) -> dict:
    """
    Interpret variant scores and provide summary.

    Args:
        scores: Dictionary of scores from AlphaGenome

    Returns:
        Dictionary with interpretation
    """
    if not scores or not isinstance(scores, dict):
        return {"interpretation": "No scores available"}

    interpretation = {
        "summary": "Variant scoring analysis",
        "total_algorithms": len(scores),
        "algorithms_used": list(scores.keys()) if isinstance(scores, dict) else [],
        "interpretation": "Multiple scoring algorithms were applied to assess variant impact"
    }

    return interpretation


def main():
    parser = argparse.ArgumentParser(
        description="Score genetic variants using AlphaGenome's 19 scoring algorithms",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Score a variant using string format
  python %(prog)s --variant chr1:1001000A>G --interval chr1:1000000-1002048

  # Score using individual parameters
  python %(prog)s --chromosome chr1 --position 1001000 --ref A --alt G \\
                   --interval-start 1000000 --interval-end 1002048

  # Score with interpretation
  python %(prog)s --variant chr1:1001000A>G --interval chr1:1000000-1002048 --interpret

Note: Variant scoring uses 19 different algorithms to assess functional impact.
      The variant position must fall within the analysis interval.
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
    parser.add_argument('--interpret', action='store_true',
                       help='Include score interpretation')

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
            # Ensure variant and interval are on the same chromosome
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

        # Score variant
        result = score_variant(
            chromosome=chromosome,
            position=position,
            ref=ref.upper(),
            alt=alt.upper(),
            interval_start=interval_start,
            interval_end=interval_end,
            organism=args.organism,
            api_key=args.api_key
        )

        # Add interpretation if requested
        if args.interpret and result.get('success') and 'result' in result:
            interpretation = interpret_scores(result['result'])
            result['interpretation'] = interpretation

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
            'scoring_algorithms': 19,
            'interpretation_included': args.interpret,
            'script': 'use_case_4_variant_scoring.py'
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

        # Exit with error code if scoring failed
        if not result.get('success', False):
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "script": "use_case_4_variant_scoring.py"
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