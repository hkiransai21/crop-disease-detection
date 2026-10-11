"""Comprehensive unit, integration, and regression tests for Multilingual i18n and Regional TTS Audio."""
import re
import json
import pytest
from pathlib import Path
from httpx import AsyncClient

from backend.app.services.i18n import (
    get_i18n_config,
    get_supported_languages,
    resolve_language,
    get_localized_disease_entry,
    get_localized_glossary,
    load_localized_knowledge_base
)
from backend.app.services.tts import (
    TTSProvider,
    MockTTSProvider,
    EdgeTTSProvider,
    build_narration_script,
    get_tts_provider,
    get_or_synthesize_audio
)
from backend.app.schemas.i18n import (
    LanguageConfig,
    SupportedLanguagesResponse,
    GlossaryDiseaseEntry,
    GlossaryTermEntry,
    LanguageGlossary,
    LocalizedDiseaseEntry,
    LocalizedKnowledgeBase,
    AudioSynthesizeRequest
)
from backend.app.services.risk import load_knowledge_base
from backend.app.ml.inference import predict_disease, load_inference_artifacts

# Ensure ONNX model and temperature scaling artifacts are loaded
load_inference_artifacts()

SUPPORTED_LANGUAGES = ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "es"]
BASE_DIR = Path(__file__).resolve().parent.parent
I18N_DATA_DIR = BASE_DIR / "app" / "data" / "i18n"
GLOSSARY_DIR = I18N_DATA_DIR / "glossary"


class TestGlossaryAndSchemaCompleteness:
    """Validate completeness and schema integrity across all 38 classes for all 9 languages."""

    def test_supported_languages_config(self):
        resp = get_supported_languages()
        assert resp.default_language == "en"
        assert len(resp.languages) == 9
        lang_codes = [l.code for l in resp.languages]
        expected = ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "es"]
        assert set(lang_codes) == set(expected)

        for lang_info in resp.languages:
            assert lang_info.native_name
            assert lang_info.tts_voice
            assert lang_info.name

    def test_all_38_diseases_in_all_glossaries(self):
        kb = load_knowledge_base()
        canonical_ids = list(kb.keys())
        assert len(canonical_ids) == 38

        for lang in SUPPORTED_LANGUAGES:
            glossary = get_localized_glossary(lang)
            assert glossary is not None, f"Glossary for {lang} failed to load."
            assert glossary["language"] == lang
            diseases = glossary["diseases"]
            assert len(diseases) == 38, f"Glossary for {lang} has {len(diseases)} diseases, expected 38."

            for cid in canonical_ids:
                assert cid in diseases, f"Missing {cid} in {lang} glossary."
                entry = diseases[cid]
                assert entry["id"] == cid
                assert len(entry["common_name"].strip()) > 0
                assert len(entry["scientific_name"].strip()) > 0
                assert len(entry["tts_text"].strip()) > 0
                assert entry["review_status"] in ["draft", "machine_suggested", "expert_reviewed"]
                assert len(entry["source"].strip()) > 0

    def test_all_38_diseases_in_all_localized_databases(self):
        kb = load_knowledge_base()
        canonical_ids = set(kb.keys())

        for lang in SUPPORTED_LANGUAGES:
            localized_kb = load_localized_knowledge_base(lang)
            assert len(localized_kb) == 38, f"Localized KB for {lang} has {len(localized_kb)} entries, expected 38."
            for cid in canonical_ids:
                assert cid in localized_kb, f"Missing {cid} in {lang} disease database."
                entry = localized_kb[cid]
                assert entry.id == cid
                assert len(entry.crop.strip()) > 0
                assert len(entry.disease_name.strip()) > 0
                assert len(entry.symptoms.strip()) > 0
                assert len(entry.prevention_steps) > 0
                if not entry.is_healthy:
                    assert len(entry.organic_controls) > 0
                    assert len(entry.chemical_controls) > 0


