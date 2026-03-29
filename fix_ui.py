import glob
import re

ui_fix_script = """
<script>
document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    document.querySelectorAll('nav a').forEach(a => {
        let isMatch = false;
        
        // Normalize text
        let text = a.textContent.trim();
        const icon = a.querySelector('.material-symbols-outlined');
        if (icon) text = text.replace(icon.textContent, '').trim();

        if ((text === 'Market Overview' || text === 'Dashboard') && currentPath.includes('dashboard')) isMatch = true;
        else if ((text === 'Sector Analysis' || text === 'Radar') && currentPath.includes('opportunity_radar')) isMatch = true;
        else if (text === 'AI Insights' && currentPath.includes('stock_analysis')) isMatch = true;
        else if ((text === 'Watchlists' || text === 'Portfolio') && currentPath.includes('portfolio')) isMatch = true;
        else if (text === 'Alerts' && currentPath.includes('alerts')) isMatch = true;

        if (isMatch) {
            // Apply top nav active state
            if (!a.querySelector('.material-symbols-outlined')) {
                a.className = "text-slate-900 dark:text-white font-semibold border-b-2 border-slate-900 dark:border-slate-50 pb-1";
            } 
            // Apply sidebar active state
            else {
                a.className = "flex items-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm rounded-xl font-medium";
            }
        }
    });
});
</script>
"""

for f in glob.glob('c:/et genai/stitch/stitch/**/*.html', recursive=True):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Regularize Top Nav
    content = re.sub(
        r'<a class="text-slate-900 dark:text-white font-semibold border-b-2[^"]*" href="#">(.*?)</a>',
        r'<a class="text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 transition-colors" href="#">\1</a>',
        content
    )
    
    # Regularize Sidebar Nav
    content = re.sub(
        r'<a class="flex items-center gap-3 px-4 py-3 bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm rounded-xl font-medium[^"]*" href="#">',
        r'<a class="flex items-center gap-3 px-4 py-3 text-slate-500 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-800/30 rounded-xl transition-transform hover:translate-x-1" href="#">',
        content
    )
    
    # Add dynamic state fixer
    if "const currentPath = window.location.pathname;" not in content:
        content = content.replace('</body>', ui_fix_script + '\n</body>')
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)

print("Applied UI fixes to all HTML files.")
