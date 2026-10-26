import React, { useRef } from "react";
import { useTranslation } from "react-i18next";
import { Camera, Image, RefreshCw, Leaf, Sun, Scan } from "lucide-react";
import { usePhoto } from "../ui/primitives";
export const ImageUploader: React.FC<{
  selectedFile: File | null;
  onFileSelect: (file: File | null) => void;
  disabled?: boolean;
}> = ({ selectedFile, onFileSelect, disabled }) => {
  const { t } = useTranslation();
  const camera = useRef<HTMLInputElement>(null);
  const gallery = useRef<HTMLInputElement>(null);
  const preview = usePhoto(selectedFile || undefined);
  const select = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
    e.target.value = "";
  };
  return (
    <section className="capture-input" aria-label={t("farmer.photo")}>
      <div className="photo-tips">
        <span>
          <Leaf aria-hidden="true" />
          {t("farmer.one_leaf")}
        </span>
        <span>
          <Sun aria-hidden="true" />
          {t("farmer.light")}
        </span>
        <span>
          <Scan aria-hidden="true" />
          {t("farmer.fill")}
        </span>
      </div>
      <input
        ref={camera}
        hidden
        type="file"
        accept="image/*"
        capture="environment"
        onChange={select}
        aria-label={t("farmer.photo")}
      />
      <input
        ref={gallery}
        hidden
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={select}
        aria-label={t("farmer.gallery")}
      />
      {preview ? (
        <>
          <img
            className="capture-preview"
            src={preview}
            alt={t("farmer.preview")}
          />
          <button
            className="button secondary"
            disabled={disabled}
            onClick={() => camera.current?.click()}
          >
            <RefreshCw aria-hidden="true" />
            {t("farmer.retake")}
          </button>
          <button
            className="button plain"
            disabled={disabled}
            onClick={() => gallery.current?.click()}
          >
            <Image aria-hidden="true" />
            {t("farmer.gallery")}
          </button>
        </>
      ) : (
        <>
          <button
            className="button primary camera-hero"
            onClick={() => camera.current?.click()}
          >
            <Camera aria-hidden="true" />
            {t("farmer.photo")}
          </button>
          <button
            className="button secondary"
            onClick={() => gallery.current?.click()}
          >
            <Image aria-hidden="true" />
            {t("farmer.gallery")}
          </button>
        </>
      )}
    </section>
  );
};
