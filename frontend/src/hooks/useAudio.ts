import { useCallback, useEffect, useRef, useState } from 'react';

export type AudioState = 'idle' | 'loading' | 'playing' | 'paused' | 'ready' | 'ended' | 'error';
type Options = { staticUrl: string; text: string; lang: string; scope: string };

export function useAudio({ staticUrl, text, lang, scope }: Options) {
  const [state, setState] = useState<AudioState>('idle');
  const [speed, setSpeed] = useState(1);
  const [source, setSource] = useState<'static' | 'dynamic' | 'browser'>('static');
  const audio = useRef<HTMLAudioElement | null>(null);
  const utterance = useRef<SpeechSynthesisUtterance | null>(null);
  const generation = useRef(0);
  const mode = useRef<'file' | 'browser'>('file');
  const rate = useRef(1);
  const voices = useRef<SpeechSynthesisVoice[]>([]);
  const cancelVoiceWait = useRef<() => void>(() => {});

  useEffect(() => {
    const synth = window.speechSynthesis;
    if (!synth) return;
    const update = () => { voices.current = synth.getVoices(); };
    update();
    synth.addEventListener('voiceschanged', update);
    return () => synth.removeEventListener('voiceschanged', update);
  }, []);

  const stop = useCallback(() => {
    generation.current += 1;
    cancelVoiceWait.current();
    if (audio.current) {
      audio.current.onerror = audio.current.onended = audio.current.onplaying = null;
      audio.current.pause();
      audio.current.removeAttribute('src');
      audio.current.load();
      audio.current = null;
    }
    if (utterance.current) {
      utterance.current.onend = utterance.current.onerror = utterance.current.onstart = null;
      window.speechSynthesis?.cancel();
      utterance.current = null;
    }
    mode.current = 'file';
    setState('idle');
  }, []);

  useEffect(() => { stop(); return stop; }, [lang, scope, staticUrl, stop]);

  const browserFallback = async (token: number) => {
    const synth = window.speechSynthesis;
    if (!synth || !text.trim()) { if (token === generation.current) setState('error'); return; }
    const find = () => synth.getVoices().find(v => v.lang.toLowerCase().replace('_', '-') === `${lang}-IN`.toLowerCase());
    let voice = find();
    if (!voice) {
      await new Promise<void>(resolve => {
        const finish = () => { clearTimeout(timer); synth.removeEventListener('voiceschanged', changed); resolve(); };
        const changed = () => { if (find()) finish(); };
        const timer = setTimeout(finish, 1500);
        cancelVoiceWait.current = finish;
        synth.addEventListener('voiceschanged', changed);
        changed();
      });
      voice = find();
    }
    if (token !== generation.current) return;
    if (!voice) { setState('error'); return; }
    const speech = new SpeechSynthesisUtterance(text);
    speech.lang = `${lang}-IN`;
    speech.voice = voice;
    speech.rate = rate.current;
    speech.onstart = () => { if (token === generation.current) setState('playing'); };
    speech.onend = () => { if (token === generation.current) setState('ended'); };
    speech.onerror = () => { if (token === generation.current) setState('error'); };
    utterance.current = speech;
    mode.current = 'browser';
    setSource('browser');
    // The fallback was reached asynchronously. Require a fresh gesture for speech.
    setState('ready');
  };

  const start = () => {
    stop();
    const token = generation.current;
    const element = new Audio();
    audio.current = element;
    element.playbackRate = rate.current;
    element.preload = 'none';
    const urls = [staticUrl];
    // Reject oversize text instead of silently truncating it.
    if (text.trim() && text.length <= 2000 && new TextEncoder().encode(text).length <= 4500) {
      urls.push(`/api/v1/audio/tts?${new URLSearchParams({ text, lang })}`);
    }
    const attempt = (index: number) => {
      if (token !== generation.current) return;
      if (index >= urls.length) { element.onerror = null; void browserFallback(token); return; }
      setSource(index === 0 ? 'static' : 'dynamic');
      setState('loading');
      let failed = false;
      const fail = (error?: unknown) => {
        if (failed || token !== generation.current) return;
        if (error instanceof DOMException && error.name === 'NotAllowedError') {
          setState('ready'); // retry same element from the next tap, do not skip sources
          return;
        }
        failed = true;
        element.onerror = null;
        attempt(index + 1);
      };
      element.onended = () => { if (token === generation.current && !failed) setState('ended'); };
      element.onplaying = () => { if (token === generation.current && !failed) setState('playing'); };
      element.onerror = () => fail();
      element.src = urls[index];
      // Called synchronously by the initial click. Reuse this element for fallbacks.
      void element.play().catch(fail);
    };
    attempt(0);
  };

  const play = () => {
    if (state === 'paused' || state === 'ready') {
      if (mode.current === 'browser' && utterance.current) {
        if (state === 'paused') window.speechSynthesis.resume();
        else window.speechSynthesis.speak(utterance.current);
        setState('playing');
      } else if (audio.current) {
        const token = generation.current;
        void audio.current.play().catch(error => {
          if (token === generation.current) setState(error?.name === 'NotAllowedError' ? 'ready' : 'error');
        });
      }
    } else start();
  };
  const pause = () => {
    if (mode.current === 'browser') window.speechSynthesis?.pause();
    else audio.current?.pause();
    setState('paused');
  };
  const changeSpeed = (value: number) => {
    if (![0.75, 1, 1.25].includes(value)) return;
    rate.current = value;
    setSpeed(value);
    if (audio.current) audio.current.playbackRate = value;
    // Web Speech cannot change an in-flight utterance's rate reliably.
    if (mode.current === 'browser' && utterance.current) {
      // Detach callbacks before cancellation; stale cancel events must not set error.
      const old = utterance.current;
      const next = new SpeechSynthesisUtterance(old.text);
      next.lang = old.lang; next.voice = old.voice; next.rate = value;
      next.onstart = old.onstart; next.onend = old.onend; next.onerror = old.onerror;
      old.onstart = old.onend = old.onerror = null;
      window.speechSynthesis.cancel();
      utterance.current = next;
      setState('ready');
    }
  };
  return { state, source, speed, play, pause, stop, replay: start, changeSpeed };
}
