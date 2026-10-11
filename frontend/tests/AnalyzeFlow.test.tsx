import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ConfidenceBar } from '../src/components/ConfidenceBar';
import { RiskGauge } from '../src/components/RiskGauge';
import { ActionChecklist } from '../src/components/ActionChecklist';
import { AudioNarrator } from '../src/components/AudioNarrator';
import { KnapsackCalculator } from '../src/components/KnapsackCalculator';
import { WhatsAppShareModal } from '../src/components/WhatsAppShareModal';
import { RiskAssessment, DiseaseEntry } from '../src/types';
import '../src/i18n/i18n';

describe('Frontend Component Tests', () => {
  it('renders ConfidenceBar with high reliability badge', () => {
    render(
      <ConfidenceBar
        confidence={0.92}
        confidenceDisplay="Very High Confidence"
        isUncertain={false}
        topK={[
          {
            class_id: 'Tomato___Early_blight',
            crop: 'Tomato',
            disease_name: 'Early Blight',
            confidence: 0.92,
            confidence_percentage: 92.0,
            is_healthy: false,
          },
        ]}
      />
    );

    expect(screen.getByText('92%')).toBeInTheDocument();
    expect(screen.getByText('High Reliability')).toBeInTheDocument();
  });

  it('renders ConfidenceBar in uncertain state with warning', () => {
    render(
      <ConfidenceBar
        confidence={0.42}
        confidenceDisplay="Low / Uncertain"
        isUncertain={true}
        uncertaintyReason="Low diagnostic confidence threshold."
        topK={[]}
      />
    );

    expect(screen.getByText('Uncertain Diagnostic')).toBeInTheDocument();
    expect(screen.getByText(/Low diagnostic confidence threshold/)).toBeInTheDocument();
  });

  it('renders RiskGauge with score and contributing factors', () => {
    const mockAssessment: RiskAssessment = {
      crop: 'Tomato',
      target_condition: 'Early Blight',
      risk_score: 78,
      risk_level: 'VERY HIGH',
      risk_color: '#ef4444',
      headline: 'CRITICAL: High Outbreak Risk',
      summary: 'Weather conditions are exceptionally favorable.',
      contributing_factors: [
        {
          factor_name: 'High Atmospheric Humidity',
          impact: 'ELEVATES_RISK',
          explanation: 'Humidity exceeds 85%.',
        },
      ],
      daily_outlook: [],
      disclaimer: 'Advisory heuristic estimate.',
    };

    render(<RiskGauge assessment={mockAssessment} />);

    expect(screen.getByText('78')).toBeInTheDocument();
    expect(screen.getByText(/CRITICAL: High Outbreak Risk/)).toBeInTheDocument();
    expect(screen.getByText('High Atmospheric Humidity')).toBeInTheDocument();
    expect(screen.getByText(/Advisory heuristic estimate/)).toBeInTheDocument();
  });

  it('renders ActionChecklist with cultural, organic, and safety notes', () => {
    const mockDisease: DiseaseEntry = {
      id: 'Tomato___Early_blight',
      crop: 'Tomato',
      disease_name: 'Early Blight',
      scientific_name: 'Alternaria solani',
      causal_agent_type: 'fungal',
      is_healthy: false,
      symptoms: 'Target spots with concentric rings.',
      spread_mechanism: 'Rain splash.',
      favorable_conditions: {
        temp_min_c: 20,
        temp_max_c: 32,
        humidity_min_pct: 80,
        leaf_wetness_hours_min: 6,
        rainfall_favorable: true,
        wind_spread: true,
      },
      prevention_steps: ['Prune bottom 12 inches of foliage.'],
      organic_controls: ['Apply copper octanoate.'],
      chemical_controls: ['Chlorothalonil, Mancozeb.'],
      severity: 'HIGH',
      when_to_consult_expert: 'If lesions reach mid-canopy.',
      safety_notes: ['Wear protective gloves and mask.'],
      sources: ['Cornell Vegetable MD Online'],
    };

    render(<ActionChecklist disease={mockDisease} />);

    expect(screen.getByText('Treatment & Prevention Checklist')).toBeInTheDocument();
    expect(screen.getByText('Prune bottom 12 inches of foliage.')).toBeInTheDocument();
    expect(screen.getByText('Wear protective gloves and mask.')).toBeInTheDocument();
    expect(screen.getByText('Cornell Vegetable MD Online')).toBeInTheDocument();
  });

  it('renders AudioNarrator with Kisan Audio Assistant and language controls', () => {
    const mockAnalysis = {
      id: 'test-123',
      predicted_label: 'Tomato___Early_blight',
      crop: 'Tomato',
      disease_name: 'Early Blight',
      confidence: 0.94,
      confidence_display: 'Very High Confidence',
      is_uncertain: false,
      top_k: [],
      model_version: 'v1.0.0_efficientnet_b0',
      image_url: '/test.jpg',
      created_at: new Date().toISOString(),
      risk_assessment: {
        crop: 'Tomato',
        target_condition: 'Early Blight',
        risk_score: 80,
        risk_level: 'VERY HIGH' as const,
        risk_color: '#ef4444',
        headline: 'Critical Risk',
        summary: 'Weather conditions are humid.',
        contributing_factors: [],
        daily_outlook: [],
        disclaimer: 'Advisory estimate.'
      },
      disease_details: {
        id: 'Tomato___Early_blight',
        crop: 'Tomato',
        disease_name: 'Early Blight',
        causal_agent_type: 'fungal',
        is_healthy: false,
        symptoms: 'Concentric rings',
        spread_mechanism: 'Rain splash',
        favorable_conditions: {
          temp_min_c: 20,
          temp_max_c: 32,
          humidity_min_pct: 80,
          leaf_wetness_hours_min: 6,
          rainfall_favorable: true,
          wind_spread: true
        },
        prevention_steps: ['Prune lower leaves'],
        organic_controls: ['Neem oil spray'],
        chemical_controls: ['Mancozeb 75% WP'],
        severity: 'HIGH',
        when_to_consult_expert: 'Check KVK',
        safety_notes: ['Wear gloves'],
        sources: ['Purdue Extension']
      }
    };

    render(<AudioNarrator analysis={mockAnalysis as any} />);

    expect(screen.getByText('Kisan Audio Assistant')).toBeInTheDocument();
    expect(screen.getAllByText(/1800-180-1551/)[0]).toBeInTheDocument();
    expect(screen.getAllByText(/Listen in/)[0]).toBeInTheDocument();
  });

  it('renders KnapsackCalculator with spray dosage and water measurement calculations', () => {
    const mockDisease: DiseaseEntry = {
      id: 'Tomato___Early_blight',
      crop: 'Tomato',
      disease_name: 'Early Blight',
      causal_agent_type: 'fungal',
      is_healthy: false,
      symptoms: 'Concentric rings',
      spread_mechanism: 'Rain splash',
      favorable_conditions: {
        temp_min_c: 20,
        temp_max_c: 32,
        humidity_min_pct: 80,
        leaf_wetness_hours_min: 6,
        rainfall_favorable: true,
        wind_spread: true,
      },
      prevention_steps: ['Prune lower leaves'],
      organic_controls: ['Neem oil spray'],
      chemical_controls: ['Mancozeb 75% WP'],
      severity: 'HIGH',
      when_to_consult_expert: 'Check KVK',
      safety_notes: ['Wear gloves'],
      sources: ['Purdue Extension'],
    };

    render(<KnapsackCalculator disease={mockDisease} cropName="Tomato" />);

    expect(screen.getByText('Spray Tank & Knapsack Pump Calculator')).toBeInTheDocument();
    expect(screen.getAllByText(/15L/)[0]).toBeInTheDocument();
    expect(screen.getByText(/Field Mixing Instructions/)).toBeInTheDocument();
  });

  it('renders WhatsAppShareModal with formatted report and copy/share actions', () => {
    const mockAnalysis = {
      id: 'test-123',
      predicted_label: 'Tomato___Early_blight',
      crop: 'Tomato',
      disease_name: 'Early Blight',
      confidence: 0.94,
      confidence_display: 'Very High Confidence',
      is_uncertain: false,
      top_k: [],
      model_version: 'v1.0.0_efficientnet_b0',
      image_url: '/test.jpg',
      created_at: new Date().toISOString(),
      disease_details: {
        id: 'Tomato___Early_blight',
        crop: 'Tomato',
        disease_name: 'Early Blight',
        causal_agent_type: 'fungal',
        is_healthy: false,
        symptoms: 'Concentric rings',
        spread_mechanism: 'Rain splash',
        favorable_conditions: {
          temp_min_c: 20,
          temp_max_c: 32,
          humidity_min_pct: 80,
          leaf_wetness_hours_min: 6,
          rainfall_favorable: true,
          wind_spread: true,
        },
        prevention_steps: ['Prune lower leaves'],
        organic_controls: ['Neem oil spray'],
        chemical_controls: ['Mancozeb 75% WP'],
        severity: 'HIGH',
        when_to_consult_expert: 'Check KVK',
        safety_notes: ['Wear gloves'],
        sources: ['Purdue Extension'],
      },
    };

    render(
      <WhatsAppShareModal
        analysis={mockAnalysis as any}
        isOpen={true}
        onClose={() => {}}
      />
    );

    expect(screen.getByText('Share Report on WhatsApp')).toBeInTheDocument();
    expect(screen.getByText('Open in WhatsApp')).toBeInTheDocument();
    expect(screen.getByText('Copy Summary Text')).toBeInTheDocument();
    expect(screen.getByText('हिन्दी (Hindi)')).toBeInTheDocument();
  });
});
