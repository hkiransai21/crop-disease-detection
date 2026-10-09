# Model Card: AgriShield Crop Disease Classifier (EfficientNet-B0)

## 1. Model Details
- **Architecture**: `EfficientNet-B0` (Pretrained on ImageNet-1k via `timm`, fine-tuned for 38 crop disease classes).
- **Model Version**: `v1.0.0_efficientnet_b0`
- **Model Format**: ONNX (Open Neural Network Exchange, Opset 17, optimized for CPU inference via ONNX Runtime).
- **Deployment Size**: 15.45 MB (FP32 ONNX graph).
- **Input Specification**: RGB image, normalized with ImageNet mean `[0.485, 0.456, 0.406]` and standard deviation `[0.229, 0.224, 0.225]`, input dimension `(1, 3, 224, 224)`.
- **Output Specification**: 38 class logits calibrated with temperature parameter $T = 0.4130$.
- **License**: MIT / Apache 2.0 compatible.

---

## 2. Intended Use & Limitations
- **Primary Intended Use**: Fast, privacy-preserving, on-device or edge CPU visual screening of common crop foliar diseases for agricultural extension and smallholder farmers.
- **Supported Crops (14 species, 38 classes)**:
  - Apple (Scab, Black Rot, Cedar Rust, Healthy)
  - Blueberry (Healthy)
  - Cherry (Powdery Mildew, Healthy)
  - Corn/Maize (Cercospora Leaf Spot/Gray Leaf Spot, Common Rust, Northern Leaf Blight, Healthy)
  - Grape (Black Rot, Esca/Black Measles, Leaf Blight/Isariopsis, Healthy)
  - Orange (Huanglongbing/Citrus Greening)
  - Peach (Bacterial Spot, Healthy)
  - Pepper Bell (Bacterial Spot, Healthy)
  - Potato (Early Blight, Late Blight, Healthy)
  - Raspberry (Healthy)
  - Soybean (Healthy)
  - Squash (Powdery Mildew)
  - Strawberry (Leaf Scorch, Healthy)
  - Tomato (Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy)
- **Out-of-Scope Use Cases**:
  - Non-foliar disease diagnosis (root rots, vascular wilts without leaf symptoms, stem cankers).
  - High-consequence regulatory quarantine determinations without confirmatory laboratory assays (PCR / ELISA).
  - Fully automated chemical pesticide application without human agronomist review.

---

## 3. Training & Validation Datasets
- **Source Dataset**: PlantVillage (54,305 curated laboratory-condition leaf photographs).
- **Deduplication**: Perceptual difference hashing (`imagehash.dhash` + `phash` with Hamming distance $\le 4$) identified 987 duplicate pairs, collapsing images into 53,318 unique clusters.
- **Split Strategy**: Group-stratified splitting ensuring identical perceptual clusters never cross train/validation/test splits:
  - **Train Set**: 37,955 images (69.89%)
  - **Validation Set**: 8,113 images (14.94%)
  - **Held-Out Test Set**: 8,237 images (15.17%)
- **Cross-Dataset Benchmark**: PlantDoc (2,572 real-world field photographs in complex lighting and background foliage) used to empirically measure the lab-to-field generalization gap.

---

## 4. Performance Metrics (Real Measured Results)

### A. PlantVillage Held-Out Test Set Evaluation ($N = 8,237$)
| Metric | Value |
| :--- | :--- |
| **Top-1 Accuracy** | **94.22%** |
| **Macro-Averaged F1 Score** | **92.32%** |
| **Weighted-Averaged F1 Score** | **94.20%** |
| **Macro Precision** | **92.79%** |
| **Macro Recall** | **92.17%** |
| **Top-3 Accuracy** | **99.08%** |

### B. PlantDoc Real Field Cross-Dataset Benchmark ($N = 2,572$)
| Metric | Lab (PlantVillage Test) | Field (PlantDoc Cross) | Generalization Gap |
| :--- | :--- | :--- | :--- |
| **Accuracy** | 94.22% | **21.30%** | **72.92% drop** |
| **Macro-F1** | 92.32% | **14.92%** | **77.40% drop** |

> **Generalization Gap Analysis**: The lab-to-field domain shift is caused by complex background foliage, variable outdoor sunlight, multiple simultaneous infections on a single leaf, and partial leaf occlusions. The system mitigates this via Shannon entropy uncertainty rejection and transparent advisory warnings.

### C. Temperature Calibration Performance
Softmax probabilities are calibrated using validation-set temperature scaling:
| Metric | Uncalibrated ($T = 1.0$) | Calibrated ($T = 0.4130$) | Improvement |
| :--- | :--- | :--- | :--- |
| **Expected Calibration Error (ECE)** | **25.71%** | **0.50%** | **98.07% reduction** |
| **Optimal Temperature $T$** | - | **0.4130** | - |

---

## 5. Deployment & Runtime Benchmarks (Apple Silicon M-Series CPU)
Measured across 100 single-image inference runs with single-thread CPU execution:

| Model Format | Model Size | Median Latency | p95 Latency | p99 Latency | Throughput | Test Accuracy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FP32 ONNX (Recommended)** | **15.45 MB** | **7.64 ms** | **8.74 ms** | **10.04 ms** | **130.9 FPS** | **94.22%** |
| INT8 Dynamic Quantization | 4.15 MB | 22.26 ms | 23.67 ms | 24.58 ms | 44.9 FPS | 2.87% |

- **PyTorch vs ONNX Runtime Numerical Parity**:
  - Maximum Logit Difference: $1.53 \times 10^{-5}$
  - Maximum Probability Difference: $1.73 \times 10^{-6}$ (Well within the $1.0 \times 10^{-4}$ tolerance threshold).

---

## 6. Explainability & Trust
- **Grad-CAM Saliency Maps**: Implemented via gradient-weighted class activations on the final convolutional layer (`conv_head`, 320 to 1280 channels). Visualizations confirm the network attends to necrotic fungal lesions, chlorotic halos, and rust pustules rather than background leaf borders.
- **Uncertainty Rejection**: Predictions with Shannon entropy $H(p) > 2.20$ or confidence $< 60\%$ are flagged with `is_uncertain: true` and display prominent advisory banners in the frontend UI.

---

## 7. Environmental & Ethical Considerations
- **Compute Efficiency**: Total two-stage training required under 1 hour on Apple Silicon GPU (`mps`), with negligible carbon emissions (<0.05 kg CO2eq).
- **False Negative Impact**: A false negative on aggressive pathogens (e.g., Potato Late Blight *Phytophthora infestans*) could risk crop loss. The system combines vision confidence with live weather outbreak modeling to warn farmers even when visual confidence is borderline.
- **Data Privacy & Consent**: All voluntary retraining samples strictly enforce the `consent_for_retraining = true` flag. Images without consent are never merged into dataset updates.
