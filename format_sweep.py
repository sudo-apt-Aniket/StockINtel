import glob
import re

files = glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True)

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    # Exchange and timezone contextualization
    new_content = content.replace("NYSE / NASDAQ Active", "NSE / BSE Active")
    new_content = new_content.replace("- NYSE", "- NSE")
    new_content = new_content.replace("- NASDAQ", "- BSE")
    new_content = new_content.replace(" EST ", " IST ")
    
    # Financial symbol adaptation. Replacing $ with ₹
    # Match $ immediately followed by a digit or uppercase letter.
    new_content = re.sub(r'\$(?=[A-Z0-9])', '₹', new_content)
    
    # Update Javascript replacements to handle the new ₹ symbol securely.
    new_content = new_content.replace(".replace('$', '')", ".replace('$', '').replace('₹', '')")
    
    if new_content != content:
        changed = True
        content = new_content
        
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Swept all files for currency formatting, timezones, and JavaScript cleanup.")
