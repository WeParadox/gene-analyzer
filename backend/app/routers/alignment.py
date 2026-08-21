from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import csv
import json
import io
import logging

from ..models.database import get_db, Gene, Sequence, Alignment
from ..models.schemas import (
    AlignmentRequest, BulkAlignmentRequest, AlignmentResponse,
    StatsResponse, ExportRequest
)
from ..services.alignment import align_sequences, calculate_sequence_stats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alignment", tags=["alignment"])


@router.post("/run", response_model=AlignmentResponse)
async def run_alignment(
    request: AlignmentRequest,
    db: AsyncSession = Depends(get_db)
):
    gene_result = await db.execute(select(Gene).where(Gene.id == request.gene_id))
    gene = gene_result.scalar_one_or_none()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    seq_result = await db.execute(select(Sequence).where(Sequence.id == request.sequence_id))
    sequence = seq_result.scalar_one_or_none()
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")

    alignment_result = align_sequences(
        reference=gene.reference_sequence,
        query=sequence.sequence
    )

    if alignment_result.get('error'):
        raise HTTPException(status_code=400, detail=alignment_result['error'])

    existing = await db.execute(
        select(Alignment).where(
            Alignment.gene_id == request.gene_id,
            Alignment.sequence_id == request.sequence_id
        )
    )
    existing_alignment = existing.scalar_one_or_none()

    if existing_alignment:
        _update_alignment_fields(existing_alignment, alignment_result)
        await db.commit()
        await db.refresh(existing_alignment)
        return existing_alignment

    new_alignment = Alignment(
        gene_id=request.gene_id,
        sequence_id=request.sequence_id,
        score=alignment_result['score'],
        identity=alignment_result['identity'],
        gaps=alignment_result['gaps'],
        aligned_ref=alignment_result['aligned_ref'],
        aligned_query=alignment_result['aligned_query'],
        match_string=alignment_result['match_string'],
        gap_characters=alignment_result['gap_characters'],
        matches=alignment_result['matches'],
        mismatches=alignment_result['mismatches'],
        comparable_positions=alignment_result['comparable_positions'],
        e_value=alignment_result['e_value'],
        bit_score=alignment_result['bit_score'],
        coverage=alignment_result['coverage'],
        query_length=alignment_result['query_length'],
        reference_length=alignment_result['reference_length'],
        alignment_length=alignment_result['alignment_length'],
        scoring_scheme=alignment_result['scoring_scheme']
    )
    db.add(new_alignment)
    await db.commit()
    await db.refresh(new_alignment)
    return new_alignment


@router.post("/run-bulk", response_model=List[AlignmentResponse])
async def run_bulk_alignment(
    request: BulkAlignmentRequest,
    db: AsyncSession = Depends(get_db)
):
    gene_result = await db.execute(select(Gene).where(Gene.id == request.gene_id))
    gene = gene_result.scalar_one_or_none()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    alignments = []
    errors = []

    for seq_id in request.sequence_ids:
        seq_result = await db.execute(select(Sequence).where(Sequence.id == seq_id))
        sequence = seq_result.scalar_one_or_none()
        if not sequence:
            errors.append(f"Sequence {seq_id} not found")
            continue

        alignment_result = align_sequences(
            reference=gene.reference_sequence,
            query=sequence.sequence
        )

        if alignment_result.get('error'):
            errors.append(f"Sequence {seq_id}: {alignment_result['error']}")
            continue

        existing = await db.execute(
            select(Alignment).where(
                Alignment.gene_id == request.gene_id,
                Alignment.sequence_id == seq_id
            )
        )
        existing_alignment = existing.scalar_one_or_none()

        if existing_alignment:
            _update_alignment_fields(existing_alignment, alignment_result)
            alignments.append(existing_alignment)
        else:
            new_alignment = Alignment(
                gene_id=request.gene_id,
                sequence_id=seq_id,
                score=alignment_result['score'],
                identity=alignment_result['identity'],
                gaps=alignment_result['gaps'],
                aligned_ref=alignment_result['aligned_ref'],
                aligned_query=alignment_result['aligned_query'],
                match_string=alignment_result['match_string'],
                gap_characters=alignment_result['gap_characters'],
                matches=alignment_result['matches'],
                mismatches=alignment_result['mismatches'],
                comparable_positions=alignment_result['comparable_positions'],
                e_value=alignment_result['e_value'],
                bit_score=alignment_result['bit_score'],
                coverage=alignment_result['coverage'],
                query_length=alignment_result['query_length'],
                reference_length=alignment_result['reference_length'],
                alignment_length=alignment_result['alignment_length'],
                scoring_scheme=alignment_result['scoring_scheme']
            )
            db.add(new_alignment)
            alignments.append(new_alignment)

    await db.commit()
    for alignment in alignments:
        await db.refresh(alignment)

    if errors:
        logger.warning(f"Bulk alignment errors: {errors}")

    return alignments


@router.get("/gene/{gene_id}", response_model=List[AlignmentResponse])
async def get_gene_alignments(
    gene_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Alignment).where(Alignment.gene_id == gene_id)
    )
    alignments = result.scalars().all()
    return alignments


