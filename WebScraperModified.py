import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import re
import threading
import csv

window = tk.Tk()
console_output = scrolledtext.ScrolledText(window, width=100, height=100)

def fetch_data(url_entry, item_entry):
    url = url_entry.get()
    product = item_entry.get()
    response = requests.get(url)
    # Clear console_output if it's not empty
    if console_output.get(1.0, tk.END) != '\n':
        console_output.delete(1.0, tk.END)
        
    console_output.insert(tk.END, f"Fetching data from URL: {url}\n")
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if the file already exists
        file_path = "soup_content.html"
        if not os.path.exists(file_path):
            # Saving soup content into a file
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(str(soup))
    
        pagination = soup.find('nav', class_='woocommerce-pagination')
        if pagination:
            page_urls = set(a['href'] for a in pagination.find_all('a', class_='page-numbers'))
            thread = threading.Thread(target=parse_image_urls, args=(page_urls, product))
            thread.start()
        else:
            console_output.insert(tk.END, "Pagination not found.\n")
    else:
        console_output.insert(tk.END, f"Failed to fetch data from URL: {url}. Status code: {response.status_code}\n")


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and any(parsed.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])

def download_images_titles(product_items, url_list, page_no, product, output_dir):
    child_folder = f'{product}\page{page_no}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        console_output.insert(tk.END, f"Directory created for {product}.\n")
    
    child_folder_path = os.path.join(output_dir, child_folder)
    if not os.path.exists(child_folder_path):
        os.makedirs(child_folder_path)
        console_output.insert(tk.END, f"Sub Directory created for {child_folder_path}.\n")
    else:
        console_output.insert(tk.END, f"{child_folder_path} directory already exists, Switching to next page of product: {product}.\n")
        return

    with open(os.path.join(child_folder_path, f"page{page_no}_titles.csv"), 'w', newline='', encoding='utf-8') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Image URL', 'Entry Title'])
        console_output.insert(tk.END, "Product items list CSV File created successfully.\n")

        for idx, item in enumerate(product_items, 1):
            console_output.insert(tk.END, f"Downloading image {idx} of {len(url_list)}\n")
            entry_title_tag = item.find('h3', class_='entry-title')
            if entry_title_tag:
                entry_title = entry_title_tag.get_text(strip=True)
            else:
                entry_title = None
            try:
                url = item.find('img')['src']
                if is_valid(url):
                    response = requests.get(url, stream=True)
                    if response.status_code == 200:
                        with open(os.path.join(child_folder_path, f"{entry_title}.jpg"), 'wb') as f:
                            for chunk in response.iter_content(1024):
                                f.write(chunk)
                        
                        csv_writer.writerow([url, entry_title])
                                
                    else:
                        console_output.insert(tk.END, f"Failed to download image {idx}. Status code: {response.status_code}\n")
                else:
                    console_output.insert(tk.END, f"Skipping invalid image URL: {url}\n")
            except Exception as e:
                console_output.insert(tk.END, f"Error downloading image {idx}: {e}\n")

def parse_image_urls(page_url, product):
    for link in page_url:
        console_output.insert(tk.END, "*******************************************************************\n")
    
        response = requests.get(link)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        product_items = soup.find_all('div', class_='product_list_item')


        img_urls = [img['src'] for item in soup.find_all('div', class_='product_list_item') for img in item.find_all('img', src=True)]
        page_number = int(re.search(r'\d+', link).group())
        
        console_output.insert(tk.END, f"Downloading Images of page{page_number}: {link}\n")
        print(f"Downloading Images of page{page_number}: {link}\n")

        download_images_titles(product_items, img_urls, page_number, product, 'pics')
    
    console_output.insert(tk.END, f"Image scraping for {product} has been completed successfully.\n")
    print(f"Image scraping for {product} has been completed successfully.\n")
    directory_path = f'pics\{product}'
    directories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    console_output.insert(tk.END, f"List of subdirectories in 'Pics\{product}' directory: {directories}\n")
    console_output.insert(tk.END, "*******************************************************************\n")

def main():
    window.title("Web Scraper Interface")

    url_label = tk.Label(window, text="Enter URL to fetch the data:")
    url_label.pack()
    url_entry = tk.Entry(window, width=100)
    url_entry.pack()
    item_label = tk.Label(window, text="Enter the type of items to create a directory:")
    item_label.pack()
    item_entry = tk.Entry(window, width=40)
    item_entry.pack()

    fetch_button = tk.Button(window, text="Fetch Data", command=lambda: fetch_data(url_entry, item_entry))
    fetch_button.pack()

    console_output.pack()

    window.mainloop()
    
if __name__ == "__main__":
    main()
