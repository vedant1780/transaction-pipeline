import pandas as pd
from dateutil import parser

from app.services.anomaly_detection import detect_anomalies


def load_csv(filepath: str):

    df = pd.read_csv(filepath)

    raw_rows = len(df)

    # Date normalization
    df["date"] = df["date"].apply(
        lambda x: parser.parse(str(x)).date().isoformat()
        if pd.notna(x)
        else None
    )

    # Amount cleanup
    df["amount"] = (
        df["amount"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
    )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce"
    )

    # Status normalization
    df["status"] = (
        df["status"]
        .fillna("UNKNOWN")
        .astype(str)
        .str.upper()
    )

    # Category normalization
    df["category"] = (
        df["category"]
        .fillna("Uncategorised")
    )

    # Currency normalization
    if "currency" in df.columns:
        df["currency"] = (
            df["currency"]
            .fillna("UNKNOWN")
            .astype(str)
            .str.upper()
        )

    # Remove rows missing critical fields
    required_columns = [
        "txn_id",
        "account_id",
        "amount"
    ]

    df = df.dropna(
        subset=required_columns
    )

    # Remove duplicates
    df = df.drop_duplicates()

    clean_rows = len(df)

    # Detect anomalies
    df, anomalies = detect_anomalies(df)

    # Category breakdown
    category_breakdown = (
        df.groupby("category")["amount"]
        .sum()
        .to_dict()
    )

    # Total INR spend
    total_spend_inr = (
        df.loc[
            df["currency"] == "INR",
            "amount"
        ]
        .sum()
    )

    # Total USD spend
    total_spend_usd = (
        df.loc[
            df["currency"] == "USD",
            "amount"
        ]
        .sum()
    )

    # Top 5 merchants
    top_merchants = (
        df.groupby("merchant")["amount"]
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .to_dict()
    )

    # Initialize LLM columns
    df["llm_category"] = None
    df["llm_raw_response"] = None
    df["llm_failed"] = False

    # Replace NaN for JSON serialization
    df = df.where(
        pd.notnull(df),
        None
    )

    return {
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "data": df.to_dict(
            orient="records"
        ),
        "anomalies": anomalies,
        "category_breakdown": category_breakdown,
        "total_spend_inr": float(
            total_spend_inr
        ),
        "total_spend_usd": float(
            total_spend_usd
        ),
        "top_merchants": top_merchants
    }