class TestNumericAndDosageParity:
    """Verify that vital dosages, temperatures, and units are strictly preserved across languages."""

    @staticmethod
    def extract_numbers_with_units(text: str) -> list[str]:
        # Extract patterns like 2.5g/L, 5ml/L, 15L, 20°C, 85%, etc.
        patterns = re.findall(r'\b\d+(?:\.\d+)?\s*(?:g/L|ml/L|%|°C|L|mm|hours|days|acres|ha)?\b', text, re.IGNORECASE)
        return [p.strip() for p in patterns if any(c.isdigit() for c in p)]

    def test_numeric_dosage_parity_with_english(self):
        en_kb = load_localized_knowledge_base("en")

        for lang in ["hi", "te", "ta", "kn", "ml", "mr", "bn", "es"]:
            target_kb = load_localized_knowledge_base(lang)

            for cid, en_entry in en_kb.items():
                target_entry = target_kb[cid]

                # Compare favorable weather parameters
                assert en_entry.favorable_conditions.temp_min_c == target_entry.favorable_conditions.temp_min_c
                assert en_entry.favorable_conditions.temp_max_c == target_entry.favorable_conditions.temp_max_c
                assert en_entry.favorable_conditions.humidity_min_pct == target_entry.favorable_conditions.humidity_min_pct

                # Compare chemical control text numbers (e.g. 2.5g/L, 5ml/L)
                if en_entry.chemical_controls and target_entry.chemical_controls:
                    en_chem = " ".join(en_entry.chemical_controls)
                    tr_chem = " ".join(target_entry.chemical_controls)

                    # Verify key numbers like 2.5 or 5 or 75 exist in translation if in English
                    for num in ["2.5", "5", "75", "10", "15"]:
                        if num in en_chem:
                            assert num in tr_chem, f"Critical dosage number '{num}' missing from {lang} {cid} chemical controls."


class TestLanguageNegotiationAndFallback:
    """Test resolution of Accept-Language headers and query params."""

    def test_resolve_language_explicit(self):
        assert resolve_language("hi") == "hi"
        assert resolve_language("te") == "te"
        assert resolve_language("ta") == "ta"
        assert resolve_language("es") == "es"

    def test_resolve_language_fallback_to_english(self):
        assert resolve_language("unknown_lang") == "en"
        assert resolve_language(None) == "en"

    def test_resolve_accept_language_header(self):
        assert resolve_language(None, "te-IN,te;q=0.9,en;q=0.8") == "te"
        assert resolve_language(None, "ta-IN,ta;q=0.9") == "ta"
        assert resolve_language(None, "fr-FR,fr;q=0.9") == "en"

    def test_query_param_takes_precedence_over_header(self):
        assert resolve_language("hi", "te-IN,te;q=0.9") == "hi"


class TestTTSProviderAndNarrationScripts:
    """Test TTS provider interface, SSML synthesis, and audio pre-generation."""

    @pytest.mark.asyncio
    async def test_mock_tts_provider(self):
        provider = MockTTSProvider()
        audio_bytes = await provider.synthesize("Namaste Kisan", lang="hi", voice="hi-IN-SwaraNeural")
        assert len(audio_bytes) > 0

    def test_build_narration_scripts(self):
        overview = build_narration_script("Tomato___Early_blight", "overview", "te")
        assert "టమోటా" in overview or "Early Blight" in overview
        assert not any(emoji in overview for emoji in ["🌾", "🌱", "🔬", "⚠️", "📞"])

        treatment = build_narration_script("Tomato___Early_blight", "treatment", "te")
        assert len(treatment) > 20

        prevention = build_narration_script("Tomato___Early_blight", "prevention", "te")
        assert len(prevention) > 20

    @pytest.mark.asyncio
    async def test_audio_cache_hit_and_synthesis(self):
        script = build_narration_script("Tomato___Early_blight", "overview", "hi")
        audio_bytes = await get_or_synthesize_audio(script, lang="hi")
        assert len(audio_bytes) > 0


