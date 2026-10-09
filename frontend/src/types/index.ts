export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  refresh_token?: string;
  expires_in: number;
}

export interface PredictionItem {
  class_id: string;
  crop: string;
  disease_name: string;
  confidence: number;
  confidence_percentage: number;
  is_healthy: boolean;
}

export interface EnvironmentalConditions {
  temp_min_c: number;
  temp_max_c: number;
  temp_optimal_c?: number;
  humidity_min_pct: number;
  leaf_wetness_hours_min: number;
  rainfall_favorable: boolean;
  wind_spread: boolean;
}

export interface DiseaseEntry {
  id: string;
  crop: string;
  disease_name: string;
  scientific_name?: string;
  causal_agent_type: string;
  is_healthy: boolean;
  symptoms: string;
  spread_mechanism: string;
  favorable_conditions: EnvironmentalConditions;
  prevention_steps: string[];
  organic_controls: string[];
  chemical_controls: string[];
  severity: string;
  when_to_consult_expert: string;
  safety_notes: string[];
  sources: string[];
}

export interface DailyForecast {
  date: string;
  temp_max_c: number;
  temp_min_c: number;
  temp_mean_c: number;
  humidity_mean_pct: number;
  precipitation_sum_mm: number;
  high_humidity_hours: number;
  wetness_risk_level: string;
}

export interface WeatherSummary {
  current_temp_c: number;
  current_humidity_pct: number;
  current_precipitation_mm: number;
  past_7d_mean_temp_c: number;
  past_7d_mean_humidity_pct: number;
  past_7d_total_rain_mm: number;
  past_7d_high_humidity_hours: number;
  forecast_7d_mean_temp_c: number;
  forecast_7d_mean_humidity_pct: number;
  forecast_7d_total_rain_mm: number;
  daily_forecasts: DailyForecast[];
  data_source: string;
  is_live: boolean;
}

export interface ContributingFactor {
  factor_name: string;
  impact: 'ELEVATES_RISK' | 'REDUCES_RISK' | 'NEUTRAL';
  explanation: string;
}

export interface DailyRiskOutlook {
  date: string;
  risk_score: number;
  risk_level: string;
  favorable_factors: string[];
}

export interface TopRegionalThreat {
  disease_id: string;
  disease_name: string;
  scientific_name?: string;
  causal_agent_type: string;
  risk_score: number;
  risk_level: string;
  risk_color: string;
  headline: string;
  summary: string;
  prevention_steps: string[];
}

export interface RiskAssessment {
  crop: string;
  target_condition: string;
  risk_score: number;
  risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'VERY HIGH';
  risk_color: string;
  headline: string;
  summary: string;
  contributing_factors: ContributingFactor[];
  daily_outlook: DailyRiskOutlook[];
  top_regional_threats?: TopRegionalThreat[];
  disclaimer: string;
}

export interface AnalysisResponse {
  id: string;
  predicted_label: string;
  crop: string;
  disease_name: string;
  confidence: number;
  confidence_display: string;
  is_uncertain: boolean;
  uncertainty_reason?: string;
  top_k: PredictionItem[];
  model_version: string;
  image_url: string;
  location_name?: string;
  latitude?: number;
  longitude?: number;
  weather_summary?: WeatherSummary;
  risk_assessment?: RiskAssessment;
  disease_details?: DiseaseEntry;
  created_at: string;
}

export interface AnalysisHistoryItem {
  id: string;
  predicted_label: string;
  crop: string;
  disease_name: string;
  confidence: number;
  is_uncertain: boolean;
  image_url: string;
  location_name?: string;
  created_at: string;
  has_feedback: boolean;
  is_feedback_correct?: boolean;
}

export interface FeedbackCreate {
  is_correct: boolean;
  corrected_label?: string;
  comments?: string;
  consent_for_retraining: boolean;
}

export interface FeedbackResponse {
  id: string;
  analysis_id: string;
  is_correct: boolean;
  corrected_label?: string;
  comments?: string;
  created_at: string;
}

export interface GeocodingResult {
  id?: number;
  name: string;
  latitude: number;
  longitude: number;
  elevation?: number;
  country?: string;
  admin1?: string;
}
