from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=settings.DEBUG)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Gene(Base):
    __tablename__ = "genes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    organism = Column(String(200), default="Unknown")
    reference_sequence = Column(Text, nullable=False)
    length = Column(Integer, nullable=False)
    gc_content = Column(Integer, default=0)
    category = Column(String(50), default="unknown")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    sequences = relationship("Sequence", back_populates="gene", cascade="all, delete-orphan")
    alignments = relationship("Alignment", back_populates="gene", cascade="all, delete-orphan")


class Sequence(Base):
    __tablename__ = "sequences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gene_id = Column(Integer, ForeignKey("genes.id"), nullable=False)
    name = Column(String(200), nullable=False)
    sequence = Column(Text, nullable=False)
    length = Column(Integer, nullable=False)
    gc_content = Column(Integer, default=0)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    gene = relationship("Gene", back_populates="sequences")
    alignments = relationship("Alignment", back_populates="sequence", cascade="all, delete-orphan")


class Alignment(Base):
    __tablename__ = "alignments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    gene_id = Column(Integer, ForeignKey("genes.id"), nullable=False)
    sequence_id = Column(Integer, ForeignKey("sequences.id"), nullable=False)
    score = Column(Integer, default=0)
    identity = Column(Integer, default=0)
    gaps = Column(Integer, default=0)
    aligned_ref = Column(Text, default="")
    aligned_query = Column(Text, default="")
    match_string = Column(Text, default="")
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    gene = relationship("Gene", back_populates="alignments")
    sequence = relationship("Sequence", back_populates="alignments")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
