from Bio import Align
from Bio.Seq import Seq
from typing import Dict, Any, List, Optional
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)

# BLASTN default parameters
BLASTN_MATCH = 2
BLASTN_MISMATCH = -3
BLASTN_GAP_OPEN = -7
BLASTN_GAP_EXTEND = -2

# Database size (effective database size in bases for E-value calculation)
# Default: 1 billion (1e9) - typical for a small bacterial database
DEFAULT_DB_SIZE = 1_000_000_000


def calculate_gc_content(sequence: str) -> int:
    sequence = sequence.upper()
    gc_count = sequence.count('G') + sequence.count('C')
    total = len(sequence.replace('N', ''))
    if total == 0:
        return 0
    return int((gc_count / total) * 100)


def validate_sequence(sequence: str, sequence_name: str = "sequence") -> tuple:
    valid_chars = set('ATCGNRYSWKMBDHV')
    sequence = sequence.upper()
    invalid_chars = set(sequence) - valid_chars
    if invalid_chars:
        return False, f"Invalid characters in {sequence_name}: {', '.join(sorted(invalid_chars))}"
    return True, ""


def validate_fasta_content(content: str) -> tuple:
    if not content or not content.strip():
        return False, "File is empty"
    if not content.strip().startswith('>'):
        return False, "Invalid FASTA format: must start with '>' header"
    if len(content) > 1_000_000:
        return False, "File too large (max 1MB)"
    return True, ""


def calculate_e_value(
    score: int,
    query_length: int,
    db_size: int = DEFAULT_DB_SIZE,
    scoring_params: Optional[Dict] = None
) -> float:
    if score <= 0:
        return float('inf')

    if scoring_params is None:
        scoring_params = {
            'match': BLASTN_MATCH,
            'mismatch': BLASTN_MISMATCH,
            'gap_open': BLASTN_GAP_OPEN,
            'gap_extend': BLASTN_GAP_EXTEND
        }

    # Karlin-Altschul parameters for BLASTN
    # Lambda and K for ungapped BLASTN
    lambda_param = 0.332
    K_param = 0.136

    # E-value = K * m * n * exp(-lambda * S)
    # where m = query length, n = database size, S = raw score
    e_value = K_param * query_length * db_size * math.exp(-lambda_param * score)

    return e_value


def calculate_bit_score(raw_score: int, db_size: int = DEFAULT_DB_SIZE) -> float:
    # Bit score = (lambda * score - ln(K)) / ln(2)
    # Simplified: lambda ≈ 0.5, K ≈ 1 for DNA
    lambda_param = 0.5
    K = 1.0

    bit_score = (lambda_param * raw_score - math.log(K)) / math.log(2)
    return max(0, bit_score)


def _reconstruct_aligned_sequences(
    reference: str,
    query: str,
    alignment
) -> tuple:
    target_coords = alignment.aligned[0]
    query_coords = alignment.aligned[1]

    target_parts = []
    query_parts = []

    prev_t_end = 0
    prev_q_end = 0

    for i in range(len(target_coords)):
        t_start, t_end = int(target_coords[i][0]), int(target_coords[i][1])
        q_start, q_end = int(query_coords[i][0]), int(query_coords[i][1])

        if i > 0:
            t_gap = t_start - prev_t_end
            q_gap = q_start - prev_q_end

            if t_gap > 0 and q_gap == 0:
                target_parts.append(reference[prev_t_end:t_start])
                query_parts.append('-' * t_gap)
            elif q_gap > 0 and t_gap == 0:
                target_parts.append('-' * q_gap)
                query_parts.append(query[prev_q_end:q_start])
            elif t_gap > 0 and q_gap > 0:
                if t_gap >= q_gap:
                    target_parts.append(reference[prev_t_end:t_start])
                    query_parts.append(query[prev_q_end:q_start] + '-' * (t_gap - q_gap))
                else:
                    target_parts.append(reference[prev_t_end:t_start] + '-' * (q_gap - t_gap))
                    query_parts.append(query[prev_q_end:q_start])

        target_parts.append(reference[t_start:t_end])
        query_parts.append(query[q_start:q_end])

        prev_t_end = t_end
        prev_q_end = q_end

    aligned_ref = ''.join(target_parts)
    aligned_query = ''.join(query_parts)

    return aligned_ref, aligned_query


