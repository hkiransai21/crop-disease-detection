"""Unit tests validating the 38-class agronomic knowledge base."""
import yaml
from pathlib import Path
from backend.app.knowledge_base.schema import KnowledgeBase, DiseaseEntry
from backend.app.services.risk import load_knowledge_base

EXPECTED_38_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___Cedar_apple_rust", "Apple___healthy",
    "Blueberry___healthy", "Cherry_(including_sour)___Powdery_mildew", "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot", "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight", "Corn_(maize)___healthy", "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)", "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)", "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)", "Peach___Bacterial_spot", "Peach___healthy",
    "Pepper,_bell___Bacterial_spot", "Pepper,_bell___healthy", "Potato___Early_blight",
    "Potato___Late_blight", "Potato___healthy", "Raspberry___healthy", "Soybean___healthy",
    "Squash___Powdery_mildew", "Strawberry___Leaf_scorch", "Strawberry___healthy",
    "Tomato___Bacterial_spot", "Tomato___Early_blight", "Tomato___Late_blight",
    "Tomato___Leaf_Mold", "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite", "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus", "Tomato___Tomato_mosaic_virus", "Tomato___healthy"
]


def test_knowledge_base_pydantic_schema_validation():
    """Verify that diseases.yaml strictly parses against Pydantic KnowledgeBase model."""
    kb_path = Path("backend/app/knowledge_base/diseases.yaml")
    assert kb_path.exists(), "diseases.yaml knowledge base file does not exist!"

    with open(kb_path, "r") as f:
        raw_data = yaml.safe_load(f)

    kb = KnowledgeBase(**raw_data)
    assert len(kb.diseases) >= 38, f"Expected at least 38 diseases, found {len(kb.diseases)}"


def test_all_38_classes_covered():
    """Ensure every single model class ID is represented in the knowledge base."""
    kb = load_knowledge_base()

    for cls_name in EXPECTED_38_CLASSES:
        assert cls_name in kb, f"Missing knowledge base entry for model class '{cls_name}'!"
        entry = kb[cls_name]
        
        # Verify mandatory attributes
        assert entry.crop, f"Empty crop name for {cls_name}"
        assert entry.disease_name, f"Empty disease name for {cls_name}"
        assert entry.symptoms, f"Empty symptoms for {cls_name}"
        assert len(entry.prevention_steps) > 0, f"Empty prevention steps for {cls_name}"
        assert len(entry.safety_notes) > 0, f"Empty safety notes for {cls_name}"
        assert len(entry.sources) > 0, f"Empty sources citations for {cls_name}"
        
        # Verify environmental condition thresholds
        cond = entry.favorable_conditions
        assert cond.temp_min_c < cond.temp_max_c, f"Invalid temp bounds for {cls_name}: {cond.temp_min_c} >= {cond.temp_max_c}"
        assert 0 <= cond.humidity_min_pct <= 100, f"Invalid humidity threshold for {cls_name}: {cond.humidity_min_pct}"
