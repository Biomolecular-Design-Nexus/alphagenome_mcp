"""
General utilities for MCP scripts.

Common helper functions extracted from use case scripts.
"""

import os
import sys
from typing import Dict, Any, Optional, List


def get_api_key(provided_key: Optional[str] = None) -> str:
    """
    Get AlphaGenome API key from argument or environment.

    Extracted from multiple use case scripts.

    Args:
        provided_key: API key provided as argument

    Returns:
        API key string

    Raises:
        ValueError: If no API key is available and not in mock mode
    """
    # Check if using mock mode first
    use_mock = os.getenv('ALPHAGENOME_USE_MOCK', '').lower() == 'true'

    if use_mock:
        return "mock_key"  # Dummy key for mock mode

    if provided_key:
        return provided_key

    # Try to get from environment
    api_key = os.getenv('ALPHAGENOME_API_KEY')
    if api_key:
        return api_key

    raise ValueError("API key required. Set ALPHAGENOME_API_KEY environment variable or use --api-key")


def handle_error(error: Exception, script_name: str) -> Dict[str, Any]:
    """
    Create standardized error response.

    Extracted from multiple use case scripts.

    Args:
        error: Exception that occurred
        script_name: Name of the script where error occurred

    Returns:
        Dictionary with error information
    """
    return {
        "success": False,
        "error": str(error),
        "type": type(error).__name__,
        "script": script_name
    }


def add_metadata(result: Dict[str, Any], script_name: str, **kwargs) -> Dict[str, Any]:
    """
    Add metadata to result dictionary.

    Extracted from multiple use case scripts.

    Args:
        result: Original result dictionary
        script_name: Name of the script
        **kwargs: Additional metadata fields

    Returns:
        Result dictionary with metadata added
    """
    if 'metadata' not in result:
        result['metadata'] = {}

    result['metadata'].update({
        'script': script_name,
        **kwargs
    })

    return result


def check_mock_mode() -> bool:
    """
    Check if we're running in mock mode.

    Returns:
        True if mock mode is enabled
    """
    return os.getenv('ALPHAGENOME_USE_MOCK', '').lower() == 'true'


def get_script_dir() -> str:
    """
    Get the directory containing the current script.

    Returns:
        Absolute path to script directory
    """
    return os.path.dirname(os.path.abspath(sys.argv[0]))


def get_project_root() -> str:
    """
    Get the project root directory.

    Returns:
        Absolute path to project root
    """
    script_dir = get_script_dir()
    if script_dir.endswith('/scripts'):
        return os.path.dirname(script_dir)
    else:
        return script_dir


def validate_output_types(output_types: Optional[List[str]]) -> Optional[List[str]]:
    """
    Validate and normalize output types.

    Args:
        output_types: List of output types to validate

    Returns:
        Validated output types or None

    Raises:
        ValueError: If invalid output types are provided
    """
    if output_types is None:
        return None

    valid_output_types = {'atac', 'cage', 'dnase', 'histone_marks', 'gene_expression'}
    normalized_types = [ot.lower() for ot in output_types]

    invalid_types = set(normalized_types) - valid_output_types
    if invalid_types:
        raise ValueError(f"Invalid output types: {invalid_types}. Valid types: {valid_output_types}")

    return normalized_types


def calculate_gc_content(sequence: str) -> float:
    """
    Calculate GC content of DNA sequence.

    Args:
        sequence: DNA sequence string

    Returns:
        GC content as percentage (0-100)
    """
    if not sequence:
        return 0.0

    gc_count = sequence.upper().count('G') + sequence.upper().count('C')
    return (gc_count / len(sequence)) * 100.0


def create_sequence_metadata(sequence: str, organism: str = "human",
                           output_types: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Create metadata for sequence analysis.

    Args:
        sequence: DNA sequence
        organism: Target organism
        output_types: Requested output types

    Returns:
        Metadata dictionary
    """
    return {
        'sequence_length': len(sequence),
        'gc_content': round(calculate_gc_content(sequence), 2),
        'organism': organism,
        'output_types_requested': output_types or 'all'
    }