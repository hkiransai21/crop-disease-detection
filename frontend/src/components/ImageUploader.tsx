import React, { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Camera, Upload, Image as ImageIcon, CheckCircle, Info, X, RefreshCw } from 'lucide-react';

interface ImageUploaderProps {
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({ selectedFile, onFileSelect }) => {
  const { t } = useTranslation();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [showTips, setShowTips] = useState(false);
  const [isDragging, setIsDragging] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      onFileSelect(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      onFileSelect(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const clearImage = () => {
    onFileSelect(null);
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl);
      setPreviewUrl(null);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  };

  return (
    <div className="space-y-3">
      {/* Hidden file & camera inputs */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/jpg"
        className="hidden"
        onChange={handleFileChange}
      />
      <input
        ref={cameraInputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleFileChange}
      />

      {/* Upload Zone */}
      {!previewUrl ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-2xl p-6 sm:p-8 text-center transition-all ${
            isDragging
              ? 'border-brand-500 bg-brand-50/50 scale-[1.01]'
              : 'border-slate-300 hover:border-brand-400 bg-slate-50/70'
          }`}
        >
          <div className="max-w-md mx-auto space-y-4">
            <div className="w-16 h-16 mx-auto rounded-2xl bg-brand-100 text-brand-700 flex items-center justify-center shadow-inner">
              <Camera className="w-8 h-8" />
            </div>

            <div>
              <h3 className="text-base font-bold text-slate-900">{t('analyze.upload_btn')}</h3>
              <p className="text-xs text-slate-500 mt-1">
                {t('analyze.upload_instruction')}
              </p>
            </div>

            {/* Action Buttons for Mobile / Desktop */}
            <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => cameraInputRef.current?.click()}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 px-5 py-3 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-sm font-bold shadow-md shadow-brand-600/20 transition-transform active:scale-95"
              >
                <Camera className="w-4 h-4" />
                <span>{t('analyze.camera_btn')}</span>
              </button>

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="w-full sm:w-auto flex items-center justify-center space-x-2 px-5 py-3 rounded-xl bg-white hover:bg-slate-50 border border-slate-300 text-slate-800 text-sm font-bold shadow-sm transition-colors"
              >
                <Upload className="w-4 h-4 text-slate-500" />
                <span>{t('analyze.choose_file')}</span>
              </button>
            </div>

            <div className="pt-2">
              <button
                type="button"
                onClick={() => setShowTips(!showTips)}
                className="inline-flex items-center space-x-1 text-xs font-semibold text-brand-700 hover:text-brand-800 hover:underline"
              >
                <Info className="w-3.5 h-3.5" />
                <span>{t('analyze.tips_title')}</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Image Preview Box */
        <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-black aspect-video max-h-80 flex items-center justify-center group">
          <img
            src={previewUrl}
            alt="Selected leaf preview"
            className="w-full h-full object-contain"
          />

          <div className="absolute top-3 right-3 flex space-x-2">
            <button
              type="button"
              onClick={() => cameraInputRef.current?.click()}
              className="p-2 rounded-full bg-black/60 text-white hover:bg-black/80 backdrop-blur-sm transition-all"
              title="Retake Photo"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={clearImage}
              className="p-2 rounded-full bg-rose-600/90 text-white hover:bg-rose-700 backdrop-blur-sm transition-all"
              title="Remove Image"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="absolute bottom-3 left-3 bg-black/60 backdrop-blur-md px-3 py-1.5 rounded-lg text-white text-xs font-medium flex items-center space-x-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-brand-400" />
            <span className="truncate max-w-[200px]">{selectedFile?.name}</span>
          </div>
        </div>
      )}

      {/* Photo Tips Modal / Dropdown */}
      {showTips && (
        <div className="p-4 rounded-xl bg-brand-50/80 border border-brand-200 text-xs text-brand-950 space-y-2 animate-fadeIn">
          <div className="flex items-center justify-between font-bold text-brand-900">
            <span className="flex items-center space-x-1.5">
              <Info className="w-4 h-4 text-brand-600" />
              <span>How to take a high-precision leaf photo:</span>
            </span>
            <button onClick={() => setShowTips(false)} className="text-brand-700 hover:text-brand-950">
              <X className="w-4 h-4" />
            </button>
          </div>
          <ul className="list-disc list-inside space-y-1 text-brand-900 leading-relaxed text-[11px]">
            <li><strong>Single Leaf:</strong> Keep the leaf centered against a plain or natural background.</li>
            <li><strong>Sharp Focus:</strong> Tap your screen to focus on the yellow spots, powdery mold, or lesions.</li>
            <li><strong>Good Lighting:</strong> Take photos in bright daylight. Avoid heavy shadows or flashlight glare.</li>
            <li><strong>Orientation:</strong> Photograph both upper surface spots and leaf undersides if mold is present.</li>
          </ul>
        </div>
      )}
    </div>
  );
};
