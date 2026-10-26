import { ReactNode, useEffect, useRef } from "react";
import { useTranslation } from "react-i18next";
import { X } from "lucide-react";
export function Modal({
  title,
  onClose,
  children,
}: {
  title: string;
  onClose: () => void;
  children: ReactNode;
}) {
  const { t } = useTranslation();
  const ref = useRef<HTMLDialogElement>(null);
  useEffect(() => {
    const previous = document.activeElement as HTMLElement;
    ref.current?.showModal();
    return () => {
      ref.current?.close();
      previous?.focus();
    };
  }, []);
  return (
    <dialog ref={ref} aria-label={title} onCancel={onClose} onClose={onClose}>
      <div className="dialog-head">
        <h2>{title}</h2>
        <button className="plain" onClick={onClose}>
          <X aria-hidden="true" />
          {t("farmer.close")}
        </button>
      </div>
      {children}
    </dialog>
  );
}
