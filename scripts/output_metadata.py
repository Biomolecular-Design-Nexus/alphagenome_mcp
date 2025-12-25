#!/usr/bin/env python3
"""
Script: output_metadata.py
Description: Get metadata about available outputs from AlphaGenome API

Original Use Case: examples/use_case_6_output_metadata.py
Dependencies Removed: Direct repo imports, simplified client interface

Usage:
    python scripts/output_metadata.py --output <output_file>

Example:
    python scripts/output_metadata.py --output results/metadata.json
    python scripts/output_metadata.py --organism human --pretty
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
def run_output_metadata(
    output_file: Optional[Union[str, Path]] = None,
    organism: str = "human",
    api_key: Optional[str] = None,
    pretty: bool = False,
    **kwargs
) -> Dict[str, Any]:
    """
    Main function for retrieving output metadata.

    Args:
        output_file: Path to save output (optional)
        organism: Target organism (default: human)
        api_key: AlphaGenome API key (optional, reads from env)
        pretty: Pretty print JSON output
        **kwargs: Override specific config parameters

    Returns:
        Dict containing:
            - success: Boolean indicating success/failure
            - result: Metadata result (if successful)
            - output_file: Path to output file (if saved)
            - metadata: Execution metadata
            - error: Error message (if failed)

    Example:
        >>> result = run_output_metadata(organism="human", pretty=True)
        >>> print(result['result']['available_outputs'])
    """
    script_name = "output_metadata.py"

    try:
        # Get API key
        client_api_key = get_api_key(api_key)

        # Initialize client
        client = AlphaGenomeClient(client_api_key)

        # Get output metadata
        metadata_result = client.get_output_metadata(organism=organism)

        # Check if request was successful
        if not metadata_result.get('success', False):
            return metadata_result

        # Create enhanced result with metadata
        result = {
            "success": True,
            "result": metadata_result,
            "metadata": {
                "organism": organism,
                "analysis_type": "output_metadata"
            },
            "output_file": None
        }

        # Add script metadata
        add_metadata(result, script_name,
                    pretty_output=pretty)

        # Add summary information to metadata
        if 'available_outputs' in metadata_result:
            result['metadata']['summary'] = {
                "total_output_types": len(metadata_result['available_outputs']),
                "output_types": metadata_result['available_outputs']
            }

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
  # Get output metadata for human
  python %(prog)s

  # Get metadata for specific organism
  python %(prog)s --organism mouse

  # Save results with pretty formatting
  python %(prog)s --output results/metadata.json --pretty

  # Get metadata and display available output types
  python %(prog)s --pretty | grep -A 10 "available_outputs"
        """
    )

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
        # Get metadata
        result = run_output_metadata(
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

        # Exit with error code if request failed
        if not result.get('success', False):
            sys.exit(1)

        return result

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        error_result = handle_error(e, "output_metadata.py")
        write_output(error_result, pretty=args.pretty)
        sys.exit(1)


if __name__ == '__main__':
    main()