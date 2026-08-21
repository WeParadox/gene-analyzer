from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..models.database import get_db, Gene, Sequence, Alignment
from ..models.schemas import AlignmentRequest, BulkAlignmentRequest, AlignmentResponse, StatsResponse
from ..services.alignment import align_sequences, calculate_sequence_stats

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

    existing = await db.execute(
        select(Alignment).where(
            Alignment.gene_id == request.gene_id,
            Alignment.sequence_id == request.sequence_id
        )
    )
    existing_alignment = existing.scalar_one_or_none()

    if existing_alignment:
        existing_alignment.score = alignment_result['score']
        existing_alignment.identity = alignment_result['identity']
        existing_alignment.gaps = alignment_result['gaps']
        existing_alignment.aligned_ref = alignment_result['aligned_ref']
        existing_alignment.aligned_query = alignment_result['aligned_query']
        existing_alignment.match_string = alignment_result['match_string']
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
        match_string=alignment_result['match_string']
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
    for seq_id in request.sequence_ids:
        seq_result = await db.execute(select(Sequence).where(Sequence.id == seq_id))
        sequence = seq_result.scalar_one_or_none()
        if not sequence:
            continue

        alignment_result = align_sequences(
            reference=gene.reference_sequence,
            query=sequence.sequence
        )

        existing = await db.execute(
            select(Alignment).where(
                Alignment.gene_id == request.gene_id,
                Alignment.sequence_id == seq_id
            )
        )
        existing_alignment = existing.scalar_one_or_none()

        if existing_alignment:
            existing_alignment.score = alignment_result['score']
            existing_alignment.identity = alignment_result['identity']
            existing_alignment.gaps = alignment_result['gaps']
            existing_alignment.aligned_ref = alignment_result['aligned_ref']
            existing_alignment.aligned_query = alignment_result['aligned_query']
            existing_alignment.match_string = alignment_result['match_string']
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
                match_string=alignment_result['match_string']
            )
            db.add(new_alignment)
            alignments.append(new_alignment)

    await db.commit()
    for alignment in alignments:
        await db.refresh(alignment)

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
        {'identity': a.identity, 'gaps': a.gaps}
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
        avg_gaps=stats['avg_gaps']
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
