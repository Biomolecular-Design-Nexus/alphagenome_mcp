# Step 3: Use Cases Report

## Use Cases Extraction Summary
- **Source Repository**: AlphaGenome-MCP-Server
- **Extraction Method**: Analyzed documentation and client methods
- **Scripts Created**: 6 standalone Python scripts
- **Demo Data**: 2 sample files with comprehensive test data
- **Integration**: All scripts include repository code via sys.path

## Extracted Use Cases

### 1. DNA Sequence Prediction (`use_case_1_dna_sequence_prediction.py`)
**Purpose**: Analyze DNA sequences for genomic features like chromatin accessibility, transcription start sites, and DNase hypersensitivity.

**Key Features**:
- Single sequence analysis from command line or file input
- Support for multiple output types (ATAC, CAGE, DNASE, etc.)
- Comprehensive sequence validation (A, T, G, C, N only)
- Pretty-printed JSON output with metadata

**API Method**: `client.predict_sequence()`

**Example Usage**:
```bash
# From file
mamba run -p ./env python examples/use_case_1_dna_sequence_prediction.py --input examples/data/sample_sequence.txt --output-types atac cage

# Command line sequence
mamba run -p ./env python examples/use_case_1_dna_sequence_prediction.py --sequence "ATGCGATCGTAG" --pretty
```

### 2. Genomic Interval Analysis (`use_case_2_genomic_interval_analysis.py`)
**Purpose**: Analyze specific chromosomal regions for regulatory elements and genomic features.

**Key Features**:
- Interval string parsing (chr:start-end format)
- Individual coordinate specification support
- Interval size validation and recommendations
- Coordinate system validation (0-based start, exclusive end)

**API Method**: `client.predict_interval()`

**Example Usage**:
```bash
# Interval string format
mamba run -p ./env python examples/use_case_2_genomic_interval_analysis.py --interval chr1:1000000-1002048 --output-types atac

# Individual coordinates
mamba run -p ./env python examples/use_case_2_genomic_interval_analysis.py --chromosome chr1 --start 1000000 --end 1002048
```

### 3. Variant Effect Prediction (`use_case_3_variant_effect_prediction.py`)
**Purpose**: Predict functional effects of genetic variants on genomic features within specified intervals.

**Key Features**:
- Variant string parsing (chr:posREF>ALT format)
- Cross-validation of variant and interval chromosomes
- Position validation within interval boundaries
- Allele validation for valid DNA bases

**API Method**: `client.predict_variant()`

**Example Usage**:
```bash
# Variant string format
mamba run -p ./env python examples/use_case_3_variant_effect_prediction.py --variant chr1:1001000A>G --interval chr1:1000000-1002048

# Individual parameters
mamba run -p ./env python examples/use_case_3_variant_effect_prediction.py --chromosome chr1 --position 1001000 --ref A --alt G --interval-start 1000000 --interval-end 1002048
```

### 4. Variant Scoring (`use_case_4_variant_scoring.py`)
**Purpose**: Score genetic variants using 19 different algorithms to assess functional impact and pathogenicity.

**Key Features**:
- Multiple scoring algorithm integration
- Score interpretation and summary
- Same flexible input as variant effect prediction
- Algorithm count reporting and metadata

**API Method**: `client.score_variant()`

**Example Usage**:
```bash
# Basic scoring
mamba run -p ./env python examples/use_case_4_variant_scoring.py --variant chr1:1001000A>G --interval chr1:1000000-1002048

# With interpretation
mamba run -p ./env python examples/use_case_4_variant_scoring.py --variant chr1:1001000A>G --interval chr1:1000000-1002048 --interpret
```

### 5. Batch Sequence Analysis (`use_case_5_batch_sequence_analysis.py`)
**Purpose**: Process multiple DNA sequences in parallel for high-throughput genomic analysis.

**Key Features**:
- File-based batch processing (one sequence per line)
- Command-line sequence list support
- Parallel execution with configurable workers
- Progress tracking with tqdm
- Summary statistics and error reporting

**API Method**: `client.predict_sequences()` (custom batch wrapper)

**Example Usage**:
```bash
# From file with progress
mamba run -p ./env python examples/use_case_5_batch_sequence_analysis.py --input examples/data/sequences.txt --max-workers 3 --summary

# Command line sequences
mamba run -p ./env python examples/use_case_5_batch_sequence_analysis.py --sequences "ATGCGATCGTAG" "GGCCTTAACCGG" --output-types atac cage
```

### 6. Output Metadata (`use_case_6_output_metadata.py`)
**Purpose**: Retrieve API metadata, capabilities, and available output types for planning analyses.

**Key Features**:
- API metadata retrieval for organisms
- Known output types documentation
- Capability constraints and limits
- Metadata parsing and interpretation

**API Method**: `client.get_output_metadata()`

**Example Usage**:
```bash
# Get API metadata
mamba run -p ./env python examples/use_case_6_output_metadata.py --organism human --parse

# List known outputs
mamba run -p ./env python examples/use_case_6_output_metadata.py --list-outputs
```

## Demo Data Files

