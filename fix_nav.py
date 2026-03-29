import glob, re

script = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('a').forEach(a => {
        let text = a.textContent.trim();
        const icon = a.querySelector('.material-symbols-outlined');
        if (icon) {
            text = text.replace(icon.textContent, '').trim();
        }
        
        let targetHref = null;
        if(text === 'Market Overview' || text === 'Dashboard') targetHref = '../dashboard/index.html';
        else if(text === 'Sector Analysis' || text === 'Radar') targetHref = '../opportunity_radar/index.html';
        else if(text === 'AI Insights') targetHref = '../stock_analysis/index.html';
        else if(text === 'Watchlists' || text === 'Portfolio') targetHref = '../portfolio/index.html';
        else if(text === 'Alerts') targetHref = '../alerts/index.html';
        
        if (targetHref && !a.href.includes(targetHref.replace('../', ''))) {
            a.href = targetHref;
        }
    });
});
</script>
"""

for f in glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove all previous injected navigation scripts
    content = re.sub(r'<script>\s*document.addEventListener[\s\S]*?querySelectorAll\([\s\S]*?</script>', '', content)
    
    content = content.replace('</body>', script + '\n</body>')
        
    with open(f, 'w', encoding='utf-8') as file:
        file.write(content)
print('Fixed navigation injection.')
