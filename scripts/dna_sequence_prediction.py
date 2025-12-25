#!/usr/bin/env python3
"""
Script: dna_sequence_prediction.py
Description: Predict genomic features for DNA sequences using AlphaGenome API

Original Use Case: examples/use_case_1_dna_sequence_prediction.py
Dependencies Removed: Direct repo imports, simplified client interface

Usage:
    python scripts/dna_sequence_prediction.py --input <input_file> --output <output_file>

Example:
    python scripts/dna_sequence_prediction.py --sequence "ATGCGATCGATCGATC" --output results/output.json
    python scripts/dna_sequence_prediction.py --input examples/data/sample_sequence.txt --pretty
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
from file_io import load_sequence_from_file, write_output
from utils import get_api_key, handle_error, add_metadata, create_sequence_metadata, validate_output_types

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "organism": "human",
    "default_output_types": ["atac", "cage", "dnase"],
    "enable_mock_mode": True
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_dna_sequence_prediction(
    input_sequence: Optional[str] = None,
    input_file: Optional[Union[str, Path]] = None,
    output_file: Optional[Union[str, Path]] = None,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    all_outputs: bool = False,
    api_key: Optional[str] = None,
    pretty: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for DNA sequence genomic feature prediction.

    Args:
        input_sequence: DNA sequence string (alternative to input_file)
        input_file: Path to text file containing DNA sequence
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
        >>> result = run_dna_sequence_prediction(input_sequence="ATGCGATCGATCGATC", pretty=True)
        >>> print(result['result']['predictions']['atac_accessibility'])
    """
    script_name = "dna_sequence_prediction.py"

    try:
        # Input validation and loading
        if input_sequence and input_file:
            raise ValueError("Specify either input_sequence or input_file, not both")

        if not input_sequence and not input_file:
            raise ValueError("Must specify either input_sequence or input_file")

        # Get DNA sequence
        if input_sequence:
            sequence = input_sequence.strip()
        else:
            input_file = Path(input_file)
            if not input_file.exists():
                raise FileNotFoundError(f"Input file not found: {input_file}")
            sequence = load_sequence_from_file(input_file)

        # Validate sequence
        if not sequence:
            raise ValueError("DNA sequence cannot be empty")

        # Check for valid DNA characters (inlined validation)
        valid_chars = set('ATGCN')
        invalid_chars = set(sequence.upper()) - valid_chars
        if invalid_chars:
            raise ValueError(f"Invalid DNA characters found: {invalid_chars}. Only A, T, G, C, N are allowed")

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
        prediction_result = client.predict_sequence(
            sequence=sequence,
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
            "metadata": create_sequence_metadata(sequence, organism, requested_output_types),
            "output_file": None
        }

        # Add script metadata
        add_metadata(result, script_name,
                    input_file=str(input_file) if input_file else None,
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
  # Analyze a DNA sequence with specific output types
  python %(prog)s --sequence "ATGCGATCGTAGCTAGCATGCAAATTTGGGCCC" --output-types atac cage dnase

  # Load sequence from file
  python %(prog)s --input examples/data/sample_sequence.txt --organism human

  # Generate all available outputs
  python %(prog)s --sequence "ATGCGATCGTAGCTAGCATGC" --all-outputs

  # Save results to file with pretty formatting
  python %(prog)s --sequence "ATGCGATCGATCGATC" --output results/pred.json --pretty
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--sequence', '-s',
                           help='DNA sequence string (A, T, G, C, N)')
    input_group.add_argument('--input', '-i',
                           help='Path to text file containing DNA sequence')

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
        # Run prediction
        result = run_dna_sequence_prediction(
            input_sequence=args.sequence,
            input_file=args.input,
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

        # Exit with error code if prediction failed
        if not result.get('success', False):
            sys.exit(1)

        return result

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error_result = handle_error(e, "dna_sequence_prediction.py")
        write_output(error_result, pretty=args.pretty)
        sys.exit(1)


if __name__ == '__main__':
    main()