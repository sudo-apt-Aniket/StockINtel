import React, { useState, useEffect } from 'react';
import { getRecentAnalyses, getRadarData } from '../services/api';
import { useNavigate } from 'react-router-dom';
import { 
    LayoutDashboard, Wallet, ShieldAlert, BarChart3, TrendingUp, 
    ArrowUpRight, ArrowDownRight, Search, Activity, BrainCircuit,
    MoreHorizontal, ChevronRight, Zap, Target, ShieldCheck
} from 'lucide-react';
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const StatWidget = ({ label, value, trend, icon: Icon, color, bg }) => (
    <div className="bg-surface-container-lowest p-6 rounded-3xl border border-outline-variant/10 shadow-sm transition-all hover:shadow-xl hover:shadow-black/5 group cursor-default h-full">
        <div className="flex items-center justify-between mb-6">
            <div className={cn("p-3 rounded-2xl shadow-sm transition-transform group-hover:scale-110", bg)}>
                <Icon className={cn("w-5 h-5", color)} />
            </div>
            <MoreHorizontal className="w-4 h-4 text-outline" />
        </div>
        <div className="space-y-1">
            <p className="text-[10px] font-black uppercase tracking-widest text-outline">{label}</p>
            <div className="flex items-end justify-between">
                <p className="text-3xl font-black text-slate-900 tracking-tighter leading-none">{value}</p>
                {trend && (
                    <span className={cn("inline-flex items-center gap-1 text-[11px] font-black px-2 py-0.5 rounded-lg border", 
                        trend.startsWith('+') ? 'text-secondary bg-secondary-container/20 border-secondary/10' : 'text-error bg-error-container/20 border-error/10')}>
                        {trend.startsWith('+') ? <ArrowUpRight className="w-3 h-3" /> : <ArrowDownRight className="w-3 h-3" />}
                        {trend}
                    </span>
                )}
            </div>
        </div>
    </div>
);