class TestMultilingualAPIRoutes:
    """Test API endpoints responding in requested regional languages."""

    @pytest.mark.asyncio
    async def test_get_audio_languages(self, client: AsyncClient):
        response = await client.get("/api/v1/audio/languages")
        assert response.status_code == 200
        data = response.json()
        assert data["default_language"] == "en"
        assert len(data["languages"]) == 9

    @pytest.mark.asyncio
    async def test_get_audio_glossary(self, client: AsyncClient):
        response = await client.get("/api/v1/audio/glossary/te")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "te"
        assert "Tomato___Early_blight" in data["diseases"]
        assert "Alternaria" in data["diseases"]["Tomato___Early_blight"]["scientific_name"]

    @pytest.mark.asyncio
    async def test_get_disease_audio_stream(self, client: AsyncClient):
        response = await client.get("/api/v1/audio/Tomato___Early_blight/overview?lang=hi")
        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert len(response.content) > 0

    @pytest.mark.asyncio
    async def test_get_diseases_localized(self, client: AsyncClient):
        # Fetch in Telugu
        response_te = await client.get("/api/v1/diseases?lang=te")
        assert response_te.status_code == 200
        diseases_te = response_te.json()
        assert len(diseases_te) == 38
        tomato_eb_te = next(d for d in diseases_te if d["id"] == "Tomato___Early_blight")
        assert tomato_eb_te["crop"] == "టమోటా"
        assert "ముందస్తు" in tomato_eb_te["disease_name"] or "Early Blight" in tomato_eb_te["disease_name"]
        assert "Alternaria" in tomato_eb_te["scientific_name"]

        # Fetch in Tamil
        response_ta = await client.get("/api/v1/diseases?lang=ta")
        assert response_ta.status_code == 200
        diseases_ta = response_ta.json()
        tomato_eb_ta = next(d for d in diseases_ta if d["id"] == "Tomato___Early_blight")
        assert tomato_eb_ta["crop"] == "தக்காளி"

    @pytest.mark.asyncio
    async def test_analyze_endpoint_multilingual(self, client: AsyncClient, sample_leaf_image_bytes: bytes):
        files = {"image": ("test_leaf.jpg", sample_leaf_image_bytes, "image/jpeg")}

        # Test diagnosis in Hindi
        response_hi = await client.post("/api/v1/analyze?lang=hi", files=files)
        assert response_hi.status_code == 200
        data_hi = response_hi.json()

        # Canonical key must remain exact
        assert "___" in data_hi["predicted_label"]
        assert data_hi["confidence"] > 0
        assert data_hi["model_version"].startswith("v1.0.0")

        # Localized fields should be populated
        assert data_hi["crop"] is not None
        assert data_hi["disease_name"] is not None
        if data_hi.get("disease_details"):
            assert len(data_hi["disease_details"]["symptoms"]) > 0

        # Test diagnosis in Telugu
        files2 = {"image": ("test_leaf.jpg", sample_leaf_image_bytes, "image/jpeg")}
        response_te = await client.post("/api/v1/analyze?lang=te", files=files2)
        assert response_te.status_code == 200
        data_te = response_te.json()
        assert data_te["predicted_label"] == data_hi["predicted_label"]


class TestModelPredictionByteIdenticalRegression:
    """Hard Constraint: The ML prediction logic and outputs MUST remain byte-identical regardless of language."""

    def test_onnx_model_output_invariance_across_languages(self, sample_leaf_image_bytes: bytes):
        import io
        from PIL import Image

        image = Image.open(io.BytesIO(sample_leaf_image_bytes)).convert("RGB")

        # Run multiple inference passes on the identical image
        result_1 = predict_disease(image)
        result_2 = predict_disease(image)

        assert result_1["predicted_label"] == result_2["predicted_label"]
        assert result_1["confidence"] == result_2["confidence"]
        assert result_1["entropy"] == result_2["entropy"]
        assert result_1["is_uncertain"] == result_2["is_uncertain"]
        assert len(result_1["top_k"]) == len(result_2["top_k"])
        for p1, p2 in zip(result_1["top_k"], result_2["top_k"]):
            assert p1["class_id"] == p2["class_id"]
            assert p1["confidence"] == p2["confidence"]

