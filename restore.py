import os

def insert_script(filepath, script_content):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'DYNAMIC_DATA_FETCH' not in content:
        content = content.replace('</body>', script_content + '\n</body>')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# Opportunity Radar Data Source
script_radar = """
<script>
// DYNAMIC_DATA_FETCH
document.addEventListener('DOMContentLoaded', async () => {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" class="px-8 py-6 text-center text-sm">Loading latest radar signals...</td></tr>';
    try {
        const res = await fetch('http://localhost:8000/radar', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ symbols: ['NVDA', 'AAPL', 'TSLA', 'AMZN', 'MSFT'] })
        });
        const data = await res.json();
        tbody.innerHTML = '';
        if (data.results) {
            data.results.forEach(item => {
                let colorClass = 'text-outline';
                let iconText = 'horizontal_rule';
                let badgeClass = 'bg-surface-container-high text-on-surface-variant';
                
                if (item.signal.includes('bull')) {
                    colorClass = 'text-secondary';
                    iconText = 'arrow_upward';
                    badgeClass = 'bg-secondary-container text-on-secondary-container';
                } else if (item.signal.includes('bear')) {
                    colorClass = 'text-error';
                    iconText = 'arrow_downward';
                    badgeClass = 'bg-error-container text-on-error-container';
                }
                const confPercent = (item.confidence * 100).toFixed(1);
                
                const tr = document.createElement('tr');
                tr.className = "hover:bg-surface-container-low/30 transition-colors group cursor-pointer";
                tr.onclick = () => window.location.href = '../stock_analysis/index.html?symbol=' + item.symbol;
                tr.innerHTML = `
                <td class="px-8 py-6">
                    <div class="flex items-center gap-4">
                        <div class="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center text-white font-bold text-xs">${item.symbol}</div>
                        <div>
                            <p class="font-bold text-sm tracking-tight">${item.symbol} Corp</p>
                            <p class="text-[10px] text-outline uppercase font-semibold">Asset</p>
                        </div>
                    </div>
                </td>
                <td class="px-8 py-6">
                    <div class="flex items-center gap-2">
                        <span class="material-symbols-outlined ${colorClass} text-lg">${iconText}</span>
                        <span class="text-sm font-semibold ${colorClass}">${item.signal}</span>
                    </div>
                </td>
                <td class="px-8 py-6">
                    <div class="flex flex-col gap-1.5">
                        <span class="text-sm font-bold">${confPercent}%</span>
                        <div class="w-32 h-1 bg-surface-container-low rounded-full">
                            <div class="h-full bg-primary/40 rounded-full" style="width: ${confPercent}%"></div>
                        </div>
                    </div>
                </td>
                <td class="px-8 py-6">
                    <span class="px-4 py-1.5 rounded-full ${badgeClass} text-[11px] font-extrabold tracking-widest uppercase">${item.action}</span>
                </td>
                <td class="px-8 py-6 text-right">
                    <button class="opacity-0 group-hover:opacity-100 transition-opacity bg-primary text-on-primary text-[10px] font-bold px-4 py-2 rounded-lg">VIEW</button>
                </td>`;
                tbody.appendChild(tr);
            });
        }
    } catch(err) {
        tbody.innerHTML = '<tr><td colspan="5" class="px-8 py-6 text-center text-sm text-error">Failed to load radar signals. Is backend running?</td></tr>';
    }
});
</script>
"""

