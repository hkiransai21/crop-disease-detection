import { tr } from '../i18n/i18n';
import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Sprout, LogIn, UserPlus, AlertCircle, Loader2, Check } from 'lucide-react';
import { api } from '../api/client';
import { User } from '../types';

interface AuthPageProps {
  onLoginSuccess: (user: User) => void;
}

export const AuthPage: React.FC<AuthPageProps> = ({ onLoginSuccess }) => {
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
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
      navigate('/analyze');
    } catch (err: any) {
      setError(err.message || tr('ui.s_558fa253eb'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto py-10 space-y-6">
      <div className="text-center space-y-2">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-brand-700 to-brand-500 text-white flex items-center justify-center mx-auto shadow-md shadow-brand-500/20">
          <Sprout className="w-6 h-6" />
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900">
          {isRegister ? tr('ui.s_f5884fa3e2') : tr('ui.s_1c9089485a')}
        </h1>
        <p className="text-xs text-slate-500">
          {isRegister
            ? tr('ui.s_828e7fd67b')
            : tr('ui.s_f20933fe08')}
        </p>
      </div>

      <div className="bg-white rounded-3xl border border-slate-200 shadow-sm p-6 sm:p-8 space-y-5">
        {/* Toggle Switch */}
        <div className="grid grid-cols-2 p-1 bg-slate-100 rounded-xl">
          <button
            type="button"
            onClick={() => {
              setIsRegister(false);
              setError(null);
            }}
            className={`py-2 text-xs font-bold rounded-lg transition-all ${
              !isRegister ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            {tr('ui.s_f8492cc1de')}</button>
          <button
            type="button"
            onClick={() => {
              setIsRegister(true);
              setError(null);
            }}
            className={`py-2 text-xs font-bold rounded-lg transition-all ${
              isRegister ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-500 hover:text-slate-800'
            }`}
          >
            {tr('ui.s_d672995a14')}</button>
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-rose-900 text-xs flex items-center space-x-2.5">
            <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
            <span className="font-semibold">{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div className="space-y-1">
              <label className="block text-xs font-bold text-slate-700">{tr('ui.s_c88ee07007')}</label>
              <input
                type="text"
                required
                placeholder={tr('ui.s_38fcda250f')}
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-brand-500 bg-slate-50/50"
              />
            </div>
          )}

          <div className="space-y-1">
            <label className="block text-xs font-bold text-slate-700">{tr('ui.s_09ba557fd1')}</label>
            <input
              type="email"
              required
              placeholder={tr('ui.s_836c332a4a')}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-brand-500 bg-slate-50/50"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-bold text-slate-700">{tr('ui.s_8be3c943b1')}</label>
            <input
              type="password"
              required
              minLength={6}
              placeholder={tr('ui.s_ce59047854')}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-300 text-xs focus:outline-none focus:border-brand-500 bg-slate-50/50"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 text-white text-xs sm:text-sm font-bold shadow-md shadow-brand-600/20 transition-all disabled:opacity-50"
          >
            {loading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : isRegister ? (
              <>
                <UserPlus className="w-4 h-4" />
                <span>{tr('ui.s_54807932a6')}</span>
              </>
            ) : (
              <>
                <LogIn className="w-4 h-4" />
                <span>{tr('ui.s_afede44075')}</span>
              </>
            )}
          </button>
        </form>

        <div className="text-center pt-2">
          <Link to="/analyze" className="text-xs font-medium text-slate-500 hover:text-slate-800">
            {tr('ui.s_2ad24bd4d2')}</Link>
        </div>
      </div>
    </div>
  );
};
