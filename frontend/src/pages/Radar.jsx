import React, { useState, useEffect } from 'react';
import { getRadarData } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { Activity, TrendingUp, TrendingDown, Target, Zap, LayoutGrid, ChevronRight, Search, CircleDashed } from 'lucide-react';
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export default function Radar() {
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchRadar = async () => {
            setLoading(true);
            try {
                const results = await getRadarData();
                setData(results);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchRadar();
    }, []);

    const filteredData = data.filter(item => 
        item.symbol.toLowerCase().includes(search.toLowerCase())
    );

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-outline-variant/10">
                <div className="space-y-1">
                    <span className="text-xs font-black uppercase tracking-[0.2em] text-on-primary-container/60 mb-1 block">Vector Scanning Engine</span>
                    <h1 className="text-4xl font-black tracking-tighter text-slate-900 leading-none">Opportunity Radar</h1>
                    <p className="text-sm font-medium text-slate-500">Live multi-asset vector processing across major Indian indices.</p>
                </div>
                <div className="relative group">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-outline group-focus-within:text-primary transition-colors" />
                    <input 
                        type="text" 
                        placeholder="Filter symbols..." 
                        className="bg-white px-10 py-2.5 rounded-xl border border-outline-variant/10 text-sm font-bold shadow-sm focus:ring-4 focus:ring-primary/5 transition-all outline-none"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                    />
                </div>
            </div>

            <div className="bg-surface-container-lowest rounded-3xl border border-outline-variant/10 shadow-sm overflow-hidden group">
                <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-surface-container-low/50">
                                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-outline">Market Asset</th>
                                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-outline">AI Signal</th>
                                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-outline">Confidence Score</th>
                                <th className="px-8 py-5 text-[10px] font-black uppercase tracking-widest text-outline">AI Suggestion</th>
                                <th className="px-8 py-5 text-right text-[10px] font-black uppercase tracking-widest text-outline">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-outline-variant/5">
                            {loading ? (
                                <tr>
                                    <td colSpan="5" className="px-8 py-20 text-center">
                                        <div className="flex flex-col items-center gap-4 animate-pulse">
                                            <CircleDashed className="w-10 h-10 text-primary-container animate-spin" />
                                            <p className="text-sm font-black text-slate-400">Processing Live Vectors...</p>
                                        </div>
                                    </td>
                                </tr>
                            ) : filteredData.map((item, i) => (
                                <tr 
                                    key={i} 
                                    onClick={() => navigate(`/analysis?symbol=${item.symbol}`)}
                                    className="hover:bg-surface-container-low transition-colors group cursor-pointer active:bg-surface-container transition-all"
                                >
                                    <td className="px-8 py-6">
                                        <div className="flex items-center gap-4">
                                            <div className="w-12 h-12 rounded-xl bg-primary-container flex items-center justify-center text-white scale-90 group-hover:scale-100 transition-transform shadow-md shadow-primary-container/20">
                                                <span className="text-xs font-black">{item.symbol.substring(0, 4)}</span>
                                            </div>
                                            <div>
                                                <p className="font-black text-lg text-slate-900 tracking-tighter">{item.symbol}</p>
                                                <p className="text-[10px] text-outline font-black uppercase group-hover:text-primary transition-colors tracking-widest">Active Neural Scan</p>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className={cn("inline-flex items-center gap-2 group-hover:translate-x-1 transition-transform", 
                                            item.signal.includes('bull') ? 'text-secondary' : 'text-error')}>
                                            {item.signal.includes('bull') ? <TrendingUp className="w-5 h-5 shadow-sm" /> : <TrendingDown className="w-5 h-5 shadow-sm" />}
                                            <span className="text-sm font-black uppercase tracking-widest">{item.signal}</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className="flex flex-col items-start gap-2">
                                            <div className="flex items-center gap-2">
                                                <span className="text-base font-black text-slate-900">{(item.confidence * 100).toFixed(1)}%</span>
                                                <Activity className="w-3 h-3 text-outline group-hover:text-primary-container transition-colors" />
                                            </div>
                                            <div className="w-32 h-2 bg-surface-container-high rounded-full overflow-hidden shadow-inner border border-outline-variant/10">
                                                <div 
                                                    className="h-full bg-primary-container/40 rounded-full transition-all duration-1000" 
                                                    style={{ width: `${item.confidence * 100}%` }}
                                                />
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-8 py-6">
                                        <div className={cn(
                                            "inline-flex px-4 py-1.5 rounded-xl text-[10px] font-black uppercase tracking-[0.2em] shadow-sm border",
                                            item.action === 'BUY' ? 'bg-secondary-container text-on-secondary-container border-secondary/10' : 
                                            item.action === 'SELL' ? 'bg-error-container text-on-error-container border-error/10' : 
                                            'bg-surface-container-high text-on-surface-variant border-outline-variant/10'
                                        )}>
                                            {item.action}
                                        </div>
                                    </td>
                                    <td className="px-8 py-6 text-right">
                                        <button className="p-3 bg-surface-container-lowest rounded-xl border border-outline-variant/10 opacity-0 group-hover:opacity-100 transition-all hover:bg-primary hover:text-white hover:scale-110 active:scale-90 shadow-sm">
                                            <ChevronRight className="w-5 h-5" />
                                        </button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Quick Summary Grid */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                {[
                    { label: 'Market State', value: 'LIVE EXCHANGE FEED', color: 'text-secondary', icon: Activity },
                    { label: 'Intelligence Tier', value: 'INSTITUTIONAL GRADE', color: 'text-primary-container', icon: Zap },
                    { label: 'Active Vector Scans', value: filteredData.length, color: 'text-slate-900', icon: Target },
                    { label: 'System Compliance', value: 'SECURE', color: 'text-outline', icon: ShieldCheckIcon },
                ].map((stat, i) => (
                    <div key={i} className="bg-surface-container-lowest p-6 rounded-2xl border border-outline-variant/10 flex items-center gap-4 group hover:shadow-lg hover:shadow-black/5 transition-all">
                        <div className="p-3 bg-surface-container-low rounded-xl group-hover:scale-110 transition-transform">
                            <stat.icon className={cn("w-5 h-5", stat.color)} />
                        </div>
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-widest text-outline leading-tight">{stat.label}</p>
                            <p className={cn("text-sm font-black leading-tight", stat.color)}>{stat.value}</p>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

function ShieldCheckIcon(props) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z" />
      <path d="m9 12 2 2 4-4" />
    </svg>
  )
}