### `examples/data/sample_sequence.txt`
- **Content**: Single 56-base DNA sequence for basic testing
- **Sequence**: `ATGCGATCGTAGCTAGCATGCAAATTTGGGCCCGTACGCATGCTAGCGATCGTAGCTAG`
- **Usage**: Input file for use cases 1 and demonstrations

### `examples/data/sequences.txt`
- **Content**: 7 synthetic DNA sequences of varying lengths (12-60 bases)
- **Format**: One sequence per line with descriptive comments
- **Usage**: Batch processing demonstrations and multi-sequence analysis

## Script Architecture

### Common Patterns
All scripts follow consistent patterns for maintainability:

1. **Import Structure**:
   ```python
   sys.path.insert(0, os.path.join(..., 'repo', 'AlphaGenome-MCP-Server'))
   from alphagenome_client import AlphaGenomeClient
   ```

2. **Error Handling**: Comprehensive try-catch blocks with structured error output
3. **API Key Management**: Environment variable or command-line argument
4. **Output Formatting**: JSON output with pretty-print option and file saving
5. **Input Validation**: Thorough validation of all input parameters
6. **Metadata Addition**: Consistent metadata structure in all outputs

### Parsing Functions
- **`parse_variant_string()`**: Handles chr:posREF>ALT format
- **`parse_interval_string()`**: Handles chr:start-end format
- **`load_sequences_from_file()`**: File parsing with comment support
- **Input validation**: Coordinate bounds, allele validation, chromosome matching

### Output Structure
All scripts produce consistent JSON output with:
```json
{
  "success": true/false,
  "result": {...},
  "error": "...",
  "metadata": {
    "script": "script_name.py",
    "parameters": {...},
    "timestamp": "..."
  }
}
```

## Supported Output Types
- **ATAC**: ATAC-seq chromatin accessibility data
- **CAGE**: CAGE transcription start site data
- **DNASE**: DNase hypersensitivity data
- **HISTONE_MARKS**: ChIP-seq histone modification data
- **GENE_EXPRESSION**: RNA-seq gene expression data
- **CONTACT_MAPS**: 3D chromatin contact maps
- **SPLICE_JUNCTIONS**: Splice junction predictions

## API Constraints & Limitations
- **Maximum sequence length**: 1M base pairs
- **Maximum interval size**: 1M base pairs
- **Supported sequence lengths**: 2KB, 16KB, 131KB, 524KB, 1MB
- **Maximum parallel workers**: 10 (configurable in batch scripts)
- **Variant scoring algorithms**: 19 per variant
- **Coordinate system**: 0-based start, exclusive end for intervals; 1-based for variants

## Testing & Validation

### Verification Status
- [x] All 6 scripts created and validated
- [x] Import paths working correctly
- [x] Demo data files created
- [x] Command-line argument parsing functional
- [x] Error handling comprehensive
- [x] Output formatting consistent
- [x] File I/O operations working

### Command Validation
All example commands in the README.md have been verified for:
- Correct argument parsing
- Proper error handling
- Expected output format
- File path resolution
- Environment activation compatibility

## Integration Notes

### Repository Integration
- **Path Strategy**: Dynamic sys.path insertion to include `repo/AlphaGenome-MCP-Server`
- **Client Import**: Direct import of `alphagenome_client.AlphaGenomeClient`
- **Error Handling**: Graceful fallback if repository code unavailable

### Environment Integration
- **Activation Method**: Compatible with `mamba run -p ./env` approach
- **Package Dependencies**: All required packages installed and tested
- **API Key Handling**: Environment variable and command-line support

## Use Case Coverage

### Primary Genomic Workflows
1. **Single sequence analysis**: Use case 1 (DNA sequence prediction)
2. **Region-based analysis**: Use case 2 (genomic intervals)
3. **Variant impact assessment**: Use cases 3 & 4 (effects and scoring)
4. **High-throughput processing**: Use case 5 (batch analysis)
5. **API exploration**: Use case 6 (metadata and capabilities)

### Scientific Applications
- **Regulatory element identification**: ATAC, CAGE, DNASE outputs
- **Transcription analysis**: TSS prediction, gene expression
- **Variant pathogenicity**: Multiple scoring algorithms
- **Chromatin structure**: Contact maps and histone marks
- **RNA processing**: Splice junction prediction

## Next Steps for MCP Server Development

### Recommended MCP Tools
Based on extracted use cases, the following MCP tools should be implemented:

1. **predict_sequence**: Single DNA sequence analysis
2. **predict_interval**: Chromosomal region analysis
3. **predict_variant**: Variant effect prediction
4. **score_variant**: Multi-algorithm variant scoring
5. **predict_sequences**: Batch sequence processing
6. **get_metadata**: API capabilities and output types

### MCP Server Architecture
- **Base Client**: Use `alphagenome_client.py` as foundation
- **Tool Wrappers**: Convert use case functions to MCP tool format
- **Error Handling**: Maintain consistent error response format
- **Validation**: Reuse validation logic from standalone scripts

### Testing Strategy
- **Unit Tests**: Validate each MCP tool individually
- **Integration Tests**: Use demo data for end-to-end testing
- **Performance Tests**: Batch processing and parallel execution
- **Error Tests**: Invalid inputs and API error scenarios