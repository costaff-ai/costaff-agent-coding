---
name: machine-learning
description: "Train, evaluate, and tune machine learning models with scikit-learn: classification, regression, cross-validation, hyperparameter tuning, and model persistence. Use when asked to predict, classify, build a model, or train an algorithm."
---

# Machine Learning Skill

## Required Packages
```
pip_install("scikit-learn pandas numpy joblib")
pip_install("xgboost lightgbm")   # optional: gradient boosting
```

## 1. Data Split
```python
from sklearn.model_selection import train_test_split

X = df.drop(columns=["target"])
y = df["target"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y  # remove stratify for regression
)
print(f"Train: {X_train.shape}, Test: {X_test.shape}")
```

## 2. Classification

### Choose a model
```python
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

model = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
# model = LogisticRegression(max_iter=1000, random_state=42)
```

### Train and evaluate
```python
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix, roc_auc_score
)
import numpy as np

model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]  # binary only

print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
print(f"ROC-AUC  : {roc_auc_score(y_test, y_prob):.4f}")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
```

## 3. Regression

### Choose a model
```python
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge, Lasso

model = RandomForestRegressor(n_estimators=200, random_state=42, n_jobs=-1)
# model = Ridge(alpha=1.0)
```

### Train and evaluate
```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mae  = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2   = r2_score(y_test, y_pred)

print(f"MAE : {mae:.4f}")
print(f"RMSE: {rmse:.4f}")
print(f"R²  : {r2:.4f}")
```

## 4. Cross-Validation
```python
from sklearn.model_selection import cross_val_score, StratifiedKFold
import numpy as np

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)  # use KFold for regression

# Classification
scores = cross_val_score(model, X, y, cv=cv, scoring="roc_auc", n_jobs=-1)
print(f"CV AUC: {scores.mean():.4f} ± {scores.std():.4f}")

# Regression
scores = cross_val_score(model, X, y, cv=5, scoring="neg_root_mean_squared_error", n_jobs=-1)
print(f"CV RMSE: {(-scores).mean():.4f} ± {(-scores).std():.4f}")
```

## 5. Hyperparameter Tuning

### RandomizedSearchCV (faster)
```python
from sklearn.model_selection import RandomizedSearchCV

param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [None, 5, 10, 20],
    "min_samples_split": [2, 5, 10],
    "max_features": ["sqrt", "log2"],
}

search = RandomizedSearchCV(
    model, param_grid, n_iter=20, cv=5,
    scoring="roc_auc", random_state=42, n_jobs=-1, verbose=1
)
search.fit(X_train, y_train)
print("Best params:", search.best_params_)
print(f"Best CV AUC: {search.best_score_:.4f}")
best_model = search.best_estimator_
```

## 6. Pipeline (preprocessing + model)
```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

numeric_features = X.select_dtypes("number").columns.tolist()
categorical_features = X.select_dtypes(["object", "category"]).columns.tolist()

numeric_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])
categorical_transformer = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
])

preprocessor = ColumnTransformer([
    ("num", numeric_transformer, numeric_features),
    ("cat", categorical_transformer, categorical_features),
])

pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("model", RandomForestClassifier(n_estimators=200, random_state=42)),
])

pipeline.fit(X_train, y_train)
y_pred = pipeline.predict(X_test)
print(f"Pipeline Accuracy: {accuracy_score(y_test, y_pred):.4f}")
```

## 7. Feature Importance
```python
import pandas as pd
import matplotlib.pyplot as plt

# For tree-based models
importances = pd.Series(
    model.feature_importances_, index=X_train.columns
).sort_values(ascending=False)

print(importances.head(20))

importances.head(20).plot.barh(figsize=(8, 8))
plt.title("Feature Importance")
plt.tight_layout()
plt.savefig("feature_importance.png", dpi=150)
plt.close()
```

## 8. Save and Load Model
```python
import joblib

# Save
joblib.dump(pipeline, "model.pkl")
print("Model saved to model.pkl")

# Load and predict
loaded = joblib.load("model.pkl")
predictions = loaded.predict(X_new)
```

## 9. Results Summary
```python
import json

summary = {
    "model": type(model).__name__,
    "train_samples": int(len(X_train)),
    "test_samples": int(len(X_test)),
    "accuracy": float(accuracy_score(y_test, y_pred)),
    "roc_auc": float(roc_auc_score(y_test, y_prob)),
    "top_features": importances.head(5).index.tolist(),
}
print(json.dumps(summary, indent=2))
```
