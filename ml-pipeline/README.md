# ML Training Pipeline

## Training
```bash
python train_classifier.py
```
Loads `data/ingredient_6L.csv`, creates health risk labels, trains GradientBoosting classifier (86% accuracy), saves models to `models/`

## Prediction
```bash
python predict.py
```
Loads trained models, predicts health risks for ingredients

## Features
18 text-based features extracted from ingredient names (fat/protein/sugar keywords, processing level, name statistics)

## Output
- `models/health_risk_classifier.pkl` - Trained model
- `models/feature_scaler.pkl` - Feature scaler
- `models/feature_extractor.pkl` - Feature config
- `models/feature_names.txt` - Feature names
- `models/classifier_report.txt` - Performance metrics

## Deployment
After training, copy models and inference code to `../backend/ml_models/` and `../backend/ml_pipeline/`
