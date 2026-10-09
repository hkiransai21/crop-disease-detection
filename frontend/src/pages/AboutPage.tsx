import React, { useState, useEffect } from 'react';
import { Shield, Info, AlertTriangle, Cpu, Database, CheckCircle2, Layers, BookOpen, Lock } from 'lucide-react';
import { api } from '../api/client';

export const AboutPage: React.FC = () => {
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
          Model Card, Safety & Transparency
        </h1>
        <p className="text-xs sm:text-sm text-slate-500">
          Complete disclosure on data sources, neural architecture, limitations, and safety protocols.
        </p>
      </div>

      {/* Model Overview Box */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-6">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Cpu className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">Neural Network Architecture & Optimization</h2>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Base Backbone</span>
            <p className="text-sm font-bold text-slate-900">EfficientNet-B0</p>
            <span className="text-[11px] text-slate-500">ImageNet Pretrained</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Deployment Runtime</span>
            <p className="text-sm font-bold text-slate-900">ONNX Runtime CPU</p>
            <span className="text-[11px] text-slate-500">Dynamic INT8 Quantized</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Classes Covered</span>
            <p className="text-sm font-bold text-slate-900">38 Diagnostic Classes</p>
            <span className="text-[11px] text-slate-500">14 Agricultural Crops</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-50 border border-slate-100 space-y-1">
            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Calibration</span>
            <p className="text-sm font-bold text-slate-900">Temperature Scaled</p>
            <span className="text-[11px] text-slate-500">ECE Reliability Optimized</span>
          </div>
        </div>

        {modelInfo && (
          <div className="p-4 rounded-xl bg-brand-50/50 border border-brand-100 text-xs space-y-2">
            <span className="font-bold text-brand-900">Active Model Version: {modelInfo.model_version}</span>
            <p className="text-slate-600 text-[11px]">
              Trained using two-stage fine-tuning with AdamW optimizer, cosine annealing, and heavy data augmentation to combat laboratory background shortcut learning.
            </p>
          </div>
        )}
      </div>

      {/* Lab vs Field Generalization Gap */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Database className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">Dataset Sources & The Field Generalization Gap</h2>
        </div>

        <div className="space-y-3 text-xs text-slate-700 leading-relaxed">
          <p>
            <strong>Primary Training Set (PlantVillage):</strong> 54,305 controlled laboratory images across 38 classes. While providing rich morphological coverage, lab images feature uniform single-color backgrounds that can cause models to learn background shortcuts.
          </p>
          <p>
            <strong>Cross-Dataset Evaluation (PlantDoc):</strong> Evaluated against real-world field photographs taken in orchards and farms under variable weather, complex background foliage, and varying light conditions.
          </p>
          <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 text-amber-950 space-y-1.5">
            <span className="font-bold text-amber-900">Honest Generalization Gap Disclosure:</span>
            <p className="text-[11px] leading-relaxed">
              Accuracy on clean lab test sets is typically higher than real-world field images due to overlapping leaves, motion blur, and co-infections in nature. Our model implements explicit confidence thresholding and Shannon entropy rejection to flag ambiguous field samples as 'Uncertain' rather than making false confident predictions.
            </p>
          </div>
        </div>
      </div>

      {/* Privacy & EXIF Stripping */}
      <div className="bg-white rounded-3xl border border-slate-200 p-6 md:p-8 shadow-sm space-y-4">
        <div className="flex items-center space-x-2 border-b border-slate-100 pb-3">
          <Lock className="w-5 h-5 text-brand-600" />
          <h2 className="text-lg font-bold text-slate-900">Farmer Data Privacy & EXIF Stripping</h2>
        </div>
        <p className="text-xs text-slate-600 leading-relaxed">
          All image uploads are immediately stripped of embedded EXIF camera and GPS metadata on our server before persistence. Coordinates for weather telemetry are processed in-memory or stored with anonymized user accounts only. Retraining datasets are generated strictly with voluntary farmer opt-in consent.
        </p>
      </div>

      {/* Mandatory Safety Notice */}
      <div className="p-6 rounded-3xl bg-rose-50 border border-rose-200 text-rose-950 space-y-3">
        <div className="flex items-center space-x-2.5 font-bold text-rose-900">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0" />
          <h3 className="text-base">Agricultural Safety Disclaimer & Limitations</h3>
        </div>
        <ul className="list-disc list-inside space-y-1.5 text-xs text-rose-900 leading-relaxed">
          <li><strong>Advisory Decision-Support:</strong> This software is an informational tool and does not substitute for certified in-person crop consultants or government plant pathology laboratories.</li>
          <li><strong>Pesticide Regulations:</strong> Pesticide active ingredients and controls listed are generic categories. Chemical registrations vary by state and nation. Always read the physical chemical product label and observe Pre-Harvest Intervals (PHI) and Re-Entry Intervals (REI).</li>
          <li><strong>Environmental Weather Risk:</strong> Outbreak risk scores are transparent agronomic heuristics combining temperature windows, high-humidity hours, and rainfall proxies. They are advisory estimates, not guaranteed forecasts.</li>
        </ul>
      </div>
    </div>
  );
};
