import { Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import TopNav from './components/TopNav';
import Dashboard from './pages/Dashboard';
import Radar from './pages/Radar';
import Analysis from './pages/Analysis';
import Portfolio from './pages/Portfolio';
import Alerts from './pages/Alerts';

function App() {
  return (
    <div className="min-h-screen bg-surface flex flex-col">
      <TopNav />
      <div className="flex flex-1 pt-16">
        <Sidebar className="hidden lg:flex w-52 fixed left-0 top-16 bottom-0" />
        <main className="flex-1 lg:pl-52 p-6 overflow-y-auto">
          <div className="max-w-screen-2xl mx-auto">
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/radar" element={<Radar />} />
              <Route path="/analysis" element={<Analysis />} />
              <Route path="/portfolio" element={<Portfolio />} />
              <Route path="/alerts" element={<Alerts />} />
            </Routes>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
