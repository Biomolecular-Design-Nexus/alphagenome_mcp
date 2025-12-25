# Step 6: MCP Tools Documentation

## Server Information
- **Server Name**: AlphaGenome-MCP-Server
- **Version**: 1.0.0
- **Created Date**: 2025-12-25
- **Server Path**: `src/server.py`
- **Environment**: Mock mode enabled for testing (`ALPHAGENOME_USE_MOCK=true`)

## Job Management Tools

| Tool | Description |
|------|-------------|
| `get_job_status` | Check job progress and status |
| `get_job_result` | Get completed job results |
| `get_job_log` | View job execution logs |
| `cancel_job` | Cancel running job |
| `list_jobs` | List all jobs with optional status filter |

## Synchronous Tools (Fast Operations < 10 min)

| Tool | Description | Source Script | Est. Runtime |
|------|-------------|---------------|--------------|
| `predict_dna_sequence` | Predict genomic features for DNA sequences | `scripts/dna_sequence_prediction.py` | ~300ms |
| `analyze_genomic_interval` | Analyze genomic intervals for regulatory features | `scripts/genomic_interval_analysis.py` | ~150ms |
| `predict_variant_effects` | Predict effects of genetic variants | `scripts/variant_effect_prediction.py` | ~200ms |
| `score_variant_pathogenicity` | Score variants with 19 pathogenicity algorithms | `scripts/variant_scoring.py` | ~200ms |
| `get_output_metadata` | Get metadata about available outputs | `scripts/output_metadata.py` | ~100ms |
| `validate_genomic_inputs` | Validate genomic inputs before processing | Built-in validation | ~50ms |
| `get_supported_organisms` | Get list of supported organisms | Built-in utility | ~10ms |
| `get_example_data` | Get information about example datasets | Built-in utility | ~10ms |

### Tool Details

#### predict_dna_sequence
- **Description**: Predict genomic features (ATAC, CAGE, DNase, etc.) for DNA sequences
- **Source Script**: `scripts/dna_sequence_prediction.py`
- **Estimated Runtime**: ~300 milliseconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| sequence | str | No* | - | DNA sequence string to analyze |
| input_file | str | No* | - | Path to file containing DNA sequence |
| organism | str | No | "human" | Target organism (human, mouse, fly) |
| output_types | List[str] | No | all | Output types (atac, cage, dnase, histone_marks, gene_expression) |
| output_file | str | No | None | Optional path to save results as JSON |

*Either sequence or input_file is required

**Example:**
```
Use predict_dna_sequence with sequence "ATGCGATCGTAGCTAGCATGC" and organism "human"
```

#### analyze_genomic_interval
- **Description**: Analyze genomic intervals for regulatory features and accessibility scores
- **Source Script**: `scripts/genomic_interval_analysis.py`
- **Estimated Runtime**: ~150 milliseconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| interval | str | Yes | - | Genomic interval in format "chr:start-end" |
| organism | str | No | "human" | Target organism |
| output_types | List[str] | No | all | Output types to analyze |
| output_file | str | No | None | Optional path to save results |

**Example:**
```
Use analyze_genomic_interval with interval "chr1:1000000-1002048" and organism "human"
```

#### predict_variant_effects
- **Description**: Predict effects of genetic variants on genomic features
- **Source Script**: `scripts/variant_effect_prediction.py`
- **Estimated Runtime**: ~200 milliseconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| variant | str | Yes | - | Variant in format "chr:posREF>ALT" |
| interval | str | Yes | - | Genomic interval containing the variant |
| organism | str | No | "human" | Target organism |
| output_types | List[str] | No | all | Output types to analyze |
| output_file | str | No | None | Optional path to save results |

**Example:**
```
Use predict_variant_effects with variant "chr1:1001000A>G" and interval "chr1:1000000-1002048"
```

#### score_variant_pathogenicity
- **Description**: Score variants using 19 different pathogenicity prediction algorithms
- **Source Script**: `scripts/variant_scoring.py`
- **Estimated Runtime**: ~200 milliseconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| variant | str | Yes | - | Variant in format "chr:posREF>ALT" |
| interval | str | Yes | - | Genomic interval containing the variant |
| organism | str | No | "human" | Target organism |
| output_file | str | No | None | Optional path to save results |

**Example:**
```
Use score_variant_pathogenicity with variant "chr1:1001000A>G" and interval "chr1:1000000-1002048"
```

#### get_output_metadata
- **Description**: Get metadata about available output types and organism information
- **Source Script**: `scripts/output_metadata.py`
- **Estimated Runtime**: ~100 milliseconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| organism | str | No | None | Target organism to get specific metadata for |
| output_file | str | No | None | Optional path to save results |

**Example:**
```
Use get_output_metadata with organism "human"
```

