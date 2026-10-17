import { tr } from '../i18n/i18n';
import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Shield, Info, AlertTriangle, Cpu, Database, CheckCircle2, Layers, BookOpen, Lock, PhoneCall } from 'lucide-react';
import { api } from '../api/client';

export const AboutPage: React.FC = () => {
  const { t } = useTranslation();
  const [modelInfo, setModelInfo] = useState<any>(null);

  useEffect(() => {
    api
      .getModelInfo()
      .then((data) => setModelInfo(data))
      .catch((err) => console.error(err));
  }, []);

  return (
    <div className="max-w-4xl mx-auto py-6 space-y-10">
      {/* Title */}
      <div className="space-y-2 text-center max-w-2xl mx-auto">
        <div className="w-12 h-12 rounded-2xl bg-brand-100 text-brand-700 flex items-center justify-center mx-auto">
          <Shield className="w-6 h-6" />
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900">
          {t('about_page.title')}
        </h1>
        <p className="text-xs sm:text-sm text-slate-500">
          {t('about_page.subtitle')}
        </p>
      </div>

      {/* Model Overview Box */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Cpu className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">{tr('ui.s_acaf6737da')}</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{tr('ui.s_c5c821ded7')}</span>
            <p className="text-sm font-bold text-slate-900">{tr('ui.s_b5789ad0bc')}</p>
            <span className="text-[11px] text-slate-500">{tr('ui.s_be3c2126e9')}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{tr('ui.s_fe961af9d8')}</span>
            <p className="text-sm font-bold text-slate-900">{tr('ui.s_17aaea2858')}</p>
            <span className="text-[11px] text-slate-500">{tr('ui.s_177075af3d')}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{tr('ui.s_cdca30cf0d')}</span>
            <p className="text-sm font-bold text-slate-900">{tr('ui.s_40bfb032d0')}</p>
            <span className="text-[11px] text-slate-500">{tr('ui.s_0e1171b474')}</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">{tr('ui.s_f5ed075f00')}</span>
            <p className="text-sm font-bold text-slate-900">{tr('ui.s_0dca369ebf')}</p>
            <span className="text-[11px] text-slate-500">{tr('ui.s_960d84092e')}</span>
          </div>
        </div>

        {modelInfo && (
          <div className="p-4 rounded-xl bg-brand-50/50 border border-brand-100 text-xs space-y-2">
            <span className="font-bold text-brand-900">{tr('ui.s_79b990023f')}{modelInfo.model_version}</span>
            <p className="text-slate-600 text-[11px]">
              {tr('ui.s_7c150d36b4')}</p>
          </div>
        )}
      </div>

      {/* Lab vs Field Generalization Gap */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Database className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">{tr('ui.s_8f0c87a7dd')}</h2>
        </div>

        <div className="space-y-3 text-xs text-slate-700 leading-relaxed">
          <p>
            <strong>{tr('ui.s_2a0f13695d')}</strong> {tr('ui.s_ab877d07e7')}</p>
          <p>
            <strong>{tr('ui.s_ee08245b74')}</strong> {tr('ui.s_7afc59bed1')}</p>
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-950 space-y-1.5">
            <span className="font-bold text-amber-900">{tr('ui.s_5cc6fd5a0b')}</span>
            <p className="text-[11px] leading-relaxed">
              {tr('ui.s_5a59600e77')}</p>
          </div>
        </div>
      </div>

      {/* Privacy & EXIF Stripping */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Lock className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">{tr('ui.s_7d4bcff067')}</h2>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          {tr('ui.s_2ff168e676')}</p>
      </div>

      {/* Mandatory Safety Notice */}
      <div className="p-6 rounded-3xl bg-rose-50 border border-rose-200 text-rose-950 space-y-3">
        <div className="flex items-center space-x-2.5 font-bold text-rose-900">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
          <h3 className="text-base">{tr('ui.s_f93a83907c')}</h3>
        </div>
        <ul className="list-disc list-inside space-y-1.5 text-xs text-rose-900 leading-relaxed">
          <li><strong>{tr('ui.s_da1d761402')}</strong> {tr('ui.s_825462fc16')}</li>
          <li><strong>{tr('ui.s_639e4ef1fd')}</strong> {tr('ui.s_77db47a730')}</li>
          <li><strong>{tr('ui.s_47709278f3')}</strong> {tr('ui.s_8a70460c60')}</li>
        </ul>
      </div>
    </div>
  );
};
