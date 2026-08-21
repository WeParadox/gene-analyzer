from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import json

from ..models.database import get_db, Gene
from ..models.schemas import GeneCreate, GeneResponse
from ..services.alignment import calculate_gc_content
from ..config import settings

router = APIRouter(prefix="/api/genes", tags=["genes"])


@router.get("/", response_model=List[GeneResponse])
async def list_genes(
    category: str = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Gene)
    if category:
        query = query.where(Gene.category == category)
    result = await db.execute(query)
    genes = result.scalars().all()
    return genes


@router.get("/{gene_id}", response_model=GeneResponse)
async def get_gene(gene_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Gene).where(Gene.id == gene_id))
    gene = result.scalar_one_or_none()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")
    return gene


@router.post("/", response_model=GeneResponse)
async def create_gene(gene: GeneCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Gene).where(Gene.name == gene.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Gene name already exists")

    new_gene = Gene(
        name=gene.name,
        description=gene.description,
        organism=gene.organism,
        reference_sequence=gene.reference_sequence.upper(),
        length=len(gene.reference_sequence),
        gc_content=calculate_gc_content(gene.reference_sequence),
        category=gene.category
    )
    db.add(new_gene)
    await db.commit()
    await db.refresh(new_gene)
    return new_gene


@router.delete("/{gene_id}")
async def delete_gene(gene_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Gene).where(Gene.id == gene_id))
    gene = result.scalar_one_or_none()
    if not gene:
        raise HTTPException(status_code=404, detail="Gene not found")

    await db.delete(gene)
    await db.commit()
    return {"message": f"Gene '{gene.name}' deleted successfully"}


@router.post("/load-demo")
async def load_demo_genes(db: AsyncSession = Depends(get_db)):
    demo_file = settings.DATA_DIR / "demo_genes.json"
    if not demo_file.exists():
        raise HTTPException(status_code=404, detail="Demo data not found")

    with open(demo_file, 'r') as f:
        demo_genes = json.load(f)

    loaded = 0
    skipped = 0
    for gene_data in demo_genes:
        existing = await db.execute(select(Gene).where(Gene.name == gene_data['name']))
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        new_gene = Gene(
            name=gene_data['name'],
            description=gene_data.get('description', ''),
            organism=gene_data.get('organism', 'Unknown'),
            reference_sequence=gene_data['reference_sequence'].upper(),
            length=len(gene_data['reference_sequence']),
            gc_content=calculate_gc_content(gene_data['reference_sequence']),
            category=gene_data.get('category', 'unknown')
        )
        db.add(new_gene)
        loaded += 1

    await db.commit()
    return {"message": f"Loaded {loaded} genes, skipped {skipped} existing"}
