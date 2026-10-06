import React, { useState } from 'react';
import {
  Share2,
  Copy,
  Check,
  X,
  Smartphone,
  ExternalLink,
  MessageCircle,
  FileText,
  PhoneCall
} from 'lucide-react';
import { AnalysisResponse } from '../types';

interface WhatsAppShareModalProps {
  analysis: AnalysisResponse;
  isOpen: boolean;
  onClose: () => void;
}

export const WhatsAppShareModal: React.FC<WhatsAppShareModalProps> = ({
  analysis,
  isOpen,
  onClose,
}) => {
  const [copied, setCopied] = useState<boolean>(false);
  const [shareLanguage, setShareLanguage] = useState<'hi' | 'en'>('hi');

  if (!isOpen) return null;

  const isHealthy = analysis.disease_details?.is_healthy || analysis.predicted_label.toLowerCase().includes('healthy');
  const crop = analysis.crop;
  const disease = analysis.disease_name;
  const confidence = Math.round(analysis.confidence * 100);
  const riskLevel = analysis.risk_assessment?.risk_level || 'MODERATE';
  const riskScore = analysis.risk_assessment?.risk_score || 50;
  const prevention = analysis.disease_details?.prevention_steps?.[0] || 'Prune visibly infected leaves';
  const organic = analysis.disease_details?.organic_controls?.[0] || 'Neem oil solution (5ml/L)';
  const chemical = analysis.disease_details?.chemical_controls?.[0] || 'Mancozeb 75% WP (2.5g/L)';

  const formattedShareTextHindi = `🌾 *कृषि शील्ड AI फसल रोग रिपोर्ट* 🌾
-----------------------------------
🌱 *फसल (Crop):* ${crop}
🔬 *रोग पहचान (Diagnosis):* ${disease} (${confidence}% विश्वसनीयता)
⚠️ *मौसम जोखिम (Risk Level):* ${riskLevel} (${riskScore}/100)

📋 *तुरंत करने वाले उपाय:*
1️⃣ *सावधानी:* ${prevention}
2️⃣ *जैविक दवा:* ${organic}
3️⃣ *रासायनिक दवा:* ${chemical}

🪣 *15 लीटर स्प्रे पंप खुराक:*
• रासायनिक: लगभग 35-40 ग्राम (2.5 बड़ा चम्मच) प्रति 15L टंकी।
• जैविक: 75 ml नीम का तेल प्रति 15L टंकी।

📞 *सरकारी किसान कॉल सेंटर:* 1800-180-1551 (टोल-फ्री)
-----------------------------------
_कृषि मित्र ऐप द्वारा स्वचालित रूप से तैयार किया गया_`;

  const formattedShareTextEnglish = `🌾 *AgriShield AI Crop Diagnostic Report* 🌾
-----------------------------------
🌱 *Crop:* ${crop}
🔬 *Identified Disease:* ${disease} (${confidence}% Confidence)
⚠️ *Outbreak Risk Level:* ${riskLevel} (${riskScore}/100)

📋 *Recommended Actions:*
1️⃣ *Cultural:* ${prevention}
2️⃣ *Organic Control:* ${organic}
3️⃣ *Chemical Spray:* ${chemical}

🪣 *15-Liter Knapsack Sprayer Dosage:*
• Chemical: ~35-40 grams (~2.5 tablespoons) per 15L tank.
• Organic: 75 ml Neem oil per 15L tank.

📞 *Kisan Call Center Helpline:* 1800-180-1551 (Toll-Free)
-----------------------------------
_Generated via AgriShield AI Plant Clinic_`;

  const activeText = shareLanguage === 'hi' ? formattedShareTextHindi : formattedShareTextEnglish;

  const handleCopy = () => {
    navigator.clipboard.writeText(activeText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleWhatsAppRedirect = () => {
    const encoded = encodeURIComponent(activeText);
    const url = `https://api.whatsapp.com/send?text=${encoded}`;
    window.open(url, '_blank');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-white rounded-3xl max-w-lg w-full p-6 shadow-2xl border border-slate-100 space-y-5 animate-scaleUp">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <div className="flex items-center space-x-2.5">
            <div className="w-9 h-9 rounded-2xl bg-emerald-100 text-emerald-700 flex items-center justify-center shadow-inner">
              <Share2 className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-slate-900">Share Report on WhatsApp</h3>
              <p className="text-[11px] text-slate-500">Send summary to Agri Shopkeeper or Krishi Officer</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="w-8 h-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Language Switcher */}
        <div className="flex items-center justify-between bg-slate-50 p-2 rounded-2xl border border-slate-200/70 text-xs">
          <span className="font-semibold text-slate-700 ml-2">Report Language:</span>
          <div className="flex space-x-1">
            <button
              onClick={() => setShareLanguage('hi')}
              className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
                shareLanguage === 'hi'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-200'
              }`}
            >
              हिन्दी (Hindi)
            </button>
            <button
              onClick={() => setShareLanguage('en')}
              className={`px-3 py-1.5 rounded-xl font-bold transition-all ${
                shareLanguage === 'en'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-600 hover:bg-slate-200'
              }`}
            >
              English
            </button>
          </div>
        </div>

        {/* WhatsApp Preview Card */}
        <div className="bg-emerald-50/70 border border-emerald-200 rounded-2xl p-4 font-mono text-[11px] text-slate-800 whitespace-pre-line leading-relaxed max-h-56 overflow-y-auto shadow-inner">
          {activeText}
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
          <button
            onClick={handleWhatsAppRedirect}
            className="flex items-center justify-center space-x-2 py-3 px-4 rounded-2xl bg-[#25D366] hover:bg-[#20bd5a] text-white text-xs font-black shadow-lg shadow-emerald-600/20 active:scale-95 transition-all"
          >
            <MessageCircle className="w-4 h-4 fill-current" />
            <span>Open in WhatsApp</span>
          </button>

          <button
            onClick={handleCopy}
            className="flex items-center justify-center space-x-2 py-3 px-4 rounded-2xl bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold active:scale-95 transition-all"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-emerald-600" />
                <span className="text-emerald-700">Copied to Clipboard!</span>
              </>
            ) : (
              <>
                <Copy className="w-4 h-4" />
                <span>Copy Summary Text</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
