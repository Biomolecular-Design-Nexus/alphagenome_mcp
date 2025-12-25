#!/usr/bin/env python3
"""MCP Server for AlphaGenome-MCP-Server

Provides both synchronous and asynchronous (submit) APIs for genomic analysis tools.
"""

from fastmcp import FastMCP
from pathlib import Path
from typing import Optional, List, Union
import sys
import os

# Setup paths
SCRIPT_DIR = Path(__file__).parent.resolve()
MCP_ROOT = SCRIPT_DIR.parent
SCRIPTS_DIR = MCP_ROOT / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(SCRIPTS_DIR))

# Set mock mode for all operations
os.environ["ALPHAGENOME_USE_MOCK"] = "true"

from jobs.manager import job_manager

# Create MCP server
mcp = FastMCP("AlphaGenome-MCP-Server")

# ==============================================================================
# Job Management Tools (for async operations)
# ==============================================================================

@mcp.tool()
def get_job_status(job_id: str) -> dict:
    """
    Get the status of a submitted job.

    Args:
        job_id: The job ID returned from a submit_* function

    Returns:
        Dictionary with job status, timestamps, and any errors
    """
    return job_manager.get_job_status(job_id)

@mcp.tool()
def get_job_result(job_id: str) -> dict:
    """
    Get the results of a completed job.

    Args:
        job_id: The job ID of a completed job

    Returns:
        Dictionary with the job results or error if not completed
    """
    return job_manager.get_job_result(job_id)

@mcp.tool()
def get_job_log(job_id: str, tail: int = 50) -> dict:
    """
    Get log output from a running or completed job.

    Args:
        job_id: The job ID to get logs for
        tail: Number of lines from end (default: 50, use 0 for all)

    Returns:
        Dictionary with log lines and total line count
    """
    return job_manager.get_job_log(job_id, tail)

@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """
    Cancel a running job.

    Args:
        job_id: The job ID to cancel

    Returns:
        Success or error message
    """
    return job_manager.cancel_job(job_id)

@mcp.tool()
def list_jobs(status: Optional[str] = None) -> dict:
    """
    List all submitted jobs.

    Args:
        status: Filter by status (pending, running, completed, failed, cancelled)

    Returns:
        List of jobs with their status
    """
    return job_manager.list_jobs(status)

# ==============================================================================
# Synchronous Tools (for fast operations)
# ==============================================================================

