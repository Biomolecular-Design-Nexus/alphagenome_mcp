#!/usr/bin/env python3
"""
Use Case 5: Batch Sequence Analysis using AlphaGenome API

This script performs parallel analysis of multiple DNA sequences for genomic features.
Supports processing sequences from files or command line input.

Example usage:
    python examples/use_case_5_batch_sequence_analysis.py --sequences "ATGC" "GGCC" "TTAA" --max-workers 3
    python examples/use_case_5_batch_sequence_analysis.py --input examples/data/sequences.txt --output-types atac cage
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


def load_sequences_from_file(file_path: str) -> List[str]:
    """
    Load DNA sequences from a text file.

    File format: one sequence per line
    """
    try:
        sequences = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line or line.startswith('#'):  # Skip empty lines and comments
                    continue

                # Remove any non-DNA characters
                sequence = ''.join(c.upper() for c in line if c.upper() in 'ATGCN')
                if sequence:
                    sequences.append(sequence)
                else:
                    print(f"Warning: No valid DNA sequence found on line {line_num}: {line}", file=sys.stderr)

        return sequences
    except Exception as e:
        raise ValueError(f"Could not read sequences from {file_path}: {e}")


def predict_sequences(sequences: List[str], organism: str = "human",
                     output_types: Optional[List[str]] = None,
                     max_workers: int = 5,
                     api_key: Optional[str] = None) -> dict:
    """
    Predict genomic features for multiple DNA sequences.

    Args:
        sequences: List of DNA sequence strings
        organism: Target organism (default: "human")
        output_types: List of output types to request (e.g., ["atac", "cage", "dnase"])
        max_workers: Maximum number of parallel workers
        api_key: AlphaGenome API key

    Returns:
        Dictionary with prediction results
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
        result = client.predict_sequences(
            sequences=sequences,
            organism=organism,
            output_types=output_types,
            max_workers=max_workers
        )
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }


def validate_sequences(sequences: List[str]) -> List[str]:
    """
    Validate and clean up DNA sequences.

    Args:
        sequences: List of sequence strings

    Returns:
        List of validated sequences

    Raises:
        ValueError: If sequences are invalid
    """
    if not sequences:
        raise ValueError("No sequences provided")

    validated = []
    valid_chars = set('ATGCN')

    for i, seq in enumerate(sequences):
        if not seq or not isinstance(seq, str):
            raise ValueError(f"Sequence {i+1} is empty or invalid")

        seq_upper = seq.upper().strip()
        invalid_chars = set(seq_upper) - valid_chars
        if invalid_chars:
            raise ValueError(f"Sequence {i+1} contains invalid characters: {invalid_chars}")

        validated.append(seq_upper)

    return validated


def main():
    parser = argparse.ArgumentParser(
        description="Perform batch analysis of DNA sequences using AlphaGenome API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze multiple sequences from command line
  python %(prog)s --sequences "ATGCGATCGTAGC" "GGCCTTAACCGG" "TTAACCGGTTAA"

  # Load sequences from file
  python %(prog)s --input examples/data/sequences.txt --max-workers 3

  # Specify output types and organism
  python %(prog)s --sequences "ATGCGATCG" "GGCCTTAAC" \\
                   --output-types atac cage dnase --organism human

File format for --input:
  One sequence per line
  Lines starting with # are treated as comments
  Empty lines are ignored
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--sequences', nargs='*',
                           help='DNA sequences as command line arguments')
    input_group.add_argument('--input', '-i',
                           help='Path to text file containing sequences (one per line)')

    # Analysis options
    parser.add_argument('--organism', default='human',
                       help='Target organism (default: human)')
    parser.add_argument('--output-types', nargs='*',
                       help='Specific output types to request (e.g., atac cage dnase)')
    parser.add_argument('--all-outputs', action='store_true',
                       help='Request all available output types')
    parser.add_argument('--max-workers', type=int, default=5,
                       help='Maximum number of parallel workers (default: 5)')

    # API options
    parser.add_argument('--api-key',
                       help='AlphaGenome API key (or set ALPHAGENOME_API_KEY env var)')

    # Output options
    parser.add_argument('--output', '-o',
                       help='Output file path (default: stdout)')
    parser.add_argument('--pretty', action='store_true',
                       help='Pretty print JSON output')
    parser.add_argument('--summary', action='store_true',
                       help='Include summary statistics')

    args = parser.parse_args()

    try:
        # Get DNA sequences
        if args.sequences:
            sequences = args.sequences
        else:
            sequences = load_sequences_from_file(args.input)

        # Validate sequences
        sequences = validate_sequences(sequences)

        if len(sequences) == 0:
            raise ValueError("No valid sequences found")

        print(f"Processing {len(sequences)} sequences with {args.max_workers} workers...", file=sys.stderr)

        # Set output types
        output_types = args.output_types if not args.all_outputs else None

        # Make predictions
        result = predict_sequences(
            sequences=sequences,
            organism=args.organism,
            output_types=output_types,
            max_workers=args.max_workers,
            api_key=args.api_key
        )

        # Add summary statistics if requested
        if args.summary and result.get('success'):
            summary = {
                'total_sequences': len(sequences),
                'sequence_lengths': [len(seq) for seq in sequences],
                'avg_sequence_length': sum(len(seq) for seq in sequences) / len(sequences),
                'min_sequence_length': min(len(seq) for seq in sequences),
                'max_sequence_length': max(len(seq) for seq in sequences),
                'total_bases': sum(len(seq) for seq in sequences)
            }
            result['summary'] = summary

        # Add analysis metadata
        result['metadata'] = {
            'input_source': 'command_line' if args.sequences else args.input,
            'sequence_count': len(sequences),
            'organism': args.organism,
            'output_types_requested': output_types or 'all',
            'max_workers': args.max_workers,
            'summary_included': args.summary,
            'script': 'use_case_5_batch_sequence_analysis.py'
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

        print(f"Successfully processed {len(sequences)} sequences", file=sys.stderr)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "script": "use_case_5_batch_sequence_analysis.py"
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