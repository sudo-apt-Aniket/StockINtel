import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Search, BrainCircuit, Activity, ShieldCheck, Zap, AlertTriangle, TrendingUp, TrendingDown, MoreHorizontal, ShoppingCart, Bell, LayoutGrid } from 'lucide-react';
import { analyzeStock } from '../services/api';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

const StatCard = ({ label, value, trend, trendValue, icon: Icon, colorClass }) => (
    <div className="bg-surface-container-lowest p-6 rounded-2xl border border-outline-variant/10 shadow-sm transition-all hover:shadow-md group">
        <div className="flex items-center justify-between mb-4">
            <span className="text-[10px] font-black uppercase tracking-widest text-outline group-hover:text-primary transition-colors">{label}</span>
            <div className={cn("p-2 rounded-lg bg-surface-container-low transition-all group-hover:scale-110 shadow-sm", colorClass)}>
                <Icon className="w-4 h-4" />
            </div>
        </div>
        <div className="flex items-end justify-between">
            <div className="space-y-1">
                <p className="text-2xl font-black text-slate-900 leading-none">{value}</p>
                {trendValue && (
                    <div className={cn("flex items-center gap-1 text-[11px] font-bold", trend === 'up' ? 'text-secondary' : 'text-error')}>
                        {trend === 'up' ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {trendValue}
                    </div>
                )}
            </div>
        </div>
    </div>
);

export default function Analysis() {
    const [searchParams, setSearchParams] = useSearchParams();
    const [symbol, setSymbol] = useState(searchParams.get('symbol') || 'RELIANCE');
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState(null);
    const [error, setError] = useState(null);

    const handleRunAnalysis = async (targetSymbol) => {
        const querySymbol = targetSymbol || symbol;
        if (!querySymbol) return;
        
        setLoading(true);
        setError(null);
        try {
            const result = await analyzeStock(querySymbol);
            setData(result);
            setSearchParams({ symbol: querySymbol });
        } catch (err) {
            console.error('Analysis error:', err);
            setError('Failed to fetch intelligence profile. Check your network or symbol.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const initialSymbol = searchParams.get('symbol');
        if (initialSymbol) {
            handleRunAnalysis(initialSymbol);
        } else {
            handleRunAnalysis('RELIANCE');
        }
    }, []);

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Context Section */}
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-6 border-b border-outline-variant/10">
                <div className="space-y-1">
                    <span className="text-xs font-black uppercase tracking-[0.2em] text-on-primary-container/60 mb-1 block">Decision Support System</span>
                    <h1 className="text-4xl font-black tracking-tighter text-slate-900 dark:text-slate-50">AI Insights Engine</h1>
                    <p className="text-sm font-medium text-slate-500">Multidimensional alpha signal processing for the Indian market.</p>
                </div>
                <div className="flex gap-2">
                    <button className="flex items-center gap-2 px-4 py-2.5 bg-white dark:bg-slate-800 border border-outline-variant/10 rounded-xl font-bold text-sm text-slate-700 dark:text-slate-200 shadow-sm active:scale-95 transition-all hover:bg-slate-50">
                        <Bell className="w-4 h-4" /> Set Alert
                    </button>
                    <button className="flex items-center gap-2 px-4 py-2.5 bg-primary dark:bg-white text-white dark:text-primary rounded-xl font-bold text-sm shadow-xl shadow-primary/10 active:scale-95 transition-all hover:opacity-90">
                        <LayoutGrid className="w-4 h-4" /> Compare Sector
                    </button>
                </div>
            </div>

            {/* Input Console */}
            <div className="bg-surface-container p-1 rounded-3xl border border-outline-variant/10 shadow-lg shadow-black/5 group">
                <div className="bg-surface-container-low p-6 rounded-[calc(1.5rem-2px)] flex flex-col md:flex-row gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-outline group-focus-within:text-primary transition-colors" />
                        <input 
                            type="text" 
                            className="w-full h-14 pl-12 pr-4 bg-surface-container-lowest border-none rounded-2xl text-xl font-black text-slate-900 placeholder:text-outline focus:ring-4 focus:ring-primary/5 shadow-sm transition-all"
                            placeholder="Enter Ticker (e.g. HDFCBANK, TCS)"
                            value={symbol}
                            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                            onKeyDown={(e) => e.key === 'Enter' && handleRunAnalysis()}
                        />
                    </div>
                    <button 
                        onClick={() => handleRunAnalysis()}
                        disabled={loading}
                        className={cn(
                            "h-14 px-10 rounded-2xl bg-primary text-white font-black text-sm flex items-center justify-center gap-3 transition-all active:scale-95 shadow-lg shadow-primary/20",
                            loading ? "opacity-70 cursor-not-allowed grayscale" : "hover:opacity-90 active:scale-95"
                        )}
                    >
                        {loading ? (
                            <Activity className="w-5 h-5 animate-spin" />
                        ) : (
                            <BrainCircuit className="w-5 h-5" />
                        )}
                        {loading ? 'CALCULATING...' : 'RUN ANALYTICS'}
                    </button>
                </div>
            </div>

            {error && (
                <div className="p-4 bg-error-container/20 border border-error/20 rounded-2xl flex items-center gap-3 text-error animate-in slide-in-from-top-2">
                    <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                    <p className="text-sm font-bold tracking-tight">{error}</p>
                </div>
            )}

            {data && !loading && (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 animate-in slide-in-from-bottom-6 duration-700 fill-mode-both">
                    {/* Main Intelligence Profile */}
                    <div className="lg:col-span-8 space-y-8">
                        <div className="bg-surface-container-lowest border border-outline-variant/10 rounded-3xl p-8 md:p-12 shadow-sm relative overflow-hidden group">
                            <div className="absolute top-0 right-0 w-96 h-96 bg-secondary/5 rounded-full -mr-32 -mt-32 blur-3xl transition-transform group-hover:scale-125" />
                            
                            <div className="relative z-10 flex flex-col md:flex-row justify-between items-start gap-8 mb-12">
                                <div className="space-y-2">
                                    <div className="flex items-center gap-3">
                                        <h2 className="text-6xl font-black tracking-tighter text-slate-900 tracking-tight">{data?.symbol || '---'}</h2>
                                        <div className={cn(
                                            "mt-2 px-4 py-1.5 rounded-full text-xs font-black tracking-widest shadow-sm border",
                                            data.signal === 'bullish' ? 'bg-secondary-container text-on-secondary-container border-secondary/10' : 'bg-error-container text-on-error/80 border-error/10'
                                        )}>
                                            {data?.signal?.toUpperCase() || 'NEUTRAL'}
                                        </div>
                                    </div>
                                    <p className="text-lg font-bold text-slate-400 tracking-tight">Market Asset Analysis Profile</p>
                                </div>
                                
                                <div className="text-right space-y-3">
                                    <div className="flex flex-col items-end gap-1">
                                        <span className="text-[10px] font-black uppercase tracking-widest text-outline">Confidence Signal</span>
                                        <div className="flex items-center gap-3">
                                            <span className="text-4xl font-black text-slate-900">{((data?.confidence || 0) * 100).toFixed(0)}%</span>
                                            <div className="w-24 h-4 bg-surface-container rounded-full overflow-hidden border border-outline-variant/5">
                                                <div className="h-full bg-secondary transition-all duration-1000" style={{ width: `${(data?.confidence || 0) * 100}%` }} />
                                            </div>
                                        </div>
                                    </div>
                                    <button className={cn(
                                        "w-full px-8 py-4 rounded-2xl font-black text-lg text-white shadow-xl flex items-center justify-center gap-3 active:scale-95 transition-all transition-transform",
                                        data.signal === 'bullish' ? 'bg-secondary shadow-secondary/20 hover:shadow-secondary/30' : 'bg-error shadow-error/20 hover:shadow-error/30'
                                    )}>
                                        <ShoppingCart className="w-6 h-6" />
                                        ACTION: {data?.action?.toUpperCase() || 'HOLD'}
                                    </button>
                                </div>
                            </div>

                            <div className="relative z-10 border-t border-outline-variant/10 pt-10">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="p-2 bg-primary-container/5 rounded-lg border border-primary-container/10">
                                        <Zap className="w-5 h-5 text-primary-container" />
                                    </div>
                                    <h3 className="text-xl font-black text-slate-900 tracking-tight">Executive Summary</h3>
                                </div>
                                <p className="text-xl font-medium text-slate-600 leading-relaxed max-w-3xl">
                                    {data?.explanation || 'No explanation available.'}
                                </p>
                            </div>
                        </div>

                        {/* Analysis Grid */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="bg-surface-container-low p-8 rounded-3xl border border-outline-variant/10 flex flex-col gap-6 group hover:bg-surface-container-low/80 transition-all">
                                <div className="flex items-center gap-3 text-secondary">
                                    <ShieldCheck className="w-6 h-6" />
                                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Institutional Reasoning</h4>
                                </div>
                                <p className="text-sm font-bold text-slate-700 leading-relaxed italic border-l-4 border-secondary/20 pl-4 py-1">
                                    "{data.reasoning}"
                                </p>
                            </div>

                            <div className="bg-surface-container-low p-8 rounded-3xl border border-outline-variant/10 flex flex-col gap-6 group hover:bg-surface-container-low/80 transition-all">
                                <div className="flex items-center gap-3 text-primary-container">
                                    <Activity className="w-6 h-6" />
                                    <h4 className="text-[10px] font-black uppercase tracking-[0.2em]">Key Market Insight</h4>
                                </div>
                                <p className="text-sm font-bold text-slate-700 leading-relaxed italic border-l-4 border-primary-container/20 pl-4 py-1">
                                    "{data.insight}"
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* Meta Intelligence Sidebar */}
                    <div className="lg:col-span-4 space-y-6">
                        <div className="bg-tertiary-container text-on-tertiary p-8 rounded-3xl relative overflow-hidden shadow-2xl shadow-tertiary-container/20 group">
                            <div className="absolute inset-0 bg-gradient-to-br from-black/20 to-transparent" />
                            <div className="relative z-10 space-y-6">
                                <div className="flex items-center gap-4">
                                    <div className="p-2 bg-white/10 rounded-xl backdrop-blur-md border border-white/10 transition-transform group-hover:rotate-12">
                                        <AlertTriangle className="w-6 h-6 text-on-tertiary/90" />
                                    </div>
                                    <h3 className="text-lg font-black tracking-tight">System Risk Assessment</h3>
                                </div>
                                <p className="text-sm font-medium text-on-tertiary/70 leading-relaxed">
                                    {data?.risk || 'Risk profile not analyzed.'}
                                </p>
                                <div className="pt-4 border-t border-white/10 space-y-4">
                                    <div className="flex items-center justify-between">
                                        <span className="text-[10px] uppercase font-black tracking-widest text-on-tertiary/40">Portfolio Impact</span>
                                        <span className="text-xs font-black px-2 py-0.5 bg-error/20 rounded-md text-on-tertiary-container/80 border border-error/10 group-hover:scale-110 transition-transform">+14.2% Risk</span>
                                    </div>
                                    <p className="text-[11px] font-semibold text-on-tertiary/50">
                                        {data.portfolio_context}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Additional Stats */}
                        <div className="grid grid-cols-1 gap-4">
                             <StatCard 
                                label="Relative Strength (RSI)" 
                                value={data?.rsi?.toFixed(1) || "50.0"} 
                                trend={(data?.rsi || 50) >= 50 ? "up" : "down"} 
                                trendValue={(data?.rsi || 50) >= 70 ? "Overbought" : (data?.rsi || 50) <= 30 ? "Oversold" : "Normal"} 
                                icon={Activity} 
                                colorClass="text-secondary" 
                             />
                             <StatCard 
                                label="Volatility Profile" 
                                value={(data?.volatility || 0) > 20 ? "High" : (data?.volatility || 0) > 5 ? "Moderate" : "Low"} 
                                trend="down" 
                                trendValue={`${(data?.volatility || 0).toFixed(2)} SD`} 
                                icon={ShieldCheck} 
                                colorClass="text-primary-container" 
                             />
                        </div>

                        <div className="p-8 bg-surface-container-lowest border border-outline-variant/10 rounded-3xl shadow-sm">
                            <div className="flex items-center justify-between mb-6">
                                <h4 className="text-sm font-black text-slate-900 tracking-tight">Signal Feed Correlation</h4>
                                <MoreHorizontal className="w-4 h-4 text-outline" />
                            </div>
                            <div className="space-y-4">
                                {[
                                    { name: 'NIFTY 50 Benchmark', score: '0.82', icon: Activity },
                                    { name: 'Sector Weighting', score: '14.2%', icon: LayoutGrid },
                                ].map((stat, i) => (
                                    <div key={i} className="flex items-center justify-between py-3 border-b border-outline-variant/5 last:border-0 hover:translate-x-1 transition-transform cursor-default">
                                        <div className="flex items-center gap-3">
                                            <stat.icon className="w-4 h-4 text-outline" />
                                            <span className="text-xs font-bold text-slate-500">{stat.name}</span>
                                        </div>
                                        <span className="text-sm font-black text-slate-800">{stat.score}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}
            
            {!data && !loading && !error && (
                <div className="flex flex-col items-center justify-center py-32 text-center space-y-6 animate-in zoom-in-95 duration-700">
                    <div className="w-24 h-24 rounded-full bg-surface-container-low flex items-center justify-center text-outline group-hover:scale-110 transition-all border border-outline-variant/5 shadow-inner">
                        <BrainCircuit className="w-12 h-12" />
                    </div>
                    <div>
                        <h2 className="text-3xl font-black text-slate-800 tracking-tight">Intelligence Ready</h2>
                        <p className="text-slate-400 font-bold max-w-sm mx-auto">Enter an NSE / BSE ticker to process real-time market signals through our neural decision engine.</p>
                    </div>
                </div>
            )}
        </div>
    );
}
