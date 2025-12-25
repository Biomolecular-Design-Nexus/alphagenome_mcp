"""
Parsing utilities for MCP scripts.

Extracted and simplified parsing functions from use case scripts.
"""

import re
from typing import Tuple


def parse_interval_string(interval_str: str) -> Tuple[str, int, int]:
    """
    Parse genomic interval string in format 'chr:start-end'.

    Extracted from examples/use_case_2_genomic_interval_analysis.py:parse_interval_string

    Args:
        interval_str: String in format "chr1:1000000-2000000"

    Returns:
        Tuple of (chromosome, start, end)

    Raises:
        ValueError: If interval format is invalid
    """
    # Match patterns like chr1:1000-2000 or chr1:1000000-2000000
    pattern = r'^([^:]+):(\d+)-(\d+)$'
    match = re.match(pattern, interval_str.strip())

    if not match:
        raise ValueError(f"Invalid interval format: {interval_str}. Expected format: chr:start-end (e.g., chr1:1000-2000)")

    chromosome = match.group(1)
    start = int(match.group(2))
    end = int(match.group(3))

    if start >= end:
        raise ValueError(f"Start position ({start}) must be less than end position ({end})")

    if start < 0:
        raise ValueError(f"Start position ({start}) cannot be negative")

    return chromosome, start, end


def parse_variant_string(variant_str: str) -> Tuple[str, int, str, str]:
    """
    Parse variant string in format 'chr:posREF>ALT'.

    Extracted from examples/use_case_3_variant_effect_prediction.py:parse_variant_string

    Args:
        variant_str: String in format "chr1:1001000A>G"

    Returns:
        Tuple of (chromosome, position, ref, alt)

    Raises:
        ValueError: If variant format is invalid
    """
    # Match patterns like chr1:1001000A>G
    pattern = r'^([^:]+):(\d+)([ATGCN]+)>([ATGCN]+)$'
    match = re.match(pattern, variant_str.strip().upper())

    if not match:
        raise ValueError(f"Invalid variant format: {variant_str}. Expected format: chr:posREF>ALT (e.g., chr1:1001000A>G)")

    chromosome = match.group(1)
    position = int(match.group(2))
    ref = match.group(3)
    alt = match.group(4)

    if position < 0:
        raise ValueError(f"Position ({position}) cannot be negative")

    if not ref or not alt:
        raise ValueError("Reference and alternate alleles cannot be empty")

    # Validate nucleotides
    valid_chars = set('ATGCN')
    if not set(ref).issubset(valid_chars):
        raise ValueError(f"Invalid characters in reference allele: {ref}")
    if not set(alt).issubset(valid_chars):
        raise ValueError(f"Invalid characters in alternate allele: {alt}")

    return chromosome, position, ref, alt


def validate_variant_in_interval(chromosome: str, position: int, interval_chr: str,
                                interval_start: int, interval_end: int) -> None:
    """
    Validate that variant is within the specified genomic interval.

    Extracted from examples/use_case_3_variant_effect_prediction.py and use_case_4_variant_scoring.py

    Args:
        chromosome: Variant chromosome
        position: Variant position
        interval_chr: Interval chromosome
        interval_start: Interval start position
        interval_end: Interval end position

    Raises:
        ValueError: If variant is not within interval
    """
    # Case-insensitive chromosome comparison (fix from step 4 execution)
    if chromosome.lower() != interval_chr.lower():
        raise ValueError(f"Variant chromosome ({chromosome}) must match interval chromosome ({interval_chr})")

    if not (interval_start <= position <= interval_end):
        raise ValueError(f"Variant position ({position}) must be within interval ({interval_start}-{interval_end})")


def normalize_chromosome(chromosome: str) -> str:
    """
    Normalize chromosome name for consistent comparison.

    Args:
        chromosome: Chromosome name (e.g., "chr1", "CHR1", "1")

    Returns:
        Normalized chromosome name
    """
    # Convert to lowercase for consistent comparison
    return chromosome.lower()


def validate_genomic_coordinates(chromosome: str, start: int, end: int) -> None:
    """
    Validate genomic coordinates.

    Args:
        chromosome: Chromosome name
        start: Start position
        end: End position

    Raises:
        ValueError: If coordinates are invalid
    """
    if start < 0:
        raise ValueError(f"Start position ({start}) cannot be negative")

    if end < 0:
        raise ValueError(f"End position ({end}) cannot be negative")

    if start >= end:
        raise ValueError(f"Start position ({start}) must be less than end position ({end})")

    if not chromosome:
        raise ValueError("Chromosome cannot be empty")