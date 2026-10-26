"""Migrate repeated immediate advice from existing localized class-specific controls.

No chemical names/doses are generated. All migrated entries require expert review.
"""
import json
from pathlib import Path


def main():
    base = Path('backend/app/data/i18n')
    for lang in ('en','hi','ta','te','kn'):
        path = base/lang/'diseases.json'
        data = json.loads(path.read_text(encoding='utf-8'))
        for entry in data['diseases']:
            # Healthy records already contain maintenance-specific prevention.
            entry['immediate_actions'] = list(entry['prevention_steps'][:2] if entry['is_healthy'] else entry['organic_controls'][:2])
            entry['review_status'] = 'machine_suggested'
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    english = json.loads((base/'en/diseases.json').read_text(encoding='utf-8'))['diseases']
    rules = {}
    for entry in english:
        rules[entry['id']] = dict(entry['favorable_conditions'],
            humidity_mode='dry' if 'Spider_mites' in entry['id'] else 'humid',
            rationale=entry['spread_mechanism'], sources=entry['sources'], review_status='machine_suggested')
    Path('backend/app/data/risk_rules.json').write_text(json.dumps({
        '_comment': 'Heuristic index, not infection probability. Existing KB thresholds and spread reasoning; expert review required. Rain/wetness use recent 72h and next 48h when available. Wind is a dispersal modifier only for wind_spread classes.',
        'weights': {'temperature_suppression_factor':0.25, 'temperature_optimal':35, 'temperature_favorable':25, 'temperature_edge':15, 'temperature_unfavorable':5,
                    'humidity_high':30, 'humidity_near':18, 'humidity_low':5, 'wetness':10, 'rain_heavy':25, 'rain_some':15, 'rain_low':5, 'wind':5},
        'rules':rules}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
