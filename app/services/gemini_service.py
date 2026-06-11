import os
from google import genai

client = genai.Client(
    api_key="AQ.Ab8RN6LXVmPuRTOW2A4WSGP5XkEW-Gkh7F2lZ_S6e1TQ3rF9Fg"
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

Anomalies:
{anomalies}

Category Breakdown:
{category_breakdown}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text