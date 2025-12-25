# MCP Scripts

Clean, self-contained scripts extracted from use cases for MCP tool wrapping.

## Design Principles

1. **Minimal Dependencies**: Only essential packages imported (no heavy ML libraries)
2. **Self-Contained**: Functions inlined where possible, shared utilities in `lib/`
3. **Configurable**: Parameters in config files, not hardcoded
4. **MCP-Ready**: Each script has a main function ready for MCP wrapping

## Scripts

| Script | Description | Repo Dependent | Config | Tested |
|--------|-------------|----------------|--------|--------|
| `dna_sequence_prediction.py` | Predict genomic features for DNA sequences | No | `configs/dna_sequence_prediction_config.json` | ✅ |
| `genomic_interval_analysis.py` | Analyze genomic intervals for regulatory features | No | `configs/genomic_interval_analysis_config.json` | ✅ |
| `variant_effect_prediction.py` | Predict effects of genetic variants | No | `configs/variant_analysis_config.json` | ✅ |
| `variant_scoring.py` | Score variants with pathogenicity algorithms | No | `configs/variant_analysis_config.json` | ✅ |
| `batch_sequence_analysis.py` | Analyze multiple sequences in batch | No | `configs/batch_analysis_config.json` | ✅ |
| `output_metadata.py` | Get metadata about available outputs | No | None | ✅ |

## Dependencies

### Essential Imports Only
All scripts use only built-in Python packages:
- `argparse`: Command-line interface
- `sys`: System operations
- `pathlib`: Path handling
- `typing`: Type hints

### No External Dependencies
- ❌ No `torch`, `tensorflow`, or heavy ML libraries
- ❌ No `numpy`, `pandas` (not needed for API client wrapper)
- ❌ No complex scientific computing packages
- ✅ Pure Python implementation with simplified client

### Repository Dependencies
- **Simplified AlphaGenome Client**: Extracted to `lib/alphagenome_client.py`
- **Mock Client**: Inlined for testing without real API access
- **Parsing Functions**: Extracted to `lib/parsers.py`

## Usage

### Environment Setup
```bash
# Activate environment (prefer mamba over conda)
mamba activate ./env  # or: conda activate ./env

# Enable mock mode for testing
export ALPHAGENOME_USE_MOCK=true
```

### Running Scripts

#### 1. DNA Sequence Prediction
```bash
# Single sequence
python scripts/dna_sequence_prediction.py --sequence "ATGCGATCGATCGATC" --pretty

# From file
python scripts/dna_sequence_prediction.py --input examples/data/sample_sequence.txt --output results/pred.json

# Specific output types
python scripts/dna_sequence_prediction.py --sequence "ATGCGATC" --output-types atac cage --pretty
```

#### 2. Genomic Interval Analysis
```bash
# Analyze interval
python scripts/genomic_interval_analysis.py --interval "chr1:1000000-1002048" --pretty

# Save to file
python scripts/genomic_interval_analysis.py --interval "chr1:1000000-1002048" --output results/interval.json
```

#### 3. Variant Effect Prediction
```bash
# Predict variant effects
python scripts/variant_effect_prediction.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --pretty

# Specific output types
python scripts/variant_effect_prediction.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --output-types atac cage
```

#### 4. Variant Scoring
```bash
# Score variant pathogenicity
python scripts/variant_scoring.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --pretty
```

#### 5. Batch Analysis
```bash
# Process multiple sequences
python scripts/batch_sequence_analysis.py --input examples/test_sequences.txt --pretty

# Save results
python scripts/batch_sequence_analysis.py --input examples/test_sequences.txt --output results/batch.json
```

#### 6. Output Metadata
```bash
# Get available output types
python scripts/output_metadata.py --pretty

# For specific organism
python scripts/output_metadata.py --organism mouse --pretty
```

### Common Options

