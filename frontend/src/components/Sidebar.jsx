import { NavLink } from 'react-router-dom'
import { Activity, PieChart, BrainCircuit, Wallet, Bell } from 'lucide-react'
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
    <aside className={cn(
      "flex flex-col border-r border-slate-200/60 bg-white/95 backdrop-blur-sm p-3 gap-2 h-full",
      className
    )}>
      {/* Brand */}
      <div className="flex items-center gap-2.5 px-2 py-3 mb-1 flex-shrink-0">
        <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-white shadow-md shadow-primary-container/30 flex-shrink-0">
          <BrainCircuit className="w-4 h-4" />
        </div>
        <div>
          <p className="font-black text-sm text-slate-900 leading-tight">Intelligence</p>
          <p className="text-[9px] uppercase tracking-widest text-slate-400 font-semibold">Domestic Tier</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-0.5 overflow-y-auto">
        <p className="text-[9px] font-black uppercase tracking-widest text-slate-400 px-3 py-1 mb-1">Navigation</p>
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2.5 px-3 py-2.5 rounded-xl transition-all duration-150 group w-full",
                isActive
                  ? "bg-slate-900 text-white shadow-sm"
                  : "text-slate-500 hover:bg-slate-100 hover:text-slate-800"
              )
            }
          >
            {({ isActive }) => (
              <>
                <item.icon className={cn("w-4 h-4 flex-shrink-0", isActive ? "text-white" : "text-slate-400 group-hover:text-slate-600")} />
                <span className={cn("text-xs font-semibold truncate", isActive ? "text-white" : "")}>
                  {item.name}
                </span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white/50 flex-shrink-0" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Market Sentiment */}
      <div className="mt-auto flex-shrink-0 px-3 py-4 bg-slate-50 rounded-xl border border-slate-200/80">
        <p className="text-[9px] font-black text-slate-400 uppercase tracking-widest mb-2">Market Mood</p>
        <div className="flex items-center justify-between gap-3 mb-1.5">
          <div className="h-1.5 flex-1 bg-slate-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-emerald-500 rounded-full transition-all duration-1000"
              style={{ width: '72%' }}
            />
          </div>
          <span className="text-xs font-black text-emerald-600 flex-shrink-0">72%</span>
        </div>
        <p className="text-[9px] text-slate-400 font-medium">Bullish Bias — NSE</p>
      </div>
    </aside>
  )
}
