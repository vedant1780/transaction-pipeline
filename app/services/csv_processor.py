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

    # IMPORTANT:
    # Replace all NaN values AFTER all processing
    df = df.replace({float("nan"): None})

    return {
        "raw_rows": raw_rows,
        "clean_rows": clean_rows,
        "data": df.to_dict(orient="records"),
        "anomalies": anomalies,
        "category_breakdown": category_breakdown
    }