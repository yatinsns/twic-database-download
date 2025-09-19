#!/usr/bin/env python3
"""
TWIC Database Scraper
Scrapes chess game data from The Week In Chess website and creates JSON files for each row.
"""

import requests
import json
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

class TWICScraper:
    def __init__(self, base_url="https://theweekinchess.com/twic"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def fetch_page(self):
        """Fetch the main TWIC page"""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_table(self, html_content):
        """Parse the HTML table and extract all row data"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the main table
        table = soup.find('table')
        if not table:
            print("No table found on the page")
            return []

        rows = []
        table_rows = table.find_all('tr')

        # Skip header row and process data rows
        for row in table_rows[1:]:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 7:  # Ensure we have all expected columns
                row_data = self.extract_row_data(cells)
                if row_data and row_data['twic_number'] is not None:  # Only add valid data rows
                    rows.append(row_data)

        return rows

    def extract_row_data(self, cells):
        """Extract data from a table row"""
        try:
            # TWIC number
            twic_text = cells[0].get_text().strip()
            twic_match = re.search(r'(\d+)', twic_text)
            twic_number = int(twic_match.group(1)) if twic_match else None

            # Date
            date = cells[1].get_text().strip()

            # HTML link
            html_link = None
            html_a = cells[2].find('a')
            if html_a and html_a.get('href'):
                html_link = urljoin(self.base_url, html_a.get('href'))

            # PGN link
            pgn_link = None
            pgn_a = cells[3].find('a')
            if pgn_a and pgn_a.get('href'):
                pgn_link = urljoin(self.base_url, pgn_a.get('href'))

            # CBV link
            cbv_link = None
            cbv_a = cells[4].find('a')
            if cbv_a and cbv_a.get('href'):
                cbv_link = urljoin(self.base_url, cbv_a.get('href'))

            # Games count
            games_text = cells[5].get_text().strip()
            games = int(games_text) if games_text.isdigit() else None

            # Stories count
            stories_text = cells[6].get_text().strip()
            stories = int(stories_text) if stories_text.isdigit() else None

            return {
                'twic_number': twic_number,
                'issue': twic_text,
                'date': date,
                'html_link': html_link,
                'pgn_link': pgn_link,
                'cbv_link': cbv_link,
                'games': games,
                'stories': stories
            }

        except Exception as e:
            print(f"Error extracting row data: {e}")
            return None

    def save_json_files(self, rows, output_dir="twic_data"):
        """Save each row as a separate JSON file"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for row in rows:
            if row['twic_number']:
                filename = f"twic_{row['twic_number']:04d}.json"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(row, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(rows)} JSON files to {output_dir}/")

    def run(self):
        """Main execution function"""
        print("Fetching TWIC page...")
        html_content = self.fetch_page()

        if not html_content:
            print("Failed to fetch page content")
            return

        print("Parsing table data...")
        rows = self.parse_table(html_content)

        if not rows:
            print("No data found")
            return

        print(f"Found {len(rows)} rows of data")

        print("Saving JSON files...")
        self.save_json_files(rows)

        # Print sample data
        if rows:
            print("\nSample data (first entry):")
            print(json.dumps(rows[0], indent=2))

if __name__ == "__main__":
    scraper = TWICScraper()
    scraper.run()