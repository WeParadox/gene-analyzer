from Bio import SeqIO
from Bio.Seq import Seq
from io import StringIO
from typing import List, Dict, Any, Tuple
import csv


def parse_fasta(file_content: str) -> List[Dict[str, str]]:
    records = []
    try:
        handle = StringIO(file_content)
        for record in SeqIO.parse(handle, "fasta"):
            records.append({
                'name': record.id,
                'description': str(record.description),
                'sequence': str(record.seq).upper()
            })
    except Exception as e:
        raise ValueError(f"Invalid FASTA format: {str(e)}")
    return records


def parse_FASTA_simple(file_content: str) -> List[Dict[str, str]]:
    records = []
    current_name = None
    current_seq = []

    for line in file_content.strip().split('\n'):
        line = line.strip()
        if line.startswith('>'):
            if current_name is not None:
                records.append({
                    'name': current_name,
                    'sequence': ''.join(current_seq)
                })
            current_name = line[1:].split()[0]
            current_seq = []
        elif line:
            current_seq.append(line.upper())

    if current_name is not None:
        records.append({
            'name': current_name,
            'sequence': ''.join(current_seq)
        })

    return records


def generate_alignment_report(
    gene_name: str,
    reference: str,
    alignments: List[Dict[str, Any]]
) -> Dict[str, Any]:
    if not alignments:
        return {
            'gene_name': gene_name,
            'reference_length': len(reference),
            'total_aligned': 0,
            'avg_identity': 0,
            'identity_distribution': {},
            'summary': 'No alignments found'
        }

    identities = [a.get('identity', 0) for a in alignments]

    distribution = {
        'high (>90%)': sum(1 for i in identities if i > 90),
        'medium (70-90%)': sum(1 for i in identities if 70 <= i <= 90),
        'low (<70%)': sum(1 for i in identities if i < 70)
    }

    return {
        'gene_name': gene_name,
        'reference_length': len(reference),
        'total_aligned': len(alignments),
        'avg_identity': sum(identities) / len(identities) if identities else 0,
        'identity_distribution': distribution,
        'summary': f"Aligned {len(alignments)} sequences with average {sum(identities)/len(identities):.1f}% identity"
    }


def format_sequence_with_html(
    aligned_ref: str,
    aligned_query: str,
    match_string: str
) -> str:
    html_parts = ['<div class="alignment-viewer">']
    html_parts.append('<div class="sequence-block">')

    line_length = 60
    for i in range(0, len(aligned_ref), line_length):
        ref_chunk = aligned_ref[i:i+line_length]
        query_chunk = aligned_query[i:i+line_length]
        match_chunk = match_string[i:i+line_length]

        html_parts.append(f'<div class="sequence-line">')
        html_parts.append(f'<span class="label">Ref:  </span><span class="sequence ref">{ref_chunk}</span>')
        html_parts.append(f'<span class="label">Match:</span><span class="sequence match">{match_chunk}</span>')
        html_parts.append(f'<span class="label">Query:</span><span class="sequence query">{query_chunk}</span>')
        html_parts.append(f'</div>')

    html_parts.append('</div></div>')
    return '\n'.join(html_parts)
