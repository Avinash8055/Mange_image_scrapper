import os
import time
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Function to search for a manga and get its link
def search_manga(manga_name):
    # Construct the search URL
    search_url = f"PROVIDE_THE_APPROPRIATE_SEARCH_URL_HERE/{manga_name.replace(' ', '_')}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # Send request to the search page
    response = requests.get(search_url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")

        # Locate the search results container
        search_results = soup.find_all("div", class_="search-story-item")

        # Check if there are results
        if search_results:
            # Get the first result and extract the link
            first_result = search_results[0]
            manga_link = first_result.find("a", href=True)["href"]
            print(f"Found manga URL: {manga_link}")
            return manga_link
        else:
            print("No results found for the given manga name.")
            return None
    else:
        print(f"Failed to fetch search page. Status code: {response.status_code}")
        return None

# Function to download images from the manga page
def download_manga_images(manga_url, start_chapter, end_chapter):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': 'PROVIDE_THE_APPROPRIATE_REFERER_URL_HERE'
    }

    response = requests.get(manga_url, headers=headers)

    if response.status_code == 200:
        print("Manga page successfully fetched!")
        soup = BeautifulSoup(response.content, "html.parser")
        body_site_div = soup.find("div", class_="body-site")
        container_main_div = body_site_div.find("div", class_="container-main")
        main_left_div = container_main_div.find("div", class_="container-main-left")
        chapter_list_div = main_left_div.find("div", class_="panel-story-chapter-list")
        chapter_links = chapter_list_div.find("ul", class_="row-content-chapter").find_all("a")

        # Reverse the chapter list to start from the first chapter
        chapter_links = chapter_links[::-1]
        total_chapters = len(chapter_links)
        print(f"Total chapters found: {total_chapters}")

        if start_chapter < 1 or end_chapter > total_chapters or start_chapter > end_chapter:
            print("Invalid chapter range. Please try again.")
            return

        # Create a folder to save images
        output_folder = "manga_images"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        for idx in range(start_chapter - 1, end_chapter):
            chapter_link = chapter_links[idx]
            chapter_url = chapter_link.get("href")
            if chapter_url:
                print(f"Processing Chapter {idx + 1} - URL: {chapter_url}")
                chapter_response = requests.get(chapter_url, headers=headers)

                if chapter_response.status_code == 200:
                    chapter_soup = BeautifulSoup(chapter_response.content, "html.parser")
                    container_reader_div = chapter_soup.find("div", class_="container-chapter-reader")
                    image_tags = container_reader_div.find_all("img")

                    for img_idx, img_tag in enumerate(image_tags, start=1):
                        img_url = img_tag.get("src")
                        if img_url:
                            try:
                                img_response = requests.get(img_url, headers=headers)
                                img_response.raise_for_status()  # Raise an error for failed requests

                                # Save the image
                                img = Image.open(BytesIO(img_response.content))
                                img_format = img.format.lower()
                                img_filename = os.path.join(output_folder, f"chapter_{idx + 1}_page_{img_idx}.{img_format}")
                                img.save(img_filename)
                                print(f"Saved image {img_filename}")

                                # Optional: Add a delay to avoid server blocks
                                time.sleep(1)

                            except Exception as e:
                                print(f"Failed to save image {img_url}: {e}")
    else:
        print(f"Failed to fetch the manga page. Status code: {response.status_code}")

# Main function to get user input and start the process
def main():
    manga_name = input("Enter the name of the manga: ")
    manga_url = search_manga(manga_name)
    if manga_url:
        start_chapter = int(input("Enter the start chapter number (1-based index): "))
        end_chapter = int(input("Enter the end chapter number: "))
        download_manga_images(manga_url, start_chapter, end_chapter)
    else:
        print("Manga not found.")

if __name__ == "__main__":
    main()
