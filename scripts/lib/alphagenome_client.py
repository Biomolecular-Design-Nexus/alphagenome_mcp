"""
Simplified AlphaGenome client for MCP scripts.

This is a minimal, self-contained version of the AlphaGenome client
extracted from repo/AlphaGenome-MCP-Server/alphagenome_client.py and
repo/AlphaGenome-MCP-Server/mock_alphagenome_client.py

Supports both mock and real API modes.
"""

import json
import os
import time
import random
from typing import Dict, List, Any, Optional

# Check if we should use mock mode for testing
USE_MOCK = os.getenv('ALPHAGENOME_USE_MOCK', 'false').lower() == 'true'


class MockAlphaGenomeClient:
    """
    Mock AlphaGenome client for testing.

    Extracted from repo/AlphaGenome-MCP-Server/mock_alphagenome_client.py
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model_version = "v1.0"

    def predict_sequence(self, sequence: str, organism: str = "human",
                        output_types: Optional[List[str]] = None,
                        ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock sequence prediction with realistic data."""
        time.sleep(0.1)  # Simulate network delay

        sequence_length = len(sequence)
        gc_content = (sequence.count('G') + sequence.count('C')) / sequence_length * 100

        # Generate mock genomic predictions
        num_predictions = max(1, sequence_length // 20)

        result = {
            "success": True,
            "sequence_info": {
                "sequence": sequence[:50] + "..." if len(sequence) > 50 else sequence,
                "length": sequence_length,
                "gc_content": round(gc_content, 2)
            },
            "predictions": {
                "atac_accessibility": [round(random.uniform(0.0, 1.0), 4) for _ in range(num_predictions)],
                "cage_tss": [round(random.uniform(0.0, 1.0), 4) for _ in range(num_predictions)],
                "dnase_hypersensitivity": [round(random.uniform(0.0, 1.0), 4) for _ in range(num_predictions)]
            },
            "metadata": {
                "organism": organism,
                "model_version": self.model_version,
                "output_types": output_types or ["atac", "cage", "dnase"]
            }
        }
        return result

    def predict_interval(self, chromosome: str, start: int, end: int,
                        organism: str = "human",
                        output_types: Optional[List[str]] = None,
                        ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock interval prediction with peak detection."""
        time.sleep(0.1)

        interval_length = end - start
        num_scores = max(10, interval_length // 1000)

        # Generate accessibility scores
        scores = [round(random.uniform(0.1, 0.9), 4) for _ in range(num_scores)]

        # Identify peaks (scores > threshold)
        threshold = 0.7
        peaks = [{"position": start + i * (interval_length // num_scores),
                 "score": score}
                for i, score in enumerate(scores) if score > threshold]

        result = {
            "success": True,
            "interval": f"{chromosome}:{start}-{end}",
            "interval_info": {
                "chromosome": chromosome,
                "start": start,
                "end": end,
                "length": interval_length,
                "organism": organism
            },
            "predictions": {
                "atac_accessibility_scores": scores,
                "peaks": peaks,
                "summary": {
                    "total_scores": len(scores),
                    "peaks_detected": len(peaks),
                    "mean_accessibility": round(sum(scores) / len(scores), 4)
                }
            },
            "metadata": {
                "model_version": self.model_version,
                "output_types": output_types or ["atac"]
            }
        }
        return result

    def predict_variant(self, chromosome: str, position: int, ref: str, alt: str,
                       interval_start: int, interval_end: int,
                       organism: str = "human",
                       output_types: Optional[List[str]] = None,
                       ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock variant effect prediction."""
        time.sleep(0.1)

        # Generate mock predictions for reference and alternate
        ref_predictions = {
            "atac_accessibility": round(random.uniform(0.2, 0.8), 4),
            "cage_tss": round(random.uniform(0.1, 0.7), 4),
            "dnase_hypersensitivity": round(random.uniform(0.3, 0.9), 4)
        }

        alt_predictions = {
            "atac_accessibility": round(ref_predictions["atac_accessibility"] + random.uniform(-0.3, 0.3), 4),
            "cage_tss": round(ref_predictions["cage_tss"] + random.uniform(-0.2, 0.2), 4),
            "dnase_hypersensitivity": round(ref_predictions["dnase_hypersensitivity"] + random.uniform(-0.4, 0.4), 4)
        }

        # Clamp values to [0, 1]
        for key in alt_predictions:
            alt_predictions[key] = max(0, min(1, alt_predictions[key]))

        result = {
            "success": True,
            "variant": f"{chromosome}:{position}{ref}>{alt}",
            "variant_info": {
                "chromosome": chromosome,
                "position": position,
                "reference": ref,
                "alternate": alt,
                "interval": f"{chromosome}:{interval_start}-{interval_end}",
                "organism": organism
            },
            "predictions": {
                "reference": ref_predictions,
                "alternate": alt_predictions,
                "effects": {
                    "atac_change": round(alt_predictions["atac_accessibility"] - ref_predictions["atac_accessibility"], 4),
                    "cage_change": round(alt_predictions["cage_tss"] - ref_predictions["cage_tss"], 4),
                    "dnase_change": round(alt_predictions["dnase_hypersensitivity"] - ref_predictions["dnase_hypersensitivity"], 4)
                }
            },
            "metadata": {
                "model_version": self.model_version,
                "output_types": output_types or ["atac", "cage", "dnase"]
            }
        }
        return result

    def score_variant(self, chromosome: str, position: int, ref: str, alt: str,
                     interval_start: int, interval_end: int,
                     organism: str = "human") -> Dict[str, Any]:
        """Mock variant scoring with multiple algorithms."""
        time.sleep(0.1)

        # Mock scores for different algorithms
        algorithms = [
            "CADD", "REVEL", "PrimateAI", "SpliceAI", "DANN", "FATHMM",
            "MutationTaster", "PolyPhen2", "SIFT", "LRT", "MutationAssessor",
            "PROVEAN", "VEST4", "MetaSVM", "MetaLR", "Eigen", "GenoCanyon",
            "fitCons", "PhyloP"
        ]

        scores = {}
        for algo in algorithms:
            scores[algo] = {
                "score": round(random.uniform(0.0, 1.0), 4),
                "prediction": random.choice(["pathogenic", "benign", "uncertain"])
            }

        # Calculate summary statistics
        score_values = [s["score"] for s in scores.values()]
        summary = {
            "mean_score": round(sum(score_values) / len(score_values), 4),
            "max_score": max(score_values),
            "min_score": min(score_values),
            "pathogenic_count": sum(1 for s in scores.values() if s["prediction"] == "pathogenic"),
            "benign_count": sum(1 for s in scores.values() if s["prediction"] == "benign"),
            "uncertain_count": sum(1 for s in scores.values() if s["prediction"] == "uncertain")
        }

        result = {
            "success": True,
            "variant": f"{chromosome}:{position}{ref}>{alt}",
            "variant_info": {
                "chromosome": chromosome,
                "position": position,
                "reference": ref,
                "alternate": alt,
                "interval": f"{chromosome}:{interval_start}-{interval_end}",
                "organism": organism
            },
            "scores": scores,
            "summary": summary,
            "interpretation": {
                "likely_pathogenic": summary["pathogenic_count"] > len(algorithms) // 2,
                "confidence": round(max(summary["pathogenic_count"], summary["benign_count"]) / len(algorithms), 2)
            },
            "metadata": {
                "algorithms_used": len(algorithms),
                "model_version": self.model_version
            }
        }
        return result

    def predict_sequences(self, sequences: List[str], organism: str = "human",
                         output_types: Optional[List[str]] = None,
                         ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Mock batch sequence prediction."""
        time.sleep(0.2)

        results = []
        for i, sequence in enumerate(sequences):
            result = self.predict_sequence(sequence, organism, output_types, ontology_terms)
            result["sequence_index"] = i
            results.append(result)

        return {
            "success": True,
            "batch_info": {
                "total_sequences": len(sequences),
                "processed": len(results),
                "organism": organism
            },
            "results": results,
            "metadata": {
                "model_version": self.model_version,
                "output_types": output_types or ["atac", "cage", "dnase"]
            }
        }

    def get_output_metadata(self, organism: str = "human") -> Dict[str, Any]:
        """Mock output metadata."""
        time.sleep(0.1)

        output_types = {
            "ATAC": {
                "description": "Chromatin accessibility predictions",
                "data_type": "float",
                "range": "[0.0, 1.0]",
                "units": "accessibility_score"
            },
            "CAGE": {
                "description": "Transcription start site predictions",
                "data_type": "float",
                "range": "[0.0, 1.0]",
                "units": "tss_score"
            },
            "DNASE": {
                "description": "DNase hypersensitivity predictions",
                "data_type": "float",
                "range": "[0.0, 1.0]",
                "units": "hypersensitivity_score"
            },
            "HISTONE_MARKS": {
                "description": "Histone modification predictions",
                "data_type": "float",
                "range": "[0.0, 1.0]",
                "units": "modification_score"
            },
            "GENE_EXPRESSION": {
                "description": "Gene expression predictions",
                "data_type": "float",
                "range": "[0.0, inf]",
                "units": "expression_level"
            }
        }

        return {
            "success": True,
            "organism": organism,
            "available_outputs": list(output_types.keys()),
            "output_descriptions": output_types,
            "model_info": {
                "version": self.model_version,
                "type": "mock_model",
                "supported_organisms": ["human", "mouse", "fly"]
            },
            "metadata": {
                "api_version": "mock_v1.0",
                "last_updated": "2024-12-25"
            }
        }


class AlphaGenomeClient:
    """
    AlphaGenome API client wrapper.

    Simplified version extracted from repo/AlphaGenome-MCP-Server/alphagenome_client.py
    """

    def __init__(self, api_key: str):
        """Initialize the AlphaGenome client with API key."""
        if not api_key:
            raise ValueError("API key is required")

        if USE_MOCK:
            # Use mock client for testing
            self.client = MockAlphaGenomeClient(api_key)
            self.is_mock = True
        else:
            # For real API, would initialize actual client here
            # This is a placeholder for the real implementation
            self.client = None
            self.is_mock = False
            raise NotImplementedError(
                "Real AlphaGenome API client not implemented in simplified version. "
                "Use ALPHAGENOME_USE_MOCK=true for testing."
            )

    def predict_sequence(self, sequence: str, organism: str = "human",
                        output_types: Optional[List[str]] = None,
                        ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Predict genomic features for a DNA sequence."""
        # Input validation
        if not sequence or not isinstance(sequence, str):
            return {
                "success": False,
                "error": "Sequence must be a non-empty string",
                "type": "ValueError"
            }

        # Check for valid DNA characters
        valid_chars = set('ATGCN')
        invalid_chars = set(sequence.upper()) - valid_chars
        if invalid_chars:
            return {
                "success": False,
                "error": f"Sequence contains invalid characters: {invalid_chars}. Only A, T, G, C, N are allowed",
                "type": "ValueError"
            }

        return self.client.predict_sequence(sequence, organism, output_types, ontology_terms)

    def predict_interval(self, chromosome: str, start: int, end: int,
                        organism: str = "human",
                        output_types: Optional[List[str]] = None,
                        ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Predict genomic features for a genomic interval."""
        # Input validation
        if start >= end:
            return {
                "success": False,
                "error": "Start position must be less than end position",
                "type": "ValueError"
            }

        if start < 0:
            return {
                "success": False,
                "error": "Start position cannot be negative",
                "type": "ValueError"
            }

        return self.client.predict_interval(chromosome, start, end, organism, output_types, ontology_terms)

    def predict_variant(self, chromosome: str, position: int, ref: str, alt: str,
                       interval_start: int, interval_end: int,
                       organism: str = "human",
                       output_types: Optional[List[str]] = None,
                       ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Predict the effect of a genetic variant."""
        # Input validation
        if not ref or not alt:
            return {
                "success": False,
                "error": "Reference and alternate alleles cannot be empty",
                "type": "ValueError"
            }

        if position < interval_start or position > interval_end:
            return {
                "success": False,
                "error": f"Variant position {position} is outside interval {interval_start}-{interval_end}",
                "type": "ValueError"
            }

        return self.client.predict_variant(chromosome, position, ref, alt, interval_start, interval_end, organism, output_types, ontology_terms)

    def score_variant(self, chromosome: str, position: int, ref: str, alt: str,
                     interval_start: int, interval_end: int,
                     organism: str = "human") -> Dict[str, Any]:
        """Score a genetic variant using recommended scorers."""
        # Same validation as predict_variant
        if not ref or not alt:
            return {
                "success": False,
                "error": "Reference and alternate alleles cannot be empty",
                "type": "ValueError"
            }

        if position < interval_start or position > interval_end:
            return {
                "success": False,
                "error": f"Variant position {position} is outside interval {interval_start}-{interval_end}",
                "type": "ValueError"
            }

        return self.client.score_variant(chromosome, position, ref, alt, interval_start, interval_end, organism)

    def predict_sequences(self, sequences: List[str], organism: str = "human",
                         output_types: Optional[List[str]] = None,
                         ontology_terms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Predict genomic features for multiple DNA sequences."""
        if not sequences:
            return {
                "success": False,
                "error": "Sequences list cannot be empty",
                "type": "ValueError"
            }

        return self.client.predict_sequences(sequences, organism, output_types, ontology_terms)

    def get_output_metadata(self, organism: str = "human") -> Dict[str, Any]:
        """Get metadata about available outputs."""
        return self.client.get_output_metadata(organism)