import requests
from bs4 import BeautifulSoup
import os



url = 'url/to/get/data'


response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

product_items = soup.find_all('div', class_='product_list_item')

def extract_img_titles(product_items, page_no, output_dir):
    child_folder = f'Noodles\page{page_no}'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    child_folder_path = os.path.join(output_dir, child_folder)
    if not os.path.exists(child_folder_path):
        os.makedirs(child_folder_path)
    else:
        return
        
    for idx, item in enumerate(product_items, 1):
        try:
            image_url = item.find('img')['src']
        except (TypeError, KeyError):
            image_url = None
        
        entry_title_tag = item.find('h3', class_='entry-title')
        if entry_title_tag:
            entry_title = entry_title_tag.get_text(strip=True)
        else:
            entry_title = None
            
        with open(os.path.join(child_folder_path, f"page10_titles.txt"), 'a') as titles_file:
                            titles_file.write(f"Product {idx} - Image URL: {image_url}, Entry Title: {entry_title}\n")
        
extract_img_titles(product_items, 'pics')