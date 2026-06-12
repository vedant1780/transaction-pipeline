import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY not found in environment variables"
    )

client = genai.Client(
    api_key=api_key
)


def generate_summary(
    raw_rows,
    clean_rows,
    anomalies,
    category_breakdown
):
    prompt = f"""
Generate a concise financial report.

Raw rows: {raw_rows}
Clean rows: {clean_rows}

Anomaly Count: {len(anomalies)}

Anomalies:
{anomalies}

Category Breakdown:
{category_breakdown}

Provide:
1. Data quality assessment
2. Spending insights
3. Anomaly observations
4. Risk assessment
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:

        return (
            "AI summary unavailable. "
            f"Reason: {str(e)}"
        )