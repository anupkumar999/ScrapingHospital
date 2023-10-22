import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re

# Define the URL you want to scrape (Newsweek's World's Best Hospitals)
newsweek_url = 'https://www.newsweek.com/rankings/worlds-best-hospitals-2023'

# Define the User-Agent header to mimic a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
}

# Function to remove HTML tags and symbols from text
def clean_html_tags(text):
    clean = re.compile('<.*?>')
    text = re.sub(clean, '', text)  # Remove HTML tags
    text = re.sub(r'\n+', ' ', text)  # Remove line gaps
    text = re.sub(r'\s+', ' ', text)  # Remove extra spaces
    return text

# Function to scrape, clean, and display hospital data
def scrape_clean_and_display_hospital_data():
    # Send an HTTP GET request to the Newsweek URL
    newsweek_response = requests.get(newsweek_url, headers=headers)

    # Check if the request to Newsweek was successful
    if newsweek_response.status_code == 200:
        # Parse the HTML content of the Newsweek page using BeautifulSoup
        newsweek_soup = BeautifulSoup(newsweek_response.text, 'html.parser')

        # Find the table element with the specified class
        table = newsweek_soup.find('table', class_='ranking-table')

        # Extract rows from the table
        rows = table.find_all('tr')

        # Initialize counters to skip the 9th and 27th links
        link_counter = 0

        # List to store scraped data
        scraped_data = []

        # Initialize variables to store the current hospital data
        current_hospital_data = {
            "p_tags": [],
            "h1_tags": [],
            "h2_tags": [],
            "h3_tags": [],
            "div_tags": [],
        }
        current_hospital_name = ""
        current_hospital_rank = ""

        # Loop through the rows and scrape content from the top 50 hospitals with links
        for row in rows[1:51]:  # Skip the header row and limit to the top 50 hospitals
            columns = row.find_all('td')
            rank = columns[0].get_text(strip=True)
            publication_name = columns[1].find('a').get_text(strip=True)
            country = columns[2].get_text(strip=True)
            city = columns[3].get_text(strip=True)
            state = columns[4].get_text(strip=True)
            link = columns[1].find('a')['href']

            # Increment the link counter
            link_counter += 1

            # Skip the 9th and 27th links and continue to the next link
            if link_counter == 9 or link_counter == 27:
                continue

            # Introduce a delay before sending the request to the hospital's link
            time.sleep(2)  # Wait for 2 seconds (adjust the delay as needed)

            # Send an HTTP GET request to the hospital's link
            hospital_response = requests.get(link, headers=headers)

            # Check if the request to the hospital's link was successful
            if hospital_response.status_code == 200:
                # Parse the HTML content of the hospital's page using BeautifulSoup
                hospital_soup = BeautifulSoup(hospital_response.text, 'html.parser')

                # Extract and clean content from p, h1, h2, h3, and div tags
                p_tags = [clean_html_tags(tag.get_text()) for tag in hospital_soup.find_all('p')]
                h1_tags = [clean_html_tags(tag.get_text()) for tag in hospital_soup.find_all('h1')]
                h2_tags = [clean_html_tags(tag.get_text()) for tag in hospital_soup.find_all('h2')]
                h3_tags = [clean_html_tags(tag.get_text()) for tag in hospital_soup.find_all('h3')]
                div_tags = [clean_html_tags(tag.get_text()) for tag in hospital_soup.find_all('div')]

                # Store the cleaned data in the current hospital data dictionary
                current_hospital_data["p_tags"] = p_tags
                current_hospital_data["h1_tags"] = h1_tags
                current_hospital_data["h2_tags"] = h2_tags
                current_hospital_data["h3_tags"] = h3_tags
                current_hospital_data["div_tags"] = div_tags

                # Store the current hospital name and rank
                current_hospital_name = publication_name
                current_hospital_rank = rank

                # Clean and display the data for this hospital
                print(f"Hospital Rank: {current_hospital_rank}")
                print(f"Hospital Name: {current_hospital_name}")
                print("=== Paragraphs ===")
                for p_tag in p_tags:
                    print(p_tag)
                print("=== H1 Tags ===")
                for h1_tag in h1_tags:
                    print(h1_tag)
                print("=== H2 Tags ===")
                for h2_tag in h2_tags:
                    print(h2_tag)
                print("=== H3 Tags ===")
                for h3_tag in h3_tags:
                    print(h3_tag)
                print("=== Div Tags ===")
                for div_tag in div_tags:
                    print(div_tag)
                print("====================")

            else:
                print(f"Failed to retrieve data from Hospital {rank}. Status code: {hospital_response.status_code}")

            # Append the current hospital data to the list
            scraped_data.append({
                "Hospital Rank": current_hospital_rank,
                "Hospital Name": current_hospital_name,
                **current_hospital_data
            })

        return scraped_data

    else:
        print(f"Failed to retrieve the Newsweek page. Status code: {newsweek_response.status_code}")

# Function to remove duplicate lines from a list of strings
def remove_duplicates(lines):
    unique_lines = []
    seen_lines = set()
    for line in lines:
        if line not in seen_lines:
            unique_lines.append(line)
            seen_lines.add(line)
    return unique_lines

# Function to save cleaned data to a CSV file
def save_data_to_csv(data, output_csv):
    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"Data has been saved to {output_csv}")

# Main program
if __name__ == "__main__":
    # Scrape, clean, and display hospital data
    scraped_data = scrape_clean_and_display_hospital_data()

    # Remove duplicate lines within each section
    for data in scraped_data:
        data['p_tags'] = remove_duplicates(data['p_tags'])
        data['h1_tags'] = remove_duplicates(data['h1_tags'])
        data['h2_tags'] = remove_duplicates(data['h2_tags'])
        data['h3_tags'] = remove_duplicates(data['h3_tags'])
        data['div_tags'] = remove_duplicates(data['div_tags'])

    # Save the cleaned data to a CSV file
    output_csv = 'cleaned_hospital_data2.csv'
    save_data_to_csv(scraped_data, output_csv)
