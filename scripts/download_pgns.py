#!/usr/bin/env python3
"""
TWIC PGN Downloader
Downloads PGN files from TWIC JSON data and organizes them in a folder structure.
"""

import json
import os
import requests
import time
from pathlib import Path
from urllib.parse import urlparse
import concurrent.futures
from threading import Lock

class TWICPGNDownloader:
    def __init__(self, json_dir="twic_data", pgn_dir="twic_pgns"):
        self.json_dir = Path(json_dir)
        self.pgn_dir = Path(pgn_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.download_stats = {
            'total': 0,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0
        }
        self.stats_lock = Lock()

    def load_json_files(self):
        """Load all JSON files and extract PGN links"""
        json_files = []

        if not self.json_dir.exists():
            print(f"JSON directory {self.json_dir} does not exist")
            return []

        for json_file in sorted(self.json_dir.glob("twic_*.json")):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('pgn_link'):
                        json_files.append(data)

            except Exception as e:
                print(f"Error reading {json_file}: {e}")

        return json_files

    def create_output_directory(self):
        """Create the output directory for PGN files"""
        self.pgn_dir.mkdir(exist_ok=True)
        print(f"PGN files will be saved to: {self.pgn_dir.absolute()}")

    def get_filename_from_url(self, url, twic_number):
        """Extract filename from URL or create one based on TWIC number"""
        try:
            parsed_url = urlparse(url)
            filename = os.path.basename(parsed_url.path)

            # If we can't get a good filename from URL, create one
            if not filename or not filename.endswith(('.zip', '.pgn')):
                filename = f"twic{twic_number:04d}.zip"

            return filename
        except:
            return f"twic{twic_number:04d}.zip"

    def download_file(self, data):
        """Download a single PGN file"""
        twic_number = data.get('twic_number')
        pgn_url = data.get('pgn_link')

        if not pgn_url:
            with self.stats_lock:
                self.download_stats['skipped'] += 1
            return f"TWIC {twic_number}: No PGN link"

        filename = self.get_filename_from_url(pgn_url, twic_number)
        file_path = self.pgn_dir / filename

        # Skip if file already exists
        if file_path.exists():
            with self.stats_lock:
                self.download_stats['skipped'] += 1
            return f"TWIC {twic_number}: Already exists - {filename}"

        try:
            # Download with timeout and stream
            response = self.session.get(pgn_url, timeout=30, stream=True)
            response.raise_for_status()

            # Write file in chunks
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            file_size = file_path.stat().st_size
            with self.stats_lock:
                self.download_stats['downloaded'] += 1

            return f"TWIC {twic_number}: Downloaded {filename} ({file_size:,} bytes)"

        except Exception as e:
            with self.stats_lock:
                self.download_stats['failed'] += 1
            return f"TWIC {twic_number}: Failed - {str(e)}"

    def download_all_pgns(self, max_workers=5):
        """Download all PGN files with concurrent downloads"""
        json_data = self.load_json_files()

        if not json_data:
            print("No JSON files with PGN links found")
            return

        self.download_stats['total'] = len(json_data)
        print(f"Found {len(json_data)} TWIC issues with PGN links")

        self.create_output_directory()

        print(f"Starting downloads with {max_workers} concurrent workers...")

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all download tasks
            future_to_data = {
                executor.submit(self.download_file, data): data
                for data in json_data
            }

            # Process completed downloads
            for i, future in enumerate(concurrent.futures.as_completed(future_to_data), 1):
                result = future.result()
                print(f"[{i}/{len(json_data)}] {result}")

                # Brief pause every 10 downloads to be respectful
                if i % 10 == 0:
                    time.sleep(1)

        self.print_final_stats()

    def print_final_stats(self):
        """Print download statistics"""
        stats = self.download_stats
        print("\n" + "="*60)
        print("DOWNLOAD SUMMARY")
        print("="*60)
        print(f"Total files:      {stats['total']}")
        print(f"Downloaded:       {stats['downloaded']}")
        print(f"Skipped:          {stats['skipped']}")
        print(f"Failed:           {stats['failed']}")
        print(f"Output directory: {self.pgn_dir.absolute()}")
        print("="*60)

    def run(self):
        """Main execution function"""
        print("TWIC PGN Downloader")
        print("="*40)
        self.download_all_pgns()

if __name__ == "__main__":
    downloader = TWICPGNDownloader()
    downloader.run()