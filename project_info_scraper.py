import requests
from bs4 import BeautifulSoup
import time
import os

def scrape_project_info():
    # Create output directory if it doesn't exist
    if not os.path.exists('project_details'):
        os.makedirs('project_details')

    # Read links from file
    with open('links.txt', 'r') as f:
        links = f.read().splitlines()

    # Process each link
    for link in links:
        try:
            # Extract project name from URL
            project_name = link.split('/')[-1]
            output_file = f'project_details/{project_name}.txt'

            # Skip if already processed
            if os.path.exists(output_file):
                print(f"Skipping {project_name} - already processed")
                continue

            # Fetch page content
            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find the app-details-left div
            details_div = soup.find('div', id='app-details-left')
            
            if details_div:
                # Get the second div within app-details-left
                divs = details_div.find_all('div', recursive=False)
                if len(divs) >= 2:
                    # Get the HTML content instead of text
                    content = str(divs[1])
                    
                    # Save to file
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"Successfully processed {project_name}")
                else:
                    print(f"Could not find second div for {project_name}")
            else:
                print(f"Could not find app-details-left for {project_name}")

            # Add a small delay to be nice to the server
            time.sleep(1)

        except Exception as e:
            print(f"Error processing {link}: {str(e)}")

if __name__ == "__main__":
    scrape_project_info()