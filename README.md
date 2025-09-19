# TWIC Database Download

A comprehensive scraper and database builder for [The Week In Chess (TWIC)](https://theweekinchess.com/twic) archives. This project extracts, downloads, and combines decades of professional chess games into a single massive PGN database.

## Overview

The Week In Chess has been publishing chess games since 1994, creating one of the largest archives of professional chess games available online. This project automates the process of:

1. **Scraping** the TWIC website to extract metadata for all issues
2. **Downloading** PGN archives from each TWIC issue
3. **Combining** all games into a single master PGN database

## Results

- **6.6+ million chess games** spanning 30+ years
- **2.6 GB** master PGN file
- **689 TWIC issues** processed (from 920 to 1610+)
- **1609 JSON metadata files** with complete issue information

## Scripts

### `scripts/scrape_twic.py`
Scrapes the main TWIC page and creates JSON files for each table row.

**Features:**
- Extracts all column data (TWIC number, date, HTML/PGN/CBV links, games count, stories count)
- Creates individual JSON files for each TWIC issue
- Handles missing data gracefully

**Usage:**
```bash
python scripts/scrape_twic.py
```

**Output:** `twic_data/` directory with 1609 JSON files

### `scripts/download_pgns.py`
Downloads PGN archives from URLs extracted from JSON metadata.

**Features:**
- Concurrent downloads (5 workers) for efficiency
- Automatic retry and error handling
- Progress tracking and statistics
- Proper file naming convention

**Usage:**
```bash
python scripts/download_pgns.py
```

**Output:** `twic_pgns/` directory with 689 ZIP files (~1.0 GB)

### `scripts/combine_pgns.py`
Extracts and combines all PGN files into a single master database.

**Features:**
- Handles ZIP extraction automatically
- Combines millions of games efficiently
- Maintains proper PGN formatting
- Progress tracking for large datasets

**Usage:**
```bash
python scripts/combine_pgns.py
```

**Output:** `twic_master.pgn` (2.6 GB, 6.6M games)

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install requests beautifulsoup4
   ```

2. **Run the complete pipeline:**
   ```bash
   # Step 1: Scrape TWIC metadata
   python scripts/scrape_twic.py

   # Step 2: Download PGN archives
   python scripts/download_pgns.py

   # Step 3: Combine into master database
   python scripts/combine_pgns.py
   ```

3. **Result:** `twic_master.pgn` contains the complete database

## File Structure

```
twic-database-download/
├── scripts/
│   ├── scrape_twic.py      # Website scraper
│   ├── download_pgns.py    # PGN downloader
│   └── combine_pgns.py     # Database combiner
├── twic_data/              # JSON metadata (gitignored)
├── twic_pgns/              # PGN archives (gitignored)
├── twic_master.pgn         # Master database (gitignored)
└── README.md
```

## Data Format

### JSON Metadata (`twic_data/`)
Each JSON file contains:
```json
{
  "twic_number": 1610,
  "issue": "1610",
  "date": "2025-09-15",
  "html_link": "https://theweekinchess.com/html/twic1610.html",
  "pgn_link": "https://theweekinchess.com/zips/twic1610g.zip",
  "cbv_link": "https://theweekinchess.com/zips/twic1610c6.zip",
  "games": 4643,
  "stories": 28
}
```

### Master PGN Database
Standard PGN format with complete game headers:
```
[Event "Tournament Name"]
[Site "Location"]
[Date "YYYY.MM.DD"]
[Round "1"]
[White "Player Name"]
[Black "Player Name"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 ...
```

## Requirements

- Python 3.6+
- `requests` library
- `beautifulsoup4` library
- ~4 GB free disk space for complete database

## Notes

- Large data files are excluded from git via `.gitignore`
- Downloads are respectful with rate limiting
- Error handling for network issues and corrupted files
- Cross-platform compatibility (Windows, macOS, Linux)

## License

This project is for educational and research purposes. The chess games themselves remain under their original licenses from TWIC.