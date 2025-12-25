#!/usr/bin/env python3
"""
Script: batch_sequence_analysis.py
Description: Analyze multiple DNA sequences in batch for genomic features

Original Use Case: examples/use_case_5_batch_sequence_analysis.py
Dependencies Removed: Direct repo imports, simplified client interface

Usage:
    python scripts/batch_sequence_analysis.py --input <sequences_file> --output <output_file>

Example:
    python scripts/batch_sequence_analysis.py --input examples/data/sequences.txt --output results/batch.json
    python scripts/batch_sequence_analysis.py --input examples/data/sequences.txt --pretty
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
from file_io import load_sequences_from_file, write_output
from utils import get_api_key, handle_error, add_metadata, validate_output_types

# ==============================================================================
# Configuration (extracted from use case)
# ==============================================================================
DEFAULT_CONFIG = {
    "organism": "human",
    "default_output_types": ["atac", "cage", "dnase"],
    "enable_mock_mode": True,
    "max_workers": 5
}

# ==============================================================================
# Core Function (main logic extracted from use case)
# ==============================================================================
def run_batch_sequence_analysis(
    input_file: Union[str, Path],
    output_file: Optional[Union[str, Path]] = None,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    all_outputs: bool = False,
    api_key: Optional[str] = None,
    max_workers: int = 5,
    pretty: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for batch sequence analysis.

    Args:
        input_file: Path to text file containing DNA sequences (one per line)
        output_file: Path to save output (optional)
        organism: Target organism (default: human)
        output_types: List of output types to request (e.g., ["atac", "cage", "dnase"])
        all_outputs: Request all available output types
        api_key: AlphaGenome API key (optional, reads from env)
        max_workers: Maximum number of parallel workers (for future use)
        pretty: Pretty print JSON output
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - success: Boolean indicating success/failure
            - result: Main batch analysis result (if successful)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata
            - error: Error message (if failed)

    Example:
        >>> result = run_batch_sequence_analysis(
        ...     input_file="examples/data/sequences.txt",
        ...     pretty=True
        ... )
        >>> print(f"Processed {result['result']['batch_info']['total_sequences']} sequences")
    """
    script_name = "batch_sequence_analysis.py"

    try:
        # Validate input file
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        # Load sequences from file
        sequences = load_sequences_from_file(input_path)

        if not sequences:
            raise ValueError("No valid sequences found in input file")

        # Set output types
        if all_outputs:
            requested_output_types = None
        else:
            requested_output_types = validate_output_types(output_types)

        # Get API key
        client_api_key = get_api_key(api_key)

        # Initialize client
        client = AlphaGenomeClient(client_api_key)

        # Make batch prediction
        batch_result = client.predict_sequences(
            sequences=sequences,
            organism=organism,
            output_types=requested_output_types
        )

        # Check if prediction was successful
        if not batch_result.get('success', False):
            return batch_result

        # Create enhanced result with metadata
        result = {
            "success": True,
            "result": batch_result,
            "metadata": {
                "input_file": str(input_path),
                "total_sequences": len(sequences),
                "organism": organism,
                "output_types_requested": requested_output_types or 'all',
                "max_workers": max_workers
            },
            "output_file": None
        }

        # Add script metadata
        add_metadata(result, script_name,
                    pretty_output=pretty)

        # Add sequence statistics to metadata
        sequence_lengths = [len(seq) for seq in sequences]
        result['metadata'].update({
            "sequence_statistics": {
                "min_length": min(sequence_lengths),
                "max_length": max(sequence_lengths),
                "mean_length": round(sum(sequence_lengths) / len(sequence_lengths), 1)
            }
        })

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
  # Analyze sequences from file with default outputs
  python %(prog)s --input examples/data/sequences.txt

  # Analyze with specific output types
  python %(prog)s --input examples/data/sequences.txt --output-types atac cage

  # Save results with pretty formatting
  python %(prog)s --input examples/data/sequences.txt --output results/batch.json --pretty

  # Analyze all output types with parallel processing
  python %(prog)s --input examples/data/sequences.txt --all-outputs --max-workers 10
        """
    )

    # Input options
    parser.add_argument('--input', '-i', required=True,
                       help='Path to text file containing DNA sequences (one per line)')

    # Analysis options
    parser.add_argument('--organism', default=DEFAULT_CONFIG["organism"],
                       help=f'Target organism (default: {DEFAULT_CONFIG["organism"]})')
    parser.add_argument('--output-types', nargs='*',
                       help='Specific output types to request (e.g., atac cage dnase)')
    parser.add_argument('--all-outputs', action='store_true',
                       help='Request all available output types')
    parser.add_argument('--max-workers', type=int, default=DEFAULT_CONFIG["max_workers"],
                       help=f'Maximum number of parallel workers (default: {DEFAULT_CONFIG["max_workers"]})')

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
        # Run batch analysis
        result = run_batch_sequence_analysis(
            input_file=args.input,
            output_file=args.output,
            organism=args.organism,
            output_types=args.output_types,
            all_outputs=args.all_outputs,
            api_key=args.api_key,
            max_workers=args.max_workers,
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
        error_result = handle_error(e, "batch_sequence_analysis.py")
        write_output(error_result, pretty=args.pretty)
        sys.exit(1)


if __name__ == '__main__':
    main()