import pandas as pd

DOMESTIC_BRANDS = [
    "SWIGGY",
    "OLA",
    "IRCTC"
]

def detect_anomalies(df):

    anomalies = []

    df["is_anomaly"] = False
    df["anomaly_reason"] = None

    # Rule 1: Amount > 3x account median
    for account_id, group in df.groupby("account_id"):

        median_amount = group["amount"].median()
        threshold = median_amount * 3

        for index, row in group.iterrows():

            if row["amount"] > threshold:

                df.loc[index, "is_anomaly"] = True
                df.loc[index, "anomaly_reason"] = (
                    "Amount exceeds 3x account median"
                )

                anomalies.append({
                    "txn_id": row["txn_id"],
                    "reason": "Amount exceeds 3x account median"
                })

    # Rule 2: Domestic merchant with USD
    for index, row in df.iterrows():

        merchant = str(row["merchant"]).upper().strip()
        currency = str(row["currency"]).upper().strip()

        if merchant in DOMESTIC_BRANDS and currency == "USD":

            df.loc[index, "is_anomaly"] = True

            if pd.isna(df.loc[index, "anomaly_reason"]):
                df.loc[index, "anomaly_reason"] = (
                    "Domestic merchant with USD currency"
                )
            else:
                df.loc[index, "anomaly_reason"] += (
                    "; Domestic merchant with USD currency"
                )

            anomalies.append({
                "txn_id": row["txn_id"],
                "reason": "Domestic merchant with USD currency"
            })

    return df, anomalies