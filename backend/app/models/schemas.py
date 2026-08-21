from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re


GENE_NAME_PATTERN = re.compile(r'^[A-Za-z0-9_\-\.]{1,100}$')
SEQUENCE_PATTERN = re.compile(r'^[ATCGNRYSWKMBDHVatcg]+$', re.IGNORECASE)


class GeneBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Gene name (alphanumeric, hyphens, underscores)")
    description: str = Field("", max_length=1000, description="Gene description")
    organism: str = Field("Unknown", max_length=200, description="Organism name")
    reference_sequence: str = Field(..., min_length=1, max_length=100000, description="Reference DNA sequence")
    category: str = Field("unknown", description="Gene category")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if not GENE_NAME_PATTERN.match(v):
            raise ValueError('Name must be alphanumeric with hyphens/underscores only')
        return v

    @field_validator('reference_sequence')
    @classmethod
    def validate_sequence(cls, v):
        v = v.upper().strip()
        if not SEQUENCE_PATTERN.match(v):
            raise ValueError('Sequence contains invalid characters. Only ATCGNRYSWKMBDHV allowed')
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v):
        allowed = {'AMR', 'virulence', 'housekeeping', 'resistance', 'unknown', 'other'}
        if v.lower() not in allowed:
            raise ValueError(f'Category must be one of: {", ".join(allowed)}')
        return v.lower()


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
    name: str = Field(..., min_length=1, max_length=200, description="Sequence identifier")
    sequence: str = Field(..., min_length=1, max_length=100000, description="DNA sequence")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Sequence name cannot be empty')
        return v.strip()

    @field_validator('sequence')
    @classmethod
    def validate_sequence(cls, v):
        v = v.upper().strip()
        if not SEQUENCE_PATTERN.match(v):
            raise ValueError('Sequence contains invalid characters. Only ATCGNRYSWKMBDHV allowed')
        return v


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
    identity: float
    gaps: int
    gap_characters: int
    matches: int
    mismatches: int
    comparable_positions: int
    aligned_ref: str
    aligned_query: str
    match_string: str
    e_value: float
    bit_score: float
    coverage: float
    query_length: int
    reference_length: int
    alignment_length: int
    scoring_scheme: str
    created_at: datetime

    class Config:
        from_attributes = True


class AlignmentRequest(BaseModel):
    gene_id: int = Field(..., gt=0, description="Gene ID")
    sequence_id: int = Field(..., gt=0, description="Sequence ID")


class BulkAlignmentRequest(BaseModel):
    gene_id: int = Field(..., gt=0, description="Gene ID")
    sequence_ids: List[int] = Field(..., min_length=1, max_length=1000, description="List of sequence IDs (max 1000)")

    @field_validator('sequence_ids')
    @classmethod
    def validate_sequence_ids(cls, v):
        if len(set(v)) != len(v):
            raise ValueError('Duplicate sequence IDs not allowed')
        return v


class StatsResponse(BaseModel):
    gene_id: int
    gene_name: str
    total_sequences: int
    avg_identity: float
    max_identity: float
    min_identity: float
    avg_gaps: float
    avg_bit_score: float
    avg_e_value: float
    total_matches: int
    total_mismatches: int
    total_gap_characters: int


class UploadResponse(BaseModel):
    message: str
    sequences: List[SequenceResponse]
    errors: List[str] = []
    warnings: List[str] = []


class ExportRequest(BaseModel):
    gene_id: int = Field(..., gt=0, description="Gene ID")
    format: str = Field("json", description="Export format: json, csv, fasta")
    include_alignment: bool = Field(True, description="Include alignment details")


class ErrorResponse(BaseModel):
    error: str
    detail: str
    code: str


class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    gene_count: int
    sequence_count: int
    alignment_count: int
