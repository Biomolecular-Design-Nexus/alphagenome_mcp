# AlphaGenome-MCP-Server

> AI-powered genomic analysis MCP server providing comprehensive DNA sequence prediction, variant analysis, and genomic feature annotation using Google DeepMind's AlphaGenome models.

## Table of Contents
- [Overview](#overview)
- [Installation](#installation)
- [Local Usage (Scripts)](#local-usage-scripts)
- [MCP Server Installation](#mcp-server-installation)
- [Using with Claude Code](#using-with-claude-code)
- [Using with Gemini CLI](#using-with-gemini-cli)
- [Available Tools](#available-tools)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

## Overview

The AlphaGenome-MCP-Server provides access to Google DeepMind's AlphaGenome models for comprehensive genomic analysis through the Model Context Protocol (MCP). It enables AI assistants to predict genomic features, analyze DNA sequences, evaluate genetic variants, and perform high-throughput batch processing.

### Features
- **DNA Sequence Analysis**: Predict chromatin accessibility, transcription start sites, DNase hypersensitivity
- **Variant Effect Prediction**: Assess functional impact of genetic variants on genomic features
- **Pathogenicity Scoring**: Score variants using 19 different algorithms for clinical interpretation
- **Genomic Interval Analysis**: Analyze specific chromosomal regions for regulatory elements
- **Batch Processing**: High-throughput analysis of multiple sequences or variants
- **Job Management**: Background processing with progress tracking for long-running tasks
- **Mock Mode**: Safe testing environment with simulated results

### Directory Structure
```
./
├── README.md               # This file
├── env/                    # Conda environment
├── src/
│   ├── server.py           # MCP server (18 tools)
│   └── jobs/               # Job management system
├── scripts/
│   ├── dna_sequence_prediction.py      # Single sequence analysis
│   ├── genomic_interval_analysis.py    # Genomic region analysis
│   ├── variant_effect_prediction.py    # Variant impact prediction
│   ├── variant_scoring.py              # Pathogenicity scoring
│   ├── batch_sequence_analysis.py      # Multi-sequence processing
│   └── output_metadata.py              # API metadata retrieval
├── examples/
│   └── data/               # Demo data
│       ├── sample_sequence.txt         # 56bp test sequence
│       ├── sequences.txt              # 7 sequences for batch testing
│       ├── test_sequence_16k.txt      # Large sequence (16KB)
│       └── test_sequences_16k.txt     # Multiple large sequences
├── configs/                # Configuration files
│   ├── default_config.json            # Main configuration
│   ├── dna_sequence_prediction_config.json
│   ├── genomic_interval_analysis_config.json
│   ├── variant_analysis_config.json
│   └── batch_analysis_config.json
└── repo/                   # Original AlphaGenome repository
    └── AlphaGenome-MCP-Server/
```

---

## Installation

### Prerequisites
- Conda or Mamba (mamba recommended for faster installation)
- Python 3.10+
- Internet connection for package installation

### Create Environment

Please strictly follow the information in `reports/step3_environment.md` for detailed environment setup. Example workflow:

```bash
# Navigate to the MCP directory
cd /home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/alphagenome_mcp

# Check package manager availability (prefer mamba)
if command -v mamba &> /dev/null; then
    PKG_MGR="mamba"
else
    PKG_MGR="conda"
fi
echo "Using package manager: $PKG_MGR"

# Create conda environment
$PKG_MGR create -p ./env python=3.11 pip -y

# Activate environment
$PKG_MGR activate ./env
# Alternative: mamba run -p ./env python script.py

# Install core dependencies
$PKG_MGR run -p ./env pip install loguru click pandas numpy tqdm

# Install AlphaGenome SDK
$PKG_MGR run -p ./env pip install alphagenome

# Install MCP dependencies
$PKG_MGR run -p ./env pip install fastmcp

# Verify installation
$PKG_MGR run -p ./env python -c "import fastmcp, alphagenome; print('✓ Installation successful')"
```

---

## Local Usage (Scripts)

You can use the scripts directly without MCP for local processing.

### Available Scripts

| Script | Description | Example Use Case |
|--------|-------------|------------------|
| `scripts/dna_sequence_prediction.py` | Predict genomic features for DNA sequences | Chromatin accessibility analysis |
| `scripts/genomic_interval_analysis.py` | Analyze genomic intervals for regulatory features | Promoter region analysis |
| `scripts/variant_effect_prediction.py` | Predict effects of genetic variants | Variant functional assessment |
| `scripts/variant_scoring.py` | Score variants with 19 pathogenicity algorithms | Clinical interpretation |
| `scripts/batch_sequence_analysis.py` | Process multiple sequences in parallel | High-throughput analysis |
| `scripts/output_metadata.py` | Retrieve API capabilities and output types | API exploration |

### Script Examples

#### DNA Sequence Prediction

```bash
# Activate environment
mamba run -p ./env python scripts/dna_sequence_prediction.py \
  --input examples/data/sample_sequence.txt \
  --output results/sequence_analysis.json \
  --output-types atac cage dnase \
  --organism human \
  --pretty
```

**Parameters:**
- `--input, -i`: Path to text file with DNA sequence (required if no --sequence)
- `--sequence, -s`: DNA sequence string directly (alternative to --input)
- `--output, -o`: Output JSON file path (default: stdout)
- `--output-types`: Space-separated list of output types (default: all)
- `--organism`: Target organism (default: human)
- `--pretty`: Pretty-print JSON output

#### Genomic Interval Analysis

```bash
mamba run -p ./env python scripts/genomic_interval_analysis.py \
  --interval chr1:1000000-1002048 \
  --output-types atac cage \
  --organism human
```

#### Variant Effect Prediction

```bash
mamba run -p ./env python scripts/variant_effect_prediction.py \
  --variant chr1:1001000A>G \
  --interval chr1:1000000-1002048 \
  --output results/variant_effects.json
```

#### Batch Sequence Analysis

```bash
mamba run -p ./env python scripts/batch_sequence_analysis.py \
  --input examples/data/sequences.txt \
  --max-workers 3 \
  --output-types atac cage \
  --summary
```

---

## MCP Server Installation

### Option 1: Using fastmcp (Recommended)

```bash
# Install MCP server for Claude Code
mamba run -p ./env fastmcp install src/server.py --name AlphaGenome-MCP-Server
```

### Option 2: Manual Installation for Claude Code

```bash
# Add MCP server to Claude Code
claude mcp add AlphaGenome-MCP-Server -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify installation
claude mcp list
```

### Option 3: Configure in settings.json

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "AlphaGenome-MCP-Server": {
      "command": "/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/alphagenome_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/alphagenome_mcp/src/server.py"]
    }
  }
}
```

---

## Using with Claude Code

After installing the MCP server, you can use it directly in Claude Code.

### Quick Start

```bash
# Start Claude Code
claude
```

### Example Prompts

#### Tool Discovery
```
What tools are available from AlphaGenome-MCP-Server?
```

#### Basic DNA Analysis
```
Use predict_dna_sequence with sequence "ATGCGATCGTAGCTAGCATGCAAATTTGGGCCCGTACGCATGCTAGCGATCGTAGCTAG" and organism "human"
```

#### Genomic Interval Analysis
```
Use analyze_genomic_interval with interval "chr1:1000000-1002048" and output_types ["atac", "cage"]
```

#### Variant Analysis
```
Use predict_variant_effects with variant "chr1:1001000A>G" and interval "chr1:1000000-1002048"
```

#### File-Based Analysis
```
Use predict_dna_sequence with input_file @examples/data/sample_sequence.txt and output_file @results/analysis.json
```

#### Long-Running Tasks (Submit API)
```
Submit a batch sequence analysis using submit_batch_sequence_analysis with input_file @examples/data/sequences.txt and job_name "batch_analysis"

Then check the job status using get_job_status

When completed, get results using get_job_result
```

#### Batch Processing
```
Process multiple variants:
Use submit_batch_variant_analysis with:
- variants: ["chr1:1001000A>G", "chr1:1001100C>T"]
- intervals: ["chr1:1000000-1002048", "chr1:1000000-1002048"]
- analysis_type: "effects"
```

### Using @ References

In Claude Code, use `@` to reference files and directories:

| Reference | Description |
|-----------|-------------|
| `@examples/data/sample_sequence.txt` | Reference a specific sequence file |
| `@examples/data/sequences.txt` | Reference batch sequence file |
| `@configs/default_config.json` | Reference configuration file |
| `@results/` | Reference output directory |

---

## Using with Gemini CLI

### Configuration

Add to `~/.gemini/settings.json`:

```json
{
  "mcpServers": {
    "AlphaGenome-MCP-Server": {
      "command": "/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/alphagenome_mcp/env/bin/python",
      "args": ["/home/xux/Desktop/NucleicMCP/NucleicMCP/tool-mcps/alphagenome_mcp/src/server.py"]
    }
  }
}
```

### Example Prompts

```bash
# Start Gemini CLI
gemini

# Example prompts (same syntax as Claude Code)
> What AlphaGenome tools are available?
> Analyze DNA sequence "ATGCGATCGTAGCTAGC" for chromatin accessibility
> Predict effects of variant chr1:1001000A>G in interval chr1:1000000-1002048
```

---

## Available Tools

### Quick Operations (Sync API)

These tools return results immediately (< 10 minutes):

| Tool | Description | Est. Runtime | Parameters |
|------|-------------|--------------|------------|
| `predict_dna_sequence` | Predict genomic features for DNA sequences | ~300ms | `sequence\|input_file`, `organism`, `output_types` |
| `analyze_genomic_interval` | Analyze genomic intervals for regulatory features | ~150ms | `interval`, `organism`, `output_types` |
| `predict_variant_effects` | Predict effects of genetic variants | ~200ms | `variant`, `interval`, `organism` |
| `score_variant_pathogenicity` | Score variants with 19 pathogenicity algorithms | ~200ms | `variant`, `interval`, `organism` |
| `get_output_metadata` | Get metadata about available outputs | ~100ms | `organism` (optional) |
| `validate_genomic_inputs` | Validate inputs before processing | ~50ms | `sequence`, `variant`, `interval` |
| `get_supported_organisms` | Get list of supported organisms | ~10ms | None |
| `get_example_data` | Get information about example datasets | ~10ms | None |

### Long-Running Tasks (Submit API)

These tools return a job_id for tracking (> 10 minutes):

| Tool | Description | Use Case | Parameters |
|------|-------------|----------|------------|
| `submit_dna_sequence_prediction` | Submit DNA sequence prediction for background | Large sequences | `sequence\|input_file`, `job_name` |
| `submit_variant_effect_prediction` | Submit variant effect prediction | Complex analysis | `variant`, `interval`, `job_name` |
| `submit_variant_scoring` | Submit variant pathogenicity scoring | Multiple algorithms | `variant`, `interval`, `job_name` |
| `submit_batch_sequence_analysis` | Submit batch sequence analysis | Multiple sequences | `input_file`, `job_name` |
| `submit_batch_variant_analysis` | Submit batch variant analysis | Multiple variants | `variants`, `intervals`, `analysis_type` |

### Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and status |
| `get_job_result` | Get results when completed |
| `get_job_log` | View execution logs with tail option |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with optional status filter |

---

## Examples

### Example 1: Single DNA Sequence Analysis

**Goal:** Analyze a DNA sequence for chromatin accessibility and transcription start sites

**Using Script:**
```bash
mamba run -p ./env python scripts/dna_sequence_prediction.py \
  --input examples/data/sample_sequence.txt \
  --output-types atac cage \
  --pretty
```

**Using MCP (in Claude Code):**
```
Use predict_dna_sequence to analyze @examples/data/sample_sequence.txt for chromatin accessibility (atac) and transcription start sites (cage)
```

**Expected Output:**
- Chromatin accessibility predictions across the sequence
- CAGE-seq transcription start site predictions
- JSON format with metadata and confidence scores

### Example 2: Genomic Interval Analysis

**Goal:** Analyze a specific chromosomal region for regulatory elements

**Using Script:**
```bash
mamba run -p ./env python scripts/genomic_interval_analysis.py \
  --interval chr1:1000000-1002048 \
  --output-types atac dnase
```

**Using MCP (in Claude Code):**
```
Analyze genomic interval "chr1:1000000-1002048" for ATAC-seq accessibility and DNase hypersensitivity
```

**Expected Output:**
- Accessibility scores across the 2048bp interval
- Peak predictions for regulatory regions
- Coordinate-based feature annotations

### Example 3: Variant Effect Prediction

**Goal:** Predict functional impact of a genetic variant

**Using Script:**
```bash
mamba run -p ./env python scripts/variant_effect_prediction.py \
  --variant chr1:1001000A>G \
  --interval chr1:1000000-1002048 \
  --output results/variant_analysis.json
```

**Using MCP (in Claude Code):**
```
Predict effects of variant chr1:1001000A>G within interval chr1:1000000-1002048 and explain the functional impact
```

**Expected Output:**
- Reference vs alternate allele predictions
- Effect size calculations for each genomic feature
- Functional impact assessment

### Example 4: Variant Pathogenicity Scoring

**Goal:** Score a variant using multiple pathogenicity algorithms

**Using MCP (in Claude Code):**
```
Score variant chr1:1001000A>G for pathogenicity using score_variant_pathogenicity with interval chr1:1000000-1002048
```

**Expected Output:**
- Scores from 19 different pathogenicity algorithms
- Consensus pathogenicity assessment
- Clinical interpretation guidance

### Example 5: Batch Processing

**Goal:** Process multiple sequences at once

**Using Script:**
```bash
mamba run -p ./env python scripts/batch_sequence_analysis.py \
  --input examples/data/sequences.txt \
  --max-workers 3 \
  --summary
```

**Using MCP (in Claude Code):**
```
Submit batch processing for all sequences in @examples/data/sequences.txt using submit_batch_sequence_analysis with job_name "multi_sequence_analysis"

Then check the status and get results when completed
```

**Expected Output:**
- Analysis results for all 7 sequences
- Summary statistics across sequences
- Progress tracking through job management

---

## Demo Data

The `examples/data/` directory contains sample data for testing:

| File | Description | Size | Use With |
|------|-------------|------|----------|
| `sample_sequence.txt` | Single 56bp test sequence for basic testing | 56bp | `predict_dna_sequence` |
| `sequences.txt` | 7 synthetic sequences for batch testing | 12-21bp each | `submit_batch_sequence_analysis` |
| `test_sequence_16k.txt` | Large sequence for performance testing | 16KB | Long-running tasks |
| `test_sequences_16k.txt` | Multiple large sequences | Multiple 16KB | Batch processing |

### Sample Sequence Content
```
# sample_sequence.txt
ATGCGATCGTAGCTAGCATGCAAATTTGGGCCCGTACGCATGCTAGCGATCGTAGCTAG

# sequences.txt (excerpt)
ATGCGATCGTAGCTAGCATGC
GGCCTTAACCGGAAGGCCTT
TTAACCGGTTAACCGGTTAA
```

---

## Configuration Files

The `configs/` directory contains configuration templates:

| Config | Description | Key Parameters |
|--------|-------------|----------------|
| `default_config.json` | Main configuration settings | `organism`, `output_types`, `validation` |
| `dna_sequence_prediction_config.json` | DNA sequence analysis settings | `max_sequence_length`, `output_types` |
| `genomic_interval_analysis_config.json` | Genomic interval settings | `coordinate_system`, `interval_limits` |
| `variant_analysis_config.json` | Variant analysis settings | `scoring_algorithms`, `effect_thresholds` |
| `batch_analysis_config.json` | Batch processing settings | `max_workers`, `max_sequences` |

### Config Example (default_config.json)

```json
{
  "organism": {
    "default": "human",
    "supported": ["human", "mouse", "fly"]
  },
  "output_types": {
    "default": ["atac", "cage", "dnase"],
    "available": ["atac", "cage", "dnase", "histone_marks", "gene_expression"]
  },
  "validation": {
    "max_sequence_length": 100000,
    "min_sequence_length": 10
  },
  "batch_processing": {
    "max_workers": 5,
    "max_sequences": 1000
  }
}
```

---

## Troubleshooting

### Environment Issues

**Problem:** Environment not found or packages missing
```bash
# Recreate environment from scratch
mamba create -p ./env python=3.11 -y
mamba run -p ./env pip install fastmcp loguru alphagenome

# Verify core imports
mamba run -p ./env python -c "
import fastmcp, alphagenome, loguru
print('✓ All packages available')
"
```

**Problem:** Import errors in scripts
```bash
# Check script imports
mamba run -p ./env python -c "
import sys
sys.path.insert(0, 'scripts')
from dna_sequence_prediction import main
print('✓ Script imports working')
"
```

### MCP Issues

**Problem:** Server not found in Claude Code
```bash
# Check MCP registration
claude mcp list | grep AlphaGenome

# Re-register if needed
claude mcp remove AlphaGenome-MCP-Server
claude mcp add AlphaGenome-MCP-Server -- $(pwd)/env/bin/python $(pwd)/src/server.py

# Verify registration
claude mcp list
```

**Problem:** Tools not working in MCP
```bash
# Test server directly
mamba run -p ./env python -c "
from src.server import mcp
tools = list(mcp.list_tools().keys())
print(f'✓ Found {len(tools)} tools: {tools[:5]}...')
"
```

**Problem:** Mock mode not working
```bash
# Check mock environment
echo $ALPHAGENOME_USE_MOCK
# Should output: true

# Set if missing
export ALPHAGENOME_USE_MOCK=true
```

### Job Issues

**Problem:** Job stuck in pending status
```bash
# Check job directory and logs
ls -la jobs/
find jobs/ -name "*.log" -exec tail -5 {} \;
```

**Problem:** Job failed with errors
```
# In Claude Code:
Use get_job_log with job_id "your-job-id" and tail 100 to see detailed error information
```

**Problem:** Job manager not working
```bash
# Test job manager directly
mamba run -p ./env python -c "
from src.jobs.manager import job_manager
print(f'✓ Job manager active, jobs: {len(job_manager.list_jobs())}')
"
```

### File Path Issues

**Problem:** Examples or config files not found
```bash
# Verify file structure
find examples/ configs/ -type f | head -10

# Check actual file paths
ls -la examples/data/
ls -la configs/
```

---

## Performance Notes

### Synchronous Tools
- **DNA sequence prediction**: ~300ms (mock mode)
- **Genomic interval analysis**: ~150ms (mock mode)
- **Variant effect prediction**: ~200ms (mock mode)
- **Variant scoring**: ~200ms for 19 algorithms (mock mode)
- **Metadata operations**: ~10-100ms (mock mode)

### Asynchronous (Submit) Tools
- **Batch sequence analysis**: Variable (depends on sequence count)
- **Large sequence analysis**: Variable (depends on sequence length)
- **Complex variant analysis**: Variable (depends on analysis complexity)
- **Job management**: <100ms per operation

### Mock Mode Benefits
- **Safe Testing**: No external API calls or charges
- **Fast Responses**: Immediate simulated results
- **Full Functionality**: All tools work with realistic mock data
- **Development**: Perfect for testing workflows and integration

---

## Development

### Running Tests

```bash
# Activate environment
mamba run -p ./env python tests/run_integration_tests.py

# Expected output: "🎉 ALL TESTS PASSED - Ready for production!"
```

### Starting Dev Server

```bash
# Run MCP server in development mode
mamba run -p ./env fastmcp dev src/server.py

# Test tools interactively
mamba run -p ./env fastmcp dev src/server.py --tools
```

### Adding New Tools

1. Create script in `scripts/` directory
2. Add tool wrapper in `src/server.py`
3. Test with integration test suite
4. Update documentation

---

## License

Based on Google DeepMind's AlphaGenome models and APIs. This MCP wrapper is provided as-is for research and educational purposes.

## Credits

- **AlphaGenome Models**: Google DeepMind
- **Original Repository**: [AlphaGenome-MCP-Server](https://github.com/deepmind/alphagenome)
- **MCP Framework**: [FastMCP](https://github.com/jlowin/fastmcp)
- **Development**: NucleicMCP project integration