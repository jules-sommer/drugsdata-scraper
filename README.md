# DrugsData ( Lame ) Scraper

## Overview
DrugsData is a powerful (read: lame, hard-coded, inefficient, jumbled mess of a...) Python web scraper designed to extract detailed (read: some) information about molecules from DrugBank. It navigates through pages of molecules, fetching data like mol weight, formula, text descriptions and categorical data, pharmacology and pharmacodynamics, and more, then saves this data in a clean, well-structured JSON format.

## Features
- Scrapes multiple pages of DrugBank drug listings, based on user inputted args.
- Extracts detailed molecule information including molecular weight, formula, descriptions, categories, links, and pharmacodynamics.
- Option to save raw HTML pages for offline analysis.
- Customizable verbosity levels for different types of output.
- Saves scraped data as a JSON file for easy integration with other applications.

## Installation
To run this scraper, you need Python 3.x and the following packages:
- `requests`
- `bs4` (BeautifulSoup)
- `json`
- `argparse`

You can install the required packages using:
```bash
pip install requests bs4 argparse
```

## Usage
Run `drugsdata.py` from the command line, providing the desired arguments:
```bash
python drugsdata.py [-n NUM_PAGES] [-v VERBOSITY] [-s SHOULD_SAVE_HTML]
```

### Arguments
- `-n`, `--num-pages`: Number of pages to scrape (default: 1).
- `-v`, `--verbosity`: Verbosity level (0: status updates, 1: molecule names, 2: full JSON).
- `-s`, `--save-html`: Save raw HTML for each page.

## Output
The scraper outputs a `drugbank_data.json` file containing all scraped data. The JSON file will have an array of drug information objects.

## Note
- Ensure compliance with DrugBank's terms of use and scraping policies.
- This scraper is intended for educational and research purposes only.

## Contributing
This was thrown together in a few hours, and I do not anticipate it becoming a >= 10k starred repo on GitHub, but obv feel free to fork this project and submit pull requests with any *enhancements*. If you find any of the obvious and plentiful bugs or have suggestions, open an issue in the repository and relentlessly mock my Python skills.
