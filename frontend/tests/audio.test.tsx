import { act, renderHook, waitFor } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import { useAudio } from '../src/hooks/useAudio';

let instances: MockAudio[];
let results: ('ok' | 'bad' | 'blocked')[];
class MockAudio {
  src = ''; playbackRate = 1; preload = ''; currentTime = 0;
  onerror: (() => void) | null = null;
  onended: (() => void) | null = null;
  onplaying: (() => void) | null = null;
  pause = vi.fn(); load = vi.fn(); removeAttribute = vi.fn();
  play = vi.fn(() => {
    const result = results.shift() || 'ok';
    if (result === 'bad') return Promise.reject(new DOMException('Invalid audio', 'NotSupportedError'));
    if (result === 'blocked') return Promise.reject(new DOMException('Gesture required', 'NotAllowedError'));
    return Promise.resolve();
  });
  constructor() { instances.push(this); }
}
let installed: SpeechSynthesisVoice[];
let synth: EventTarget & { getVoices: ReturnType<typeof vi.fn>; speak: ReturnType<typeof vi.fn>; cancel: ReturnType<typeof vi.fn>; pause: ReturnType<typeof vi.fn>; resume: ReturnType<typeof vi.fn> };
const options = { staticUrl: '/api/v1/audio/files/kn/apple/diagnosis.mp3', text: 'Read the leaf symptoms carefully.', lang: 'kn', scope: 'route-one' };

beforeEach(() => {
  instances = []; results = []; installed = [];
  synth = Object.assign(new EventTarget(), { getVoices: vi.fn(() => installed), speak: vi.fn(), cancel: vi.fn(), pause: vi.fn(), resume: vi.fn() });
  vi.stubGlobal('Audio', MockAudio);
  vi.stubGlobal('speechSynthesis', synth);
  vi.stubGlobal('SpeechSynthesisUtterance', class { constructor(public text: string) {} });
});
afterEach(() => { vi.unstubAllGlobals(); vi.useRealTimers(); });

describe('useAudio', () => {
  it('stops narration when another player starts, including weather replay', () => {
    const first = renderHook(() => useAudio(options));
    const second = renderHook(() => useAudio({...options,staticUrl:'/voice/risk-kn-high.mp3'}));
    act(() => first.result.current.play());
    act(() => instances[0].onplaying?.());
    expect(first.result.current.state).toBe('playing');
    act(() => second.result.current.replay());
    expect(first.result.current.state).toBe('idle');
    expect(instances[0].pause).toHaveBeenCalled();
  });
  it('plays static first and supports loading, play, pause, resume, speed, end, replay and stop', async () => {
    const { result } = renderHook(() => useAudio(options));
    expect(result.current.state).toBe('idle');
    act(() => result.current.play());
    expect(result.current.state).toBe('loading');
    expect(instances[0].src).toBe(options.staticUrl);
    act(() => instances[0].onplaying?.());
    expect(result.current.state).toBe('playing');
    act(() => result.current.pause());
    expect(result.current.state).toBe('paused');
    act(() => result.current.play());
    expect(instances[0].play).toHaveBeenCalledTimes(2);
    act(() => result.current.changeSpeed(0.75));
    expect(instances[0].playbackRate).toBe(0.75);
    act(() => instances[0].onended?.());
    expect(result.current.state).toBe('ended');
    act(() => result.current.replay());
    expect(instances).toHaveLength(2);
    act(() => result.current.stop());
    expect(result.current.state).toBe('idle');
    expect(instances[1].pause).toHaveBeenCalled();
  });

  it('falls back once from static to dynamic, using the same element', async () => {
    results = ['bad', 'ok'];
    const { result } = renderHook(() => useAudio(options));
    act(() => result.current.play());
    await waitFor(() => expect(result.current.source).toBe('dynamic'));
    expect(instances).toHaveLength(1);
    expect(instances[0].src).toContain('/api/v1/audio/tts?');
    expect(new URL(instances[0].src, 'http://localhost').searchParams.get('lang')).toBe('kn');
    act(() => instances[0].onplaying?.());
    expect(result.current.state).toBe('playing');
  });

  it('waits for voiceschanged and requires a new tap for matching browser speech', async () => {
    results = ['bad', 'bad'];
    const { result } = renderHook(() => useAudio(options));
    act(() => result.current.play());
    await waitFor(() => expect(synth.getVoices.mock.calls.length).toBeGreaterThanOrEqual(2));
    act(() => { installed = [{ lang: 'kn-IN' } as SpeechSynthesisVoice]; synth.dispatchEvent(new Event('voiceschanged')); });
    await waitFor(() => expect(result.current.state).toBe('ready'));
    expect(result.current.source).toBe('browser');
    expect(synth.speak).not.toHaveBeenCalled();
    act(() => result.current.play());
    expect(synth.speak.mock.calls[0][0].lang).toBe('kn-IN');
    expect(synth.speak.mock.calls[0][0].voice.lang).toBe('kn-IN');
  });

  it('reports error instead of speaking with an unrelated voice', async () => {
    vi.useFakeTimers(); results = ['bad', 'bad'];
    installed = [{ lang: 'en-US' } as SpeechSynthesisVoice];
    const { result } = renderHook(() => useAudio(options));
    await act(async () => result.current.play());
    await act(async () => vi.advanceTimersByTimeAsync(1600));
    expect(result.current.state).toBe('error');
    expect(synth.speak).not.toHaveBeenCalled();
  });

  it('keeps the same source after autoplay denial and retries on a tap', async () => {
    results = ['blocked', 'ok'];
    const { result } = renderHook(() => useAudio(options));
    act(() => result.current.play());
    await waitFor(() => expect(result.current.state).toBe('ready'));
    expect(result.current.source).toBe('static');
    act(() => result.current.play());
    expect(instances[0].play).toHaveBeenCalledTimes(2);
    expect(instances[0].src).toBe(options.staticUrl);
  });

  it('cancels pending fallback on stop, language change, navigation and unmount', async () => {
    const { result, rerender, unmount } = renderHook(props => useAudio(props), { initialProps: options });
    results = ['bad'];
    act(() => result.current.play());
    act(() => result.current.stop());
    await act(async () => {});
    expect(instances[0].play).toHaveBeenCalledTimes(1);
    act(() => result.current.play());
    rerender({ ...options, lang: 'ta' });
    expect(result.current.state).toBe('idle');
    act(() => result.current.play());
    rerender({ ...options, lang: 'ta', scope: 'route-two' });
    expect(result.current.state).toBe('idle');
    act(() => result.current.play());
    const last = instances.at(-1)!;
    unmount();
    expect(last.pause).toHaveBeenCalled();
    expect(last.onerror).toBeNull();
  });
});
