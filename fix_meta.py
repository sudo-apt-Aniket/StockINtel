import glob
import re

files = glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True)

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Fix the meta tag catastrophe
    new_content = re.sub(r'<bhartiartl(.*?)/?>', r'<meta\1>', content, flags=re.IGNORECASE)
    
    if new_content != content:
        changed = True
        content = new_content
        
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Fixed broken meta tags.")
