import tkinter as tk
from tkinter import scrolledtext
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os
import re

window = tk.Tk()
console_output = scrolledtext.ScrolledText(window, width=100, height=100)

def fetch_data(url_entry, item_entry, console_output):
    url = url_entry.get()
    product = item_entry.get()
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    pagination = soup.find('nav', class_='woocommerce-pagination')
    console_output.insert(tk.END, f"Fetching data from URL: {url}\n")
    if pagination:
        page_urls = set(a['href'] for a in pagination.find_all('a', class_='page-numbers'))
        parse_image_urls(page_urls, product, console_output)
    else:
        console_output.insert(tk.END, "Pagination not found.\n")

def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and any(parsed.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])

def download_images_Titles(product_items, url_list, page_no, console, product, output_dir):
    child_folder = f'{product}\page{page_no}'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        console.insert(tk.END, f"Directory created for {product}.\n")
    
    child_folder_path = os.path.join(output_dir, child_folder)
    if not os.path.exists(child_folder_path):
        os.makedirs(child_folder_path)
        console.insert(tk.END, f"Sub Directory created for {child_folder_path}.\n")
    else:
        console.insert(tk.END, f"Directory already exists, Switching to next product items page: {output_dir}.\n")
        return

    for idx, item in enumerate(product_items, 1):
        print(f"Downloading image {idx} of {len(url_list)}")
        console.insert(tk.END, f"Downloading image {idx} of {len(url_list)}")
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
                    
                    with open(os.path.join(child_folder_path, f"page{page_no}_titles.txt"), 'a') as titles_file:
                            titles_file.write(f"Product {idx} - Image URL: {url}, Entry Title: {entry_title}\n")
                    console.insert(tk.END, "Product items list created successfully.\n")
                            
                else:
                    console.insert(tk.END, f"Failed to download image {idx}. Status code: {response.status_code}\n")
                    print(f"Failed to download image {idx}. Status code: {response.status_code}\n")
            else:
                console.insert(tk.END, f"Skipping invalid image URL: {url}\n")
                print(f"Skipping invalid image URL: {url}\n")
        except Exception as e:
            console.insert(tk.END, f"Error downloading image {idx}: {e}\n")
            print(f"Error downloading image {idx}: {e}\n")
    console.insert(tk.END, "Web scraping process has been completed for {product}. You can check all the images downloaded in your local folder. If any images are missing, please provide the link to a different page of the same product.")
    print("Web scraping process has been completed.")


def parse_image_urls(page_url, product, output):
    count = 1
    for link in page_url:
        output.insert(tk.END, "*************************************************\n")
        output.insert(tk.END, f"Downloading Images of page{count}: {link}\n")
        print(f"Downloading Images of page{count}: ", link)
        response = requests.get(link)

        soup = BeautifulSoup(response.text, 'html.parser')
        
        product_items = soup.find_all('div', class_='product_list_item')


        img_urls = [img['src'] for item in soup.find_all('div', class_='product_list_item') for img in item.find_all('img', src=True)]
        page_number = int(re.search(r'\d+', link).group())

        download_images_Titles(product_items, img_urls, page_number, output, product, 'pics')
        count += 1

def main():
    window.title("Web Scraper Widget")

    url_label = tk.Label(window, text="Enter URL:")
    url_label.pack()
    url_entry = tk.Entry(window, width=100)
    url_entry.pack()
    item_label = tk.Label(window, text="Enter the type of items to create a directory:")
    item_label.pack()
    item_entry = tk.Entry(window, width=40)
    item_entry.pack()

    fetch_button = tk.Button(window, text="Fetch Data", command=lambda: fetch_data(url_entry, item_entry, console_output))
    fetch_button.pack()

    console_output.pack()

    window.mainloop()
    
if __name__ == "__main__":
    main()
