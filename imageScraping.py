import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

url = 'Url/to/fetch_data'


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme) and any(parsed.path.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif'])

def download_images(url_list, output_dir):
    child_folder = f'Bevande\page'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    child_folder_path = os.path.join(output_dir, child_folder)
    if not os.path.exists(child_folder_path):
        os.makedirs(child_folder_path)
    else:
        return

    for idx, url in enumerate(img_urls, 1):
        print(f"Downloading image {idx} of {len(url_list)}")
        try:
            if is_valid(url):
                response = requests.get(url, stream=True)
                if response.status_code == 200:
                    with open(os.path.join(child_folder_path, f"picture{idx}.jpg"), 'wb') as f:
                        for chunk in response.iter_content(1024):
                            f.write(chunk)          
                else:
                    print(f"Failed to download image {idx}. Status code: {response.status_code}")
            else:
                print(f"Skipping invalid image URL: {url}")
        except Exception as e:
            print(f"Error downloading image {idx}: {e}")

    
response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

img_urls = [img['src'] for item in soup.find_all('div', class_='product_list_item') for img in item.find_all('img', src=True)]
download_images(img_urls, 'pics')