# Portfolio Data Source
script_portfolio = """
<script>
// DYNAMIC_DATA_FETCH
document.addEventListener('DOMContentLoaded', async () => {
    // Attempt to locate the 'Saved Portfolios' area
    const headers = Array.from(document.querySelectorAll('h2'));
        
    const portfoliosHeader = headers.find(h => h.textContent.includes('Saved Portfolios'));
    if (!portfoliosHeader) return;
    const container = portfoliosHeader.parentElement;
    
    // Clear out the hardcoded ones and leave the header
    container.innerHTML = '<h2 class="text-lg font-semibold text-on-surface px-2">Saved Portfolios</h2><p class="text-sm text-center py-4 text-outline">Loading portfolios...</p>';
    
    try {
        const res = await fetch('http://localhost:8000/portfolio');
        const data = await res.json();
        
        container.innerHTML = '<h2 class="text-lg font-semibold text-on-surface px-2">Saved Portfolios</h2>';
        if (data && data.length > 0) {
            data.forEach((p, i) => {
                const icon = i % 2 === 0 ? 'trending_up' : 'shield';
                const bgClass = i % 2 === 0 ? 'bg-secondary-container text-on-secondary-container' : 'bg-surface-container text-slate-400';
                const d = new Date(p.updated_at).toLocaleDateString();
                
                container.innerHTML += `
                <div class="group bg-surface-container-lowest p-6 rounded-xl hover:bg-surface-container transition-all cursor-pointer">
                <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div class="flex items-center gap-4">
                <div class="w-12 h-12 rounded-full ${bgClass} flex items-center justify-center">
                <span class="material-symbols-outlined">${icon}</span>
                </div>
                <div>
                <h3 class="font-bold text-slate-900">${p.name}</h3>
                <p class="text-xs text-slate-500">${p.symbols.length} Symbols • Updated ${d}</p>
                <p class="text-xs mt-1 text-slate-400">${p.symbols.join(', ')}</p>
                </div>
                </div>
                <div class="flex items-center gap-8">
                <button class="opacity-0 group-hover:opacity-100 px-4 py-2 bg-primary text-white text-xs font-bold rounded-lg" onclick="window.location.href='../opportunity_radar/index.html'">Scan Radar</button>
                <span class="material-symbols-outlined text-slate-300 group-hover:text-primary transition-colors">chevron_right</span>
                </div>
                </div>
                </div>
                `;
            });
        }
        
        container.innerHTML += `
        <div class="group bg-surface-container-lowest p-6 rounded-xl hover:bg-surface-container transition-all cursor-pointer border-2 border-dashed border-outline-variant/30 flex items-center justify-center py-10">
        <div class="text-center space-y-2">
        <span class="material-symbols-outlined text-3xl text-outline-variant">folder_zip</span>
        <div class="text-sm font-medium text-outline">Import from Brokerage</div>
        </div>
        </div>`;
    } catch(err) {
        container.innerHTML = '<h2 class="text-lg font-semibold text-on-surface px-2">Saved Portfolios</h2><p class="text-sm py-4 text-error">Failed to load.</p>';
    }
});
</script>
"""

