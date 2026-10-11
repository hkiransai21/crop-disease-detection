import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  Droplet,
  Beaker,
  Scale,
  Sparkles,
  SunMedium,
  CheckCircle2,
  Wind,
  Layers
} from 'lucide-react';
import { DiseaseEntry } from '../types';

interface KnapsackCalculatorProps {
  disease: DiseaseEntry;
  cropName: string;
}

export const KnapsackCalculator: React.FC<KnapsackCalculatorProps> = ({ disease, cropName }) => {
  const { t } = useTranslation();
  const isHealthy = disease.is_healthy;

  // Selected Tank Size (Liters)
  const [tankSize, setTankSize] = useState<number>(15);
  // Number of Tanks to prepare
  const [numTanks, setNumTanks] = useState<number>(1);
  // Treatment Type
  const [treatmentMode, setTreatmentMode] = useState<'organic' | 'chemical'>('organic');

  if (isHealthy) {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-3xl p-5 text-emerald-900 flex items-center space-x-3.5">
        <div className="w-10 h-10 rounded-2xl bg-emerald-200/80 flex items-center justify-center text-emerald-800 shrink-0">
          <CheckCircle2 className="w-6 h-6" />
        </div>
        <div>
          <h4 className="text-sm font-bold">{t('result.calc_healthy_notice')}</h4>
          <p className="text-xs text-emerald-700">
            {cropName}: {t('result.calc_healthy_notice')}
          </p>
        </div>
      </div>
    );
  }

  // Baseline standard dosages per liter based on mode
  // Organic: 5ml / Liter (e.g. Neem Oil 1500ppm or bio-agent)
  // Chemical: 2.5g / Liter (standard for protective fungicides like Mancozeb / Copper Oxychloride)
  const dosagePerLiter = treatmentMode === 'organic' ? 5.0 : 2.5;
  const unit = treatmentMode === 'organic' ? 'ml' : 'grams';

  const singleTankQty = dosagePerLiter * tankSize;
  const totalQty = singleTankQty * numTanks;
  const totalWaterLiters = tankSize * numTanks;

  // Spoon / Measuring Cap conversion helper (1 tbsp ≈ 15g powder or 15ml liquid)
  const spoonsPerTank = (singleTankQty / 15).toFixed(1);

  return (
    <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-5 sm:p-6 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
        <div className="flex items-center space-x-2.5">
          <div className="w-9 h-9 rounded-xl bg-blue-100 text-blue-700 flex items-center justify-center">
            <Beaker className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              {t('result.calc_title')}
            </h3>
            <p className="text-xs text-slate-500">
              {t('result.calc_subtitle')}
            </p>
          </div>
        </div>

        <span className="self-start sm:self-auto px-2.5 py-1 rounded-full bg-blue-50 text-blue-800 text-[11px] font-bold">
          Dosage Helper
        </span>
      </div>

      {/* Mode Selection: Organic vs Chemical */}
      <div className="grid grid-cols-2 gap-3">
        <button
          onClick={() => setTreatmentMode('organic')}
          className={`p-3 rounded-2xl border text-left transition-all ${
            treatmentMode === 'organic'
              ? 'bg-emerald-50/80 border-emerald-500 ring-2 ring-emerald-500/20 text-emerald-950'
              : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold">{t('result.calc_organic_mode')}</span>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-emerald-200/70 text-emerald-800">
              Eco-Friendly
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Neem Oil (1500ppm) @ 5ml / Liter
          </p>
        </button>

        <button
          onClick={() => setTreatmentMode('chemical')}
          className={`p-3 rounded-2xl border text-left transition-all ${
            treatmentMode === 'chemical'
              ? 'bg-blue-50/80 border-blue-500 ring-2 ring-blue-500/20 text-blue-950'
              : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold">{t('result.calc_chemical_mode')}</span>
            <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full bg-blue-200/70 text-blue-800">
              Standard
            </span>
          </div>
          <p className="text-[11px] text-slate-500 mt-1">
            Mancozeb 75% WP or Copper Oxychloride @ 2.5g / Liter
          </p>
        </button>
      </div>

      {/* Configuration Controls: Tank Size & Tank Count */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50 p-4 rounded-2xl border border-slate-200/70">
        {/* Tank Size Selector */}
        <div className="space-y-1.5">
          <label className="text-xs font-bold text-slate-700 flex items-center space-x-1.5">
            <Droplet className="w-3.5 h-3.5 text-blue-600" />
            <span>{t('result.calc_tank_size')}:</span>
          </label>
          <div className="grid grid-cols-4 gap-1.5">
            {[10, 15, 16, 20].map((liters) => (
              <button
                key={liters}
                onClick={() => setTankSize(liters)}
                className={`py-2 text-center rounded-xl text-xs font-bold transition-all ${
                  tankSize === liters
                    ? 'bg-blue-600 text-white shadow-sm'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                {liters}L
                {liters === 15 && <span className="block text-[9px] font-normal opacity-90">(Standard)</span>}
              </button>
            ))}
          </div>
        </div>

        {/* Number of Tanks Counter */}
        <div className="space-y-1.5">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700">
            <label className="flex items-center space-x-1.5">
              <Layers className="w-3.5 h-3.5 text-brand-600" />
              <span>{t('result.calc_tank_count')}</span>
            </label>
            <span className="text-[11px] text-brand-700 font-semibold">
              {numTanks === 8 ? '≈ 1 Acre Coverage' : `${numTanks} Tank${numTanks > 1 ? 's' : ''}`}
            </span>
          </div>

          <div className="flex items-center space-x-2">
            {[1, 2, 4, 8].map((count) => (
              <button
                key={count}
                onClick={() => setNumTanks(count)}
                className={`flex-1 py-2 text-center rounded-xl text-xs font-bold transition-all ${
                  numTanks === count
                    ? 'bg-brand-600 text-white shadow-sm'
                    : 'bg-white border border-slate-200 text-slate-700 hover:bg-slate-100'
                }`}
              >
                {count === 8 ? '8 (1 Acre)' : `${count} Tank${count > 1 ? 's' : ''}`}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Visual Calculation Results Card */}
      <div className="bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 text-white rounded-2xl p-4 sm:p-5 shadow-inner space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <div className="flex items-center space-x-2">
            <Scale className="w-4 h-4 text-amber-400" />
            <span className="text-xs font-bold text-slate-200">{t('result.calc_dose_per_tank')}</span>
          </div>
          <span className="text-[11px] font-mono text-amber-300">
            {dosagePerLiter} {unit} per 1 Liter
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-center">
          {/* Dose per Tank */}
          <div className="bg-white/10 rounded-xl p-3 border border-white/10">
            <span className="text-[11px] font-medium text-slate-300 block">{t('result.calc_dose_per_tank')} ({tankSize}L)</span>
            <span className="text-2xl font-black text-amber-300 mt-1 block">
              {singleTankQty} <span className="text-xs font-bold text-white">{unit}</span>
            </span>
            <span className="text-[10px] text-slate-300 mt-0.5 block">
              ≈ {spoonsPerTank} tablespoons
            </span>
          </div>

          {/* Clean Water Required */}
          <div className="bg-white/10 rounded-xl p-3 border border-white/10">
            <span className="text-[11px] font-medium text-slate-300 block">{t('result.calc_water_needed')}</span>
            <span className="text-2xl font-black text-blue-300 mt-1 block">
              {totalWaterLiters} <span className="text-xs font-bold text-white">Liters</span>
            </span>
            <span className="text-[10px] text-slate-300 mt-0.5 block">
              {numTanks} full tank{numTanks > 1 ? 's' : ''}
            </span>
          </div>

          {/* Total Medicine Needed */}
          <div className="bg-white/10 rounded-xl p-3 border border-white/10">
            <span className="text-[11px] font-medium text-slate-300 block">{t('result.calc_medicine_needed')}</span>
            <span className="text-2xl font-black text-emerald-300 mt-1 block">
              {totalQty} <span className="text-xs font-bold text-white">{unit}</span>
            </span>
            <span className="text-[10px] text-slate-300 mt-0.5 block">
              For all {numTanks} tanks
            </span>
          </div>
        </div>

        {/* 4-Step Practical Mixing Guide */}
        <div className="bg-black/30 rounded-xl p-3.5 border border-white/5 space-y-2 text-xs">
          <span className="font-bold text-amber-300 flex items-center space-x-1.5">
            <Sparkles className="w-3.5 h-3.5" />
            <span>{t('result.calc_mixing_guide')}</span>
          </span>
          <ol className="list-decimal list-inside space-y-1 text-slate-300 text-[11px] leading-relaxed">
            <li>Take 1 Liter of clean water in a separate bucket.</li>
            <li>Add <strong className="text-white">{singleTankQty} {unit}</strong> and stir thoroughly until completely dissolved.</li>
            <li>Fill the {tankSize}L sprayer half-full with clean water, then pour the pre-mixed solution through the strainer.</li>
            <li>Top up with clean water to the {tankSize}L mark and mix gently before spraying.</li>
          </ol>
        </div>
      </div>

      {/* Safety & Best Practice Sprayer Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-[11px] text-slate-600">
        <div className="flex items-center space-x-2 bg-amber-50 p-2.5 rounded-xl border border-amber-200 text-amber-900">
          <SunMedium className="w-4 h-4 text-amber-600 shrink-0" />
          <span>{t('result.calc_morning_badge')}</span>
        </div>

        <div className="flex items-center space-x-2 bg-slate-50 p-2.5 rounded-xl border border-slate-200 text-slate-700">
          <Wind className="w-4 h-4 text-blue-600 shrink-0" />
          <span>{t('result.calc_wind_badge')}</span>
        </div>
      </div>
    </div>
  );
};
