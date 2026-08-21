# Changelog

All notable changes to the Gene Analyzer tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-08-21

### Added
- BLASTN default scoring parameters (match=+2, mismatch=-3, gap_open=-7, gap_extend=-2)
- E-value calculation for statistical significance
- Bit score calculation for normalized scoring
- Match/mismatch/gap character counts in alignment results
- Coverage statistic
- Alignment length tracking
- Export endpoints (JSON, CSV, FASTA formats)
- Comprehensive input validation
- Unit tests for alignment logic
- Validation dataset with known answers
- Health check endpoint with database stats
- Request timing header (X-Process-Time)
- Structured logging
- CHANGELOG.md
- LICENSE file
- API error codes

### Changed
- Identity calculation now reports decimal precision (e.g., 98.28 instead of 98)
- Improved error messages with specific details
- Database schema updated with new alignment fields
- Updated Pydantic schemas with validation and documentation

### Fixed
- Gap counting now correctly counts gap events, not characters
- Bulk alignment now checks for existing alignments (deduplication)
- BioPython 1.88 compatibility for alignment coordinate reconstruction

## [1.0.0] - 2026-08-21

### Added
- Initial release
- Gene database management (CRUD)
- FASTA file upload and parsing
- Pairwise sequence alignment
- Interactive alignment viewer
- Statistics dashboard
- 10 demo genes (AMR, virulence, housekeeping)
- React frontend with Bootstrap UI
- Docker Compose deployment
- API documentation (Swagger/Redoc)
