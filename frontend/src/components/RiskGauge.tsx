import React from 'react';
import { AlertTriangle, TrendingUp, ShieldAlert, CheckCircle2, CloudRain, Droplets, Thermometer, Wind } from 'lucide-react';
import { RiskAssessment } from '../types';

interface RiskGaugeProps {
  assessment: RiskAssessment;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ assessment }) => {
  const { risk_score, risk_level, risk_color, headline, summary, contributing_factors, daily_outlook, top_regional_threats, disclaimer } = assessment;

  const getBadgeColor = (level: string) => {
    switch (level) {
      case 'VERY HIGH':
        return 'bg-rose-100 text-rose-800 border-rose-300';
      case 'HIGH':
        return 'bg-amber-100 text-amber-800 border-amber-300';
      case 'MODERATE':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 md:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 pb-4">
        <div>
          <div className="flex items-center space-x-2">
            <ShieldAlert className="w-5 h-5 text-brand-600" />
            <h3 className="text-lg font-bold text-slate-900">Environmental Outbreak Risk</h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">Based on local microclimate weather & agronomic disease models</p>
        </div>

        <div className={`self-start sm:self-auto px-3.5 py-1.5 rounded-full text-xs font-bold uppercase tracking-wider border flex items-center space-x-1.5 ${getBadgeColor(risk_level)}`}>
          <span className="w-2 h-2 rounded-full" style={{ backgroundColor: risk_color }}></span>
          <span>{risk_level} RISK ({risk_score}/100)</span>
        </div>
      </div>

      {/* Main Score & Headline */}
      <div className="grid grid-cols-1 md:grid-cols-12 gap-6 items-center">
        {/* Score Ring / Bar */}
        <div className="md:col-span-4 flex flex-col items-center justify-center p-4 rounded-xl bg-slate-50 border border-slate-100">
          <div className="relative flex items-center justify-center">
            <svg className="w-32 h-32 transform -rotate-90">
              <circle
                cx="64"
                cy="64"
                r="52"
                stroke="#e2e8f0"
                strokeWidth="10"
                fill="transparent"
              />
              <circle
                cx="64"
                cy="64"
                r="52"
                stroke={risk_color}
                strokeWidth="10"
                strokeDasharray={326.7}
                strokeDashoffset={326.7 - (326.7 * risk_score) / 100}
                strokeLinecap="round"
                fill="transparent"
                className="transition-all duration-1000 ease-out"
              />
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-3xl font-extrabold text-slate-900">{risk_score}</span>
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider">Score</span>
            </div>
          </div>
          <span className="text-xs font-medium text-slate-600 mt-2 text-center">0 = Minimal &bull; 100 = Severe</span>
        </div>

        {/* Headline & Summary */}
        <div className="md:col-span-8 space-y-2.5">
          <h4 className="text-base font-bold text-slate-900">{headline}</h4>
          <p className="text-sm text-slate-600 leading-relaxed">{summary}</p>
        </div>
      </div>

      {/* Contributing Factors */}
      {contributing_factors && contributing_factors.length > 0 && (
        <div className="space-y-3">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500 flex items-center space-x-1.5">
            <TrendingUp className="w-4 h-4 text-slate-500" />
            <span>Key Environmental Contributing Factors</span>
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            {contributing_factors.map((factor, idx) => {
              const isElevating = factor.impact === 'ELEVATES_RISK';
              const isReducing = factor.impact === 'REDUCES_RISK';
              return (
                <div
                  key={idx}
                  className={`p-3 rounded-xl border text-xs space-y-1 ${
                    isElevating
                      ? 'bg-rose-50/60 border-rose-200/80 text-rose-950'
                      : isReducing
                      ? 'bg-emerald-50/60 border-emerald-200/80 text-emerald-950'
                      : 'bg-slate-50 border-slate-200 text-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between font-semibold">
                    <span>{factor.factor_name}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[10px] font-bold ${
                      isElevating ? 'bg-rose-200 text-rose-900' : isReducing ? 'bg-emerald-200 text-emerald-900' : 'bg-slate-200 text-slate-700'
                    }`}>
                      {factor.impact.replace('_', ' ')}
                    </span>
                  </div>
                  <p className="text-slate-600 leading-normal">{factor.explanation}</p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* 7-Day Risk Outlook Bar */}
      {daily_outlook && daily_outlook.length > 0 && (
        <div className="space-y-2 pt-2 border-t border-slate-100">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">7-Day Outbreak Risk Forecast</span>
          <div className="grid grid-cols-7 gap-1.5 text-center">
            {daily_outlook.slice(0, 7).map((d, i) => {
              const dayScore = d.risk_score;
              const barColor = dayScore >= 65 ? 'bg-rose-500' : dayScore >= 45 ? 'bg-amber-500' : 'bg-emerald-500';
              const dateObj = new Date(d.date);
              const dayName = isNaN(dateObj.getTime()) ? `D${i+1}` : dateObj.toLocaleDateString('en-US', { weekday: 'short' });
              return (
                <div key={i} className="p-2 rounded-lg bg-slate-50 border border-slate-100 flex flex-col items-center justify-between">
                  <span className="text-[11px] font-medium text-slate-500">{dayName}</span>
                  <div className="w-full bg-slate-200 h-1.5 rounded-full my-1.5 overflow-hidden">
                    <div className={`h-full ${barColor}`} style={{ width: `${dayScore}%` }}></div>
                  </div>
                  <span className="text-xs font-bold text-slate-800">{dayScore}%</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Top Regional Threats (For Healthy Plants) */}
      {top_regional_threats && top_regional_threats.length > 0 && (
        <div className="space-y-3 pt-2 border-t border-slate-100">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Highest Weather Risks for this Crop</span>
          <div className="space-y-2">
            {top_regional_threats.map((threat, i) => (
              <div key={i} className="flex items-center justify-between p-3 rounded-xl bg-slate-50 border border-slate-200/80 text-xs">
                <div>
                  <span className="font-bold text-slate-900">{threat.disease_name}</span>
                  <p className="text-slate-500 text-[11px] mt-0.5">{threat.headline}</p>
                </div>
                <span className={`px-2.5 py-1 rounded-md font-bold text-[11px] uppercase ${getBadgeColor(threat.risk_level)}`}>
                  {threat.risk_score}% ({threat.risk_level})
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Advisory Disclaimer */}
      <div className="p-3 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs flex items-start space-x-2">
        <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
        <p className="leading-tight text-[11px]">{disclaimer}</p>
      </div>
    </div>
  );
};
