import { tr } from "../i18n/i18n";
import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  Sprout,
  LogIn,
  UserPlus,
  AlertCircle,
  Loader2,
  Check,
} from "lucide-react";
import { api } from "../api/client";
import { User } from "../types";

interface AuthPageProps {
  onLoginSuccess: (user: User) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      if (isRegister) {
        await api.register({
          email: email.trim(),
          password,
          full_name: fullName.trim() || undefined,
        });
      }

      // Login to obtain JWT
      await api.login({ email: email.trim(), password });
      const user = await api.getMe();
      onLoginSuccess(user);
      navigate("/analyze");
    } catch (err: any) {
      setError(tr("ui.s_558fa253eb"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div>
        <div>
          <Sprout />
        </div>
        <h1>{isRegister ? tr("ui.s_f5884fa3e2") : tr("ui.s_1c9089485a")}</h1>
        <p>{isRegister ? tr("ui.s_828e7fd67b") : tr("ui.s_f20933fe08")}</p>
      </div>

      <div>
        {/* Toggle Switch */}
        <div>
          <button
            type="button"
            onClick={() => {
              setIsRegister(false);
              setError(null);
            }}
          >
            {tr("ui.s_f8492cc1de")}
          </button>
          <button
            type="button"
            onClick={() => {
              setIsRegister(true);
              setError(null);
            }}
          >
            {tr("ui.s_d672995a14")}
          </button>
        </div>

        {error && (
          <div>
            <AlertCircle />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div>
              <label htmlFor="full-name">{tr("ui.s_c88ee07007")}</label>
              <input
                id="full-name"
                type="text"
                required
                placeholder={tr("ui.s_38fcda250f")}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          )}

          <div>
            <label htmlFor="email">{tr("ui.s_09ba557fd1")}</label>
            <input
              id="email"
              type="email"
              required
              placeholder={tr("ui.s_836c332a4a")}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label htmlFor="password">{tr("ui.s_8be3c943b1")}</label>
            <input
              id="password"
              type="password"
              required
              minLength={6}
              placeholder={tr("ui.s_ce59047854")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button type="submit" disabled={loading}>
            {loading ? (
              <span role="status">{tr("farmer.loading")}</span>
            ) : isRegister ? (
              <>
                <UserPlus />
                <span>{tr("ui.s_54807932a6")}</span>
              </>
            ) : (
              <>
                <LogIn />
                <span>{tr("ui.s_afede44075")}</span>
              </>
            )}
          </button>
        </form>

        <div>
          <Link to="/analyze">{tr("ui.s_2ad24bd4d2")}</Link>
        </div>
      </div>
    </div>
  );
};
