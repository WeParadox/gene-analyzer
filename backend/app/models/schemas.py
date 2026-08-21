from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GeneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = ""
    organism: str = "Unknown"
    reference_sequence: str = Field(..., min_length=1)
    category: str = "unknown"


class GeneCreate(GeneBase):
    pass


class GeneResponse(GeneBase):
    id: int
    length: int
    gc_content: int
    created_at: datetime

    class Config:
        from_attributes = True


class SequenceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    sequence: str = Field(..., min_length=1)


class SequenceCreate(SequenceBase):
    gene_id: int


class SequenceResponse(SequenceBase):
    id: int
    gene_id: int
    length: int
    gc_content: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


class AlignmentResponse(BaseModel):
    id: int
    gene_id: int
    sequence_id: int
    score: int
    identity: int
    gaps: int
    aligned_ref: str
    aligned_query: str
    match_string: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlignmentRequest(BaseModel):
    gene_id: int
    sequence_id: int


class BulkAlignmentRequest(BaseModel):
    gene_id: int
    sequence_ids: List[int]


class StatsResponse(BaseModel):
    gene_id: int
    gene_name: str
    total_sequences: int
    avg_identity: float
    max_identity: float
    min_identity: float
    avg_gaps: float


class UploadResponse(BaseModel):
    message: str
    sequences: List[SequenceResponse]
    errors: List[str] = []