---

## Submit Tools (Long Operations > 10 min)

| Tool | Description | Source Script | Est. Runtime | Batch Support |
|------|-------------|---------------|--------------|---------------|
| `submit_dna_sequence_prediction` | Submit DNA sequence prediction for background processing | `scripts/dna_sequence_prediction.py` | Variable | ✅ Yes |
| `submit_variant_effect_prediction` | Submit variant effect prediction for background processing | `scripts/variant_effect_prediction.py` | Variable | ✅ Yes |
| `submit_variant_scoring` | Submit variant pathogenicity scoring for background processing | `scripts/variant_scoring.py` | Variable | ✅ Yes |
| `submit_batch_sequence_analysis` | Submit batch sequence analysis for background processing | `scripts/batch_sequence_analysis.py` | >10 min | ✅ Native batch |
| `submit_batch_variant_analysis` | Submit batch variant analysis for multiple variants | Multiple scripts | Variable | ✅ Yes |

### Tool Details

#### submit_dna_sequence_prediction
- **Description**: Submit DNA sequence prediction for background processing
- **Source Script**: `scripts/dna_sequence_prediction.py`
- **Estimated Runtime**: Variable (depends on sequence length and complexity)
- **Supports Batch**: ✅ Yes

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| sequence | str | No* | - | DNA sequence string to analyze |
| input_file | str | No* | - | Path to file containing DNA sequence |
| organism | str | No | "human" | Target organism |
| output_types | List[str] | No | all | Output types |
| output_dir | str | No | auto | Directory to save outputs |
| job_name | str | No | auto | Custom job name |

*Either sequence or input_file is required

**Example:**
```
Use submit_dna_sequence_prediction with sequence "ATGCGATCGTAGCTAGC..." and job_name "large_sequence_analysis"
```

#### submit_batch_sequence_analysis
- **Description**: Submit batch sequence analysis for processing multiple sequences
- **Source Script**: `scripts/batch_sequence_analysis.py`
- **Estimated Runtime**: >10 minutes (depends on number of sequences)
- **Supports Batch**: ✅ Native batch processing

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| input_file | str | Yes | - | Path to text file with DNA sequences (one per line) |
| organism | str | No | "human" | Target organism |
| output_types | List[str] | No | all | Output types |
| output_dir | str | No | auto | Directory to save outputs |
| job_name | str | No | auto | Custom job name |

**Example:**
```
Use submit_batch_sequence_analysis with input_file "examples/data/test_sequences.txt"
```

#### submit_batch_variant_analysis
- **Description**: Submit batch variant analysis for processing multiple variants
- **Source Script**: Multiple scripts (variant_effect_prediction.py or variant_scoring.py)
- **Estimated Runtime**: Variable (depends on number of variants)
- **Supports Batch**: ✅ Yes

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| variants | List[str] | Yes | - | List of variants in format "chr:posREF>ALT" |
| intervals | List[str] | Yes | - | List of genomic intervals (one per variant) |
| analysis_type | str | No | "effects" | Type of analysis ("effects" or "scoring") |
| organism | str | No | "human" | Target organism |
| output_types | List[str] | No | all | Output types (for effects analysis) |
| output_dir | str | No | auto | Directory to save outputs |
| job_name | str | No | auto | Custom job name |

**Example:**
```
Use submit_batch_variant_analysis with variants ["chr1:1001000A>G", "chr2:2001000C>T"] and intervals ["chr1:1000000-1002048", "chr2:2000000-2002048"]
```

---

## Utility Tools

| Tool | Description | Type |
|------|-------------|------|
| `validate_genomic_inputs` | Validate genomic inputs before processing | Sync |
| `get_supported_organisms` | Get list of supported organisms | Sync |
| `get_example_data` | Get information about example datasets | Sync |

### Tool Details

#### validate_genomic_inputs
- **Description**: Validate genomic inputs (sequences, variants, intervals) before processing
- **Type**: Synchronous
- **Estimated Runtime**: ~50 milliseconds

**Parameters:**
| Name | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| sequence | str | No | - | DNA sequence to validate |
| variant | str | No | - | Variant string to validate |
| interval | str | No | - | Genomic interval to validate |

**Example:**
```
Use validate_genomic_inputs with sequence "ATGCGATCG", variant "chr1:1000A>G", and interval "chr1:900-1100"
```

---

## Workflow Examples

### Quick Analysis (Sync)
```
1. Validate inputs:
   Use validate_genomic_inputs with sequence "ATGCGATCGTAGC" and interval "chr1:1000-2000"
   → Returns: validation results for each input

2. Analyze sequence:
   Use predict_dna_sequence with sequence "ATGCGATCGTAGC" and organism "human"
   → Returns: prediction results immediately (~300ms)

3. Analyze interval:
   Use analyze_genomic_interval with interval "chr1:1000-2000"
   → Returns: accessibility scores and peaks immediately (~150ms)
```

