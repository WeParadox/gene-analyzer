# Gene Analyzer - Usage Guide

## What Is This Tool?

Gene Analyzer is a web tool for analyzing amplified gene sequences using pairwise alignment. It's designed for **targeted gene panels** — similar to how IMGT/HLA focuses on HLA genes, this tool lets you define your own set of gene targets (up to 50) and analyze sequences against their references.

---

## Is It Like IMGT for HLA?

| Feature | IMGT/HLA | Gene Analyzer |
|---------|----------|---------------|
| **Scope** | HLA genes only | Any gene targets you define |
| **Reference database** | Pre-built (millions of alleles) | You provide reference sequences |
| **Allele naming** | Official WHO nomenclature | Your own naming scheme |
| **Alignment** | Specialized for HLA polymorphism | General pairwise alignment (Needleman-Wunsch) |
| **Use case** | Clinical HLA typing | Research: AMR genes, virulence factors, housekeeping genes, custom panels |
| **Cost** | Free (EBI-hosted) | Free (self-hosted) |

**Bottom line**: This tool gives you IMGT-like functionality for your own gene targets. You define the genes and references; the tool handles alignment, identity scoring, and visualization.

---

## Quick Start

### 1. Start the Tool

```bash
cd gene-analyzer/backend
uvicorn app.main:app --reload --port 8000
```

Frontend (if Node.js installed):
```bash
cd gene-analyzer/frontend
npm run dev
```

### 2. Access

- **Frontend UI**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs

---

## Step-by-Step Guide

### Step 1: Load or Add Gene Targets

On first launch, 10 demo genes are loaded automatically. To add your own:

#### Via UI
1. Click **"+ Add Gene"** in the left panel
2. Fill in:
   - **Gene Name**: e.g., `blaCTX-M-15`
   - **Description**: Function, resistance mechanism, etc.
   - **Organism**: e.g., `Klebsiella pneumoniae`
   - **Category**: AMR, virulence, housekeeping, or other
   - **Reference Sequence**: Your ~150bp reference (paste FASTA sequence)
3. Click **"Add Gene"**

#### Via API
```bash
curl -X POST http://localhost:8000/api/genes/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "blaCTX-M-15",
    "description": "ESBL, resistance to 3rd-gen cephalosporins",
    "organism": "Klebsiella pneumoniae",
    "reference_sequence": "ATGCGTTTATGCGCTGGGCGATACCG...",
    "category": "AMR"
  }'
```

#### Batch Load (Script)
```python
import requests
import json

with open('my_genes.json') as f:
    genes = json.load(f)

for gene in genes:
    resp = requests.post('http://localhost:8000/api/genes/', json=gene)
    print(f"Added {gene['name']}: {resp.status_code}")
```

---

### Step 2: Upload Sequences

Prepare your sequences in FASTA format:

```
>patient_001
ATGCGTTTATGCGCTGGGCGATACCGAAACGATCACCGCAATGGCGGCGACGCTGGCGATCAACGGCCCGGGCACGCTGGCGATCGGCAAC
>patient_002
ATGCGTTTATGCGCTGGGCGATACCGAAACGATCACCGCAATGGCGGCGACGCTGGCGATCAACGGCCCGGGCACGCTGGCGATCGGCAAC
>patient_003
ATGCGTTTATGCGCTGGGCGATACCGAAACGATCACCGCAATGGCGGCGACGCTGGCGATCAACGGCCCGGGCACGCTGGCGATCGGCAAC
```

#### Via UI
1. Select a gene from the left panel
2. Click **"Upload FASTA"** or drag & drop your file
3. Sequences appear in the list

#### Via API
```bash
curl -X POST "http://localhost:8000/api/sequences/upload?gene_id=1" \
  -F "file=@my_sequences.fasta"
```

---

### Step 3: Run Alignment

#### Via UI
- Click **"Align All"** to align every sequence against the reference
- Or click the **🎯** icon on individual sequences

#### Via API
```bash
# Single alignment
curl -X POST http://localhost:8000/api/alignment/run \
  -H "Content-Type: application/json" \
  -d '{"gene_id": 1, "sequence_id": 3}'

# Bulk alignment
curl -X POST http://localhost:8000/api/alignment/run-bulk \
  -H "Content-Type: application/json" \
  -d '{"gene_id": 1, "sequence_ids": [1, 2, 3, 4, 5]}'
```

