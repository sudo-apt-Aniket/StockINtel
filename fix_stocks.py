import glob
import re

for filepath in glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Radar fetch logic update
    content = content.replace("['NVDA', 'AAPL', 'TSLA', 'AMZN', 'MSFT']", "['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ITC']")
    
    # Dashboard fetch logic update
    content = content.replace("['NVDA', 'AMZN', 'AAPL']", "['RELIANCE', 'TCS', 'INFY']")

    # Hardcoded HTML element updates across files
    content = content.replace(">NVDA<", ">RELIANCE<")
    content = content.replace(">$NVDA<", ">$RELIANCE<")
    content = content.replace('"$NVDA"', '"$RELIANCE"')
    content = content.replace("NVIDIA Corporation", "Reliance Industries")
    content = content.replace("NVIDIA", "Reliance")
    content = content.replace("Apple Inc.", "Tata Consultancy Services")
    content = content.replace(">AAPL<", ">TCS<")
    content = content.replace(">AAP<", ">TCS<")
    content = content.replace(">AMZN<", ">INFY<")
    content = content.replace(">MSFT<", ">HDFCBANK<")
    content = content.replace(">TSLA<", ">ITC<")
    content = content.replace("AAPL, BTC", "RELIANCE, TCS")
    content = content.replace("NVDA, AAPL", "RELIANCE, TCS")
    content = content.replace("e.g. AAPL", "e.g. TCS")
    
    # Specific UI text
    content = content.replace("High Volatility: NVDA", "High Volatility: RELIANCE")
    content = content.replace("Adding $NVDA will increase", "Adding $RELIANCE will increase")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Swapped US stocks for Indian stocks in frontend templates.")
