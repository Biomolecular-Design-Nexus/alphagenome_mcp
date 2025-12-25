#!/usr/bin/env python3
"""
Use Case 6: Output Metadata Retrieval using AlphaGenome API

This script retrieves metadata about available output types and capabilities
from the AlphaGenome API, helping users understand what analyses are available.

Example usage:
    python examples/use_case_6_output_metadata.py --organism human
    python examples/use_case_6_output_metadata.py --list-outputs
"""

import argparse
import json
import sys
import os
from typing import Optional

# Add the repo directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'repo', 'AlphaGenome-MCP-Server'))

try:
    from alphagenome_client import AlphaGenomeClient
except ImportError:
    print("Error: Could not import AlphaGenome client. Please ensure the environment is set up correctly.")
    sys.exit(1)


def get_output_metadata(organism: str = "human", api_key: Optional[str] = None) -> dict:
    """
    Get metadata about available outputs for an organism.

    Args:
        organism: Target organism (default: "human")
        api_key: AlphaGenome API key

    Returns:
        Dictionary with metadata results
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
        result = client.get_output_metadata(organism=organism)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "type": type(e).__name__
        }


def parse_metadata(metadata: dict) -> dict:
    """
    Parse and organize metadata into a more readable format.

    Args:
        metadata: Raw metadata from AlphaGenome API

    Returns:
        Structured metadata information
    """
    if not metadata or not isinstance(metadata, dict):
        return {"parsed": "No metadata available"}

    parsed = {
        "summary": "AlphaGenome API output metadata",
        "available_outputs": [],
        "capabilities": {}
    }

    # This would be customized based on actual API response structure
    # For now, provide a general parsing framework
    try:
        if 'result' in metadata:
            result_data = metadata['result']
            parsed["raw_metadata"] = result_data

            # Extract output types if available
            if isinstance(result_data, dict):
                for key, value in result_data.items():
                    if 'output' in key.lower() or 'type' in key.lower():
                        parsed["available_outputs"].append({
                            "name": key,
                            "info": value
                        })

    except Exception as e:
        parsed["parsing_error"] = str(e)

    return parsed


def list_known_outputs() -> dict:
    """
    List known output types from documentation.

    Returns:
        Dictionary with known output types
    """
    known_outputs = {
        "summary": "Known AlphaGenome output types",
        "output_types": [
            {
                "name": "ATAC",
                "description": "ATAC-seq chromatin accessibility data",
                "usage": "atac"
            },
            {
                "name": "CAGE",
                "description": "CAGE transcription start site data",
                "usage": "cage"
            },
            {
                "name": "DNASE",
                "description": "DNase hypersensitivity data",
                "usage": "dnase"
            },
            {
                "name": "HISTONE_MARKS",
                "description": "ChIP-seq histone modification data",
                "usage": "histone_marks"
            },
            {
                "name": "GENE_EXPRESSION",
                "description": "RNA-seq gene expression data",
                "usage": "gene_expression"
            },
            {
                "name": "CONTACT_MAPS",
                "description": "3D chromatin contact maps",
                "usage": "contact_maps"
            },
            {
                "name": "SPLICE_JUNCTIONS",
                "description": "Splice junction predictions",
                "usage": "splice_junctions"
            }
        ],
        "constraints": {
            "max_sequence_length": "1M base pairs",
            "max_interval_size": "1M base pairs",
            "supported_lengths": ["2KB", "16KB", "131KB", "524KB", "1MB"],
            "max_parallel_workers": 10,
            "variant_scoring_algorithms": 19
        },
        "organisms": {
            "supported": ["human", "homo_sapiens"],
            "default": "human"
        }
    }

    return known_outputs


def main():
    parser = argparse.ArgumentParser(
        description="Retrieve AlphaGenome API metadata and capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get metadata for human organism
  python %(prog)s --organism human

  # List known output types from documentation
  python %(prog)s --list-outputs

  # Get metadata with detailed parsing
  python %(prog)s --organism human --parse
        """
    )

    # Analysis options
    parser.add_argument('--organism', default='human',
                       help='Target organism (default: human)')
    parser.add_argument('--list-outputs', action='store_true',
                       help='List known output types from documentation')
    parser.add_argument('--parse', action='store_true',
                       help='Parse and structure the metadata')

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
        if args.list_outputs:
            # Return known outputs without API call
            result = list_known_outputs()
        else:
            # Get metadata from API
            result = get_output_metadata(
                organism=args.organism,
                api_key=args.api_key
            )

            # Parse metadata if requested
            if args.parse and result.get('success'):
                parsed_metadata = parse_metadata(result)
                result['parsed_metadata'] = parsed_metadata

        # Add analysis metadata
        result['metadata'] = {
            'organism': args.organism,
            'source': 'documentation' if args.list_outputs else 'api',
            'parsing_enabled': args.parse,
            'script': 'use_case_6_output_metadata.py'
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

        # Exit with error code if API call failed (but not for list-outputs)
        if not args.list_outputs and not result.get('success', False):
            sys.exit(1)

    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "type": type(e).__name__,
            "script": "use_case_6_output_metadata.py"
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