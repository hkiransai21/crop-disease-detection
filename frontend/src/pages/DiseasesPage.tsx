import { tr } from '../i18n/i18n';
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { BookOpen, Search, Filter, Leaf, Bug, FlaskConical, ExternalLink, ChevronRight, X, ShieldCheck } from 'lucide-react';
import { api } from '../api/client';
import { DiseaseEntry } from '../types';

export const DiseasesPage: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [diseases, setDiseases] = useState<DiseaseEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCrop, setSelectedCrop] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeModalEntry, setActiveModalEntry] = useState<DiseaseEntry | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setActiveModalEntry(null);
    setSelectedCrop('');
    api
      .getDiseases(undefined, undefined, i18n.language)
      .then((data) => { if (!cancelled) setDiseases(data); })
      .catch((err) => console.error(err))
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [i18n.language]);

  const uniqueCrops = Array.from(new Set(diseases.map((d) => d.crop))).filter(Boolean);
  const uniqueAgents = ['fungal', 'bacterial', 'viral', 'pest', 'none'];

  const filteredDiseases = diseases.filter((d) => {
    const matchesCrop = selectedCrop ? d.crop.toLowerCase() === selectedCrop.toLowerCase() : true;
    const matchesAgent = selectedAgent ? d.causal_agent_type.toLowerCase() === selectedAgent.toLowerCase() : true;
    const matchesSearch = searchQuery
      ? d.disease_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.crop.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (d.scientific_name && d.scientific_name.toLowerCase().includes(searchQuery.toLowerCase())) ||
        d.symptoms.toLowerCase().includes(searchQuery.toLowerCase())
      : true;
    return matchesCrop && matchesAgent && matchesSearch;
  });

  return (
    <div className="max-w-6xl mx-auto py-6 space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">{t('diseases_page.title')}</h1>
        <p className="text-xs sm:text-sm text-slate-500">
          {t('diseases_page.subtitle')}
        </p>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-col sm:flex-row gap-3 bg-white p-3 rounded-2xl border border-slate-200 shadow-sm">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder={t('diseases_page.search_placeholder')}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-9 pr-3 py-2 rounded-xl border border-slate-200 text-xs text-slate-900 focus:outline-none focus:border-brand-500 bg-slate-50"
          />
        </div>

        <select
          value={selectedCrop}
          onChange={(e) => setSelectedCrop(e.target.value)}
          className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 focus:outline-none focus:border-brand-500 bg-slate-50"
        >
          <option value="">{t('diseases_page.all_crops')} ({uniqueCrops.length})</option>
          {uniqueCrops.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>

        <select
          value={selectedAgent}
          onChange={(e) => setSelectedAgent(e.target.value)}
          className="px-3 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 focus:outline-none focus:border-brand-500 bg-slate-50"
        >
          <option value="">{t('diseases_page.all_agents')}</option>
          {uniqueAgents.map((a) => (
            <option key={a} value={a}>
              {t(`agents.${a}`)}
            </option>
          ))}
        </select>
      </div>

      {/* Diseases Grid */}
      {loading ? (
        <div className="py-20 text-center space-y-2">
          <div className="w-10 h-10 border-4 border-brand-600 border-t-transparent rounded-full animate-spin mx-auto"></div>
          <p className="text-xs font-semibold text-slate-500">{t('diseases_page.loading')}</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredDiseases.map((entry) => {
            const isHealthy = entry.is_healthy;
            return (
              <div
                key={entry.id}
                onClick={() => setActiveModalEntry(entry)}
                className="bg-white rounded-2xl border border-slate-200/90 hover:border-brand-400 p-5 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-800 text-[10px] font-bold uppercase tracking-wider border border-brand-100">
                      {entry.crop}
                    </span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                      isHealthy
                        ? 'bg-emerald-100 text-emerald-800'
                        : entry.causal_agent_type === 'fungal'
                        ? 'bg-amber-100 text-amber-800'
                        : entry.causal_agent_type === 'bacterial'
                        ? 'bg-blue-100 text-blue-800'
                        : entry.causal_agent_type === 'viral'
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-slate-100 text-slate-700'
                    }`}>
                      {t(`agents.${entry.causal_agent_type}`)}
                    </span>
                  </div>

                  <div>
                    <h3 className="text-sm font-bold text-slate-900 group-hover:text-brand-700 transition-colors">
                      {entry.disease_name}
                    </h3>
                    {entry.scientific_name && (
                      <p className="text-[11px] text-slate-400 italic truncate">{entry.scientific_name}</p>
                    )}
                  </div>

                  <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                    {entry.symptoms}
                  </p>
                </div>

                <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-xs text-brand-700 font-bold">
                  <span>{tr('ui.s_9090697f4f')}</span>
                  <ChevronRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Full Monograph Modal */}
      {activeModalEntry && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto p-6 md:p-8 shadow-2xl border border-slate-200 space-y-6">
            <div className="flex items-start justify-between border-b border-slate-100 pb-4">
              <div className="space-y-1">
                <span className="px-2.5 py-0.5 rounded-full bg-brand-50 text-brand-800 text-[10px] font-bold uppercase tracking-wider">
                  {activeModalEntry.crop}
                </span>
                <h2 className="text-xl font-bold text-slate-900">{activeModalEntry.disease_name}</h2>
                {activeModalEntry.scientific_name && (
                  <p className="text-xs text-slate-500 italic">{tr('ui.s_1f25584166')}{activeModalEntry.scientific_name}</p>
                )}
              </div>
              <button
                onClick={() => setActiveModalEntry(null)}
                className="p-1 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Diagnostic Symptoms */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{tr('ui.s_aee3645a0a')}</h4>
              <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-xl border border-slate-100">
                {activeModalEntry.symptoms}
              </p>
            </div>

            {/* Dissemination & Weather */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 text-xs space-y-1">
                <span className="font-bold text-slate-800">{tr('ui.s_24a52d94a1')}</span>
                <p className="text-slate-600 text-[11px] leading-relaxed">{activeModalEntry.spread_mechanism}</p>
              </div>

              <div className="p-3 rounded-xl bg-amber-50/60 border border-amber-200/70 text-xs space-y-1 text-amber-950">
                <span className="font-bold text-amber-900">{tr('ui.s_63320dac33')}</span>
                <p className="text-[11px] leading-relaxed">
                  {tr('ui.s_fa0c175254')}{activeModalEntry.favorable_conditions.temp_min_c}{tr('ui.s_3f18a82d78')}{activeModalEntry.favorable_conditions.temp_max_c}{tr('ui.s_6acf1c5ccb')}{activeModalEntry.favorable_conditions.temp_optimal_c ?? 'N/A'}{tr('ui.s_70a5bedac4')}{activeModalEntry.favorable_conditions.humidity_min_pct}%
                </p>
              </div>
            </div>

            {/* Prevention Steps */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{tr('ui.s_3b9d6d10f3')}</h4>
              <ul className="list-disc list-inside space-y-1 text-xs text-slate-700">
                {activeModalEntry.prevention_steps.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ul>
            </div>

            {/* Organic Controls */}
            {activeModalEntry.organic_controls.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{tr('ui.s_faa55775b7')}</h4>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-700">
                  {activeModalEntry.organic_controls.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Chemical Controls */}
            {activeModalEntry.chemical_controls.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">{tr('ui.s_4452fa9d4f')}</h4>
                <ul className="list-disc list-inside space-y-1 text-xs text-slate-700">
                  {activeModalEntry.chemical_controls.map((s, i) => (
                    <li key={i}>{s}</li>
                  ))}
                </ul>
              </div>
            )}

            <p className="bg-amber-50 p-3 rounded-xl text-sm leading-relaxed">{activeModalEntry.safety_notice}</p>
            <p className="text-xs text-slate-600">{tr('ui.s_8ab0919883')}</p>
            {/* Extension Sources */}
            {activeModalEntry.sources.length > 0 && (
              <div className="pt-2 border-t border-slate-100 space-y-1">
                <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{tr('ui.s_f6e5bfc882')}</span>
                <div className="space-y-1">
                  {activeModalEntry.sources.map((src, i) => (
                    <div key={i} className="flex items-center space-x-1.5 text-[11px] text-slate-500">
                      <ExternalLink className="w-3 h-3 text-slate-400" />
                      <span className="break-words">{src}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={() => setActiveModalEntry(null)}
                className="px-5 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold"
              >
                {tr('ui.s_2573d13e0e')}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
