import pandas as pd
from pathlib import Path

RAW_FILE = Path("data/raw/crypto_raw.csv")
PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def clean_crypto_data(input_file: Path) -> pd.DataFrame:
    if not input_file.exists():
        raise FileNotFoundError(f"{input_file} not found. Run data_collection.py first.")
    
    df = pd.read_csv(input_file)

    selected_colunms = [
        "id",
        "symbol",
        "name",
        "current_price",
        "market_cap",
        "total_volume",
        "circulating_supply",

"price_change_percentage_24h_in_currency",

"price_change_percentage_7d_in_currency",

"price_change_percentage_30d_in_currency"
    ]

    existing_columns = [col for col in selected_colunms if col in df.columns]
    df = df[existing_columns].copy()

    numeric_columns = [
        "current_price",
        "market_cap",
        "total_volume",
        "circulating_supply",

"price_change_percentage_24h_in_currency",

"price_change_percentage_7d_in_currency",

"price_change_percentage_30d_in_currency"   
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            
    df = df.drop_duplicates(subset=["id", "symbol", "name"])
    df = df.dropna(subset=["id", "symbol", "name"])

    for col in numeric_columns:
        if col in df.columns:
            df[col] = df[col].fillna(df[col].median())

    return df

def save_clean_data(df: pd.DataFrame, filename: str = "crypto_clean.csv") -> None:
    output_path = PROCESSED_DIR/filename
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned data to {output_path}")

if __name__ == "__main__":
    cleaned_df = clean_crypto_data(RAW_FILE)
    save_clean_data(cleaned_df)
    print(cleaned_df.head())