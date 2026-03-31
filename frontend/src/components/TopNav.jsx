import { NavLink } from 'react-router-dom'
import { Search, Settings, HelpCircle, Bell, Globe } from 'lucide-react'

export default function TopNav() {
  return (
    <nav className="fixed top-0 w-full h-16 z-50 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl border-b border-slate-200/50 dark:border-slate-800/50 shadow-sm font-['Inter'] antialiased">
      <div className="flex items-center justify-between px-6 h-full max-w-screen-2xl mx-auto">
        <div className="flex items-center gap-12">
          <div className="text-xl font-black tracking-tight text-slate-900 dark:text-slate-50 flex items-center gap-2 select-none group">
            <div className="w-8 h-8 rounded-lg bg-primary-container flex items-center justify-center text-white scale-90 group-hover:scale-100 transition-transform shadow-md shadow-primary-container/30">SI</div>
            StockIntel
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm">
            {[
              { name: 'Dashboard', path: '/dashboard' },
              { name: 'Radar', path: '/radar' },
              { name: 'Portfolio', path: '/portfolio' },
              { name: 'Alerts', path: '/alerts' },
            ].map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `font-semibold pb-1 transition-all duration-200 group relative ${
                    isActive
                      ? 'text-slate-900 dark:text-white border-b-2 border-slate-900 dark:border-slate-50 scale-105 px-2'
                      : 'text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-slate-200 hover:scale-105 active:scale-95'
                  }`
                }
              >
                {item.name}
                <div className="absolute inset-0 bg-slate-100/30 opacity-0 group-hover:opacity-100 dark:bg-white/10 rounded-lg -m-2 -z-10 transition-opacity" />
              </NavLink>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center bg-surface-container-low px-3 py-1.5 rounded-xl border border-outline-variant/5 shadow-sm focus-within:ring-2 focus-within:ring-primary-container/10 transition-all group overflow-hidden">
            <Search className="w-4 h-4 text-outline group-focus-within:text-primary-container transition-colors" />
            <input 
              type="text" 
              placeholder="Quick search..." 
              className="bg-transparent border-none focus:ring-0 text-xs w-40 placeholder:text-outline font-medium"
            />
          </div>
          
          <div className="flex items-center gap-1">
            <button className="p-2.5 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 rounded-xl transition-all active:scale-95 text-slate-500 group relative">
              <Bell className="w-4 h-4 group-hover:text-primary transition-colors" />
              <div className="absolute top-2.5 right-2.5 w-1.5 h-1.5 bg-error rounded-full ring-2 ring-white dark:ring-slate-950" />
            </button>
            <button className="p-2.5 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 rounded-xl transition-all active:scale-95 text-slate-500 group">
              <Settings className="w-4 h-4 group-hover:text-primary transition-colors" />
            </button>
          </div>
          
          <div className="flex items-center gap-3 pl-3 ml-2 border-l border-outline-variant/10">
            <div className="text-right hidden sm:block leading-none">
              <p className="text-xs font-bold text-slate-900 dark:text-slate-50 mb-0.5">Analyst Tier</p>
              <p className="text-[10px] uppercase font-black tracking-widest text-slate-400">NSE / BSE</p>
            </div>
            <div className="w-9 h-9 rounded-full bg-slate-200 overflow-hidden ring-2 ring-white dark:ring-slate-950 border border-outline-variant/10 shadow-sm cursor-pointer active:scale-90 transition-all">
              <img 
                src="/assets/avatar.png" 
                alt="Profile" 
                className="w-full h-full object-cover"
                onError={(e) => { e.target.onerror = null; e.target.src = 'https://ui-avatars.com/api/?name=Analyst&background=1e293b&color=fff&size=96'; }}
              />
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}
