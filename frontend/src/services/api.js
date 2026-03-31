import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const analyzeStock = async (symbol, timeframe = '1d') => {
  const { data } = await api.post('/analyze', { symbol, timeframe });
  return data;
};

export const getRadarData = async (symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ITC']) => {
  const { data } = await api.post('/radar', { symbols });
  return data.results;
};

export const getPortfolios = async () => {
  const { data } = await api.get('/portfolio');
  return data;
};

export const getAlerts = async () => {
  const { data } = await api.get('/alerts');
  return data;
};

export const updateAlertStatus = async (alertId, status) => {
  const { data } = await api.patch(`/alerts/${alertId}`, { status });
  return data;
};

export const getRecentAnalyses = async () => {
  const { data } = await api.get('/analyses');
  return data;
};

export default api;
