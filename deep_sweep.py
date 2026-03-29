import glob
import re
import os

files = glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True)

# Extended mapping to remove ALL western/US specific tech ticker placeholders entirely
replacements = {
    r'\$NVDA': '$RELIANCE',
    r'NVDA': 'RELIANCE',
    r'NVIDIA Corporation': 'Reliance Industries',
    r'NVIDIA Corp': 'Reliance Industries',
    r'NVIDIA': 'Reliance',
    r'\$AAPL': '$TCS',
    r'AAPL': 'TCS',
    r'Apple Inc\.': 'Tata Consultancy Services',
    r'\$MSFT': '$HDFCBANK',
    r'MSFT': 'HDFCBANK',
    r'Microsoft Corp\.': 'HDFC Bank',
    r'\$TSLA': '$ITC',
    r'TSLA': 'ITC',
    r'Tesla, Inc\.': 'ITC Limited',
    r'Tesla': 'ITC',
    r'\$AMZN': '$INFY',
    r'AMZN': 'INFY',
    r'Amazon\.com, Inc\.': 'Infosys Limited',
    r'BTC': 'SBIN',
    r'GOOGL': 'ICICIBANK',
    r'META': 'BHARTIARTL',
    r'BABA': 'WIPRO',
    r'AMD': 'MARUTI',
    r'TSM': 'LT',
    r'S&amp;P 500': 'NIFTY 50',
    r'S&P 500': 'NIFTY 50',
    r'Tech Exposure': 'IT Sector Exposure',
}

for filepath in files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    changed = False
    for k, v in replacements.items():
        new_content = re.sub(k, v, content, flags=re.IGNORECASE)
        if new_content != content:
            changed = True
            content = new_content
            
    # Also fix any bad array strings if there are any remaining
    content = content.replace("['RELIANCE', 'TCS', 'ITC', 'INFY', 'HDFCBANK']", "['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ITC']")
    
    if changed:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

print("Swept all files for foreign tickers/placeholders and replaced with Indian domestic contextualized values.")