### Variant Analysis (Sync)
```
1. Predict variant effects:
   Use predict_variant_effects with variant "chr1:1500A>G" and interval "chr1:1000-2000"
   → Returns: reference vs alternate predictions immediately (~200ms)

2. Score pathogenicity:
   Use score_variant_pathogenicity with variant "chr1:1500A>G" and interval "chr1:1000-2000"
   → Returns: scores from 19 algorithms immediately (~200ms)
```

### Long-Running Task (Submit API)
```
1. Submit job:
   Use submit_dna_sequence_prediction with input_file "large_sequence.txt" and job_name "large_analysis"
   → Returns: {"job_id": "abc123", "status": "submitted"}

2. Check status:
   Use get_job_status with job_id "abc123"
   → Returns: {"status": "running", "started_at": "...", ...}

3. View logs (optional):
   Use get_job_log with job_id "abc123"
   → Returns: execution logs with progress information

4. Get result:
   Use get_job_result with job_id "abc123"
   → Returns: {"status": "success", "result": {...}} when completed
```

### Batch Processing
```
1. Submit batch job:
   Use submit_batch_sequence_analysis with input_file "examples/data/test_sequences.txt"
   → Returns: {"job_id": "def456", "status": "submitted"}

2. Monitor progress:
   Use get_job_status with job_id "def456"
   → Check status periodically until completion

3. Get results:
   Use get_job_result with job_id "def456"
   → Returns: batch analysis results for all sequences
```

### Batch Variant Analysis
```
1. Submit batch variant job:
   Use submit_batch_variant_analysis with:
   - variants: ["chr1:1001000A>G", "chr2:2001000C>T"]
   - intervals: ["chr1:1000000-1002048", "chr2:2000000-2002048"]
   - analysis_type: "effects"
   → Returns: {"job_id": "ghi789", "status": "submitted"}

2. Get results when completed:
   Use get_job_result with job_id "ghi789"
   → Returns: variant effect results for all variants
```

---

## Supported Data Formats

### Input Formats
- **DNA Sequences**: Plain text strings (A, T, G, C, N characters)
- **Sequence Files**: Text files with one sequence per line
- **Genomic Intervals**: Format "chr:start-end" (e.g., "chr1:1000000-1002048")
- **Variants**: Format "chr:posREF>ALT" (e.g., "chr1:1001000A>G")

### Output Formats
- **JSON**: Structured results with metadata
- **Pretty JSON**: Human-readable formatted JSON

### Organisms
- **human**: Homo sapiens (default)
- **mouse**: Mus musculus
- **fly**: Drosophila melanogaster

### Output Types
- **atac**: ATAC-seq accessibility predictions
- **cage**: CAGE-seq expression predictions
- **dnase**: DNase-seq accessibility predictions
- **histone_marks**: Histone modification predictions
- **gene_expression**: Gene expression predictions

---

## Error Handling

All tools return structured error responses:

```json
{
  "status": "error",
  "error": "Descriptive error message"
}
```

Common error types:
- **File not found**: Input file doesn't exist
- **Invalid input**: Malformed sequences, variants, or intervals
- **Validation error**: Input doesn't meet format requirements
- **Job not found**: Invalid job_id provided
- **Job not completed**: Trying to get results from incomplete job

---

## Environment Requirements

- **Python Environment**: Conda/mamba environment with fastmcp and loguru
- **Mock Mode**: Enabled by default (`ALPHAGENOME_USE_MOCK=true`)
- **Dependencies**: All scripts use zero heavy dependencies (no torch, numpy, pandas)

---

## Testing

The MCP server has been tested with:
- ✅ All script imports working correctly
- ✅ Mock client functionality verified
- ✅ Genomic input validation working
- ✅ Job management system operational
- ✅ Server startup without errors
- ✅ All tool function signatures correct

Run tests:
```bash
mamba run -p ./env python test_simple.py
```

---

## Performance Notes

**Synchronous Tools**:
- All sync tools complete in under 10 minutes (typically <500ms in mock mode)
- Suitable for interactive use with LLMs
- Immediate response with structured results

**Submit Tools**:
- Designed for long-running or batch operations
- Background processing with job tracking
- Suitable for large datasets or complex analysis

**Mock Mode Performance**:
- DNA sequence prediction: ~100-300ms
- Genomic interval analysis: ~100-150ms
- Variant effect prediction: ~100-200ms
- Variant scoring: ~100-200ms (19 algorithms)
- Batch sequence analysis: ~300-500ms (3 sequences)
- Metadata retrieval: ~100ms