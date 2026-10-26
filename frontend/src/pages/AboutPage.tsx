import { tr } from "../i18n/i18n";
import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";
import {
  Shield,
  Info,
  AlertTriangle,
  Cpu,
  Database,
  CheckCircle2,
  Layers,
  BookOpen,
  Lock,
  PhoneCall,
} from "lucide-react";
import { api } from "../api/client";

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
    <div>
      {/* Title */}
      <div>
        <div>
          <Shield />
        </div>
        <h1>{t("about_page.title")}</h1>
        <p>{t("about_page.subtitle")}</p>
      </div>

      {/* Model Overview Box */}
      <div>
        <div>
          <Cpu />
          <h2>{tr("ui.s_acaf6737da")}</h2>
        </div>

        <div>
          <div>
            <span>{tr("ui.s_c5c821ded7")}</span>
            <p>{tr("ui.s_b5789ad0bc")}</p>
            <span>{tr("ui.s_be3c2126e9")}</span>
          </div>

          <div>
            <span>{tr("ui.s_fe961af9d8")}</span>
            <p>{tr("ui.s_17aaea2858")}</p>
            <span>{tr("ui.s_177075af3d")}</span>
          </div>

          <div>
            <span>{tr("ui.s_cdca30cf0d")}</span>
            <p>{tr("ui.s_40bfb032d0")}</p>
            <span>{tr("ui.s_0e1171b474")}</span>
          </div>

          <div>
            <span>{tr("ui.s_f5ed075f00")}</span>
            <p>{tr("ui.s_0dca369ebf")}</p>
            <span>{tr("ui.s_960d84092e")}</span>
          </div>
        </div>

        {modelInfo && (
          <div>
            <span>
              {tr("ui.s_79b990023f")}
              {modelInfo.model_version}
            </span>
            <p>{tr("ui.s_7c150d36b4")}</p>
          </div>
        )}
      </div>

      {/* Lab vs Field Generalization Gap */}
      <div>
        <div>
          <Database />
          <h2>{tr("ui.s_8f0c87a7dd")}</h2>
        </div>

        <div>
          <p>
            <strong>{tr("ui.s_2a0f13695d")}</strong> {tr("ui.s_ab877d07e7")}
          </p>
          <p>
            <strong>{tr("ui.s_ee08245b74")}</strong> {tr("ui.s_7afc59bed1")}
          </p>
          <div>
            <span>{tr("ui.s_5cc6fd5a0b")}</span>
            <p>{tr("ui.s_5a59600e77")}</p>
          </div>
        </div>
      </div>

      {/* Privacy & EXIF Stripping */}
      <div>
        <div>
          <Lock />
          <h2>{tr("ui.s_7d4bcff067")}</h2>
        </div>
        <p>{tr("ui.s_2ff168e676")}</p>
      </div>

      {/* Mandatory Safety Notice */}
      <div>
        <div>
          <AlertTriangle />
          <h3>{tr("ui.s_f93a83907c")}</h3>
        </div>
        <ul>
          <li>
            <strong>{tr("ui.s_da1d761402")}</strong> {tr("ui.s_825462fc16")}
          </li>
          <li>
            <strong>{tr("ui.s_639e4ef1fd")}</strong> {tr("ui.s_77db47a730")}
          </li>
          <li>
            <strong>{tr("ui.s_47709278f3")}</strong> {tr("ui.s_8a70460c60")}
          </li>
        </ul>
      </div>
    </div>
  );
};
