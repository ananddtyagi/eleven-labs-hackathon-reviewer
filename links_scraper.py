import requests
from bs4 import BeautifulSoup
import re

def scrape_devpost_links(url, i, output_file='devpost_links.txt'):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses

        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the div with id "submission-gallery"
        submission_gallery = soup.find('div', id='submission-gallery')

        if not submission_gallery:
            print("No submission gallery found.")
            return

        # Find all 'a' tags with href starting with "https://devpost.com/"
        links = submission_gallery.find_all('a', href=re.compile(r'^https://devpost\.com/'))

        # Extract the href attribute from each link
        devpost_links = [link['href'] for link in links]

        # Write the links to a file
        with open(output_file + str(i) + '.txt', 'w') as file:
            for link in devpost_links:
                file.write(link + '\n')

        print(f"Collected {len(devpost_links)} links and stored in {output_file}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    url_base = "https://elevenlabs-worldwide-hackathon.devpost.com/submissions/search?filter%5Blocation%5D%5B%5D=online%2Fvirtual"
    for i in range(8):
        url = url_base + "&page=" + str(i+1)
        scrape_devpost_links(url,i )