| Option | Description | Example |
|--------|-------------|---------|
| `--pretty` | Pretty print JSON output | `--pretty` |
| `--output` | Save to file | `--output results/output.json` |
| `--organism` | Target organism | `--organism human` |
| `--output-types` | Specific outputs | `--output-types atac cage dnase` |
| `--all-outputs` | Request all output types | `--all-outputs` |
| `--api-key` | API key (or use env var) | `--api-key YOUR_KEY` |

## Shared Library

**Path**: `scripts/lib/`

| Module | Functions | Description |
|--------|-----------|-------------|
| `alphagenome_client.py` | AlphaGenomeClient, MockAlphaGenomeClient | Simplified API client with mock support |
| `file_io.py` | 8 functions | File I/O utilities for sequences and JSON |
| `parsers.py` | 6 functions | Genomic coordinate and variant parsing |
| `utils.py` | 8 functions | General utilities (API keys, metadata, validation) |

**Total Functions**: 30 (all essential, no bloat)

## Configuration Files

**Path**: `configs/`

| Config File | Description | Used By |
|-------------|-------------|---------|
| `default_config.json` | Default settings for all scripts | All scripts |
| `dna_sequence_prediction_config.json` | Sequence prediction settings | `dna_sequence_prediction.py` |
| `genomic_interval_analysis_config.json` | Interval analysis settings | `genomic_interval_analysis.py` |
| `variant_analysis_config.json` | Variant analysis settings | `variant_*.py` scripts |
| `batch_analysis_config.json` | Batch processing settings | `batch_sequence_analysis.py` |

## For MCP Wrapping (Step 6)

Each script exports a main function that can be wrapped:

```python
# Example MCP wrapper
from scripts.dna_sequence_prediction import run_dna_sequence_prediction

@mcp.tool()
def predict_sequence(input_sequence: str, organism: str = "human") -> dict:
    """Predict genomic features for DNA sequence."""
    return run_dna_sequence_prediction(
        input_sequence=input_sequence,
        organism=organism
    )
```

### Function Signatures for MCP

| Script | Main Function | Key Parameters |
|--------|---------------|----------------|
| `dna_sequence_prediction.py` | `run_dna_sequence_prediction()` | `input_sequence`, `organism`, `output_types` |
| `genomic_interval_analysis.py` | `run_genomic_interval_analysis()` | `interval`, `organism`, `output_types` |
| `variant_effect_prediction.py` | `run_variant_effect_prediction()` | `variant`, `interval`, `organism` |
| `variant_scoring.py` | `run_variant_scoring()` | `variant`, `interval`, `organism` |
| `batch_sequence_analysis.py` | `run_batch_sequence_analysis()` | `input_file`, `organism`, `output_types` |
| `output_metadata.py` | `run_output_metadata()` | `organism` |

## Testing

All scripts tested with mock mode:

```bash
# Test all scripts
export ALPHAGENOME_USE_MOCK=true

python scripts/dna_sequence_prediction.py --sequence "ATGCGATC" --pretty
python scripts/genomic_interval_analysis.py --interval "chr1:1000000-1002048" --pretty
python scripts/variant_effect_prediction.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --pretty
python scripts/variant_scoring.py --variant "chr1:1001000A>G" --interval "chr1:1000000-1002048" --pretty
python scripts/batch_sequence_analysis.py --input examples/test_sequences.txt --pretty
python scripts/output_metadata.py --pretty
```

**Status**: ✅ All scripts tested and working

## Dependencies Checklist

For each script, verified:
- ✅ No unnecessary imports
- ✅ Simple utility functions are inlined
- ✅ Complex repo functions use simplified versions
- ✅ Paths are relative, not absolute
- ✅ Config values are externalized
- ✅ No hardcoded credentials or API keys
- ✅ Mock mode supports testing without real API

## Important Notes

- **Goal is MCP-ready scripts**: These will be wrapped in Step 6
- **Mock mode enabled by default**: Set `ALPHAGENOME_USE_MOCK=true` for testing
- **No heavy dependencies**: Pure Python with minimal imports
- **Self-contained**: Can run independently of original repo structure
- **Configurable**: All parameters can be controlled via command line or config files