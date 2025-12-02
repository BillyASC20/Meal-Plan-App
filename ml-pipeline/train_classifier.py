"""
Train health risk classifier for ingredients.
Uses rule-based labeling combined with ML for generalization.
"""

import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from health_rules import classify_ingredient_health_risk, get_risk_level
from feature_engineering import IngredientFeatureExtractor, normalize_ingredient_name


def load_and_prepare_data(data_dir='data'):
    """Load CSV files and prepare training data."""
    print("Loading ingredient data...")
    
    # Try to load all available CSV files
    data_dir = Path(data_dir)
    ingredients = []
    
    # Load ingredient_6L.csv
    if (data_dir / 'ingredient_6L.csv').exists():
        df = pd.read_csv(data_dir / 'ingredient_6L.csv')
        if 'name' in df.columns:
            ingredients.extend(df['name'].dropna().tolist())
    
    # Load unique_indexed_ingredients.csv
    if (data_dir / 'unique_indexed_ingredients.csv').exists():
        df = pd.read_csv(data_dir / 'unique_indexed_ingredients.csv')
        if 'descrip' in df.columns:
            ingredients.extend(df['descrip'].dropna().tolist())
    
    # Load cleaned_ingredients.csv
    if (data_dir / 'cleaned_ingredients.csv').exists():
        df = pd.read_csv(data_dir / 'cleaned_ingredients.csv')
        # Try common column names
        for col in df.columns:
            if 'name' in col.lower() or 'ingredient' in col.lower():
                ingredients.extend(df[col].dropna().tolist())
                break
    
    if not ingredients:
        raise ValueError("No ingredient data found. Please place CSV files in data/ directory")
    
    # Remove duplicates and normalize
    ingredients = list(set(ingredients))
    ingredients = [normalize_ingredient_name(ing) for ing in ingredients]
    
    print(f"Loaded {len(ingredients)} unique ingredients")
    return ingredients


def create_labeled_dataset(ingredients):
    """Create labeled dataset using rule-based classification."""
    print("Creating labeled dataset...")
    
    data = []
    for ingredient in ingredients:
        risks = classify_ingredient_health_risk(ingredient)
        risk_level = get_risk_level(risks)
        
        data.append({
            'ingredient': ingredient,
            'risk_level': risk_level,
            **risks  # Include individual risk flags
        })
    
    df = pd.DataFrame(data)
    
    # Print class distribution
    print("\nClass distribution:")
    print(df['risk_level'].value_counts())
    print(f"\nTotal samples: {len(df)}")
    
    return df


def extract_features(df, extractor):
    """Extract features from ingredient names."""
    print("Extracting features...")
    
    feature_matrix = extractor.extract_batch_features(df['ingredient'].tolist())
    feature_names = extractor.get_feature_names()
    
    X = pd.DataFrame(feature_matrix, columns=feature_names)
    y = df['risk_level']
    
    return X, y, feature_names


def train_models(X_train, X_test, y_train, y_test, feature_names):
    """Train multiple classifiers and return the best one."""
    print("\nTraining classifiers...")
    
    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            class_weight='balanced'
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    results = {}
    for name, model in models.items():
        print(f"\nTraining {name}...")
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"{name} Accuracy: {accuracy:.4f}")
        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'predictions': y_pred
        }
    
    # Choose best model
    best_model_name = max(results, key=lambda k: results[k]['accuracy'])
    best_model = results[best_model_name]['model']
    
    print(f"\n✅ Best model: {best_model_name}")
    
    return best_model, scaler, results


def plot_feature_importance(model, feature_names, output_path='models/feature_importance.png'):
    """Plot and save feature importance."""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        
        plt.figure(figsize=(10, 8))
        plt.title('Feature Importances')
        plt.barh(range(len(indices)), importances[indices])
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.xlabel('Relative Importance')
        plt.tight_layout()
        plt.savefig(output_path)
        print(f"Feature importance plot saved to {output_path}")
        plt.close()


def plot_confusion_matrix(y_test, y_pred, output_path='models/confusion_matrix.png'):
    """Plot and save confusion matrix."""
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig(output_path)
    print(f"Confusion matrix saved to {output_path}")
    plt.close()


def save_model(model, scaler, extractor, feature_names, output_dir='models'):
    """Save trained model and associated objects."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Save model
    joblib.dump(model, output_dir / 'health_risk_classifier.pkl')
    joblib.dump(scaler, output_dir / 'feature_scaler.pkl')
    joblib.dump(extractor, output_dir / 'feature_extractor.pkl')
    
    # Save feature names
    with open(output_dir / 'feature_names.txt', 'w') as f:
        f.write('\n'.join(feature_names))
    
    print(f"\n✅ Model saved to {output_dir}/")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("INGREDIENT HEALTH RISK CLASSIFIER - TRAINING PIPELINE")
    print("=" * 60)
    
    # Load data
    ingredients = load_and_prepare_data('data')
    
    # Create labeled dataset
    df = create_labeled_dataset(ingredients)
    
    # Save labeled dataset for reference
    df.to_csv('models/labeled_ingredients.csv', index=False)
    print(f"\nLabeled dataset saved to models/labeled_ingredients.csv")
    
    # Extract features
    extractor = IngredientFeatureExtractor()
    X, y, feature_names = extract_features(df, extractor)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train models
    best_model, scaler, results = train_models(X_train, X_test, y_train, y_test, feature_names)
    
    # Get best predictions for visualization
    best_model_name = max(results, key=lambda k: results[k]['accuracy'])
    y_pred = results[best_model_name]['predictions']
    
    # Plot feature importance
    plot_feature_importance(best_model, feature_names)
    
    # Plot confusion matrix
    plot_confusion_matrix(y_test, y_pred)
    
    # Save model
    save_model(best_model, scaler, extractor, feature_names)
    
    # Save classification report
    with open('models/classifier_report.txt', 'w') as f:
        f.write("INGREDIENT HEALTH RISK CLASSIFIER - EVALUATION REPORT\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Best Model: {best_model_name}\n")
        f.write(f"Accuracy: {results[best_model_name]['accuracy']:.4f}\n\n")
        f.write("Classification Report:\n")
        f.write(classification_report(y_test, y_pred))
    
    print("\n" + "=" * 60)
    print("✅ TRAINING COMPLETE")
    print("=" * 60)
    print("\nModel files saved in models/ directory:")
    print("  - health_risk_classifier.pkl")
    print("  - feature_scaler.pkl")
    print("  - feature_extractor.pkl")
    print("  - feature_names.txt")
    print("  - labeled_ingredients.csv")
    print("  - classifier_report.txt")
    print("  - feature_importance.png")
    print("  - confusion_matrix.png")
    print("\nUse predict.py to classify new ingredients!")


if __name__ == '__main__':
    main()
