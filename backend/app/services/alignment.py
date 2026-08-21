from Bio import Align
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Align import substitution_matrices
from typing import Dict, Any, Tuple
import numpy as np


def calculate_gc_content(sequence: str) -> int:
    sequence = sequence.upper()
    gc_count = sequence.count('G') + sequence.count('C')
    total = len(sequence.replace('N', ''))
    if total == 0:
        return 0
    return int((gc_count / total) * 100)


def validate_sequence(sequence: str) -> bool:
    valid_chars = set('ATCGNRYSWKMBDHV')
    return all(c in valid_chars for c in sequence.upper())


def align_sequences(
    reference: str,
    query: str,
    match_score: int = 2,
    mismatch_score: int = -1,
    gap_open: float = -10,
    gap_extend: float = -0.5
) -> Dict[str, Any]:
    aligner = Align.PairwiseAligner()
    aligner.mode = 'global'
    aligner.match_score = match_score
    aligner.mismatch_score = mismatch_score
    aligner.open_gap_score = gap_open
    aligner.extend_gap_score = gap_extend

    ref_seq = Seq(reference.upper())
    query_seq = Seq(query.upper())

    alignments = aligner.align(ref_seq, query_seq)

    if not alignments:
        return {
            'score': 0,
            'identity': 0,
            'gaps': 0,
            'aligned_ref': '',
            'aligned_query': '',
            'match_string': ''
        }

    best_alignment = alignments[0]
    aligned_ref = str(best_alignment.sequences[0])
    aligned_query = str(best_alignment.sequences[1])

    match_chars = []
    identity_count = 0
    gap_count = 0

    for r, q in zip(aligned_ref, aligned_query):
        if r == '-':
            match_chars.append(' ')
            gap_count += 1
        elif q == '-':
            match_chars.append(' ')
            gap_count += 1
        elif r == q:
            match_chars.append('|')
            identity_count += 1
        else:
            match_chars.append('.')

    total_length = len(aligned_ref)
    identity_pct = int((identity_count / total_length) * 100) if total_length > 0 else 0

    return {
        'score': int(best_alignment.score),
        'identity': identity_pct,
        'gaps': gap_count,
        'aligned_ref': aligned_ref,
        'aligned_query': aligned_query,
        'match_string': ''.join(match_chars)
    }


def calculate_sequence_stats(sequences: list) -> Dict[str, Any]:
    if not sequences:
        return {
            'avg_identity': 0,
            'max_identity': 0,
            'min_identity': 0,
            'avg_gaps': 0
        }

    identities = [s.get('identity', 0) for s in sequences]
    gaps = [s.get('gaps', 0) for s in sequences]

    return {
        'avg_identity': float(np.mean(identities)) if identities else 0,
        'max_identity': max(identities) if identities else 0,
        'min_identity': min(identities) if identities else 0,
        'avg_gaps': float(np.mean(gaps)) if gaps else 0
    }
