import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

INPUT_FILE = Path("data/processed/crypto_features.csv")
OUTPUT_DIR = Path("outputs/tables")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    if not INPUT_FILE.exists():
        raise FileNotFoundError("Run feature_engineering.py first.")
    return pd.read_csv(INPUT_FILE)


def train_model(df: pd.DataFrame):
    feature_columns = [
        "volatility_score",
        "speculation_score",
        "liquidity_score",
        "shariah_risk_score"
    ]

    X = df[feature_columns]
    y = df["classification"]

    print("\nClass distribution:")
    print(y.value_counts())

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return model, X_test, y_test, y_pred, feature_columns


def save_results(y_test, y_pred):
    report = classification_report(y_test, y_pred, output_dict=True, zero_division=0)
    report_df = pd.DataFrame(report).transpose()
    report_path = OUTPUT_DIR / "classification_report.csv"
    report_df.to_csv(report_path)

    matrix = confusion_matrix(y_test, y_pred)
    matrix_df = pd.DataFrame(matrix)
    matrix_path = OUTPUT_DIR / "confusion_matrix.csv"
    matrix_df.to_csv(matrix_path, index=False)

    print(f"Saved classification report to: {report_path}")
    print(f"Saved confusion matrix to: {matrix_path}")


def show_feature_importance(model, feature_columns):
    importance_df = pd.DataFrame({
        "feature": feature_columns,
        "importance": model.feature_importances_
    }).sort_values("importance", ascending=False)

    output_path = OUTPUT_DIR / "feature_importance.csv"
    importance_df.to_csv(output_path, index=False)

    print("\nFeature Importance:")
    print(importance_df)
    print(f"\nSaved feature importance to: {output_path}")


def main():
    df = load_data()
    model, X_test, y_test, y_pred, feature_columns = train_model(df)

    acc = accuracy_score(y_test, y_pred)
    print(f"Model Accuracy: {acc:.4f}\n")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, zero_division=0))

    save_results(y_test, y_pred)
    show_feature_importance(model, feature_columns)


if __name__ == "__main__":
    main()