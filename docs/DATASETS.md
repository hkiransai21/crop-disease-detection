# Datasets, Provenance & Data Integrity

## 1. Datasets Overview

The diagnostic model is trained on the authoritative PlantVillage benchmark and evaluated cross-dataset on the PlantDoc real-world field benchmark.

| Dataset | Origin / Reference | Image Count | Class Count | Domain Context | License |
|---|---|---|---|---|---|
| **PlantVillage** | Hughes, D. & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics.* | 54,303 raw | 38 classes (14 crops) | Controlled lab environment, uniform background | CC BY-SA 4.0 |
| **PlantDoc** | Singh, D. et al. (2020). *PlantDoc: A Dataset for Visual Plant Disease Detection in the Wild.* CoDS-COMAD. | 2,598 images | 13 overlapping / 27 total classes | Real-world in-situ field conditions, complex backgrounds, variable lighting | MIT License |

---

## 2. The 38 PlantVillage Diagnostic Classes

1. `Apple___Apple_scab` (*Venturia inaequalis*)
2. `Apple___Black_rot` (*Botryosphaeria obtusa*)
3. `Apple___Cedar_apple_rust` (*Gymnosporangium juniperi-virginianae*)
4. `Apple___healthy`
5. `Blueberry___healthy`
6. `Cherry_(including_sour)___Powdery_mildew` (*Podosphaera clandestina*)
7. `Cherry_(including_sour)___healthy`
8. `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot` (*Cercospora zeae-maydis*)
9. `Corn_(maize)___Common_rust_` (*Puccinia sorghi*)
10. `Corn_(maize)___Northern_Leaf_Blight` (*Exserohilum turcicum*)
11. `Corn_(maize)___healthy`
12. `Grape___Black_rot` (*Guignardia bidwellii*)
13. `Grape___Esca_(Black_Measles)` (*Phaeomoniella chlamydospora* complex)
14. `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)` (*Pseudocercospora cladosporioides*)
15. `Grape___healthy`
16. `Orange___Haunglongbing_(Citrus_greening)` (*Candidatus Liberibacter*)
17. `Peach___Bacterial_spot` (*Xanthomonas arboricola pv. pruni*)
18. `Peach___healthy`
19. `Pepper,_bell___Bacterial_spot` (*Xanthomonas campestris pv. vesicatoria*)
20. `Pepper,_bell___healthy`
21. `Potato___Early_blight` (*Alternaria solani*)
22. `Potato___Late_blight` (*Phytophthora infestans*)
23. `Potato___healthy`
24. `Raspberry___healthy`
25. `Soybean___healthy`
26. `Squash___Powdery_mildew` (*Podosphaera xanthii*)
27. `Strawberry___Leaf_scorch` (*Diplocarpon earlianum*)
28. `Strawberry___healthy`
29. `Tomato___Bacterial_spot` (*Xanthomonas perforans*)
30. `Tomato___Early_blight` (*Alternaria solani*)
31. `Tomato___Late_blight` (*Phytophthora infestans*)
32. `Tomato___Leaf_Mold` (*Passalora fulva*)
33. `Tomato___Septoria_leaf_spot` (*Septoria lycopersici*)
34. `Tomato___Spider_mites Two-spotted_spider_mite` (*Tetranychus urticae*)
35. `Tomato___Target_Spot` (*Corynespora cassiicola*)
36. `Tomato___Tomato_Yellow_Leaf_Curl_Virus` (TYLCV, Begomovirus)
37. `Tomato___Tomato_mosaic_virus` (ToMV, Tobamovirus)
38. `Tomato___healthy`

---

## 3. Data Integrity & Leakage Prevention Protocol

### A. Perceptual Hashing Deduplication (`imagehash`)
PlantVillage contains numerous near-duplicate captures of the same leaf photographed from slightly different angles or zoom levels. If random splitting is applied, these duplicates leak across train, validation, and test sets, artificially inflating test accuracy.

**Protocol (`ml/src/prepare_splits.py`)**:
1. Compute 64-bit difference hash (`dhash`) and perceptual hash (`phash`) for every image.
2. Group images with a Hamming distance $\le 4$ into duplicate clusters (`hash_group_id`).
3. Execute **Group-Stratified Splitting** (70% Train, 15% Validation, 15% Test) so that all images in a hash cluster are strictly assigned to the exact same partition.
4. Persist the split manifest to `ml/data/processed/split_manifest.csv` with SHA-256 hashes for cryptographic reproducibility.

---

## 4. Cross-Dataset Mapping (PlantDoc)

PlantDoc uses different naming conventions and includes disease classes that do not exist in PlantVillage. To ensure fair and transparent cross-dataset generalization benchmarking, explicit mapping rules are defined in `ml/configs/plantdoc_mapping.json`:

```json
{
  "overlapping_classes": {
    "Apple Scab Leaf": "Apple___Apple_scab",
    "Apple rust leaf": "Apple___Cedar_apple_rust",
    "Apple leaf": "Apple___healthy",
    "Cherry leaf": "Cherry_(including_sour)___healthy",
    "Corn leaf blight": "Corn_(maize)___Northern_Leaf_Blight",
    "Corn rust leaf": "Corn_(maize)___Common_rust_",
    "Grape leaf black rot": "Grape___Black_rot",
    "Grape leaf": "Grape___healthy",
    "Peach leaf": "Peach___healthy",
    "Potato leaf early blight": "Potato___Early_blight",
    "Potato leaf late blight": "Potato___Late_blight",
    "Tomato leaf early blight": "Tomato___Early_blight",
    "Tomato leaf late blight": "Tomato___Late_blight",
    "Tomato leaf bacterial spot": "Tomato___Bacterial_spot",
    "Tomato leaf mosaic virus": "Tomato___Tomato_mosaic_virus",
    "Tomato leaf yellow virus": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato leaf": "Tomato___healthy"
  },
  "unmapped_classes": [
    "Bell_pepper leaf spot",
    "Blueberry leaf",
    "Raspberry leaf",
    "Soyabean leaf",
    "Squash Powdery mildew leaf",
    "Strawberry leaf"
  ]
}
```
Cross-dataset evaluation evaluates the model exclusively on the validated overlapping classes to measure real-world domain transfer.