---

### Step 4: Interpret Results

#### Alignment Viewer
```
Ref:   ATCG-ATCG
       |||| ||||
Query: ATCGAATCG
```
- `|` = Match (yellow)
- `.` = Mismatch (red)
- ` ` = Gap (insertion/deletion)

#### Statistics
| Metric | Meaning |
|--------|---------|
| **Identity %** | Percentage of matching bases (excluding gap positions) |
| **Gaps** | Number of indel events (not individual gap characters) |
| **Score** | Alignment score (higher = better match) |

#### Identity Ranges
| Identity | Interpretation |
|----------|---------------|
| >95% | Highly conserved / same allele |
| 80-95% | Related variant / SNP differences |
| 60-80% | Distant homolog / possible contamination |
| <60% | Non-target or severely degraded |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/genes/` | List all genes |
| POST | `/api/genes/` | Create a gene |
| GET | `/api/genes/{id}` | Get gene details |
| DELETE | `/api/genes/{id}` | Delete a gene |
| POST | `/api/genes/load-demo` | Load demo dataset |
| GET | `/api/sequences/` | List sequences (optional: `?gene_id=X`) |
| POST | `/api/sequences/upload?gene_id=X` | Upload FASTA file |
| DELETE | `/api/sequences/{id}` | Delete a sequence |
| POST | `/api/alignment/run` | Run single alignment |
| POST | `/api/alignment/run-bulk` | Run bulk alignment |
| GET | `/api/alignment/gene/{id}` | Get alignments for a gene |
| GET | `/api/alignment/stats/{id}` | Get alignment statistics |

---

## Alignment Algorithm

- **Algorithm**: Needleman-Wunsch (global pairwise alignment)
- **Scoring**: Match = +2, Mismatch = -1, Gap open = -10, Gap extend = -0.5
- **Identity**: Calculated as `matches / comparable_positions` (gap positions excluded)
- **Gaps**: Counted as gap events (single insertion/deletion), not individual gap characters

---

## Example Workflow: AMR Gene Panel

1. **Define your panel** (50 AMR genes):
   ```bash
   for gene in blaCTX-M-15 blaKPC-2 blaNDM-1 mcr-1 vanA; do
     curl -X POST http://localhost:8000/api/genes/ \
       -H "Content-Type: application/json" \
       -d "{\"name\": \"$gene\", \"category\": \"AMR\", \"reference_sequence\": \"...\"}"
   done
   ```

2. **Upload clinical isolates**:
   ```bash
   for isolate in isolate_001.fasta isolate_002.fasta isolate_003.fasta; do
     gene_id=$(curl -s http://localhost:8000/api/genes/ | python3 -c "import sys,json; print([g['id'] for g in json.load(sys.stdin) if '$isolate' in g['name']][0])")
     curl -X POST "http://localhost:8000/api/sequences/upload?gene_id=$gene_id" -F "file=@$isolate"
   done
   ```

3. **Run alignments and get results**:
   ```bash
   curl -s http://localhost:8000/api/alignment/stats/1 | python3 -m json.tool
   ```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No sequences found" | Check FASTA format (must start with `>`) |
| "Invalid sequence characters" | Only ATCGNRYSWKMBDHV allowed |
| Low identity scores | Check if correct reference gene selected |
| Frontend not loading | Ensure backend is running on port 8000 |
| Upload fails | Check file size (< 10MB) and encoding (UTF-8) |

---

## Comparison: When to Use What

| Scenario | Tool |
|----------|------|
| Clinical HLA typing | IMGT/HLA |
| Custom gene panel analysis | **Gene Analyzer** |
| Whole-genome alignment | MUMmer, minimap2 |
| Multiple sequence alignment | MAFFT, MUSCLE, ClustalW |
| SNP calling from reads | BWA + GATK, FreeBayes |
| Phylogenetic analysis | RAxML, IQ-TREE |

---

## Limitations

1. **Pairwise only**: Compares one query to one reference (not multiple sequences simultaneously)
2. **No variant calling**: Doesn't call SNPs from raw reads — needs pre-amplified sequences
3. **No database of alleles**: You provide all reference sequences
4. **Max ~50 genes**: Designed for targeted panels, not genome-wide analysis
5. **~150bp references**: Works best with short amplicons (can handle longer sequences but slower)
