import React from 'react';
import { AlertCircle, CheckCircle2, ChevronDown, HelpCircle } from 'lucide-react';
import { PredictionItem } from '../types';

interface ConfidenceBarProps {
  confidence: number;
  confidenceDisplay: string;
  isUncertain: boolean;
  uncertaintyReason?: string;
  topK: PredictionItem[];
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({
  confidence,
  confidenceDisplay,
  isUncertain,
  uncertaintyReason,
  topK,
}) => {
  const [showAlternatives, setShowAlternatives] = React.useState(false);
  const pct = Math.round(confidence * 100);

  const getColor = () => {
    if (isUncertain) return 'bg-amber-500';
    if (pct >= 85) return 'bg-brand-600';
    if (pct >= 65) return 'bg-emerald-500';
    return 'bg-amber-500';
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-sm p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">Diagnostic Confidence</span>
          <div className="flex items-center space-x-2 mt-0.5">
            <span className="text-2xl font-black text-slate-900">{pct}%</span>
            <span className="text-sm font-semibold text-slate-700">({confidenceDisplay})</span>
          </div>
        </div>

        {isUncertain ? (
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-amber-100 text-amber-900 border border-amber-300 text-xs font-bold">
            <AlertCircle className="w-4 h-4 text-amber-700" />
            <span>Uncertain Diagnostic</span>
          </div>
        ) : (
          <div className="flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-emerald-100 text-emerald-900 border border-emerald-300 text-xs font-bold">
            <CheckCircle2 className="w-4 h-4 text-emerald-700" />
            <span>High Reliability</span>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-slate-100 h-3 rounded-full overflow-hidden p-0.5 border border-slate-200/50">
        <div
          className={`h-full rounded-full transition-all duration-1000 ease-out ${getColor()}`}
          style={{ width: `${Math.max(5, pct)}%` }}
        ></div>
      </div>

      {/* Uncertainty Notice */}
      {isUncertain && (
        <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-amber-900 text-xs space-y-1">
          <div className="font-bold flex items-center space-x-1.5">
            <AlertCircle className="w-4 h-4 text-amber-600" />
            <span>Advisory Notice: Retake or Confirm with Expert</span>
          </div>
          <p className="text-amber-800 leading-relaxed text-[11px]">
            {uncertaintyReason || 'The leaf image lacks strong characteristic diagnostic markers. Please verify under natural lighting or show to a local agricultural extension officer.'}
          </p>
        </div>
      )}

      {/* Top Alternative Matches Toggle */}
      {topK && topK.length > 1 && (
        <div className="pt-2 border-t border-slate-100">
          <button
            onClick={() => setShowAlternatives(!showAlternatives)}
            className="w-full flex items-center justify-between text-xs font-semibold text-slate-600 hover:text-slate-900 py-1"
          >
            <span>View Alternative Match Possibilities ({topK.length})</span>
            <ChevronDown className={`w-4 h-4 transition-transform ${showAlternatives ? 'rotate-180' : ''}`} />
          </button>

          {showAlternatives && (
            <div className="mt-2 space-y-2 pt-2">
              {topK.map((item, idx) => (
                <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs">
                  <div>
                    <span className="font-bold text-slate-800">{item.crop}: {item.disease_name}</span>
                    <span className="text-[10px] text-slate-500 ml-2">{item.is_healthy ? '(Healthy)' : '(Pathogen)'}</span>
                  </div>
                  <span className="font-mono font-bold text-slate-700">{item.confidence_percentage}%</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