@mcp.tool()
def predict_dna_sequence(
    sequence: Optional[str] = None,
    input_file: Optional[str] = None,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_file: Optional[str] = None
) -> dict:
    """
    Predict genomic features for DNA sequences (fast operation).

    Fast operation suitable for single sequences (~300ms).
    For batch processing of multiple sequences, use submit_dna_sequence_prediction.

    Args:
        sequence: DNA sequence string to analyze
        input_file: Path to file containing DNA sequence (alternative to sequence)
        organism: Target organism (default: human)
        output_types: List of output types (atac, cage, dnase, histone_marks, gene_expression)
        output_file: Optional path to save results as JSON

    Returns:
        Dictionary with prediction results and metadata

    Example:
        predict_dna_sequence(sequence="ATGCGATCGTAGCTAGC", organism="human")
    """
    try:
        from dna_sequence_prediction import run_dna_sequence_prediction

        result = run_dna_sequence_prediction(
            sequence=sequence,
            input_file=input_file,
            organism=organism,
            output_types=output_types,
            output_file=output_file,
            pretty=True
        )
        return {"status": "success", **result}
    except FileNotFoundError as e:
        return {"status": "error", "error": f"File not found: {e}"}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid input: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def analyze_genomic_interval(
    interval: str,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_file: Optional[str] = None
) -> dict:
    """
    Analyze genomic intervals for regulatory features (fast operation).

    Fast operation suitable for single intervals (~150ms).

    Args:
        interval: Genomic interval in format "chr:start-end" (e.g., "chr1:1000000-1002048")
        organism: Target organism (default: human)
        output_types: List of output types (atac, cage, dnase, histone_marks, gene_expression)
        output_file: Optional path to save results as JSON

    Returns:
        Dictionary with accessibility scores and peaks data

    Example:
        analyze_genomic_interval(interval="chr1:1000000-1002048", organism="human")
    """
    try:
        from genomic_interval_analysis import run_genomic_interval_analysis

        result = run_genomic_interval_analysis(
            interval=interval,
            organism=organism,
            output_types=output_types,
            output_file=output_file,
            pretty=True
        )
        return {"status": "success", **result}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid interval format: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def predict_variant_effects(
    variant: str,
    interval: str,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_file: Optional[str] = None
) -> dict:
    """
    Predict effects of genetic variants (fast operation).

    Fast operation suitable for single variants (~200ms).
    For batch processing of multiple variants, use submit_variant_effect_prediction.

    Args:
        variant: Variant in format "chr:posREF>ALT" (e.g., "chr1:1001000A>G")
        interval: Genomic interval containing the variant (e.g., "chr1:1000000-1002048")
        organism: Target organism (default: human)
        output_types: List of output types (atac, cage, dnase, histone_marks, gene_expression)
        output_file: Optional path to save results as JSON

    Returns:
        Dictionary with reference/alt predictions and effect scores

    Example:
        predict_variant_effects(variant="chr1:1001000A>G", interval="chr1:1000000-1002048")
    """
    try:
        from variant_effect_prediction import run_variant_effect_prediction

        result = run_variant_effect_prediction(
            variant=variant,
            interval=interval,
            organism=organism,
            output_types=output_types,
            output_file=output_file,
            pretty=True
        )
        return {"status": "success", **result}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid variant or interval format: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def score_variant_pathogenicity(
    variant: str,
    interval: str,
    organism: str = "human",
    output_file: Optional[str] = None
) -> dict:
    """
    Score variants with pathogenicity algorithms (fast operation).

    Fast operation suitable for single variants (~200ms).
    Runs 19 different pathogenicity scoring algorithms.
    For batch processing of multiple variants, use submit_variant_scoring.

    Args:
        variant: Variant in format "chr:posREF>ALT" (e.g., "chr1:1001000A>G")
        interval: Genomic interval containing the variant (e.g., "chr1:1000000-1002048")
        organism: Target organism (default: human)
        output_file: Optional path to save results as JSON

    Returns:
        Dictionary with scores from 19 pathogenicity algorithms

    Example:
        score_variant_pathogenicity(variant="chr1:1001000A>G", interval="chr1:1000000-1002048")
    """
    try:
        from variant_scoring import run_variant_scoring

        result = run_variant_scoring(
            variant=variant,
            interval=interval,
            organism=organism,
            output_file=output_file,
            pretty=True
        )
        return {"status": "success", **result}
    except ValueError as e:
        return {"status": "error", "error": f"Invalid variant or interval format: {e}"}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def get_output_metadata(
    organism: Optional[str] = None,
    output_file: Optional[str] = None
) -> dict:
    """
    Get metadata about available outputs and organisms (fast operation).

    Fast operation suitable for metadata queries (~100ms).

    Args:
        organism: Target organism to get specific metadata for (optional)
        output_file: Optional path to save results as JSON

    Returns:
        Dictionary with available output types and descriptions

    Example:
        get_output_metadata(organism="human")
    """
    try:
        from output_metadata import run_output_metadata

        result = run_output_metadata(
            organism=organism,
            output_file=output_file,
            pretty=True
        )
        return {"status": "success", **result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

# ==============================================================================
# Submit Tools (for long-running operations and batch processing)
# ==============================================================================

@mcp.tool()
def submit_dna_sequence_prediction(
    sequence: Optional[str] = None,
    input_file: Optional[str] = None,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit DNA sequence prediction for background processing.

    This operation may take more than 10 minutes for large sequences.
    Use get_job_status() to monitor progress and get_job_result() to retrieve results.

    Args:
        sequence: DNA sequence string to analyze
        input_file: Path to file containing DNA sequence (alternative to sequence)
        organism: Target organism (default: human)
        output_types: List of output types (atac, cage, dnase, histone_marks, gene_expression)
        output_dir: Directory to save outputs
        job_name: Optional name for the job (for easier tracking)

    Returns:
        Dictionary with job_id for tracking. Use:
        - get_job_status(job_id) to check progress
        - get_job_result(job_id) to get results when completed
        - get_job_log(job_id) to see execution logs
    """
    script_path = str(SCRIPTS_DIR / "dna_sequence_prediction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "sequence": sequence,
            "input_file": input_file,
            "organism": organism,
            "output_types": output_types,
            "output_dir": output_dir
        },
        job_name=job_name or "dna_sequence_prediction"
    )

@mcp.tool()
def submit_variant_effect_prediction(
    variant: str,
    interval: str,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit variant effect prediction for background processing.

    This operation may take more than 10 minutes for complex analysis.
    Use get_job_status() to monitor progress and get_job_result() to retrieve results.

    Args:
        variant: Variant in format "chr:posREF>ALT" (e.g., "chr1:1001000A>G")
        interval: Genomic interval containing the variant
        organism: Target organism (default: human)
        output_types: List of output types (atac, cage, dnase, histone_marks, gene_expression)
        output_dir: Directory to save outputs
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the prediction job
    """
    script_path = str(SCRIPTS_DIR / "variant_effect_prediction.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "variant": variant,
            "interval": interval,
            "organism": organism,
            "output_types": output_types,
            "output_dir": output_dir
        },
        job_name=job_name or "variant_effect_prediction"
    )

@mcp.tool()
def submit_variant_scoring(
    variant: str,
    interval: str,
    organism: str = "human",
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit variant pathogenicity scoring for background processing.

    This operation runs 19 scoring algorithms and may take more than 10 minutes.
    Use get_job_status() to monitor progress and get_job_result() to retrieve results.

    Args:
        variant: Variant in format "chr:posREF>ALT"
        interval: Genomic interval containing the variant
        organism: Target organism (default: human)
        output_dir: Directory to save outputs
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the scoring job
    """
    script_path = str(SCRIPTS_DIR / "variant_scoring.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "variant": variant,
            "interval": interval,
            "organism": organism,
            "output_dir": output_dir
        },
        job_name=job_name or "variant_scoring"
    )

@mcp.tool()
def submit_batch_sequence_analysis(
    input_file: str,
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch sequence analysis for background processing.

    This operation analyzes multiple sequences and may take more than 10 minutes.
    Suitable for processing many sequences at once.

    Args:
        input_file: Path to text file with DNA sequences (one per line)
        organism: Target organism (default: human)
        output_types: List of output types (atac, cage, dnase, histone_marks, gene_expression)
        output_dir: Directory to save outputs
        job_name: Optional name for the job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    script_path = str(SCRIPTS_DIR / "batch_sequence_analysis.py")

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "input_file": input_file,
            "organism": organism,
            "output_types": output_types,
            "output_dir": output_dir
        },
        job_name=job_name or "batch_sequence_analysis"
    )

# ==============================================================================
# Batch Processing Tools
# ==============================================================================

@mcp.tool()
def submit_batch_variant_analysis(
    variants: List[str],
    intervals: List[str],
    analysis_type: str = "effects",
    organism: str = "human",
    output_types: Optional[List[str]] = None,
    output_dir: Optional[str] = None,
    job_name: Optional[str] = None
) -> dict:
    """
    Submit batch variant analysis for multiple variants.

    Processes multiple variants in a single job. Suitable for:
    - Processing many variants at once
    - Large-scale variant analysis
    - Parallel processing of independent variants

    Args:
        variants: List of variants in format "chr:posREF>ALT"
        intervals: List of genomic intervals (one per variant)
        analysis_type: Type of analysis - "effects" or "scoring"
        organism: Target organism (default: human)
        output_types: List of output types (for effects analysis)
        output_dir: Directory to save all outputs
        job_name: Optional name for the batch job

    Returns:
        Dictionary with job_id for tracking the batch job
    """
    if len(variants) != len(intervals):
        return {
            "status": "error",
            "error": "Number of variants must match number of intervals"
        }

    if analysis_type == "effects":
        script_path = str(SCRIPTS_DIR / "variant_effect_prediction.py")
    elif analysis_type == "scoring":
        script_path = str(SCRIPTS_DIR / "variant_scoring.py")
    else:
        return {
            "status": "error",
            "error": "analysis_type must be 'effects' or 'scoring'"
        }

    # For batch processing, we'll process variants sequentially
    # This could be enhanced to run multiple scripts in parallel
    variants_str = ",".join(variants)
    intervals_str = ",".join(intervals)

    return job_manager.submit_job(
        script_path=script_path,
        args={
            "variant": variants_str,
            "interval": intervals_str,
            "organism": organism,
            "output_types": output_types,
            "output_dir": output_dir
        },
        job_name=job_name or f"batch_variant_{analysis_type}_{len(variants)}_variants"
    )

# ==============================================================================
# Validation and Utilities
# ==============================================================================

@mcp.tool()
def validate_genomic_inputs(
    sequence: Optional[str] = None,
    variant: Optional[str] = None,
    interval: Optional[str] = None
) -> dict:
    """
    Validate genomic inputs before processing.

    Args:
        sequence: DNA sequence to validate (optional)
        variant: Variant string to validate (optional)
        interval: Genomic interval to validate (optional)

    Returns:
        Dictionary with validation results for each input
    """
    try:
        from lib.parsers import parse_interval_string, parse_variant_string
        from lib.file_io import validate_dna_sequence

        results = {}

        if sequence:
            try:
                validate_dna_sequence(sequence)
                results["sequence"] = {"valid": True, "length": len(sequence)}
            except Exception as e:
                results["sequence"] = {"valid": False, "error": str(e)}

        if interval:
            try:
                chrom, start, end = parse_interval_string(interval)
                results["interval"] = {
                    "valid": True,
                    "chromosome": chrom,
                    "start": start,
                    "end": end,
                    "length": end - start
                }
            except Exception as e:
                results["interval"] = {"valid": False, "error": str(e)}

        if variant:
            try:
                chrom, pos, ref, alt = parse_variant_string(variant)
                results["variant"] = {
                    "valid": True,
                    "chromosome": chrom,
                    "position": pos,
                    "reference": ref,
                    "alternate": alt
                }
            except Exception as e:
                results["variant"] = {"valid": False, "error": str(e)}

        return {"status": "success", "validation": results}

    except Exception as e:
        return {"status": "error", "error": str(e)}

@mcp.tool()
def get_supported_organisms() -> dict:
    """
    Get list of organisms supported by AlphaGenome.

    Returns:
        Dictionary with available organism names and descriptions
    """
    return {
        "status": "success",
        "organisms": {
            "human": "Homo sapiens (default)",
            "mouse": "Mus musculus",
            "fly": "Drosophila melanogaster"
        },
        "output_types": [
            "atac",
            "cage",
            "dnase",
            "histone_marks",
            "gene_expression"
        ],
        "default_organism": "human"
    }

@mcp.tool()
def get_example_data() -> dict:
    """
    Get information about available example datasets for testing.

    Returns:
        Dictionary with example files and their descriptions
    """
    examples_dir = SCRIPTS_DIR.parent / "examples" / "data"

    examples = {
        "sequences": {
            "sample_sequence.txt": "Single DNA sequence (60 bp)",
            "test_sequences.txt": "Multiple test sequences (3 sequences)",
            "test_sequence_16k.txt": "Large test sequence (16k bp)",
            "test_sequences_16k.txt": "Multiple large sequences"
        },
        "genomic_intervals": {
            "example": "chr1:1000000-1002048",
            "description": "2048 bp interval on chromosome 1"
        },
        "variants": {
            "example": "chr1:1001000A>G",
            "description": "A to G substitution on chromosome 1"
        },
        "batch_files": {
            "sequences.txt": "Batch processing test file"
        }
    }

    # Check which files actually exist
    existing_files = {}
    if examples_dir.exists():
        for category, files in examples.items():
            if category == "sequences":
                existing_files[category] = {}
                for filename, desc in files.items():
                    file_path = examples_dir / filename
                    if file_path.exists():
                        existing_files[category][filename] = {
                            "description": desc,
                            "path": str(file_path),
                            "exists": True
                        }
                    else:
                        existing_files[category][filename] = {
                            "description": desc,
                            "path": str(file_path),
                            "exists": False
                        }
            else:
                existing_files[category] = files

    return {
        "status": "success",
        "examples_directory": str(examples_dir),
        "examples": existing_files
    }

# ==============================================================================
# Entry Point
# ==============================================================================

if __name__ == "__main__":
    mcp.run()