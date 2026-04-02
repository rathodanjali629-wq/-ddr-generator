from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()

def generate_ddr(inspection_text, thermal_text):
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))

    prompt = """You are a professional property inspection report writer.

Generate a complete DDR (Detailed Diagnostic Report) with this structure:

1. PROPERTY ISSUE SUMMARY
2. AREA-WISE OBSERVATIONS
3. PROBABLE ROOT CAUSE
4. SEVERITY ASSESSMENT (Low/Medium/High with reasoning)
5. RECOMMENDED ACTIONS
6. ADDITIONAL NOTES
7. MISSING OR UNCLEAR INFORMATION (write Not Available if needed)

Rules:
- Do NOT invent facts not present in documents
- If info missing write Not Available
- If conflict mention the conflict
- Use simple client-friendly language

--- INSPECTION REPORT ---
""" + inspection_text + """

--- THERMAL REPORT ---
""" + thermal_text + """

Generate complete DDR now:
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4000
    )

    return response.choices[0].message.content