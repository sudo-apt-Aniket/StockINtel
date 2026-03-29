import { NavLink } from 'react-router-dom'
import { LayoutDashboard, Radar, BrainCircuit, Wallet, Bell, PieChart, Activity, Search } from 'lucide-react'
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs) {
  return twMerge(clsx(inputs));
}

const navItems = [
  { name: 'Market Overview', path: '/dashboard', icon: Activity },
  { name: 'Sector Analysis', path: '/radar', icon: PieChart },
  { name: 'AI Insights', path: '/analysis', icon: BrainCircuit },
  { name: 'Portfolio', path: '/portfolio', icon: Wallet },
  { name: 'Alerts', path: '/alerts', icon: Bell },
]

export default function Sidebar({ className }) {
  return (
    <aside className={cn("flex flex-col border-r border-outline-variant/10 bg-slate-50 dark:bg-slate-900 p-4 gap-4 h-full", className)}>
      <div className="flex items-center gap-3 px-3 py-2 mb-2 flex-shrink-0">
        <div className="w-10 h-10 rounded-xl bg-primary-container flex items-center justify-center text-white shadow-lg shadow-primary-container/20">
          <BrainCircuit className="w-6 h-6" />
        </div>
        <div>
          <p className="font-bold text-lg text-slate-900 dark:text-slate-50 leading-tight">Intelligence</p>
          <p className="text-[10px] uppercase tracking-widest text-on-primary-container font-semibold opacity-70">Domestic Tier</p>
        </div>
      </div>

      <nav className="flex-1 space-y-1 overflow-y-auto pr-2 custom-scrollbar">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group relative w-full",
                isActive
                  ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm font-semibold translate-x-1"
                  : "text-slate-500 dark:text-slate-400 hover:bg-slate-200/50 dark:hover:bg-slate-800/30 hover:translate-x-1 active:scale-95 text-xs font-bold uppercase tracking-wider"
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={cn("w-5 h-5", isActive ? "text-primary dark:text-white" : "text-slate-400 group-hover:text-slate-600 transition-colors")} />
                <span className={cn("text-xs transition-colors", isActive ? "" : "opacity-80")}>{item.name}</span>
                {isActive && <div className="absolute left-0 w-1 h-1/2 bg-primary rounded-full" />}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto px-4 py-5 bg-white dark:bg-slate-800 rounded-2xl border border-outline-variant/10 shadow-sm flex-shrink-0">
        <p className="text-[10px] font-black text-on-tertiary-container uppercase tracking-widest mb-3 opacity-60">Market Sentiment</p>
        <div className="flex items-center justify-between gap-4">
          <div className="h-2.5 flex-1 bg-surface-container-high rounded-full overflow-hidden shadow-inner">
            <div 
              className="h-full bg-secondary rounded-full shadow-lg shadow-secondary/20 transition-all duration-1000" 
              style={{ width: '72%' }}
            />
          </div>
          <span className="text-xs font-black text-secondary">72%</span>
        </div>
      </div>
    </aside>
  )
}
