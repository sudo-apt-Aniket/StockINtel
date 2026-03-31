import React, { useState, useEffect } from 'react';
import { getAlerts, updateAlertStatus } from '../services/api';
import { Bell, Filter, MoreHorizontal, Check, Trash, ShieldAlert, Activity, LayoutGrid, Zap, TrendingUp, TrendingDown, Clock, Search } from 'lucide-react';
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export default function Alerts() {
    const [alerts, setAlerts] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchAlerts = async () => {
        setLoading(true);
        try {
            const data = await getAlerts();
            setAlerts(data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAlerts();
    }, []);

    const handleUpdate = async (id, status) => {
        try {
            await updateAlertStatus(id, status);
            fetchAlerts();
        } catch (err) {
            console.error(err);
        }
    };

    return (
        <div className="space-y-12 animate-in fade-in slide-in-from-right-10 duration-1000">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8 pb-8 border-b border-outline-variant/10">
                <div className="space-y-1">
                    <span className="text-xs font-black uppercase tracking-[0.2em] text-on-primary-container/60 mb-2 block">Alpha System Monitor</span>
                    <h1 className="text-5xl font-black tracking-tighter text-slate-900 leading-none">Security & Alerts</h1>
                    <p className="text-lg font-bold text-slate-400 max-w-xl tracking-tight mt-2">Centralized exception monitoring for domestic asset strategies.</p>
                </div>
                <div className="flex gap-3">
                    <div className="flex bg-surface-container p-1.5 rounded-2xl shadow-inner border border-outline-variant/5">
                        <button className="px-4 py-2 bg-white rounded-xl shadow-sm text-[10px] font-black uppercase tracking-widest text-slate-900">Active</button>
                        <button className="px-4 py-2 text-outline text-[10px] font-black uppercase tracking-widest hover:text-slate-500 transition-colors">History</button>
                    </div>
                    <button className="p-4 bg-white border border-outline-variant/10 rounded-2xl shadow-sm hover:bg-slate-50 transition-all active:scale-95 group">
                        <Filter className="w-5 h-5 text-outline group-hover:text-primary transition-colors" />
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                <div className="lg:col-span-8 space-y-6">
                    {loading ? (
                        [1,2,3,4].map(i => <div key={i} className="h-40 bg-surface-container-low animate-pulse rounded-[3rem]" />)
                    ) : alerts.length > 0 ? alerts.map((alert, i) => (
                        <div key={i} className={cn(
                            "group p-8 rounded-[3rem] border shadow-sm transition-all hover:shadow-2xl hover:shadow-black/5 relative overflow-hidden active:scale-[0.99] hover:-translate-y-1",
                            alert.status === 'acknowledged' 
                                ? 'bg-surface-container opacity-60 grayscale-[0.3] border-outline-variant/10 shadow-inner' 
                                : 'bg-surface-container-lowest border-outline-variant/10'
                        )}>
                            <div className="absolute top-0 right-0 w-32 h-32 bg-primary-container/5 rounded-full -mr-16 -mt-16 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity" />
                            
                            <div className="flex flex-col md:flex-row gap-8 relative z-10">
                                <div className="flex-1 space-y-6">
                                    <div className="flex items-center gap-4">
                                        <div className={cn("p-2.5 rounded-xl border flex items-center justify-center font-black text-[10px] tracking-[0.2em] transform transition-transform group-hover:scale-110", 
                                            alert.status === 'open' ? 'bg-error-container/20 text-error border-error/10 shadow-sm' : 'bg-surface-container-high text-outline border-outline-variant/10 shadow-inner')}>
                                            {alert.symbol}
                                        </div>
                                        <div className="flex items-center gap-2 text-xs font-black uppercase tracking-widest text-outline">
                                            <Clock className="w-3 h-3" />
                                            {new Date(alert.created_at).toLocaleDateString()} • {new Date(alert.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} IST
                                        </div>
                                    </div>
                                    
                                    <div className="space-y-2">
                                        <h3 className="text-2xl font-black text-slate-900 tracking-tighter leading-none group-hover:text-primary-container transition-colors">{alert.alert}</h3>
                                        <p className="text-base font-bold text-slate-500 leading-relaxed max-w-2xl">{alert.recommendation}</p>
                                    </div>

                                    <div className="flex items-center gap-4">
                                         <div className="flex items-center gap-2 px-3 py-1 bg-surface-container rounded-lg group-hover:bg-primary-container group-hover:text-white transition-all shadow-sm">
                                             <Activity className="w-3.5 h-3.5" />
                                             <span className="text-[10px] font-black uppercase tracking-widest">Confidence Index: {(alert.confidence * 100).toFixed(0)}%</span>
                                         </div>
                                         <div className="w-1.5 h-1.5 rounded-full bg-outline-variant shadow-inner" />
                                         <span className="text-[10px] uppercase font-black tracking-widest text-outline">Risk Vector: {alert.confidence > 0.8 ? 'High Conviction' : 'Standard Baseline'}</span>
                                    </div>
                                </div>

                                <div className="flex flex-col gap-3 min-w-[200px] border-t md:border-t-0 md:border-l border-outline-variant/10 pt-8 md:pt-0 md:pl-8">
                                    <button 
                                        onClick={() => handleUpdate(alert.alert_id, alert.status === 'open' ? 'acknowledged' : 'open')}
                                        className={cn("w-full py-4 rounded-2xl font-black text-xs tracking-widest transition-all shadow-sm border active:scale-95 flex items-center justify-center gap-2", 
                                            alert.status === 'open' ? 'bg-primary text-white hover:bg-slate-800' : 'bg-surface-container-lowest text-slate-600 hover:bg-slate-50 border-outline-variant/10 shadow-inner')}
                                    >
                                        {alert.status === 'open' ? <Check className="w-4 h-4 shadow-sm" /> : <TrendingUp className="w-4 h-4" />}
                                        {alert.status === 'open' ? 'ACKNOWLEDGE' : 'REOPEN ALERT'}
                                    </button>
                                    <button 
                                        onClick={() => handleUpdate(alert.alert_id, 'closed')}
                                        className="w-full py-4 text-error font-black text-xs tracking-widest rounded-2xl hover:bg-error-container/20 transition-all flex items-center justify-center gap-2 active:scale-95 group/del"
                                    >
                                        <Trash className="w-4 h-4 group-hover/del:scale-110 transition-transform" />
                                        ARCHIVE CASE
                                    </button>
                                </div>
                            </div>
                        </div>
                    )) : (
                        <div className="flex flex-col items-center justify-center py-40 border-4 border-dashed border-outline-variant/20 rounded-[3rem] text-center space-y-6">
                            <div className="w-24 h-24 rounded-full bg-surface-container/50 border border-outline-variant/5 flex items-center justify-center text-outline shadow-inner animate-pulse">
                                <Zap className="w-10 h-10" />
                            </div>
                            <div>
                                <h3 className="text-2xl font-black text-slate-800 tracking-tight">Signal Feed Zero</h3>
                                <p className="text-base font-bold text-outline lowercase tracking-tighter max-w-sm mx-auto p-4 leading-relaxed">Intelligence sensors are active and monitoring domestic vectors. no current exceptions detected.</p>
                            </div>
                        </div>
                    )}
                </div>

                <aside className="lg:col-span-4 space-y-8">
                    <div className="bg-primary-container rounded-[2.5rem] p-10 text-white shadow-2xl shadow-primary-container/20 space-y-10 group overflow-hidden relative border border-white/5">
                        <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-32 -mt-32 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                        
                        <div className="space-y-6 relative z-10">
                            <div className="w-16 h-16 bg-white/10 rounded-3xl border border-white/10 flex items-center justify-center shadow-lg transition-all group-hover:scale-110 group-hover:rotate-6">
                                <ShieldAlert className="w-8 h-8" />
                            </div>
                            <div className="space-y-2">
                                <h3 className="text-3xl font-black tracking-tighter leading-none">Security Center</h3>
                                <p className="text-on-primary-container/60 text-base font-bold leading-relaxed">Advanced vector-based risk management and anomaly detection for institutional capital scale.</p>
                            </div>
                        </div>
                        
                        <div className="space-y-6 relative z-10">
                            {[
                                { label: 'Signal Guard', status: 'Active', icon: TrendingUp },
                                { label: 'Intelligence Sensor', status: 'Optimal', icon: Activity },
                                { label: 'HFT Vector Block', status: 'Active', icon: LayoutGrid },
                            ].map((s, i) => (
                                <div key={i} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/5 group/row hover:bg-white/10 transition-all cursor-default">
                                    <div className="flex items-center gap-3">
                                        <s.icon className="w-4 h-4 text-white/40 group-hover/row:text-white transition-colors" />
                                        <span className="text-[10px] font-black uppercase tracking-widest text-white/60">{s.label}</span>
                                    </div>
                                    <span className="text-xs font-black text-white px-2.5 py-1 bg-white/10 rounded-lg shadow-sm">{s.status}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-surface-container-low p-10 rounded-[2.5rem] border border-outline-variant/5 shadow-inner space-y-8 group">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-white rounded-2xl group-hover:scale-110 transition-transform shadow-sm">
                                <Bell className="w-5 h-5 text-primary" />
                            </div>
                            <h3 className="text-xl font-black text-slate-900 tracking-tight">Configuration</h3>
                        </div>
                        <div className="space-y-6">
                            <div className="space-y-3">
                                <label className="text-[10px] font-black uppercase tracking-widest text-outline pl-2">Intelligence Threshold</label>
                                <div className="flex items-center justify-between gap-4">
                                     <input type="range" className="flex-1 accent-primary h-1.5 bg-surface-container rounded-full appearance-none cursor-pointer" />
                                     <span className="text-sm font-black text-slate-900 leading-none">85%</span>
                                </div>
                                <p className="text-[10px] font-bold text-outline leading-tight px-2">System will only emit alerts when neural confidence exceeds this parameter.</p>
                            </div>
                        </div>
                        <button className="w-full py-4 bg-white border border-outline-variant/10 rounded-2xl font-black text-xs tracking-widest text-slate-600 shadow-sm hover:translate-y-[-2px] hover:shadow-lg transition-all active:scale-95">RECALIBRATE SENSORS</button>
                    </div>
                </aside>
            </div>
        </div>
    );
}
