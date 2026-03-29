import glob

files = glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True)

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False

    new_content = content.replace("Blackwell architecture", "5G rollout and retail infrastructure expansion")
    new_content = new_content.replace("H200 chips", "Jio subscriber additions")
    new_content = new_content.replace("Data center revenue projected +22% QoQ.", "Digital services revenue projected +22% QoQ.")
    new_content = new_content.replace("Supply chain easing for", "Network density improving for")
    
    if new_content != content:
        changed = True
        content = new_content
        
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Swept hardcoded narrative paragraphs.")
