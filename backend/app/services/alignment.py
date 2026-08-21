from Bio import Align
from Bio.Seq import Seq
from typing import Dict, Any, List
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

    aligned_ref, aligned_query = _reconstruct_aligned_sequences(
        reference.upper(), query.upper(), best_alignment
    )

    match_chars = []
    identity_count = 0
    gap_events = 0
    in_gap = False
    comparable_positions = 0

    for r, q in zip(aligned_ref, aligned_query):
        if r == '-' or q == '-':
            match_chars.append(' ')
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

    identity_pct = int((identity_count / comparable_positions) * 100) if comparable_positions > 0 else 0

    return {
        'score': int(best_alignment.score),
        'identity': identity_pct,
        'gaps': gap_events,
        'aligned_ref': aligned_ref,
        'aligned_query': aligned_query,
        'match_string': ''.join(match_chars)
    }


def calculate_sequence_stats(sequences: List[Dict[str, Any]]) -> Dict[str, Any]:
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
