import requests
import pandas as pd
from pathlib import Path
from datetime import datetime

print("This data was collected at:", datetime.now())

API_URL = "https://api.coingecko.com/api/v3/coins/markets" 
RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)


def fetch_crypto_data(vs_currency: str = "usd", per_page: int = 70, page: int = 1) -> pd.DataFrame:
    params = {
        "vs_currency": vs_currency,
        "order": "market_cap_desc",
        "per_page": per_page,
        "sparkline": False,
        "price_change_percentage": "24h, 7d, 30d"
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data:
        raise ValueError("No data returned from gecko API")
    df = pd.DataFrame(data)
    return df


def save_raw_data(df: pd.DataFrame, filename: str = "crypto_raw.csv") -> None:
    output_path = RAW_DIR / filename
    df.to_csv(output_path, index=False)
    print(f"saved raw data to {output_path}")

if __name__ == "__main__":
    crypto_df = fetch_crypto_data()
    crypto_df["data_collected_at"] = datetime.now()
    save_raw_data(crypto_df)
    print(crypto_df[["id", "symbol", "name", "current_price", "market_cap"]].head())