@router.get("/stats/{gene_id}", response_model=StatsResponse)
async def get_alignment_stats(
    gene_id: int,
    db: AsyncSession = Depends(get_db)
):
    gene_result = await db.execute(select(Gene).where(Gene.id == gene_id))
    gene = gene_result.scalar_one_or_none()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    alignments_result = await db.execute(
        select(Alignment).where(Alignment.gene_id == gene_id)
    )
    alignments = alignments_result.scalars().all()

    alignment_dicts = [
        {
            'identity': a.identity,
            'gaps': a.gaps,
            'bit_score': a.bit_score,
            'e_value': a.e_value,
            'matches': a.matches,
            'mismatches': a.mismatches,
            'gap_characters': a.gap_characters
        }
        for a in alignments
    ]
    stats = calculate_sequence_stats(alignment_dicts)

    return StatsResponse(
        gene_id=gene_id,
        gene_name=gene.name,
        total_sequences=len(alignments),
        avg_identity=stats['avg_identity'],
        max_identity=stats['max_identity'],
        min_identity=stats['min_identity'],
        avg_gaps=stats['avg_gaps'],
        avg_bit_score=stats['avg_bit_score'],
        avg_e_value=stats['avg_e_value'],
        total_matches=stats['total_matches'],
        total_mismatches=stats['total_mismatches'],
        total_gap_characters=stats['total_gap_characters']
    )


@router.get("/export/{gene_id}")
async def export_alignments(
    gene_id: int,
    format: str = Query("json", pattern="^(json|csv|fasta)$"),
    include_alignment: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    gene_result = await db.execute(select(Gene).where(Gene.id == gene_id))
    gene = gene_result.scalar_one_or_none()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    alignments_result = await db.execute(
        select(Alignment).where(Alignment.gene_id == gene_id)
    )
    alignments = alignments_result.scalars().all()

    if not alignments:
        raise HTTPException(status_code=404, detail="No alignments found for this gene")

    if format == "json":
        return _export_json(gene, alignments, include_alignment)
    elif format == "csv":
        return _export_csv(gene, alignments, include_alignment)
    elif format == "fasta":
        return _export_fasta(gene, alignments)

    raise HTTPException(status_code=400, detail="Invalid format")


def _update_alignment_fields(alignment, result):
    alignment.score = result['score']
    alignment.identity = result['identity']
    alignment.gaps = result['gaps']
    alignment.aligned_ref = result['aligned_ref']
    alignment.aligned_query = result['aligned_query']
    alignment.match_string = result['match_string']
    alignment.gap_characters = result['gap_characters']
    alignment.matches = result['matches']
    alignment.mismatches = result['mismatches']
    alignment.comparable_positions = result['comparable_positions']
    alignment.e_value = result['e_value']
    alignment.bit_score = result['bit_score']
    alignment.coverage = result['coverage']
    alignment.query_length = result['query_length']
    alignment.reference_length = result['reference_length']
    alignment.alignment_length = result['alignment_length']
    alignment.scoring_scheme = result['scoring_scheme']


def _export_json(gene, alignments, include_alignment):
    data = {
        'gene': {
            'name': gene.name,
            'description': gene.description,
            'organism': gene.organism,
            'reference_sequence': gene.reference_sequence,
            'length': gene.length,
            'gc_content': gene.gc_content,
            'category': gene.category
        },
        'alignments': []
    }

    for a in alignments:
        alignment_data = {
            'sequence_id': a.sequence_id,
            'score': a.score,
            'identity': a.identity,
            'gaps': a.gaps,
            'gap_characters': a.gap_characters,
            'matches': a.matches,
            'mismatches': a.mismatches,
            'comparable_positions': a.comparable_positions,
            'e_value': a.e_value,
            'bit_score': a.bit_score,
            'coverage': a.coverage,
            'query_length': a.query_length,
            'reference_length': a.reference_length,
            'alignment_length': a.alignment_length,
            'scoring_scheme': a.scoring_scheme
        }
        if include_alignment:
            alignment_data['aligned_ref'] = a.aligned_ref
            alignment_data['aligned_query'] = a.aligned_query
            alignment_data['match_string'] = a.match_string
        data['alignments'].append(alignment_data)

    return data


def _export_csv(gene, alignments, include_alignment):
    output = io.StringIO()
    writer = csv.writer(output)

    headers = [
        'sequence_id', 'score', 'identity', 'gaps', 'gap_characters',
        'matches', 'mismatches', 'e_value', 'bit_score', 'coverage',
        'query_length', 'reference_length', 'alignment_length'
    ]
    if include_alignment:
        headers.extend(['aligned_ref', 'aligned_query', 'match_string'])

    writer.writerow(headers)

    for a in alignments:
        row = [
            a.sequence_id, a.score, a.identity, a.gaps, a.gap_characters,
            a.matches, a.mismatches, a.e_value, a.bit_score, a.coverage,
            a.query_length, a.reference_length, a.alignment_length
        ]
        if include_alignment:
            row.extend([a.aligned_ref, a.aligned_query, a.match_string])
        writer.writerow(row)

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={gene.name}_alignments.csv"}
    )


def _export_fasta(gene, alignments):
    output = io.StringIO()
    output.write(f">reference_{gene.name}\n{gene.reference_sequence}\n\n")

    for a in alignments:
        output.write(f">seq_{a.sequence_id}_aligned\n{a.aligned_ref}\n\n")

    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={gene.name}_alignments.fasta"}
    )


@router.delete("/{alignment_id}")
async def delete_alignment(alignment_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alignment).where(Alignment.id == alignment_id))
    alignment = result.scalar_one_or_none()
    if not alignment:
        raise HTTPException(status_code=404, detail="Alignment not found")

    await db.delete(alignment)
    await db.commit()
    return {"message": "Alignment deleted successfully"}