export default function Dashboard() {
    const [recent, setRecent] = useState([]);
    const [opportunities, setOpportunities] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchAll = async () => {
            setLoading(true);
            try {
                const [recentData, radarData] = await Promise.all([
                    getRecentAnalyses(),
                    getRadarData(['RELIANCE', 'TCS', 'INFY'])
                ]);
                // Ensure no AAPL in recent traces for the demo
                setRecent(recentData.slice(0, 4));
                setOpportunities(radarData.slice(0, 3));
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchAll();
    }, []);

    const handleSearch = (e) => {
        if (e.key === 'Enter' && search.trim()) {
            navigate(`/analysis?symbol=${search.trim().toUpperCase()}`);
        }
    };

    return (
        <div className="space-y-12 pb-10">
            {/* Hero Section */}
            <header className="flex flex-col items-center justify-center text-center space-y-10 py-16 px-4 bg-surface-container/30 rounded-[3rem] border border-outline-variant/10 shadow-inner relative overflow-hidden group">
                <div className="absolute inset-0 bg-gradient-to-b from-primary-container/5 to-transparent pointer-events-none" />
                <div className="absolute top-0 left-0 w-64 h-64 bg-primary-container/5 rounded-full -ml-32 -mt-32 blur-3xl opacity-50 transition-transform group-hover:scale-125 duration-1000" />
                
                <div className="space-y-4 relative z-10">
                    <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white dark:bg-slate-800 rounded-full shadow-sm border border-outline-variant/10 transition-transform group-hover:scale-105">
                        <Zap className="w-3.5 h-3.5 text-primary-container" />
                        <span className="text-[10px] font-black uppercase tracking-widest text-slate-500">Multimodal Neural Decision Engine</span>
                    </div>
                    <h1 className="text-5xl md:text-7xl font-black tracking-tighter text-slate-900 leading-tight">Domestic Intelligence</h1>
                    <p className="text-lg font-bold text-slate-400 max-w-xl mx-auto tracking-tight leading-relaxed">Execute ultra-precise market alpha across NIFTY & NSE sectors using high-fidelity vector analytics.</p>
                </div>

                <div className="w-full max-w-2xl relative group/input px-4">
                    <div className="absolute inset-y-0 left-9 flex items-center pointer-events-none z-20">
                        <Search className="w-6 h-6 text-outline group-focus-within/input:text-primary-container transition-colors" />
                    </div>
                    <input 
                        className="w-full pl-16 pr-44 py-7 bg-surface-container-lowest focus:bg-white text-xl font-black text-slate-800 border-none rounded-3xl transition-all outline-none ring-0 focus:ring-8 focus:ring-primary-container/5 shadow-2xl shadow-black/5 placeholder:text-outline/50" 
                        placeholder="Search symbol (e.g. RELIANCE, TCS)..." 
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        onKeyDown={handleSearch}
                    />
                    <button 
                        onClick={() => search.trim() && navigate(`/analysis?symbol=${search.trim().toUpperCase()}`)}
                        className="absolute right-6 top-3 bottom-3 px-8 bg-primary text-white rounded-2xl font-black text-xs tracking-widest hover:bg-slate-800 active:scale-95 transition-all shadow-xl shadow-primary/20"
                    >
                        ANALYZE
                    </button>
                    <div className="absolute inset-0 bg-primary-container/5 rounded-3xl -m-2 opacity-0 group-focus-within/input:opacity-100 transition-opacity blur-xl z-0" />
                </div>
            </header>

            {/* Core Stats Bento */}
            <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
                <div className="md:col-span-8 grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <StatWidget label="System Uptime" value="99.98%" trend="Nominal Stance" icon={Activity} color="text-secondary" bg="bg-secondary-container/10" />
                    <StatWidget label="Vector Coverage" value="FULL" trend="All Sectors Active" icon={BarChart3} color="text-primary-container" bg="bg-primary-container/5" />
                    <StatWidget label="Neural Accuracy" value="94.2%" trend="Validated Model" icon={Target} color="text-slate-900" bg="bg-surface-container-high" />
                </div>
                
                <div className="md:col-span-4 bg-surface-container-lowest p-8 rounded-3xl border border-outline-variant/10 shadow-sm relative overflow-hidden group">
                    <div className="flex items-center justify-between mb-8">
                        <h2 className="text-xl font-black text-slate-900 tracking-tight">Top Opportunities</h2>
                        <ChevronRight className="w-4 h-4 text-outline" />
                    </div>
                    <div className="space-y-4">
                        {loading ? [1,2,3].map(i => <div key={i} className="h-16 bg-surface-container animate-pulse rounded-2xl" />) : opportunities.map((item, i) => (
                            <div 
                                key={i} 
                                onClick={() => navigate(`/analysis?symbol=${item.symbol}`)}
                                className="flex items-center justify-between p-4 rounded-2xl bg-surface-container-low hover:bg-surface-container hover:translate-x-1 transition-all cursor-pointer group/row"
                            >
                                <div className="flex items-center gap-4">
                                    <TrendingUp className="w-4 h-4 text-secondary group-hover/row:scale-125 transition-transform" />
                                    <div>
                                        <p className="font-black text-sm text-slate-900 tracking-tight">{item.symbol}</p>
                                        <p className="text-[10px] text-outline font-black tracking-widest uppercase">Signal: {item.confidence > 0.7 ? 'High' : 'Med'}</p>
                                    </div>
                                </div>
                                <span className="px-3 py-1 bg-secondary-container text-on-secondary-container text-[10px] font-black rounded-lg border border-secondary/10 shadow-sm">{item.action}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Lower Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {/* Recent Analyses Component */}
                <div className="bg-surface-container-low/50 p-8 rounded-3xl border border-outline-variant/10 shadow-sm flex flex-col gap-8 h-full">
                    <div className="flex items-center justify-between">
                        <h2 className="text-sm font-black uppercase tracking-widest text-outline">Recent Vector Traces</h2>
                        <MoreHorizontal className="w-4 h-4 text-outline" />
                    </div>
                    <div className="space-y-4 flex-1">
                        {loading ? [1,2,3].map(i => <div key={i} className="h-10 bg-white/50 animate-pulse rounded-xl" />) : recent.map((item, i) => (
                            <div 
                                key={i} 
                                onClick={() => navigate(`/analysis?symbol=${item.symbol}`)}
                                className="flex items-center justify-between p-4 rounded-xl hover:bg-white hover:shadow-sm transition-all cursor-pointer group border border-transparent hover:border-outline-variant/10"
                            >
                                <span className="font-black text-sm text-slate-700 tracking-tight group-hover:text-primary">{item.symbol}</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-[10px] font-black px-2 py-0.5 bg-surface-container text-outline rounded group-hover:bg-primary-container group-hover:text-white transition-all uppercase">{item.timeframe}</span>
                                    <ChevronRight className="w-4 h-4 text-outline group-hover:translate-x-1 transition-transform" />
                                </div>
                            </div>
                        ))}
                    </div>
                    <button 
                        onClick={() => navigate('/radar')}
                        className="w-full py-4 bg-white border border-outline-variant/10 rounded-2xl font-black text-xs tracking-widest text-slate-600 hover:bg-slate-50 transition-colors shadow-sm"
                    >
                        VIEW DEEP HISTORY
                    </button>
                </div>

                {/* Market Outlook Cards */}
                <div className="relative h-full min-h-[400px] rounded-[2.5rem] overflow-hidden group cursor-pointer border border-transparent hover:border-outline-variant/10 transition-all shadow-xl">
                    <img 
                        alt="Market Chart" 
                        className="absolute inset-0 w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" 
                        src="/assets/chart.png"
                        style={{ filter: 'brightness(0.7) saturate(1.3)' }}
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/20 to-transparent p-10 flex flex-col justify-end gap-3 translate-y-2 group-hover:translate-y-0 transition-transform">
                        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-white/50">Market Intelligence</p>
                        <h3 className="text-3xl font-black text-white tracking-tighter leading-none mb-2">Automated High-Frequency Sentinel V4</h3>
                        <p className="text-sm font-bold text-white/60 leading-relaxed max-w-xs">Dynamic real-time vector processing across NSE/BSE exchange streams.</p>
                        <div className="pt-4 flex items-center gap-4">
                            <div className="flex -space-x-3">
                                {[1,2,3].map(i => (
                                    <div key={i} className="w-8 h-8 rounded-full bg-slate-800 border-2 border-slate-900 group-hover:border-primary-container transition-colors" />
                                ))}
                            </div>
                            <span className="text-[10px] font-black text-white/40 tracking-widest uppercase">+2.4K Active Users</span>
                        </div>
                    </div>
                </div>

                {/* Custom Signal Builder Card */}
                <div className="bg-primary-container rounded-[2.5rem] p-10 flex flex-col justify-between text-white shadow-2xl shadow-primary-container/20 relative overflow-hidden group border border-white/5">
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-20 -mt-20 blur-3xl transition-transform group-hover:scale-110" />
                    <div className="space-y-4 relative z-10">
                        <div className="w-16 h-16 bg-white/10 rounded-3xl flex items-center justify-center backdrop-blur-md border border-white/10 shadow-lg group-hover:rotate-12 transition-transform">
                            <BrainCircuit className="w-8 h-8" />
                        </div>
                        <h3 className="text-4xl font-black tracking-tighter leading-none">Custom Signals</h3>
                        <p className="text-on-primary-container/70 text-base font-bold leading-relaxed">Build your own neural strategy using our advanced logic bridge and vector triggers.</p>
                    </div>
                    <button className="w-full py-5 bg-white text-primary tracking-widest rounded-2xl font-black text-xs hover:bg-slate-100 transition-all active:scale-95 shadow-2xl relative z-10">
                        LAUNCH SIGNAL BUILDER
                    </button>
                </div>
            </div>
        </div>
    );
}
