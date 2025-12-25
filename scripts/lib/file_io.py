"""
I/O utilities for MCP scripts.

Extracted and simplified from repo code to minimize dependencies.
"""

import json
from pathlib import Path
from typing import Union, Any, List


def load_json(file_path: Union[str, Path]) -> dict:
    """Load JSON file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def save_json(data: dict, file_path: Union[str, Path], pretty: bool = True) -> None:
    """Save data to JSON file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        if pretty:
            json.dump(data, f, indent=2)
        else:
            json.dump(data, f)


def load_text(file_path: Union[str, Path]) -> str:
    """Load text file."""
    with open(file_path, 'r') as f:
        return f.read().strip()


def save_text(text: str, file_path: Union[str, Path]) -> None:
    """Save text to file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, 'w') as f:
        f.write(text)


def load_sequence_from_file(file_path: Union[str, Path]) -> str:
    """
    Load DNA sequence from a text file.

    Extracted from examples/use_case_1_dna_sequence_prediction.py:load_sequence_from_file
    """
    try:
        with open(file_path, 'r') as f:
            # Read first line and strip whitespace
            sequence = f.readline().strip()
            # Remove any non-DNA characters
            sequence = ''.join(c.upper() for c in sequence if c.upper() in 'ATGCN')
            return sequence
    except Exception as e:
        raise ValueError(f"Could not read sequence from {file_path}: {e}")


def load_sequences_from_file(file_path: Union[str, Path]) -> List[str]:
    """
    Load multiple DNA sequences from a text file (one per line).

    Extracted from examples/use_case_5_batch_sequence_analysis.py:load_sequences_from_file
    """
    try:
        sequences = []
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                sequence = line.strip()
                if sequence:  # Skip empty lines
                    # Clean sequence (remove non-DNA characters)
                    cleaned_sequence = ''.join(c.upper() for c in sequence if c.upper() in 'ATGCN')
                    if cleaned_sequence:
                        sequences.append(cleaned_sequence)
                    else:
                        raise ValueError(f"Line {line_num} contains no valid DNA characters: {sequence}")

        if not sequences:
            raise ValueError("No valid DNA sequences found in file")

        return sequences
    except Exception as e:
        raise ValueError(f"Could not read sequences from {file_path}: {e}")


def validate_dna_sequence(sequence: str) -> None:
    """
    Validate DNA sequence contains only valid characters.

    Extracted from multiple use case scripts.
    """
    if not sequence:
        raise ValueError("DNA sequence cannot be empty")

    # Check for valid DNA characters
    valid_chars = set('ATGCN')
    invalid_chars = set(sequence.upper()) - valid_chars
    if invalid_chars:
        raise ValueError(f"Invalid DNA characters found: {invalid_chars}. Only A, T, G, C, N are allowed")


def format_output(data: Any, pretty: bool = False) -> str:
    """Format data as JSON string."""
    if pretty:
        return json.dumps(data, indent=2)
    else:
        return json.dumps(data)


def write_output(data: Any, output_file: Union[str, Path, None] = None, pretty: bool = False) -> str:
    """
    Write output to file or return as string.

    Returns the formatted output string.
    """
    output_str = format_output(data, pretty)

    if output_file:
        save_text(output_str, output_file)
        return f"Results written to {output_file}"
    else:
        print(output_str)
        return output_str