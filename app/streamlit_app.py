from pathlib import Path
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Crypto Intelligence & Risk Screening System",
    page_icon="📊",
    layout="wide"
)

language = st.sidebar.selectbox(
    label="Language / اللغة",
    options=["English", "العربية"],
    key="language_selector"
)

TEXT = {
    "English": {
        "title": "Crypto Intelligence & Risk Screening System",
        "caption": "A data-driven framework for screening cryptocurrency assets using volatility, speculation, liquidity, and strategic risk indicators.",
        "beta": "Beta Version: Live analytical prototype",
        "disclaimer": "This platform is a decision-support intelligence tool and not financial advice.",
        "dataset": "Dataset",
        "analysis": "Coin Analysis",
        "visuals": "Visuals",
    },
    "العربية": {
        "title": "نظام استخباراتي لتحليل مخاطر العملات الرقمية",
        "caption": "إطار قائم على البيانات لفحص العملات الرقمية باستخدام مؤشرات التقلب، المضاربة، السيولة، والمخاطر.",
        "beta": "نسخة تجريبية: نموذج تحليلي قابل للاستخدام",
        "disclaimer": "هذا النظام أداة مساعدة لاتخاذ القرار وليس نصيحة مالية.",
        "dataset": "البيانات",
        "analysis": "تحليل العملة",
        "visuals": "الرسوم البيانية",
    }
}

DATA_FILE = Path("data/processed/crypto_features.csv")
FIGURES_DIR = Path("outputs/figures")

@st.cache_data
def load_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(
            "crypto_features.csv not found. Run your backend pipeline first."
        )
    df = pd.read_csv(file_path)

    if "risk_score" not in df.columns and "shariah_risk_score" in df.columns:
        df["risk_score"] = df["shariah_risk_score"]

    if "classification" in df.columns:
        df["classification"] = df["classification"].replace({
            "halal_candidate": "Stable",
            "low_risk": "Stable",
            "doubtdul": "Watchlist",
            "high_risk": "High Volatility"
        })

    return df

def show_metric_cards(df: pd.DataFrame) -> None:
    total_coins = len(df)
    avg_risk = df["risk_score"].mean()

    stable_count = (df["classification"] == "Stable").sum()
    watchlist_count = (df["classification"] == "Watchlist").sum()
    high_volatility_count = (df["classification"] == "High Volatility").sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Coins", total_coins)
    col2.metric("Average Risk Score", f"{avg_risk:.2f}")
    col3.metric("Stable", stable_count)
    col4.metric("Watchlist", watchlist_count)
    col5.metric("High Volatility", high_volatility_count)

def show_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    classifications = sorted(df["classification"].dropna().unique().tolist())

    selected_classes = st.sidebar.multiselect(
        "Select Classification",
        options=classifications,
        default=classifications
    )

    min_risk = float(df["risk_score"].min())
    max_risk = float(df["risk_score"].max())

    risk_range = st.sidebar.slider(
        "Risk Score Range",
        min_value=min_risk,
        max_value=max_risk,
        value=(min_risk, max_risk)
    )

    search_term = st.sidebar.text_input("Search Coin Name or Symbol")

    filtered_df = df.copy()

    if selected_classes:
        filtered_df = filtered_df[
            filtered_df["classification"].isin(selected_classes)
        ]

    filtered_df = filtered_df[
        (filtered_df["risk_score"] >= risk_range[0]) &
        (filtered_df["risk_score"] <= risk_range[1])
    ]

    if search_term:
        search_term = search_term.lower().strip()

        filtered_df = filtered_df[

            filtered_df["name"].astype(str).str.lower().str.contains(search_term, na=False) |

            filtered_df["symbol"].astype(str).str.lower().str.contains(search_term, na=False)
        ]

    return filtered_df

def show_top_table(df: pd.DataFrame) -> None:
    st.subheader("Screened Cryptocurrency Assets")
    if df.empty:
        st.warning("No coins match selected filters.")
        return
    display_columns = {
        "name": "Name",
        "symbol": "Symbol",
        "market_cap": "Market Cap",
        "volatility_score": "Volatility Score",
        "speculation_score": "Speculation Score",
        "liquidity_score": "Liquidity Score",
        "risk_score": "Risk Score",
        "classification": "Classification"
    }

    available_columns = [col for col in display_columns if col in df.columns]

    sort_map = {
            "Risk Score": "risk_score",
            "Market Cap": "market_cap",
            "Volatility": "volatility_score",
            "Speculaton": "speculation_score",
            "Liquidity": "liquidity_score"
    }

    sort_option = st.selectbox(
        "Sort Table By",
    options=list(sort_map.keys()),
    key="sort_selector"
)

    ascending = st.checkbox("Sort Ascending", value=False)

    table_df = df[available_columns].sort_values(
        by=sort_map[sort_option],
        ascending=ascending
    )
    
    st.dataframe(
        table_df.style.format({
            "market_cap": "${:,.0f}",
            "risk_score": "{:.2f}",
            "volatility_score": "{:.2f}",
            "speculation_score": "{:.2f}",
            "liquidity_score": "{:.2f}",
        }),
        use_container_width=True
    )

