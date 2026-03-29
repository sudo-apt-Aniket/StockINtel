import React, { useState, useEffect } from 'react';
import { getPortfolios } from '../services/api';
import { Wallet, Plus, Download, TrendingUp, Shield, ChevronRight, Activity, PieChart, Briefcase, Search } from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export default function Portfolio() {
    const [portfolios, setPortfolios] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchPortfolios = async () => {
            try {
                const data = await getPortfolios();
                setPortfolios(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchPortfolios();
    }, []);

    return (
        <div className="space-y-12 animate-in fade-in slide-in-from-bottom-6 duration-1000">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 pb-8 border-b border-outline-variant/10">
                <div className="space-y-1">
                    <span className="text-xs font-black uppercase tracking-[0.2em] text-on-primary-container/60 mb-2 block">Alpha Curation Engine</span>
                    <h1 className="text-5xl font-black tracking-tighter text-slate-900 leading-none">Portfolio Management</h1>
                    <p className="text-lg font-bold text-slate-400 max-w-xl tracking-tight mt-2">Scale your domestic capital allocation with institutional precision tools.</p>
                </div>
                <div className="flex gap-4">
                    <button className="flex items-center gap-3 bg-white border border-outline-variant/10 px-6 py-3.5 rounded-2xl font-black text-xs tracking-widest text-slate-700 active:scale-95 transition-all shadow-sm group hover:bg-slate-50">
                        <Download className="w-4 h-4 text-outline group-hover:text-primary transition-colors" />
                        EXPORT
                    </button>
                    <button className="flex items-center gap-3 bg-primary text-white px-8 py-3.5 rounded-2xl font-black text-xs tracking-widest active:scale-95 transition-all shadow-xl shadow-primary/20 hover:opacity-90">
                        <Plus className="w-5 h-5" />
                        CREATE NEW
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
                <aside className="lg:col-span-4 space-y-8">
                    <div className="bg-surface-container-low p-8 rounded-[2.5rem] border border-outline-variant/5 shadow-inner space-y-8 group transition-all">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-primary-container/5 rounded-2xl border border-primary-container/10 group-hover:scale-110 transition-transform">
                                <Briefcase className="w-6 h-6 text-primary-container" />
                            </div>
                            <h2 className="text-xl font-black text-slate-900 tracking-tight">Add Portfolio</h2>
                        </div>
                        
                        <div className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-outline pl-2">Portfolio Name</label>
                                <input 
                                    className="w-full bg-surface-container-lowest border-outline-variant/10 border rounded-2xl px-5 py-4 text-sm font-bold focus:ring-4 focus:ring-primary-container/5 transition-all outline-none" 
                                    placeholder="e.g. NIFTY Core Growth" 
                                    type="text"
                                />
                            </div>
                            <div className="space-y-2">
                                <label className="text-[10px] font-black uppercase tracking-widest text-outline pl-2">Market Symbols</label>
                                <div className="flex gap-3">
                                    <div className="flex-1 relative">
                                        <input 
                                            className="w-full bg-surface-container-lowest border-outline-variant/10 border rounded-2xl pl-12 pr-4 py-4 text-sm font-bold focus:ring-4 focus:ring-primary-container/5 transition-all outline-none" 
                                            placeholder="RELIANCE, TCS..." 
                                            type="text"
                                        />
                                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-outline" />
                                    </div>
                                    <button className="p-4 bg-primary text-white rounded-2xl flex items-center justify-center shadow-lg shadow-primary/10 active:scale-95 hover:bg-slate-800 transition-all">
                                        <Plus className="w-6 h-6" />
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <button className="w-full bg-primary text-white py-5 rounded-2xl font-black text-xs tracking-widest active:scale-95 transition-transform shadow-xl shadow-primary/20 hover:opacity-90">
                            INITIALIZE PORTFOLIO
                        </button>
                    </div>

                    <div className="bg-tertiary-container/5 p-8 rounded-[2.5rem] border border-tertiary-container/10 shadow-sm group">
                        <div className="flex items-center gap-4 mb-6">
                            <div className="p-3 bg-white rounded-2xl border border-tertiary-container/10 group-hover:rotate-6 transition-all">
                                <Shield className="w-5 h-5 text-on-tertiary-container" />
                            </div>
                            <h2 className="text-xl font-black text-slate-900 tracking-tight">Sector Exposure</h2>
                        </div>
                        
                        <div className="space-y-6">
                            {[
                                { name: 'Technology', pct: 65, color: 'bg-primary-container' },
                                { name: 'Energy', pct: 15, color: 'bg-secondary' },
                                { name: 'Healthcare', pct: 12, color: 'bg-on-primary-container' },
                                { name: 'Other', pct: 8, color: 'bg-outline' },
                            ].map((s, i) => (
                                <div key={i} className="space-y-2 group/bar cursor-default">
                                    <div className="flex items-center justify-between text-xs font-black uppercase tracking-tighter">
                                        <span className="text-slate-500">{s.name}</span>
                                        <span className="text-slate-900 font-black">{s.pct}%</span>
                                    </div>
                                    <div className="h-2.5 w-full bg-surface-container rounded-full overflow-hidden shadow-inner border border-outline-variant/5">
                                        <div className={cn("h-full transition-all duration-1000", s.color)} style={{ width: `${s.pct}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </aside>

                <div className="lg:col-span-8 space-y-6">
                    <div className="flex items-center justify-between px-4 mb-2">
                         <h2 className="text-sm font-black uppercase tracking-widest text-outline">Active Allocation Targets</h2>
                         <div className="flex gap-2">
                             <div className="w-2 h-2 rounded-full bg-secondary animate-pulse" />
                             <span className="text-[10px] font-black uppercase tracking-widest text-secondary">Live Processing</span>
                         </div>
                    </div>

                    {loading ? [1,2,3].map(i => <div key={i} className="h-32 bg-surface-container-low animate-pulse rounded-3xl" />) : portfolios.length > 0 ? portfolios.map((p, i) => (
                        <div key={i} className="group bg-surface-container-lowest p-8 rounded-[2.5rem] border border-outline-variant/10 shadow-sm hover:shadow-2xl hover:shadow-black/5 transition-all cursor-pointer relative overflow-hidden active:scale-[0.99] hover:-translate-y-1">
                            <div className="absolute top-0 right-0 w-64 h-64 bg-primary-container/5 rounded-full -mr-32 -mt-32 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                            
                            <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-8">
                                <div className="flex items-center gap-6">
                                    <div className={cn("w-16 h-16 rounded-3xl flex items-center justify-center transition-all group-hover:rotate-6 shadow-md border border-outline-variant/5", 
                                        i % 2 === 0 ? 'bg-secondary-container/30 text-secondary' : 'bg-surface-container-high/50 text-outline')}>
                                        {i % 2 === 0 ? <TrendingUp className="w-8 h-8 rotate-45" /> : <Shield className="w-8 h-8" />}
                                    </div>
                                    <div className="space-y-1">
                                        <h3 className="text-2xl font-black text-slate-900 tracking-tighter leading-none">{p.name}</h3>
                                        <p className="text-sm font-bold text-slate-400 leading-tight">{p.symbols.length} Vector Targets • Updated {new Date(p.updated_at).toLocaleDateString()}</p>
                                        <div className="flex gap-2 mt-2">
                                            {p.symbols.slice(0, 4).map(s => (
                                                <span key={s} className="px-2.5 py-1 bg-surface-container rounded-lg text-[10px] font-black text-outline uppercase tracking-widest">{s}</span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="flex items-center gap-12 border-t md:border-t-0 md:border-l border-outline-variant/10 pt-6 md:pt-0 md:pl-10">
                                    <div className="text-right leading-none">
                                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-outline mb-2">Net Value</p>
                                        <p className="text-2xl font-black text-slate-900 tracking-tighter">₹85,200</p>
                                    </div>
                                    <div className="text-right leading-none">
                                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-outline mb-2">Alpha Yield</p>
                                        <p className="text-2xl font-black text-secondary tracking-tighter">+14.2%</p>
                                    </div>
                                    <div className="w-12 h-12 bg-surface-container rounded-2xl flex items-center justify-center group-hover:bg-primary group-hover:text-white transition-all group-hover:translate-x-1 outline outline-4 outline-transparent group-hover:outline-primary/5 shadow-sm">
                                        <ChevronRight className="w-6 h-6" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    )) : (
                        <div className="flex flex-col items-center justify-center py-20 text-center border-4 border-dashed border-outline-variant/20 rounded-[3rem] space-y-6">
                             <div className="w-20 h-20 rounded-full bg-surface-container-low flex items-center justify-center text-outline shadow-inner">
                                 <Briefcase className="w-10 h-10" />
                             </div>
                             <p className="text-lg font-black text-outline lowercase tracking-tighter max-w-xs">no active portfolios detected in intelligence stream.</p>
                             <button className="px-8 py-3 bg-primary text-white rounded-2xl font-black text-xs tracking-widest shadow-xl shadow-primary/20 transition-all hover:scale-105 active:scale-95 uppercase">Initial System Load</button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
