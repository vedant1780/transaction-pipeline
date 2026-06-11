import os
from google import genai
from dotenv import load_dotenv
load_dotenv()
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
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