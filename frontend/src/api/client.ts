/**
 * API client with automatic auth header injection, error parsing, client-side image downscaling,
 * and multilingual language negotiation.
 */
import {
  User,
  AuthTokens,
  AnalysisResponse,
  AnalysisHistoryItem,
  FeedbackCreate,
  FeedbackResponse,
  GeocodingResult,
  WeatherSummary,
  DiseaseEntry
} from '../types';
import i18n from '../i18n/i18n';

const API_BASE = '/api/v1';

class ApiClient {
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('agrishield_token');
  }

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('agrishield_token', token);
    } else {
      localStorage.removeItem('agrishield_token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private getCurrentLang(): string {
    return i18n.language ? i18n.language.split('-')[0].split('_')[0] : 'en';
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Accept-Language': this.getCurrentLang(),
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    if (!(options.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    });

    if (response.status === 401) {
      this.setToken(null);
    }

    if (!response.ok) {
      let errorMsg = 'An unexpected network error occurred';
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorMsg;
      } catch {
        errorMsg = response.statusText;
      }
      throw new Error(errorMsg);
    }

    if (response.status === 204) {
      return {} as T;
    }

    return response.json();
  }

  // --- Auth ---
  async register(data: { email: string; password: string; full_name?: string }): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async login(data: { email: string; password: string }): Promise<AuthTokens> {
    const res = await this.request<AuthTokens>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    this.setToken(res.access_token);
    return res;
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  logout() {
    this.setToken(null);
  }

  // --- Client-Side Image Downscaling ---
  async downscaleImage(file: File, maxDimension: number = 1024): Promise<Blob> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          let { width, height } = img;
          if (width > maxDimension || height > maxDimension) {
            if (width > height) {
              height = Math.round((height * maxDimension) / width);
              width = maxDimension;
            } else {
              width = Math.round((width * maxDimension) / height);
              height = maxDimension;
            }
          }

          const canvas = document.createElement('canvas');
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext('2d');
          if (!ctx) {
            resolve(file);
            return;
          }
          ctx.drawImage(img, 0, 0, width, height);
          canvas.toBlob(
            (blob) => {
              if (blob) resolve(blob);
              else resolve(file);
            },
            'image/jpeg',
            0.88
          );
        };
        img.onerror = reject;
        img.src = e.target?.result as string;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  // --- Analysis ---
  async analyzeImage(
    file: File,
    params: {
      latitude?: number;
      longitude?: number;
      location_name?: string;
      manual_temp_c?: number;
      manual_humidity_pct?: number;
      manual_rainfall_mm?: number;
      lang?: string;
    } = {}
  ): Promise<AnalysisResponse> {
    const downscaledBlob = await this.downscaleImage(file, 1024);
    const formData = new FormData();
    formData.append('image', downscaledBlob, file.name || 'crop_leaf.jpg');

    if (params.latitude !== undefined) formData.append('latitude', params.latitude.toString());
    if (params.longitude !== undefined) formData.append('longitude', params.longitude.toString());
    if (params.location_name) formData.append('location_name', params.location_name);
    if (params.manual_temp_c !== undefined) formData.append('manual_temp_c', params.manual_temp_c.toString());
    if (params.manual_humidity_pct !== undefined) formData.append('manual_humidity_pct', params.manual_humidity_pct.toString());
    if (params.manual_rainfall_mm !== undefined) formData.append('manual_rainfall_mm', params.manual_rainfall_mm.toString());
    formData.append('lang', params.lang || this.getCurrentLang());

    return this.request<AnalysisResponse>('/analyze', {
      method: 'POST',
      body: formData,
    });
  }

  // --- History ---
  async getHistory(limit: number = 50, offset: number = 0, lang?: string): Promise<AnalysisHistoryItem[]> {
    const targetLang = lang || this.getCurrentLang();
    return this.request<AnalysisHistoryItem[]>(`/history?limit=${limit}&offset=${offset}&lang=${encodeURIComponent(targetLang)}`);
  }

  async getHistoryDetail(id: string, lang?: string): Promise<AnalysisResponse> {
    const targetLang = lang || this.getCurrentLang();
    return this.request<AnalysisResponse>(`/history/${id}?lang=${encodeURIComponent(targetLang)}`);
  }

  async deleteHistory(id: string): Promise<void> {
    return this.request<void>(`/history/${id}`, {
      method: 'DELETE',
    });
  }

  // --- Feedback ---
  async submitFeedback(analysisId: string, feedback: FeedbackCreate): Promise<FeedbackResponse> {
    return this.request<FeedbackResponse>(`/history/${analysisId}/feedback`, {
      method: 'POST',
      body: JSON.stringify(feedback),
    });
  }

  // --- Weather & Geocode ---
  async getWeather(lat: number, lon: number): Promise<WeatherSummary> {
    return this.request<WeatherSummary>(`/weather?lat=${lat}&lon=${lon}`);
  }

  async geocode(query: string): Promise<GeocodingResult[]> {
    return this.request<GeocodingResult[]>(`/geocode?q=${encodeURIComponent(query)}`);
  }

  // --- Diseases Knowledge Base ---
  async getDiseases(crop?: string, causalAgent?: string, lang?: string): Promise<DiseaseEntry[]> {
    const targetLang = lang || this.getCurrentLang();
    const params = new URLSearchParams();
    if (crop) params.append('crop', crop);
    if (causalAgent) params.append('causal_agent', causalAgent);
    params.append('lang', targetLang);
    return this.request<DiseaseEntry[]>(`/diseases?${params.toString()}`);
  }

  async getDiseaseById(id: string, lang?: string): Promise<DiseaseEntry> {
    const targetLang = lang || this.getCurrentLang();
    return this.request<DiseaseEntry>(`/diseases/${encodeURIComponent(id)}?lang=${encodeURIComponent(targetLang)}`);
  }

  // --- Audio Narration ---
  getAudioUrl(diseaseId: string, section: string, lang?: string): string {
    const targetLang = lang || this.getCurrentLang();
    return `${API_BASE}/audio/files/${encodeURIComponent(targetLang)}/${encodeURIComponent(diseaseId)}/${encodeURIComponent(section === 'overview' ? 'diagnosis' : section)}.mp3`;
  }

  async getAudioLanguages(): Promise<any> {
    return this.request<any>('/audio/languages');
  }

  async getGlossary(lang?: string): Promise<any> {
    const targetLang = lang || this.getCurrentLang();
    return this.request<any>(`/audio/glossary/${encodeURIComponent(targetLang)}`);
  }

  async synthesizeAudioBlob(text: string, lang?: string): Promise<Blob> {
    const targetLang = lang || this.getCurrentLang();
    const response = await fetch(`${API_BASE}/audio/tts?${new URLSearchParams({ text, lang: targetLang })}`);
    if (!response.ok) {
      throw new Error('Failed to synthesize audio');
    }
    return response.blob();
  }

  // --- Model Metadata ---
  async getModelInfo(): Promise<any> {
    return this.request<any>('/model/info');
  }
}

export const api = new ApiClient();
