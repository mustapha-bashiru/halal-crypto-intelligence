import pandas as pd
from pathlib import Path

INPUT_FILE = Path("data/processed/crypto_clean.csv")
OUTPUT_FILE =  Path("data/processed/crypto_features.csv")


def min_max_scale(series: pd.Series) -> pd.Series:
    min_val = series.min()
    max_val = series.max()

    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series([0.0] * len(series), index=series.index)
    
    return (series - min_val) / (max_val - min_val)

def compute_volatility_score(df: pd.DataFrame) -> pd.Series:
    raw_volatility = (

df["price_change_percentage_24h_in_currency"].abs() +

df["price_change_percentage_7d_in_currency"].abs() +

df["price_change_percentage_30d_in_currency"].abs() 
    
    ) / 3
    return min_max_scale(raw_volatility)


def compute_speculation_score(df: pd.DataFrame) -> pd.Series:
    raw_speculation = df["total_volume"] / (df["market_cap"] + 1)
    return min_max_scale(raw_speculation)

def compute_liquidity_score(df: pd.DataFrame) -> pd.Series:
    raw_liquidity = df["total_volume"] / (df["circulating_supply"] + 1)
    return min_max_scale(raw_liquidity)

def compute_shariah_risk(volatility: pd.Series, speculation: pd.Series, liquidity: pd.Series) -> pd.Series:
    # this is a simple model(improve later)
    return (0.5 * volatility) + (0.3 * speculation) + (0.2 * liquidity)


def classify_shariah(score: float) -> str:
    if score < 0.35:
        return "halal_candidate"
    elif score < 0.65:
        return "doubtful"
    else:
        return "high_risk"


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df["volatility_score"] = compute_liquidity_score(df)
    df["speculation_score"] = compute_speculation_score(df)
    df["liquidity_score"] = compute_liquidity_score(df)

    df["shariah_risk_score"] = compute_shariah_risk(
        df["volatility_score"],
        df["speculation_score"],
        df["liquidity_score"]
    )

    df["classification"] = df["shariah_risk_score"].apply(classify_shariah)
    return df

def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError("Run data_cleaning.py first")
    
    df = pd.read_csv(INPUT_FILE)
    df = add_features(df)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Feature engineering complete. Saved to: {OUTPUT_FILE}")
    print(df[[
        "name", 
        "shariah_risk_score", 
        "classification",
        "liquidity_score",
        "speculation_score",
        "volatility_score"
        ]].head())

if __name__ == "__main__": 
    main()