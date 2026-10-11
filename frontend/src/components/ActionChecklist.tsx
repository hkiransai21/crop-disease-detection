import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { CheckSquare, ShieldCheck, Leaf, FlaskConical, AlertTriangle, ExternalLink, UserCheck } from 'lucide-react';
import { DiseaseEntry } from '../types';

interface ActionChecklistProps {
  disease: DiseaseEntry;
}

export const ActionChecklist: React.FC<ActionChecklistProps> = ({ disease }) => {
  const { t } = useTranslation();
  const [activeTab, setActiveTab] = useState<'cultural' | 'organic' | 'chemical'>('cultural');

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 md:p-6 space-y-5">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-brand-600" />
          <h3 className="text-lg font-bold text-slate-900">{t('result.actions_title')}</h3>
        </div>
        <span className="text-xs font-semibold text-slate-500 bg-slate-100 px-2.5 py-1 rounded-full">
          Curated University Guidance
        </span>
      </div>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-slate-100 pb-2">
        <button
          onClick={() => setActiveTab('cultural')}
          className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'cultural'
              ? 'bg-brand-600 text-white shadow-sm shadow-brand-600/20'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <CheckSquare className="w-4 h-4" />
          <span>{t('result.cultural_tab')}</span>
        </button>

        <button
          onClick={() => setActiveTab('organic')}
          className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'organic'
              ? 'bg-brand-600 text-white shadow-sm shadow-brand-600/20'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <Leaf className="w-4 h-4" />
          <span>{t('result.organic_tab')}</span>
        </button>

        <button
          onClick={() => setActiveTab('chemical')}
          className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-bold transition-all ${
            activeTab === 'chemical'
              ? 'bg-brand-600 text-white shadow-sm shadow-brand-600/20'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          <FlaskConical className="w-4 h-4" />
          <span>{t('result.chemical_tab')}</span>
        </button>
      </div>

      {/* Tab Content */}
      <div className="space-y-3 min-h-[140px]">
        {activeTab === 'cultural' && (
          <div className="space-y-2.5">
            <ul className="space-y-2">
              {disease.prevention_steps.map((step, idx) => (
                <li key={idx} className="flex items-start space-x-2.5 text-xs text-slate-700 bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                  <span className="w-5 h-5 rounded-full bg-brand-100 text-brand-800 flex items-center justify-center font-bold text-[11px] shrink-0 mt-0.5">
                    {idx + 1}
                  </span>
                  <span className="leading-relaxed">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'organic' && (
          <div className="space-y-2.5">
            <ul className="space-y-2">
              {disease.organic_controls.map((step, idx) => (
                <li key={idx} className="flex items-start space-x-2.5 text-xs text-slate-700 bg-emerald-50/50 p-2.5 rounded-xl border border-emerald-100">
                  <Leaf className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {activeTab === 'chemical' && (
          <div className="space-y-2.5">
            <ul className="space-y-2">
              {disease.chemical_controls.map((step, idx) => (
                <li key={idx} className="flex items-start space-x-2.5 text-xs text-slate-700 bg-blue-50/50 p-2.5 rounded-xl border border-blue-100">
                  <FlaskConical className="w-4 h-4 text-blue-600 shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{step}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Escalation to Extension Officer */}
      <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200 flex items-start space-x-2.5 text-xs text-slate-700">
        <UserCheck className="w-4 h-4 text-brand-600 shrink-0 mt-0.5" />
        <div>
          <span className="font-bold text-slate-900">{t('result.consult_expert_title')}: </span>
          <span>{disease.when_to_consult_expert}</span>
        </div>
      </div>

      {/* Mandatory Safety Box */}
      <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-950 space-y-2 text-xs">
        <div className="flex items-center space-x-2 font-bold text-rose-900">
          <AlertTriangle className="w-4 h-4 text-rose-600" />
          <span>{t('result.safety_title')}</span>
        </div>
        <ul className="list-disc list-inside space-y-1 text-rose-900 text-[11px] leading-relaxed">
          {disease.safety_notes.map((note, idx) => (
            <li key={idx}>{note}</li>
          ))}
        </ul>
      </div>

      {/* Cited Sources */}
      {disease.sources && disease.sources.length > 0 && (
        <div className="pt-2 border-t border-slate-100 space-y-1">
          <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">{t('result.sources_title')}</span>
          <div className="space-y-1">
            {disease.sources.map((src, idx) => (
              <div key={idx} className="flex items-center space-x-1.5 text-[11px] text-slate-500">
                <ExternalLink className="w-3 h-3 text-slate-400" />
                <span className="truncate">{src}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
