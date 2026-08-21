# Gene Analyzer

A free, open-source web tool for analyzing amplified gene sequences with pairwise alignment. Similar to IMGT/HLA but designed for custom gene targets.

## Features

- **Gene Database**: Store and manage reference sequences for up to 50 target genes
- **FASTA Upload**: Upload user sequences in FASTA format
- **Sequence Alignment**: Pairwise alignment using Needleman-Wunsch algorithm
- **Interactive Visualization**: Color-coded alignment viewer with mismatch highlighting
- **Statistics Dashboard**: Identity distribution, gap analysis, and summary statistics
- **Export**: Download results and reports

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

1. **Load Demo Data**: On first launch, the app loads 10 demo genes automatically
2. **Select Gene**: Choose a gene target from the left panel
3. **Upload Sequences**: Click "Upload FASTA" to add your amplified sequences
4. **Run Alignment**: Click "Align All" or align individual sequences
5. **View Results**: See alignment visualization and statistics

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
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   └── utils/               # API utilities
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Demo Dataset

The app includes 10 sample genes for testing:

- **AMR genes**: blaCTX-M-15, blaKPC-2, blaNDM-1, blaOXA-48, mcr-1, vanA
- **Virulence genes**: luxS, fimH
- **Housekeeping genes**: rpoB, gyrA

## License

MIT License - Free for personal and commercial use.

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
