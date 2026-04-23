from pathlib import Path
import pandas as pd
import streamlit as st
 
st.set_page_config(
    page_title="Halal Cryptocurrency Intelligence ",
    page_icon="📊",
    layout="wide"
)

DATA_FILE = Path("data/processed/crypto_features.csv")
FIGURES_DIR = Path("outputs/figures")

@st.cache_data
def load_data(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        raise FileNotFoundError(
            "crypto_features.csv not found. Run data_collection.py, "
            "data_cleaning.py, and feature_engineering.py first."
        )
    return pd.read_csv(file_path)

def show_metric_cards(df: pd.DataFrame) -> None:
    total_coins = len(df)
    avg_risk = df["shariah_risk_score"].mean()

    halal_count = (df["classification"] == "halal_candidate").sum()
    doubtful_count = (df["classification"] == "doubtful").sum()
    high_risk_count = (df["classification"] == "high_risk").sum()

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Coins", total_coins)
    col2.metric("Average Risk Score", f"{avg_risk:.3f}")
    col3.metric("Halal Candidate", halal_count)
    col4.metric("Doubtful", doubtful_count)
    col5.metric("High Risk", high_risk_count)

def show_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.header("Filters")

    classifications = sorted(df["classification"].dropna().unique().tolist())
    selected_classes = st.sidebar.multiselect(
        "Select classification",
        options=classifications,
        default=classifications
    )

    min_risk, max_risk = float(df["shariah_risk_score"].min()), float(df["shariah_risk_score"].max())
    risk_range = st.sidebar.slider(
        "Shariah risk score range",
        min_value=min_risk,
        max_value=max_risk,
        value=(min_risk, max_risk)
    )

    search_term = st.sidebar.text_input("Search coin name or symbol")

    filtered_df = df.copy()

    if selected_classes:
        filtered_df = filtered_df[filtered_df["classification"].isin(selected_classes)]

    filtered_df = filtered_df[
        (filtered_df["shariah_risk_score"] >= risk_range[0]) &
        (filtered_df["shariah_risk_score"] <= risk_range[1])
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

    display_columns = [
        "name",
        "symbol",
        "market_cap",
        "volatility_score",
        "speculation_score",
        "liquidity_score",
        "shariah_risk_score",
        "classification"
    ]

    available_columns = [col for col in display_columns if col in df.columns]
    sort_option = st.selectbox(
        "Sort table by",
        options=[
            "shariah_risk_score",
            "market_cap",
            "volatility_score",
            "speculation_score",
            "liquidity_score"
        ]
    )

    ascending = st.checkbox("Sort ascending", value=False)

    table_df = df[available_columns].sort_values(by=sort_option, ascending=ascending)
    st.dataframe(
    table_df.style.format({
        "market_cap": "${:,.0f}",
        "current_price": "${:,.2f}",
        "total_volume": "{:,.0f}",
        "shariah_risk_score": "{:.3f}",
        "volatility_score": "{:.3f}",
        "speculation_score": "{:.3f}",
        "liquidity_score": "{:.3f}",
    }),
    use_container_width=True
)

def show_coin_breakdown(df: pd.DataFrame) -> None:
    st.subheader("Single Coin Breakdown")

    # Get coin names
    coin_names = df["name"].dropna().unique().tolist()

    if not coin_names:
        st.info("No coin names available.")
        return

    # Select coin
    selected_coin = st.selectbox("Choose a coin", options=sorted(coin_names))

    # Get selected coin data
    coin_row = df[df["name"] == selected_coin].iloc[0]

    # Show main metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Volatility Score", f"{coin_row['volatility_score']:.3f}")
    col2.metric("Speculation Score", f"{coin_row['speculation_score']:.3f}")
    col3.metric("Liquidity Score", f"{coin_row['liquidity_score']:.3f}")
    col4.metric("Risk Score", f"{coin_row['shariah_risk_score']:.3f}")

    st.write(f"**Classification:** {coin_row['classification']}")

    # 🔥 WHY EXPLANATION
    st.subheader("Why this classification?")

    vol = coin_row["volatility_score"]
    spec = coin_row["speculation_score"]
    liq = coin_row["liquidity_score"]

    st.write(f"Volatility Score: {vol:.3f}")
    st.write(f"Speculation Score: {spec:.3f}")
    st.write(f"Liquidity Score: {liq:.3f}")

    # Feature dominance explanation
    if vol > spec and vol > liq:
        st.info("This coin is mainly driven by HIGH VOLATILITY.")
    elif spec > vol and spec > liq:
        st.info("This coin shows HIGH SPECULATION (trading activity).")
    else:
        st.info("This coin has notable LIQUIDITY impact.")

    # Final classification explanation
    if coin_row["classification"] == "high_risk":
        st.error("Overall classification is HIGH RISK due to elevated combined indicators.")
    elif coin_row["classification"] == "doubtful":
        st.warning("This coin falls into a moderate risk category.")
    else:
        st.success("This coin shows relatively low risk indicators.")

    st.write(f"**Classification:** {coin_row['classification']}")
    st.write(
                """
This score is a prototype screening output based on engineered market indicators.
It is not a final Shariah ruling, but a transparent analytical framework.
"""
    )

def show_figures() -> None:
    st.subheader("Visual Outputs")

    figure_files = [
        ("Risk Distribution", FIGURES_DIR / "risk_distribution.png"),
        ("Top 10 Risk Scores", FIGURES_DIR / "top_10_risk_scores.png"),
        ("Classification Counts", FIGURES_DIR / "classification_counts.png"),
    ]

    cols = st.columns(len(figure_files))

    for col, (title, fig_path) in zip(cols, figure_files):
        with col:
            st.markdown(f"**{title}**")
            if fig_path.exists():
                st.image(str(fig_path), use_container_width=True)
            else:
                st.warning(f"{fig_path.name} not found. Run visualization.py first.")

def show_feature_importance() -> None:
    st.subheader("Feature Importance")

    feature_file = Path("outputs/tables/feature_importance.csv")

    if not feature_file.exists():
        st.warning("feature_importance.csv not found. Run screening_model.py first.")
        return

    importance_df = pd.read_csv(feature_file)

    if importance_df.empty:
        st.info("No feature importance data available.")
        return

    st.dataframe(importance_df, use_container_width=True)

    st.bar_chart(
        importance_df.set_index("feature")["importance"]
    )

    top_feature = importance_df.iloc[0]
    st.info(
        f"The most influential feature in the model is "
        f"'{top_feature['feature']}' with importance score "
        f"{top_feature['importance']:.3f}."
    )

def main() -> None:
    st.title("Halal Cryptocurrency Intelligence System")
    st.caption(
        "A data-driven framework for screening cryptocurrency assets through "
        "engineered financial indicators inspired by Islamic finance principles."
    )

    try:
        df = load_data(DATA_FILE)
        if "data_collected_at" in df.columns: 
            last_updated = df["data_collected_at"].iloc(0)
            st.caption(f"Last Updated: {last_updated}")

        if st.button("Refresh Data"):
            st.write("Run backend scripts to fetch new data")

    except Exception as e:
        st.error(str(e))
        st.stop()

    show_metric_cards(df)

    st.markdown("---")
    filtered_df = show_filters(df)

    tab1, tab2, tab3, tab4 = st.tabs(
    ["Dataset", "Coin Analysis", "Visuals", "Feature Importance"]
)

    with tab1:
        show_top_table(filtered_df)

    with tab2:
        show_coin_breakdown(filtered_df if not filtered_df.empty else df)

    with tab3:
        show_figures()

    with tab4:
        show_feature_importance()

if __name__ == "__main__":
    main()