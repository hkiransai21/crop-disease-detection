import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { History, Trash2, Calendar, MapPin, AlertCircle, CheckCircle2, Search, Sprout, ArrowRight, ExternalLink } from 'lucide-react';
import { api } from '../api/client';
import { AnalysisHistoryItem, User } from '../types';

interface HistoryPageProps {
  user: User | null;
}

export const HistoryPage: React.FC<HistoryPageProps> = ({ user }) => {
  const navigate = useNavigate();
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterCrop, setFilterCrop] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteTargetId, setDeleteTargetId] = useState<string | null>(null);

  useEffect(() => {
    if (!user) {
      setLoading(false);
      return;
    }

    setLoading(true);
    api
      .getHistory(100)
      .then((data) => setHistory(data))
      .catch((err) => setError(err.message || 'Failed to load diagnosis history.'))
      .finally(() => setLoading(false));
  }, [user]);

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await api.deleteHistory(id);
      setHistory(history.filter((item) => item.id !== id));
      setDeleteTargetId(null);
    } catch (err: any) {
      alert(err.message || 'Failed to delete record.');
    }
  };

  if (!user) {
    return (
      <div className="max-w-md mx-auto py-16 text-center space-y-4">
        <div className="w-16 h-16 rounded-2xl bg-brand-100 text-brand-700 flex items-center justify-center mx-auto">
          <History className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-900">Diagnosis History</h2>
        <p className="text-xs text-slate-500 leading-relaxed">
          Sign in or register for a free farm account to store, track, and review your historical leaf analyses over time.
        </p>
        <div className="pt-2">
          <Link
            to="/auth"
            className="inline-flex items-center space-x-2 px-6 py-3 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-md shadow-brand-600/20"
          >
            <span>Sign In / Create Account</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  const filteredHistory = history.filter((item) => {
    const matchesCrop = filterCrop ? item.crop.toLowerCase() === filterCrop.toLowerCase() : true;
    const matchesQuery = searchQuery
      ? item.disease_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        item.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (item.location_name && item.location_name.toLowerCase().includes(searchQuery.toLowerCase()))
      : true;
    return matchesCrop && matchesQuery;
  });

  const uniqueCrops = Array.from(new Set(history.map((h) => h.crop))).filter(Boolean);

  return (
    <div className="max-w-5xl mx-auto py-6 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900">My Diagnosis History</h1>
          <p className="text-xs text-slate-500">Track disease progression across your fields and seasons</p>
        </div>

        <Link
          to="/analyze"
          className="self-start sm:self-auto inline-flex items-center space-x-2 px-4 py-2 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold shadow-sm"
        >
          <Sprout className="w-4 h-4" />
          <span>New Diagnosis</span>
        </Link>
      </div>

      {/* Filters Bar */}
      <div className="flex flex-col sm:flex-row gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-sm">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search disease, crop, or place..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-500 bg-slate-50"
          />
        </div>

        {uniqueCrops.length > 0 && (
          <select
            value={filterCrop}
            onChange={(e) => setFilterCrop(e.target.value)}
            className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 focus:outline-none focus:border-brand-500 bg-slate-50"
          >
            <option value="">All Crops ({history.length})</option>
            {uniqueCrops.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        )}
      </div>

      {/* History Grid */}
      {loading ? (
        <div className="py-20 text-center space-y-2">
          <div className="w-10 h-10 border-4 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-semibold text-slate-500">Loading your farm records...</p>
        </div>
      ) : filteredHistory.length === 0 ? (
        <div className="py-16 text-center space-y-3 bg-white rounded-3xl border border-slate-200 p-8">
          <div className="w-14 h-14 rounded-2xl bg-slate-100 text-slate-400 flex items-center justify-center mx-auto">
            <Sprout className="w-7 h-7" />
          </div>
          <h3 className="text-base font-bold text-slate-800">No diagnosis records found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {searchQuery || filterCrop
              ? 'No diagnoses match your search filter criteria.'
              : 'You have not scanned any crop leaves yet.'}
          </p>
          <div className="pt-2">
            <Link
              to="/analyze"
              className="inline-flex items-center space-x-2 px-5 py-2.5 rounded-xl bg-brand-600 text-white text-xs font-bold"
            >
              <span>Scan Your First Leaf</span>
            </Link>
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredHistory.map((item) => {
            const isHealthy = item.predicted_label.toLowerCase().includes('healthy');
            return (
              <div
                key={item.id}
                onClick={() => navigate(`/result/${item.id}`)}
                className="bg-white rounded-2xl border border-slate-200/90 hover:border-brand-400 shadow-sm hover:shadow-md transition-all p-4 cursor-pointer flex flex-col justify-between space-y-3 group"
              >
                <div className="space-y-3">
                  {/* Thumbnail & Badges */}
                  <div className="relative aspect-video rounded-xl overflow-hidden bg-slate-900 flex items-center justify-center">
                    <img
                      src={item.image_url}
                      alt={item.disease_name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />

                    <div className="absolute top-2 left-2 flex gap-1">
                      <span className="px-2 py-0.5 rounded-md bg-black/60 backdrop-blur-sm text-white text-[10px] font-bold">
                        {item.crop}
                      </span>
                    </div>

                    <div className="absolute top-2 right-2">
                      {isHealthy ? (
                        <span className="px-2 py-0.5 rounded-md bg-emerald-600 text-white text-[10px] font-bold flex items-center space-x-1">
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Healthy</span>
                        </span>
                      ) : item.is_uncertain ? (
                        <span className="px-2 py-0.5 rounded-md bg-amber-500 text-white text-[10px] font-bold flex items-center space-x-1">
                          <AlertCircle className="w-3 h-3" />
                          <span>Uncertain</span>
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 rounded-md bg-slate-900/80 backdrop-blur-sm text-white text-[10px] font-bold">
                          {Math.round(item.confidence * 100)}% Conf
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Disease Details */}
                  <div>
                    <h4 className="text-sm font-bold text-slate-900 group-hover:text-brand-700 transition-colors">
                      {item.disease_name}
                    </h4>
                    {item.location_name && (
                      <p className="text-[11px] text-slate-500 flex items-center space-x-1 mt-1 truncate">
                        <MapPin className="w-3 h-3 text-slate-400 shrink-0" />
                        <span className="truncate">{item.location_name}</span>
                      </p>
                    )}
                  </div>
                </div>

                {/* Footer Sub-bar */}
                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-400">
                  <span className="flex items-center space-x-1">
                    <Calendar className="w-3 h-3" />
                    <span>{new Date(item.created_at).toLocaleDateString()}</span>
                  </span>

                  <div className="flex items-center space-x-2">
                    {item.has_feedback && (
                      <span className="px-1.5 py-0.5 rounded bg-brand-50 text-brand-700 font-semibold text-[10px]">
                        Verified
                      </span>
                    )}

                    <button
                      onClick={(e) => handleDelete(item.id, e)}
                      className="p-1 text-slate-400 hover:text-rose-600 transition-colors"
                      title="Delete diagnosis record"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
