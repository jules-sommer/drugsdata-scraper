import requests
from bs4 import BeautifulSoup
import json
import argparse
import os

# Set up the argument parser
parser = argparse.ArgumentParser(description='Scrape DrugBank data.')
parser.add_argument('-n', '--num-pages', type=int, default=1,
                    help='Number of pages to scrape.')
parser.add_argument('-v', '--verbosity', type=int, choices=[0, 1, 2], default=0,
                    help='Verbosity level: 0 for status updates, 1 for molecule names, 2 for full JSON.')
parser.add_argument('-s', '--save-html', action='store_true',
                    help='Save the raw HTML for each page.')
args = parser.parse_args()

# The base URL for DrugBank drugs listing
BASE_URL = "https://go.drugbank.com/drugs?approved=0&nutraceutical=0&illicit=0&investigational=0&withdrawn=0&experimental=0&us=0&ca=0&eu=0&commit=Apply+Filter&page="

empty_vals = ["not annotated", "not available"]

# Function to get content by ID
def get_content_by_id(soup, section_id):
    element = soup.find(id=section_id)
    if element:
        return element.get_text(strip=True)
    return None

def format_formula(formula):
    # Remove any whitespace from the formula
    formatted_formula = ''.join(formula.split())
    return formatted_formula

def format_empty_values(value):
    if value.lower() in empty_vals:
        return None
    return value

def extract_section_sibling(soup, section_id, get_text=True):
    section = soup.find('dt', {'id': section_id})
    if section:
        sibling = section.find_next_sibling('dd')
        if sibling:
            if get_text:
                return sibling.get_text(strip=True)
            else:
                return sibling
    return None

# Function to scrape a single page
def scrape_page(page_number, save_html=args.save_html):
    url = f"{BASE_URL}{page_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    if save_html:
        # Create a directory for the HTML files if it doesn't exist
        os.makedirs('html_pages', exist_ok=True)
        # Define the filename based on the page number
        filename = f'html_pages/page_{page_number}.html'
        # Write the raw HTML to the file
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"Saved raw HTML for page {page_number} to {filename}")

    # Find the table with the drugs list
    drugs_table = soup.find('table', {'id': 'drugs-table'})
    drugs = []

    for row in drugs_table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if cols:
            # Extract the weight and formula from the 'weight-value' column
            weight_formula = cols[1].get_text(separator=" ").split()
            weight = weight_formula[0]  # The first element is always the weight
            formula = " ".join(weight_formula[1:])  # The rest is the formula
            formatted_formula = format_formula(formula)  # Format the formula

            description = format_empty_values(cols[3].text.strip())

            # Extract categories, check for 'empty' categories, and replace with None if necessary
            raw_categories = cols[4].text.strip()
            if raw_categories:
                categories = [category.strip() for category in raw_categories.split(',')]
                # Check if categories only contain 'empty' values
                if all(category.lower() in empty_vals for category in categories):
                    categories = None
            else:
                categories = None

            # Extract the DrugBank page link
            drug_link_tag = cols[0].find('a', href=True)
            drug_link = f"https://go.drugbank.com{drug_link_tag['href']}" if drug_link_tag else None

            if(drug_link):
              response = requests.get(drug_link)
              drug_page = BeautifulSoup(response.text, 'html.parser')

              if save_html:
                # Define the filename based on the page number
                fileslug = drug_link_tag['href'].split('/')[-1]
                filename = f"html_pages/page_{page_number}_{fileslug}.html"
                # Write the raw HTML to the file
                with open(filename, 'w', encoding='utf-8') as file:
                    file.write(response.text)
                print(f"Saved raw HTML for DB-ID#:{filename} on (p{page_number}) full drug info page to {filename}")

              type = extract_section_sibling(drug_page, 'type')
              background = format_empty_values(extract_section_sibling(drug_page, 'background'))
              
              summary = extract_section_sibling(drug_page, 'summary')
              indication = format_empty_values(extract_section_sibling(drug_page, 'indication', get_text=False).find('p').text.strip())
              pharmacodynamics = format_empty_values(extract_section_sibling(drug_page, 'pharmacodynamics'))
              
              moa = extract_section_sibling(drug_page, 'mechanism-of-action', get_text=False)
              
              moa_table = moa.find('table', {'id': 'drug-moa-target-table'}) if moa else None
              moa_data = []

              if(moa_table):
                # Iterate over each row in the table body
                for row in moa_table.find_all('tr')[1:]:  # Skipping the header row
                    # Get all cells in the row
                    cells = row.find_all('td')

                    # Extract data from each cell
                    target = cells[0].get_text(strip=True)
                    actions = cells[1].get_text(strip=True)
                    organism = cells[2].get_text(strip=True)

                    # Append the data to the list as a dictionary
                    moa_data.append({
                        'Target': target,
                        'Actions': actions,
                        'Organism': organism
                    })

              iupac_name = extract_section_sibling(drug_page, 'iupac-name')
              smiles = extract_section_sibling(drug_page, 'smiles')
              groups = extract_section_sibling(drug_page, 'groups')
              synonyms = extract_section_sibling(drug_page, 'synonyms', get_text=False).find_all('li')
              
              # create a list of synonyms from <ul> containing <li> tags
              synonym_list = []

              if(synonyms):
                for synonym in synonyms:
                  synonym_list.append(synonym.text.strip())

            drug_info = {
              'smiles': smiles if(drug_link) else None,
              'molecule': cols[0].text.strip(),
              'iupac_name': iupac_name if(drug_link) else None,
              'summary': summary,
              'weight': weight,
              'formula': formatted_formula,
              'description': description if not(drug_link) else background,
              'categories': categories,  # Could be None or a list of categories
              'link': drug_link if(drug_link) else None,
              'type': type,
              'groups': groups,
              'synonyms': synonym_list,
              'indication': indication,
              'pharmacodynamics': pharmacodynamics,
              'moa': moa_data
            }
            drugs.append(drug_info)

            # Print based on verbosity level
            if args.verbosity == 1:
                print(drug_info['molecule'])
                print('-----------\n')
            elif args.verbosity == 2:
                print(json.dumps(drug_info, ensure_ascii=False, indent=2))
    return drugs

# Scrape the specified number of pages
print('Starting scrape...')
all_drugs = []
for i in range(1, args.num_pages + 1):
    drugs = scrape_page(i)
    all_drugs.extend(drugs)
    print(f'Page {i} scraped.')

print('Scraping completed.')

# Save the aggregated data to a JSON file
with open('drugbank_data.json', 'w', encoding='utf-8') as file:
    json.dump(all_drugs, file, ensure_ascii=False, indent=2)

if args.verbosity > 0:
    print('Scraped data has been saved to drugbank_data.json')
