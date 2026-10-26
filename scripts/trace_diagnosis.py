"""Reproducible evidence capture; never changes model artifacts or invents fixtures."""
import asyncio
import hashlib
import json
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from httpx import AsyncClient, ASGITransport
from backend.app.ml import inference
from backend.app.main import app
from backend.app.services.i18n import load_localized_knowledge_base


async def main():
    output = Path(sys.argv[1])
    output.mkdir(parents=True, exist_ok=True)
    inference.load_inference_artifacts()
    records = []
    async with AsyncClient(transport=ASGITransport(app=app), base_url='http://test') as client:
        for path in sorted(Path('backend/tests/fixtures/leaves').glob('*.jpg')):
            image = Image.open(path).convert('RGB')
            tensor = inference.preprocess_image(image)
            logits = inference._ORT_SESSION.run(None, {inference._ORT_SESSION.get_inputs()[0].name: tensor})[0][0]
            raw = np.exp(logits - logits.max()); raw /= raw.sum()
            prediction = inference.predict_disease(image)
            response = await client.post('/api/v1/analyze', files={'image': (path.name, path.read_bytes(), 'image/jpeg')})
            records.append(dict(image=path.name, sha256=hashlib.sha256(path.read_bytes()).hexdigest(), logits=logits.tolist(),
                raw_top3=[{'class': inference._LABELS[i], 'probability': float(raw[i])} for i in np.argsort(raw)[::-1][:3]],
                prediction=prediction, status=response.status_code, final_json=response.json()))
    (output/'images.json').write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    counts = {lang: {field: len({str(getattr(d, field)) for d in load_localized_knowledge_base(lang).values()})
        for field in ('symptoms','immediate_actions','organic_controls','chemical_controls','prevention_steps')}
        for lang in ('en','hi','ta','te','kn')}
    (output/'content-counts.json').write_text(json.dumps(counts, indent=2), encoding='utf-8')
    hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('ml/models').glob('*') if p.is_file()}
    (output/'model-hashes.json').write_text(json.dumps(hashes, indent=2), encoding='utf-8')
    print(json.dumps([{'image': r['image'], 'label': r['prediction']['predicted_label'], 'entropy': r['prediction']['entropy'], 'uncertain': r['prediction']['is_uncertain'], 'status': r['status']} for r in records], indent=2))


if __name__ == '__main__':
    asyncio.run(main())
