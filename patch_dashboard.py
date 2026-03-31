content = open('c:/et genai/frontend/src/pages/Dashboard.jsx', 'r', encoding='utf-8').read()
idx = content.find('unsplash')
if idx < 0:
    print('Not found')
else:
    start = content.rfind('<img', 0, idx)
    end = content.find('/>', idx) + 2
    old_block = content[start:end]
    print('OLD:', repr(old_block))
    new_block = '''<img 
                        alt="Market Chart" 
                        className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" 
                        src="/assets/chart.png"
                        style={{ filter: 'brightness(0.7) saturate(1.3)' }}
                    />'''
    new_content = content[:start] + new_block + content[end:]
    open('c:/et genai/frontend/src/pages/Dashboard.jsx', 'w', encoding='utf-8').write(new_content)
    print('Done!')
