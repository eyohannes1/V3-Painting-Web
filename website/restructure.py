import os
import shutil
import re

base_dir = r"b:\AI Automation\Website\Clients\V3 Painting\website"
code_dir = os.path.join(base_dir, "code")
images_dir = os.path.join(base_dir, "images")
assets_dir = os.path.join(base_dir, "assets")

assets_images = os.path.join(assets_dir, "images")
assets_css = os.path.join(assets_dir, "css")
assets_js = os.path.join(assets_dir, "js")

# Create directories
os.makedirs(assets_images, exist_ok=True)
os.makedirs(assets_css, exist_ok=True)
os.makedirs(assets_js, exist_ok=True)

# Move images
if os.path.exists(images_dir):
    for f in os.listdir(images_dir):
        shutil.move(os.path.join(images_dir, f), os.path.join(assets_images, f))
    os.rmdir(images_dir)

# Move JS and CSS
if os.path.exists(code_dir):
    for f in os.listdir(code_dir):
        if f.endswith('.js'):
            shutil.move(os.path.join(code_dir, f), os.path.join(assets_js, f))
        elif f.endswith('.css'):
            shutil.move(os.path.join(code_dir, f), os.path.join(assets_css, f))

# Move index.html to root
index_path = os.path.join(code_dir, "index.html")
new_index_path = os.path.join(base_dir, "index.html")
if os.path.exists(index_path):
    shutil.move(index_path, new_index_path)

# Update index.html paths
if os.path.exists(new_index_path):
    with open(new_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the bad image replace from earlier
    content = content.replace("../images.squarespace-cdn.com", "https://images.squarespace-cdn.com")
    
    # Update local paths
    content = content.replace('src="', 'src="assets/js/')
    content = content.replace('href="', 'href="assets/css/')
    
    # However, we only want to replace local JS and CSS, not http links!
    # Let's use regex for safer replacement.
    pass # we'll do this in memory

def fix_paths(html_content):
    # Fix broken srcset
    html_content = html_content.replace("../images.squarespace-cdn.com", "https://images.squarespace-cdn.com")
    
    # Fix image data-src and src
    html_content = html_content.replace('data-src="../images/', 'data-src="assets/images/')
    html_content = html_content.replace('src="../images/', 'src="assets/images/')
    
    # Fix scripts (local)
    html_content = re.sub(r'src="([^:"]+\.js)"', r'src="assets/js/\1"', html_content)
    # Fix css (local)
    html_content = re.sub(r'href="([^:"]+\.css)"', r'href="assets/css/\1"', html_content)
    
    return html_content

if os.path.exists(new_index_path):
    with open(new_index_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = fix_paths(content)
    with open(new_index_path, 'w', encoding='utf-8') as f:
        f.write(content)

# Remove code dir if empty
if os.path.exists(code_dir) and not os.listdir(code_dir):
    os.rmdir(code_dir)

print("Restructure complete!")
