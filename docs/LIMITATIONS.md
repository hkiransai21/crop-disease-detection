# System Limitations, Boundaries & Safety Disclaimers

## 1. Laboratory vs Field Generalization Gap (Domain Shift)

- **Root Cause**: PlantVillage training images were captured under controlled laboratory lighting with detached leaves mounted against uniform gray/black backdrops. In contrast, real farm photos contain complex soil backgrounds, weed foliage, direct sunlight glare, shadows, insect feeding damage, and multi-pathogen co-infections.
- **Measured Impact**: As benchmarked in `ml/reports/generalization_gap.json`, model performance on real-world in-situ field photos (PlantDoc) exhibits a measurable accuracy drop compared to lab test splits.
- **Mitigation**: We employ heavy data augmentations (random resized cropping, color jitter, Gaussian blur, random erasing, brightness perturbation) and an uncertainty rejection threshold to prevent over-confident misdiagnoses on out-of-domain images.

---

## 2. Rule-Based Risk Engine Boundaries

- **Nature of the Model**: The Outbreak Risk Engine is a transparent agronomic heuristic based on published university microclimate thresholds. It is **not** an epidemiological simulation or a validated machine learning forecast model.
- **Limitations**:
  - The engine models microclimate conditions (temperature, humidity, rainfall) but does **not** account for soil pH, cultivar resistance genes, regional spore trap surveillance, or historical fungicide spray schedules.
  - Weather data from Open-Meteo is derived from numerical weather prediction (NWP) models (ERA5, GFS, ECMWF) interpolated to ~1-10km grid cells. Local microclimates (e.g. sheltered valley vs windy hill, furrow canopy humidity) may differ from regional station averages.
- **Mandatory Disclaimer**: All risk scores are presented strictly as advisory risk estimates to assist scouting, never as definitive infection guarantees.

---

## 3. Supported Crops & Out-of-Scope Handling

The system currently supports 14 crops across 38 distinct conditions:
- **Supported Crops**: Apple, Blueberry, Cherry, Corn (Maize), Grape, Orange (Citrus), Peach, Pepper (Bell), Potato, Raspberry, Soybean, Squash, Strawberry, Tomato.
- **Out-of-Scope Inputs**: Uploading photos of unsupported crops (e.g., Rice, Wheat, Cassava, Banana, Coffee), non-leaf plant organs (bark, roots), or non-plant objects triggers the uncertainty rejection mechanism when prediction entropy is high or confidence is below 60%. Farmers are advised to consult local extension offices for unsupported crops.

---

## 4. Pesticide Safety & Legal Disclaimers

- **No Dosages Stated**: Chemical controls in the knowledge base list only generic active-ingredient classes (e.g. "Copper fungicides", "Azoxystrobin", "Chlorothalonil"). Exact application rates, spray volumes, tank-mixing compatibility, and re-entry intervals vary by national jurisdiction and specific commercial brand formulation.
- **Legal Prerequisite**: Users are instructed in every recommendation card to read the physical product label and follow local agricultural regulations before purchasing or applying any pesticide.
- **Human in the Loop**: When disease severity is categorized as HIGH or CRITICAL, the system provides explicit criteria for escalating to a licensed agronomist or local agricultural extension officer.
