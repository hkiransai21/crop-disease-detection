import { tr } from '../i18n/i18n';
import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import {
  Sprout,
  BookOpen,
  ArrowRight,
  AlertTriangle,
  Cpu
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { t } = useTranslation();

  const supportedCrops = [
    'Apple', 'Blueberry', 'Cherry', tr('ui.s_7740e59458'), 'Grape',
    tr('ui.s_acb025cb5f'), 'Peach', tr('ui.s_12cd9a115f'), 'Potato', 'Raspberry',
    'Soybean', 'Squash', 'Strawberry', 'Tomato'
  ];

  return (
    <div className="space-y-16 py-6 md:py-10">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-brand-950 via-brand-900 to-slate-900 text-white p-8 md:p-14 shadow-xl border border-brand-800/40">
        <div className="absolute -right-16 -bottom-16 w-96 h-96 bg-brand-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="absolute -left-16 -top-16 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="max-w-3xl space-y-6 relative z-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-brand-500/20 border border-brand-400/30 text-brand-300 text-xs font-bold uppercase tracking-wider backdrop-blur-md">
            <Cpu className="w-3.5 h-3.5" />
            <span>{t('hero.badge')}</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold tracking-tight leading-tight">
            {t('hero.title')}
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed max-w-2xl">
            {t('hero.subtitle')}
          </p>

          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-4">
            <Link
              to="/analyze"
              className="flex items-center justify-center space-x-2.5 px-6 py-4 rounded-2xl bg-brand-500 hover:bg-brand-400 text-slate-950 font-extrabold text-base shadow-lg shadow-brand-500/30 transition-all hover:scale-[1.02] active:scale-98"
            >
              <Sprout className="w-5 h-5 text-slate-950" />
              <span>{t('hero.cta_start')}</span>
              <ArrowRight className="w-4 h-4 text-slate-950" />
            </Link>

            <Link
              to="/diseases"
              className="flex items-center justify-center space-x-2 px-6 py-4 rounded-2xl bg-white/10 hover:bg-white/15 border border-white/15 text-white font-bold text-base transition-colors"
            >
              <BookOpen className="w-5 h-5 text-slate-300" />
              <span>{t('hero.cta_guide')}</span>
            </Link>
          </div>
        </div>
      </section>

      {/* How it Works (3-Step Farmer Flow) */}
      <section className="space-y-8">
        <div className="text-center max-w-2xl mx-auto space-y-2">
          <h2 className="text-2xl sm:text-3xl font-bold text-slate-900">{t('hero.how_title')}</h2>
          <p className="text-sm text-slate-500">
            {t('hero.how_subtitle')}
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4 hover:border-brand-300 transition-colors">
            <div className="w-12 h-12 rounded-2xl bg-brand-50 text-brand-700 flex items-center justify-center font-bold text-lg border border-brand-100">
              {tr('ui.s_356a192b79')}</div>
            <h3 className="text-lg font-bold text-slate-900">{t('hero.step1_title')}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t('hero.step1_desc')}
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4 hover:border-brand-300 transition-colors">
            <div className="w-12 h-12 rounded-2xl bg-amber-50 text-amber-700 flex items-center justify-center font-bold text-lg border border-amber-100">
              {tr('ui.s_da4b9237ba')}</div>
            <h3 className="text-lg font-bold text-slate-900">{t('hero.step2_title')}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t('hero.step2_desc')}
            </p>
          </div>

          <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-sm space-y-4 hover:border-brand-300 transition-colors">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center font-bold text-lg border border-emerald-100">
              {tr('ui.s_77de68daec')}</div>
            <h3 className="text-lg font-bold text-slate-900">{t('hero.step3_title')}</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              {t('hero.step3_desc')}
            </p>
          </div>
        </div>
      </section>

      {/* Supported Crops */}
      <section className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
          <div>
            <h3 className="text-lg font-bold text-slate-900">{tr('ui.s_8e0ab8050a')}</h3>
            <p className="text-xs text-slate-500">{tr('ui.s_97fc43750e')}</p>
          </div>
          <span className="text-xs font-bold text-brand-700 bg-brand-50 px-3 py-1 rounded-full self-start sm:self-auto">
            {tr('ui.s_ee2f9362bf')}</span>
        </div>

        <div className="flex flex-wrap gap-2">
          {supportedCrops.map((crop, idx) => (
            <span
              key={idx}
              className="px-3.5 py-1.5 rounded-xl bg-slate-50 border border-slate-200 text-xs font-bold text-slate-800 hover:bg-brand-50 hover:border-brand-200 transition-colors"
            >
              {crop}
            </span>
          ))}
        </div>
      </section>

      {/* Safety & Advisory Disclaimer Banner */}
      <section className="p-6 rounded-2xl bg-amber-50/80 border border-amber-200/80 text-amber-950 flex flex-col sm:flex-row items-start sm:items-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center shrink-0">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="space-y-1 text-xs">
          <h4 className="font-bold text-amber-900 text-sm">{tr('ui.s_0db19550bc')}</h4>
          <p className="leading-relaxed text-amber-900/90 text-[11px]">
            {t('footer.disclaimer')}
          </p>
        </div>
      </section>
    </div>
  );
};