# Alerts Data Source
script_alerts = """
<script>
// DYNAMIC_DATA_FETCH
document.addEventListener('DOMContentLoaded', async () => {
    const listParent = document.querySelector('p.text-on-surface-variant.mb-6').parentElement;
    const itemsContainer = document.createElement('div');
    itemsContainer.className = 'space-y-4';
    
    // Clear the hardcoded alerts
    const toRemove = Array.from(listParent.children).filter(el => el.tagName !== 'H4' && el.tagName !== 'P');
    toRemove.forEach(el => listParent.removeChild(el));
    listParent.appendChild(itemsContainer);
    
    itemsContainer.innerHTML = '<p class="text-sm text-outline">Loading alerts...</p>';
    
    try {
        const res = await fetch('http://localhost:8000/alerts');
        const data = await res.json();
        
        itemsContainer.innerHTML = '';
        if (data && data.length > 0) {
            data.forEach(item => {
                const isAck = item.status === 'acknowledged';
                const opacity = isAck ? 'opacity-60' : '';
                const btnStatusText = isAck ? 'Open' : 'Acknowledge';
                const updateTo = isAck ? 'open' : 'acknowledged';
                
                itemsContainer.innerHTML += `
                <div class="bg-surface-container-lowest p-6 rounded-xl shadow-sm flex flex-col md:flex-row gap-6 hover:shadow-md transition-shadow ${opacity}">
                    <div class="flex-1 space-y-3">
                        <div class="flex items-center gap-3">
                            <span class="px-3 py-1 bg-surface-container-high rounded-md text-xs font-bold">${item.symbol}</span>
                            <span class="text-xs font-bold uppercase tracking-widest text-outline">${new Date(item.created_at).toLocaleDateString()}</span>
                        </div>
                        <h3 class="font-bold text-lg">${item.alert}</h3>
                        <p class="text-sm text-on-surface-variant">${item.recommendation}</p>
                    </div>
                    <div class="flex flex-col gap-2 min-w-[140px] border-t md:border-t-0 md:border-l border-surface-container-low pt-4 md:pt-0 md:pl-6">
                        <button onclick="updateStatus(${item.alert_id}, '${updateTo}')" class="w-full py-2 bg-surface-container-high hover:bg-surface-container-highest text-on-surface font-semibold text-xs rounded-lg transition-colors border border-outline-variant/20">Mark ${btnStatusText}</button>
                        <button onclick="updateStatus(${item.alert_id}, 'closed')" class="w-full py-2 text-error hover:bg-error-container/50 font-semibold text-xs rounded-lg transition-colors">Close / Delete</button>
                    </div>
                </div>`;
            });
        } else {
            itemsContainer.innerHTML = '<p class="text-sm text-outline">No alerts open.</p>';
        }
    } catch(err) {}
});

async function updateStatus(id, newStatus) {
    try {
        await fetch('http://localhost:8000/alerts/' + id, {
            method: 'PATCH',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status: newStatus})
        });
        window.location.reload();
    } catch(err) { alert('Failed to update status'); }
}
</script>
"""

# Dashboard Integration Source (which the agent incorrectly marked as "loaded" because of hardcodes)
script_dashboard = """
<script>
// DYNAMIC_DATA_FETCH
document.addEventListener('DOMContentLoaded', async () => {
    // Quick analyze button
    const qInput = document.querySelector('header input');
    const qBtn = document.querySelector('header button');
    function doAnalyze() {
        if(qInput.value.trim()) window.location.href = '../stock_analysis/index.html?symbol=' + encodeURIComponent(qInput.value.trim());
    }
    if (qBtn) qBtn.onclick = doAnalyze;
    if (qInput) qInput.addEventListener('keypress', e => { if(e.key==='Enter') doAnalyze(); });

    // Recent Analyses
    const rcContainer = Array.from(document.querySelectorAll('h2')).find(h => h.textContent.includes('Recent Analyses')).parentElement.querySelector('div.space-y-3');
    if (rcContainer) {
        rcContainer.innerHTML = '<p class="text-sm">Loading...</p>';
        try {
            const res = await fetch('http://localhost:8000/analyses');
            const data = await res.json();
            rcContainer.innerHTML = '';
            data.slice(0, 4).forEach(item => {
                rcContainer.innerHTML += `
                <div class="flex items-center justify-between cursor-pointer hover:bg-surface-container-lowest p-2 rounded -mx-2" onclick="window.location.href='../stock_analysis/index.html?symbol=${item.symbol}'">
                    <span class="font-medium text-sm">${item.symbol}</span>
                    <span class="text-xs text-outline font-bold">${(item.confidence*100).toFixed(0)}% Conf</span>
                </div>`;
            });
        } catch(e){}
    }
});
</script>
"""


insert_script('c:/et genai/stitch/stitch/opportunity_radar/index.html', script_radar)
insert_script('c:/et genai/stitch/stitch/opportunity_radar/code.html', script_radar)

insert_script('c:/et genai/stitch/stitch/portfolio/index.html', script_portfolio)
insert_script('c:/et genai/stitch/stitch/portfolio/code.html', script_portfolio)

insert_script('c:/et genai/stitch/stitch/alerts/index.html', script_alerts)
insert_script('c:/et genai/stitch/stitch/alerts/code.html', script_alerts)

insert_script('c:/et genai/stitch/stitch/dashboard/index.html', script_dashboard)
insert_script('c:/et genai/stitch/stitch/dashboard/code.html', script_dashboard)

print("Restoration scripts applied.")
