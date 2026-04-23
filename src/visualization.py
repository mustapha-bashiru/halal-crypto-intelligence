import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

INPUT_FILE = Path("data/processed/crypto_features.csv")
OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def plot_risk_distribution(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    df["shariah_risk_score"].hist(bins=20)
    plt.title("Distribution of Shariah Risk Scores")
    plt.xlabel("Shariah Risk Score")
    plt.ylabel("Frequency")
    plt.tight_layout()

    output_path = OUTPUT_DIR / "risk_distribution.png"
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_top_coins(df: pd.DataFrame):
    top = df.sort_values("market_cap", ascending=False).head(10)

    plt.figure(figsize=(10, 6))
    plt.bar(top["symbol"], top["shariah_risk_score"])
    plt.title("Top 10 Coins by Market Cap: Shariah Risk Score")
    plt.xlabel("Coin Symbol")
    plt.ylabel("Shariah Risk Score")
    plt.tight_layout()

    output_path = OUTPUT_DIR / "top_10_risk_scores.png"
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_classification_counts(df):
    counts = df["classification"].value_counts()

    plt.figure(figsize=(8, 5))
    plt.bar(counts.index.astype(str), counts.to_numpy(dtype=float))

    plt.title("Classification Counts")
    plt.xlabel("Classification")
    plt.ylabel("Number of Coins")

    plt.tight_layout()
    plt.show()


    output_path = OUTPUT_DIR / "classification_counts.png"
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError("Run feature_engineering.py first.")

    df = pd.read_csv(INPUT_FILE)

    plot_risk_distribution(df)
    plot_top_coins(df)
    plot_classification_counts(df)


if __name__ == "__main__":
    main()