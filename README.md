# Gene Analyzer

A free, open-source web tool for analyzing amplified gene sequences with pairwise alignment. Similar to IMGT/HLA but designed for custom gene targets.

## Features

- **Gene Database**: Store and manage reference sequences for up to 50 target genes
- **FASTA Upload**: Upload user sequences in FASTA format
- **BLASTN Alignment**: Standard BLASTN scoring parameters (match=+2, mismatch=-3, gap_open=-7, gap_extend=-2)
- **Statistical Scores**: E-value, bit score, coverage, identity, and gap analysis
- **Interactive Visualization**: Color-coded alignment viewer with mismatch highlighting
- **Statistics Dashboard**: Identity distribution, gap analysis, and summary statistics
- **Export**: Download results in JSON, CSV, or FASTA formats
- **Input Validation**: Comprehensive sequence and parameter validation
- **Unit Tests**: Automated test suite for alignment logic

## Tech Stack

- **Backend**: Python FastAPI + BioPython + SQLite
- **Frontend**: React + Bootstrap + Plotly.js
- **Deployment**: Docker Compose

## Quick Start

### Using Docker (Recommended)

```bash
cd gene-analyzer
docker-compose up --build
```

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Manual Setup

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

See [USAGE.md](USAGE.md) for the complete guide.

**Quick Start:**
1. **Load Demo Data**: On first launch, the app loads 10 demo genes automatically
2. **Select Gene**: Choose a gene target from the left panel
3. **Upload Sequences**: Click "Upload FASTA" to add your amplified sequences
4. **Run Alignment**: Click "Align All" or align individual sequences
5. **View Results**: See alignment visualization and statistics
6. **Export**: Download results in JSON, CSV, or FASTA format

## Alignment Algorithm

- **Algorithm**: Needleman-Wunsch (global pairwise alignment)
- **Scoring**: BLASTN defaults (match=+2, mismatch=-3, gap_open=-7, gap_extend=-2)
- **E-value**: Statistical significance using Karlin-Altschul statistics
- **Bit score**: Normalized alignment score
- **Identity**: Calculated as `matches / comparable_positions` (gap positions excluded)
- **Gaps**: Counted as gap events (single insertion/deletion), not individual gap characters

## How It Compares to IMGT

| Feature | IMGT/HLA | Gene Analyzer |
|---------|----------|---------------|
| **Scope** | HLA genes only | Any gene targets you define |
| **References** | Pre-built (millions of alleles) | You provide reference sequences |
| **Use case** | Clinical HLA typing | Research: AMR, virulence, custom panels |
| **Cost** | Free (EBI-hosted) | Free (self-hosted) |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/genes/` | List all genes |
| POST | `/api/genes/` | Create new gene |
| POST | `/api/genes/load-demo` | Load demo dataset |
| POST | `/api/sequences/upload` | Upload FASTA file |
| POST | `/api/alignment/run` | Run single alignment |
| POST | `/api/alignment/run-bulk` | Run bulk alignment |
| GET | `/api/alignment/gene/{id}` | Get gene alignments |
| GET | `/api/alignment/stats/{id}` | Get alignment stats |
| GET | `/api/alignment/export/{id}` | Export results (JSON/CSV/FASTA) |
| GET | `/health` | Health check with stats |

## Testing

Run the test suite:

```bash
cd backend
pip install pytest
pytest tests/ -v
```

## Project Structure

```
gene-analyzer/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration
│   │   ├── models/              # Database models
│   │   ├── routers/             # API endpoints
│   │   ├── services/            # Business logic
│   │   └── data/                # Demo data
│   ├── tests/                   # Unit tests
│   │   ├── test_alignment.py    # Alignment tests
│   │   └── validation_dataset.json
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   └── utils/               # API utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── CHANGELOG.md
├── LICENSE
├── README.md
└── USAGE.md
```

## Demo Dataset

The app includes 10 sample genes for testing:

- **AMR genes**: blaCTX-M-15, blaKPC-2, blaNDM-1, blaOXA-48, mcr-1, vanA
- **Virulence genes**: luxS, fimH
- **Housekeeping genes**: rpoB, gyrA

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