def align_sequences(
    reference: str,
    query: str,
    db_size: int = DEFAULT_DB_SIZE,
    mode: str = 'global'
) -> Dict[str, Any]:
    # Validate inputs
    ref_valid, ref_error = validate_sequence(reference, "reference")
    if not ref_valid:
        logger.error(f"Invalid reference: {ref_error}")
        return _empty_alignment_result(error=ref_error)

    query_valid, query_error = validate_sequence(query, "query")
    if not query_valid:
        logger.error(f"Invalid query: {query_error}")
        return _empty_alignment_result(error=query_error)

    # Truncate if too long (prevent DoS)
    max_seq_len = 100_000
    if len(reference) > max_seq_len:
        reference = reference[:max_seq_len]
        logger.warning(f"Reference truncated to {max_seq_len} bp")
    if len(query) > max_seq_len:
        query = query[:max_seq_len]
        logger.warning(f"Query truncated to {max_seq_len} bp")

    try:
        aligner = Align.PairwiseAligner(scoring='blastn')
        aligner.mode = mode

        ref_seq = Seq(reference.upper())
        query_seq = Seq(query.upper())

        alignments = aligner.align(ref_seq, query_seq)

        if not alignments:
            return _empty_alignment_result(error="No alignment found")

        best_alignment = alignments[0]

        aligned_ref, aligned_query = _reconstruct_aligned_sequences(
            reference.upper(), query.upper(), best_alignment
        )

        match_chars = []
        identity_count = 0
        mismatch_count = 0
        gap_events = 0
        gap_characters = 0
        in_gap = False
        comparable_positions = 0

        for r, q in zip(aligned_ref, aligned_query):
            if r == '-' or q == '-':
                match_chars.append(' ')
                gap_characters += 1
                if not in_gap:
                    gap_events += 1
                    in_gap = True
            else:
                in_gap = False
                comparable_positions += 1
                if r == q:
                    match_chars.append('|')
                    identity_count += 1
                else:
                    match_chars.append('.')
                    mismatch_count += 1

        identity_pct = round((identity_count / comparable_positions) * 100, 2) if comparable_positions > 0 else 0.0

        raw_score = int(best_alignment.score)
        e_value = calculate_e_value(raw_score, len(query), db_size)
        bit_score = calculate_bit_score(raw_score, db_size)

        coverage = round((len(aligned_ref.replace('-', '')) / len(reference)) * 100, 2) if len(reference) > 0 else 0

        return {
            'score': raw_score,
            'identity': identity_pct,
            'gaps': gap_events,
            'gap_characters': gap_characters,
            'matches': identity_count,
            'mismatches': mismatch_count,
            'comparable_positions': comparable_positions,
            'aligned_ref': aligned_ref,
            'aligned_query': aligned_query,
            'match_string': ''.join(match_chars),
            'e_value': e_value,
            'bit_score': round(bit_score, 2),
            'coverage': coverage,
            'query_length': len(query),
            'reference_length': len(reference),
            'alignment_length': len(aligned_ref),
            'scoring_scheme': 'BLASTN (match=+2, mismatch=-3, gap_open=-7, gap_extend=-2)',
            'error': None
        }

    except Exception as e:
        logger.error(f"Alignment failed: {str(e)}")
        return _empty_alignment_result(error=f"Alignment failed: {str(e)}")


def _empty_alignment_result(error: str = "") -> Dict[str, Any]:
    return {
        'score': 0,
        'identity': 0.0,
        'gaps': 0,
        'gap_characters': 0,
        'matches': 0,
        'mismatches': 0,
        'comparable_positions': 0,
        'aligned_ref': '',
        'aligned_query': '',
        'match_string': '',
        'e_value': float('inf'),
        'bit_score': 0.0,
        'coverage': 0.0,
        'query_length': 0,
        'reference_length': 0,
        'alignment_length': 0,
        'scoring_scheme': 'BLASTN (match=+2, mismatch=-3, gap_open=-7, gap_extend=-2)',
        'error': error
    }


def calculate_sequence_stats(sequences: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not sequences:
        return {
            'avg_identity': 0.0,
            'max_identity': 0.0,
            'min_identity': 0.0,
            'avg_gaps': 0.0,
            'avg_bit_score': 0.0,
            'avg_e_value': 0.0,
            'total_matches': 0,
            'total_mismatches': 0,
            'total_gap_characters': 0
        }

    identities = [s.get('identity', 0) for s in sequences]
    gaps = [s.get('gaps', 0) for s in sequences]
    bit_scores = [s.get('bit_score', 0) for s in sequences]
    e_values = [s.get('e_value', float('inf')) for s in sequences if s.get('e_value', float('inf')) != float('inf')]

    return {
        'avg_identity': round(float(np.mean(identities)), 2) if identities else 0.0,
        'max_identity': max(identities) if identities else 0.0,
        'min_identity': min(identities) if identities else 0.0,
        'avg_gaps': round(float(np.mean(gaps)), 2) if gaps else 0.0,
        'avg_bit_score': round(float(np.mean(bit_scores)), 2) if bit_scores else 0.0,
        'avg_e_value': float(np.mean(e_values)) if e_values else float('inf'),
        'total_matches': sum(s.get('matches', 0) for s in sequences),
        'total_mismatches': sum(s.get('mismatches', 0) for s in sequences),
        'total_gap_characters': sum(s.get('gap_characters', 0) for s in sequences)
    }