def show_coin_breakdown(df: pd.DataFrame) -> None:
    st.subheader("Single Coin Breakdown")

    coin_names = df["name"].dropna().unique().tolist()

    if not coin_names:
        st.info("No coin names available.")
        return
    
    selected_coin = st.selectbox(
        "Choose a Coin",
        options=sorted(coin_names)
    )

    coin_row = df[df["name"] == selected_coin].iloc[0]

    vol = coin_row["volatility_score"]
    spec = coin_row["speculation_score"]
    liq = coin_row["liquidity_score"]
    risk = coin_row["risk_score"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Volatility", f"{vol:.3f}")
    col2.metric("Speculation", f"{spec:.3f}")
    col3.metric("Liquidity", f"{liq:.3f}")
    col4.metric("Risk Score", f"{risk:.3f}")

    st.write(f"### Classification: {coin_row['classification']}")

    # WHY THIS CLASSIFICATION
    st.subheader("Why This Classification?")

    score_map = {
        "Volatility": vol,
        "Speculation": spec,
        "Liquidity": liq
    }

    dominant_factor = max(score_map.items(), key=lambda item: item[1])[0]
    
    st.write(f"**Volatility Score:** {vol:.3f}")
    st.write(f"**Speculation Score:** {spec:.3f}")
    st.write(f"**Liquidity Score:** {liq:.3f}")
    st.info(f"Primary driver of this classification: {dominant_factor}")

    if coin_row["classification"] == "High Volatility":
        st.error(
            "This asset shows elevated combined indicators and is currently classified as high volatility asset."
        )
    elif coin_row["classification"] == "Watchlist":
        st.warning(
            "This asset falls into a watchlist category and may require deeper review."
        )
    else:
        st.success(
            "This asset currently demonstrates relatively stable model indicators."
        )
    st.caption(
        "Disclaimer: Risk classifications reflect this model's volatility, liquidity, and speculation framework - not project legitimacy or guaranteed financial outcome."
    )

def show_figures() -> None:
    st.subheader("Visual Outputs")

    figure_files = [
        ("Risk Distribution", FIGURES_DIR / "risk_distribution.png"),
        ("Top 10 Risk Scores", FIGURES_DIR / "top_10_risk_scores.png"),
        ("Classification Counts", FIGURES_DIR / "classification_counts.png")
    ]

    cols = st.columns(len(figure_files))

    for col, (title, fig_path) in zip(cols, figure_files):
        with col:
            st.markdown(""" 
            ### Smarter crypto screening using data-driven risk indicators.
            Evaluate assests through volatility, speculation, liquidity, and risk behavior.
                        """)
            if fig_path.exists():
                st.image(str(fig_path), use_container_width=True)
            else:
                st.info("Visual currently unavailable.")

def main() -> None:

    t = TEXT[language]

    st.title(t["title"])
    st.caption(t["caption"])
    st.info(t["beta"])
    st.warning(t["disclaimer"])

    tab1, tab2, tab3 = st.tabs(
        [t["dataset"], t["analysis"], t["visuals"]]
    )

    try:
        df = load_data(DATA_FILE)
        if "data_collected_at" in df.columns:
            last_updated = df["data_collected_at"].iloc[0]
            st.caption(f"Last Updated: {last_updated}")

            st.caption("Data source: processed crypto market dataset.")
        
    except Exception as e:
        st.error(str(e))
        st.stop()

    # METRICS
    show_metric_cards(df)
    
    st.markdown("---")

    # FILTERED DATA
    filtered_df = show_filters(df)
    # TABS
    tab1, tab2, tab3 = st.tabs(
        ["Dataset", "Coin Analysis", "Visuals"]
    )

    with tab1:
        show_top_table(filtered_df)

    with tab2:
        if filtered_df.empty:
            show_coin_breakdown(df)

        else:
            show_coin_breakdown(filtered_df)
    with tab3:
        show_figures()
  
if __name__ == "__main__":
    main()