#!/usr/bin/env python3
"""
Use Case 1: DNA Sequence Prediction using AlphaGenome API

This script analyzes DNA sequences for genomic features like chromatin accessibility,
transcription start sites, and regulatory elements.

Example usage:
    python examples/use_case_1_dna_sequence_prediction.py --sequence "ATGCGATCGTAGCTAGCATGCAAATTTGGGCCC" --output-types atac cage dnase
    python examples/use_case_1_dna_sequence_prediction.py --input examples/data/sample_sequence.txt
"""

import argparse
import json
import sys
import os
from typing import List, Optional

# Add the repo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'repo', 'AlphaGenome-MCP-Server'))

try:
    from alphagenome_client import AlphaGenomeClient
except ImportError:
    print("Error: Could not import AlphaGenome client. Please ensure the environment is set up correctly.")
    sys.exit(1)


def load_sequence_from_file(file_path: str) -> str:
    """Load DNA sequence from a text file."""
    try:
        with open(file_path, 'r') as f:
            # Read first line and strip whitespace
            sequence = f.readline().strip()
            # Remove any non-DNA characters
            sequence = ''.join(c.upper() for c in sequence if c.upper() in 'ATGCN')
            return sequence
    except Exception as e:
        raise ValueError(f"Could not read sequence from {file_path}: {e}")


def predict_dna_sequence(sequence: str, organism: str = "human",
                        output_types: Optional[List[str]] = None,
                        api_key: Optional[str] = None) -> dict:
    """
    Predict genomic features for a DNA sequence.

    Args:
        sequence: DNA sequence string (A, T, G, C, N)
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
        result = client.predict_sequence(
            sequence=sequence,
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
        description="Predict genomic features for DNA sequences using AlphaGenome API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a DNA sequence with specific output types
  python %(prog)s --sequence "ATGCGATCGTAGCTAGCATGCAAATTTGGGCCC" --output-types atac cage dnase

  # Load sequence from file
  python %(prog)s --input examples/data/sample_sequence.txt --organism human

  # Generate all available outputs
  python %(prog)s --sequence "ATGCGATCGTAGCTAGCATGC" --all-outputs
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--sequence', '-s',
                           help='DNA sequence string (A, T, G, C, N)')
    input_group.add_argument('--input', '-i',
                           help='Path to text file containing DNA sequence')

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
        # Get DNA sequence
        if args.sequence:
            sequence = args.sequence.strip()
        else:
            sequence = load_sequence_from_file(args.input)

        # Validate sequence
        if not sequence:
            raise ValueError("DNA sequence cannot be empty")

        # Check for valid DNA characters
        valid_chars = set('ATGCN')
        invalid_chars = set(sequence.upper()) - valid_chars
        if invalid_chars:
            raise ValueError(f"Invalid DNA characters found: {invalid_chars}")

        # Set output types
        output_types = args.output_types if not args.all_outputs else None

        # Make prediction
        result = predict_dna_sequence(
            sequence=sequence,
            organism=args.organism,
            output_types=output_types,
            api_key=args.api_key
        )

        # Add analysis metadata
        result['metadata'] = {
            'sequence_length': len(sequence),
            'organism': args.organism,
            'output_types_requested': output_types or 'all',
            'script': 'use_case_1_dna_sequence_prediction.py'
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
            "script": "use_case_1_dna_sequence_prediction.py"
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