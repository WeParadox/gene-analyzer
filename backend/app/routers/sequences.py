from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..models.database import get_db, Gene, Sequence
from ..models.schemas import SequenceCreate, SequenceResponse, UploadResponse
from ..services.alignment import calculate_gc_content, validate_sequence
from ..services.analysis import parse_fasta

router = APIRouter(prefix="/api/sequences", tags=["sequences"])


@router.get("/", response_model=List[SequenceResponse])
async def list_sequences(
    gene_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Sequence)
    if gene_id:
        query = query.where(Sequence.gene_id == gene_id)
    result = await db.execute(query)
    sequences = result.scalars().all()
    return sequences


@router.get("/{sequence_id}", response_model=SequenceResponse)
async def get_sequence(sequence_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sequence).where(Sequence.id == sequence_id))
    sequence = result.scalar_one_or_none()
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return sequence


@router.post("/", response_model=SequenceResponse)
async def create_sequence(sequence: SequenceCreate, db: AsyncSession = Depends(get_db)):
    gene_result = await db.execute(select(Gene).where(Gene.id == sequence.gene_id))
    if not gene_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Gene not found")

    if not validate_sequence(sequence.sequence):
        raise HTTPException(status_code=400, detail="Invalid sequence characters")

    new_sequence = Sequence(
        gene_id=sequence.gene_id,
        name=sequence.name,
        sequence=sequence.sequence.upper(),
        length=len(sequence.sequence),
        gc_content=calculate_gc_content(sequence.sequence)
    )
    db.add(new_sequence)
    await db.commit()
    await db.refresh(new_sequence)
    return new_sequence


@router.post("/upload", response_model=UploadResponse)
async def upload_fasta(
    gene_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    gene_result = await db.execute(select(Gene).where(Gene.id == gene_id))
    if not gene_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Gene not found")

    if not file.filename.endswith(('.fasta', '.fa', '.fna', '.txt')):
        raise HTTPException(status_code=400, detail="Invalid file format. Expected FASTA")

    content = await file.read()
    try:
        text_content = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

    try:
        records = parse_fasta(text_content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not records:
        raise HTTPException(status_code=400, detail="No sequences found in file")

    created_sequences = []
    errors = []

    for i, record in enumerate(records):
        if not validate_sequence(record['sequence']):
            errors.append(f"Sequence {i+1} ({record['name']}): Invalid characters")
            continue

        new_sequence = Sequence(
            gene_id=gene_id,
            name=record['name'],
            sequence=record['sequence'],
            length=len(record['sequence']),
            gc_content=calculate_gc_content(record['sequence'])
        )
        db.add(new_sequence)
        created_sequences.append(new_sequence)

    await db.commit()

    for seq in created_sequences:
        await db.refresh(seq)

    return UploadResponse(
        message=f"Uploaded {len(created_sequences)} sequences",
        sequences=created_sequences,
        errors=errors
    )


@router.delete("/{sequence_id}")
async def delete_sequence(sequence_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Sequence).where(Sequence.id == sequence_id))
    sequence = result.scalar_one_or_none()
    if not sequence:
        raise HTTPException(status_code=404, detail="Sequence not found")

    await db.delete(sequence)
    await db.commit()
    return {"message": f"Sequence '{sequence.name}' deleted successfully"}
